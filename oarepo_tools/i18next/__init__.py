import inspect
import json
import os
import shutil
from pathlib import Path
from subprocess import check_call

import click
import polib

npm_proj_cwd = os.path.dirname(inspect.getfile(inspect.currentframe()))
npm_proj_env = dict(os.environ)


def install_i18next(i18next_translations_dir: Path):
    # check if i18next.js exists and if it does not, create it
    i18next_entrypoint = i18next_translations_dir / "i18next.js"

    if not i18next_translations_dir.exists():
        i18next_translations_dir.mkdir(parents=True)

    if not i18next_entrypoint.exists():
        shutil.copy(Path(__file__).parent / "i18next.js", i18next_entrypoint)
        click.secho(f"Created i18next.js in {i18next_entrypoint}", fg="green")

    # Make sure NPM project is installed & up-to-date
    click.secho("Installing / updating React-i18next dependencies", fg="green")
    check_call(
        ["npm", "install"],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )


def extract_i18next_messages(base_dir: Path, working_dir: Path, i18n_configuration):
    npm_proj_env["LANGUAGES"] = ",".join(i18n_configuration["languages"] or ["en"])

    source_path_patterns = [
        os.path.join(base_dir / source_path, "**/*.{js,jsx,ts,tsx}")
        for source_path in i18n_configuration["i18next_source_paths"]
    ]

    # Extract JS translations strings
    click.secho(
        f"Extracting i18next  messages from sources matching {source_path_patterns} -> {working_dir}",
        fg="green",
    )
    check_call(
        [
            "npm",
            "run",
            "extract_messages",
            "--",
            "--output",
            working_dir,
            *source_path_patterns,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    translations_file = working_dir / "extracted-messages.json"
    extracted_data = json.loads(translations_file.read_text(None))

    # Fix any incorrectly extracted  (by <Trans>) values, set all to ""
    for key in extracted_data.keys():
        extracted_data[key] = ""

    translations_file.write_text(json.dumps(extracted_data), "utf-8")
    return working_dir


def generate_pot_from_i18next_translations(translations_dir):
    # Generate gettext POT file from extracted JS translation strings
    click.secho(
        f"Generating POT file from extracted i18next JSON translations in: {translations_dir}",
        fg="green",
    )
    check_call(
        [
            "npm",
            "run",
            "generate_pot",
            "--",
            translations_dir,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    return translations_dir / "messages.pot"


def merge_i18next_catalogues(source_catalogue_file: Path, target_catalogue_file: Path):
    source_catalogue = json.loads(source_catalogue_file.read_text(None))
    target_catalogue = polib.pofile(str(target_catalogue_file))

    target_catalogue_by_msgid = {entry.msgid: entry for entry in target_catalogue}

    for key, value in source_catalogue.items():
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
            merge_i18next_catalogues(source_catalogue_file, target_catalogue_file)
        else:
            click.secho(
                f"Target catalogue file {target_catalogue_file} does not exist, "
                f"can not merge {source_catalogue_file}",
                fg="red",
            )
