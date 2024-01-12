import inspect
import json
import os
import shutil
from pathlib import Path
from subprocess import check_call
import sys

import click
import polib

from oarepo_tools import validate_output_translations_dir, validate_source_paths

npm_proj_cwd = os.path.dirname(inspect.getfile(inspect.currentframe()))
npm_proj_env = dict(os.environ)


def ensure_i18next_output_translations(
    base_dir: Path, i18n_configuration: dict
) -> Path:
    """
    Checks if i18next output directory exists and contains the necessary `i18next.js` entrypoint.
    When missing, this function will createit.

    This will also install any necessary `react-i18next` dev dependencies from `package.json`.

    :param base_dir: Python package root directory (containing `setup.cfg` or `oarepo.yaml`)
    :param i18n_configuration:
    :return root directory path of i18next output translations
    :raises SystemExit
    """
    output_dir = validate_output_translations_dir(
        base_dir,
        i18n_configuration,
        "i18next_output_translations",
        create_if_missing=True,
    )
    if not output_dir:
        click.secho(
            f"configuration error: `i18next_output_translations` directory missing or invalid.",
            fg="red",
        )
        sys.exit(1)

    # check if i18next.js exists and if it does not, create it
    i18next_entrypoint = output_dir / "i18next.js"

    if not i18next_entrypoint.exists():
        shutil.copy(Path(__file__).parent / "i18next.js", i18next_entrypoint)
        click.secho(f"Created i18next.js in {i18next_entrypoint}", fg="green")
    else:
        shutil.copy(Path(__file__).parent / "i18next.js", i18next_entrypoint)
        click.secho(f"Updated i18next.js in {i18next_entrypoint}", fg="yellow")

    # Make sure NPM project is installed & up-to-date
    click.secho("Installing / updating React-i18next dependencies", fg="green")
    check_call(
        ["npm", "install"],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    return output_dir


def _json_to_pot(input_path: Path, output_path: Path) -> Path:
    # Generate gettext POT file from extracted JS translation strings
    check_call(
        ["npm", "run", "generate_pot", "--", input_path, output_path],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    return output_path


def extract_i18next_messages(base_dir: Path, temp_dir: Path, i18n_configuration):
    """
    Extracts all JS(X) i18next translation keys from `i18next_source_paths`
    using `i18next-scanner` and stores it in a `messages.pot` catalogue in the root of `temp_dir`.

    :param base_dir: Python package root directory (containing `setup.cfg` or `oarepo.yaml`)
    :param temp_dir: a temporary directory to store results (to not to overwrite ones from babel)
    :param i18n_configuration:
    :return: path to the resulting `messages.pot` catalogue
    """

    i18next_source_paths = validate_source_paths(
        base_dir, i18n_configuration, "i18next_source_paths"
    )

    if not i18next_source_paths:
        click.secho(
            f"Skipping i18next extraction: no valid source paths",
            fg="yellow",
        )
        return

    npm_proj_env["LANGUAGES"] = ",".join(i18n_configuration["languages"] or ["en"])

    source_path_patterns = [
        os.path.join(str(source_path), "**/*.{js,jsx,ts,tsx}")
        for source_path in i18next_source_paths
    ]

    # Extract JS translations strings
    click.secho(
        f"Extracting i18next messages from sources matching {source_path_patterns} -> {temp_dir}",
        fg="green",
    )
    check_call(
        [
            "npm",
            "run",
            "extract_messages",
            "--",
            "--output",
            temp_dir,
            *source_path_patterns,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    translations_file = temp_dir / "extracted-messages.json"
    extracted_data = json.loads(translations_file.read_text("utf-8"))

    # Fix any incorrectly extracted (e.g. by <Trans>) values, set all to ""
    for key in extracted_data.keys():
        extracted_data[key] = ""

    translations_file.write_text(json.dumps(extracted_data), "utf-8")

    messages_pot = temp_dir / "messages.pot"
    _json_to_pot(translations_file, messages_pot)

    # Cleanup helper json file
    translations_file.unlink()

    return messages_pot


def i18next_messages_to_po(source_messages_file: Path, target_catalogue_file: Path):
    source_messages = json.loads(source_messages_file.read_text("utf-8"))
    target_catalogue = polib.pofile(str(target_catalogue_file))

    target_catalogue_by_msgid = {entry.msgid: entry for entry in target_catalogue}

    for key, value in source_messages.items():
        if key in target_catalogue_by_msgid:
            if value:
                target_catalogue_by_msgid[key].msgstr = value
        else:
            target_catalogue.append(polib.POEntry(msgid=key, msgstr=value))

    target_catalogue.save(str(target_catalogue_file))


def merge_catalogues_from_i18next_translation_dir(
    source_translation_dir, target_translation_dir
):
    for source_catalogue_file in source_translation_dir.glob("*/translations.json"):
        click.secho(
            f"Merging i18next {source_catalogue_file} into {target_translation_dir}",
            fg="yellow",
        )
        language = source_catalogue_file.parent.name

        target_catalogue_file = (
            target_translation_dir
            / "messages"
            / language
            / "LC_MESSAGES"
            / "messages.po"
        )
        if target_catalogue_file.exists():
            i18next_messages_to_po(source_catalogue_file, target_catalogue_file)
        else:
            click.secho(
                f"Target catalogue file {target_catalogue_file} does not exist, "
                f"can not merge {source_catalogue_file}",
                fg="red",
            )
