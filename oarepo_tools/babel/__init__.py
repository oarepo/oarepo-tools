import re
import shutil
import sys
from pathlib import Path

import click

from oarepo_tools import validate_output_translations_dir, validate_source_paths

try:
    from babel.messages.frontend import CommandLineInterface
except ImportError:
    click.secho(
        "Babel is not installed in the current virtualenv. "
        'Please install it using "pip install babel" or '
        "add babel, polib and jinja2 to your dev depedencies.",
        fg="red",
    )
    sys.exit(1)

try:
    import polib
except ImportError:
    click.secho(
        "polib is not installed in the current virtualenv. "
        'Please install it using "pip install polib" or '
        "add babel, polib and jinja2 to your dev depedencies.",
        fg="red",
    )
    sys.exit(1)


try:
    import jinja2
except ImportError:
    click.secho(
        "Jinja2 is not installed in the current virtualenv. "
        'Please install it using "pip install jinja2" or '
        "add babel, polib and jinja2 to your dev depedencies.",
        fg="red",
    )
    sys.exit(1)


def ensure_babel_configuration(base_dir: Path):
    """Ensures that babel.ini is installed in package root and up-to-date.

    :param base_dir: Python package root directory (containing `setup.cfg` or `oarepo.yaml`)
    :return: path to the babel.ini configuration file
    """
    babel_ini_file = base_dir / "babel.ini"
    # check if babel.ini exists and if it does not, create it
    if not babel_ini_file.exists():
        shutil.copy(Path(__file__).parent / "babel.ini", babel_ini_file)
        click.secho(f"Created babel.ini in {base_dir}", fg="green")
    else:
        shutil.copy(Path(__file__).parent / "babel.ini", babel_ini_file)
        click.secho(f"Updated babel.ini in {base_dir}", fg="yellow")

    return babel_ini_file


def ensure_babel_output_translations(base_dir: Path, i18n_configuration: dict) -> Path:
    """Ensures that babel messages catalogue structure is created for every supported language.

    :param base_dir: Python package root directory (containing `setup.cfg` or `oarepo.yaml`)
    :param i18n_configuration:
    :return: root path of babel messages catalogue
    :raises SystemExit
    """
    output_dir = validate_output_translations_dir(
        base_dir,
        i18n_configuration,
        "babel_output_translations",
        create_if_missing=True,
    )
    if not output_dir:
        click.secho(
            f"configuration error: `babel_output_translations` directory missing or invalid.",
            fg="red",
        )
        sys.exit(1)

    for language in i18n_configuration.get("languages", ("cs", "en")):
        catalogue_dir = output_dir / language / "LC_MESSAGES"
        if not catalogue_dir.exists():
            catalogue_dir.mkdir(parents=True)
            click.secho(f"Created {catalogue_dir}", fg="green")
        messages = catalogue_dir / "messages.po"
        if not messages.exists():
            messages.touch()
            click.secho(f"Created {messages}", fg="green")

    return output_dir


def extract_babel_messages(
    base_dir: Path, babel_ini_file: Path, output_dir: Path, i18n_configuration: dict
):
    """
    Collects all gettext translation keys from `babel_source_paths` using `pybabel` and
    stores it in a `messages.pot` catalogue in the root of `output_dir`.

    :param base_dir: Python package root directory (containing `setup.cfg` or `oarepo.yaml`)
    :param babel_ini_file: path to the `babel.ini` configuration file
    :param output_dir: path to a directory, where `messages.pot` should be created
    :param i18n_configuration: _description_
    :return: returns a path to the resulting `messages.pot` catalogue
    """
    babel_source_paths = validate_source_paths(
        base_dir, i18n_configuration, "babel_source_paths"
    )
    if not babel_source_paths:
        click.secho(
            f"Skipping babel extraction: no valid source paths",
            fg="yellow",
        )
        return

    jinjax_extra_source = output_dir / "jinjax_messages.jinja"
    babel_source_paths.append(jinjax_extra_source)

    messages_pot = output_dir / "messages.pot"

    click.secho(
        f"Extracting babel messages from {', '.join([str(p) for p in babel_source_paths])} -> {str(messages_pot)}"
    )

    jinjax_code = ""
    i18string_regex = re.compile(r"([^\{]|^)(\{\s*_\(.*?\)\s*\})[^\}]")

    for source_path in babel_source_paths:
        for fpath in Path(source_path).glob("**/*.jinja"):
            jinjax_code += fpath.read_text().replace("\n", " ")

    with open(str(jinjax_extra_source), mode="w+") as jinjax_trans:
        for match in re.finditer(i18string_regex, jinjax_code):
            i18str = f"{{{match.group(match.lastindex)}}}"
            jinjax_trans.write(f"{i18str}\n")

    CommandLineInterface().run(
        [
            "pybabel",
            "extract",
            "-F",
            babel_ini_file,
            "-k",
            "lazy_gettext",
            "-o",
            str(messages_pot),
            *[str(s) for s in babel_source_paths],
        ]
    )

    # Cleanup helper file for special JinjaX translation keys
    Path(jinjax_extra_source).unlink()

    return messages_pot


def update_babel_translations(messages_pot: Path, translations_dir: Path):
    """
    Updates message catalogues with entries from `messages_pot` file
    for each language messages catalogue in `translation_dir`.

    :param messages_pot: path to the source `messages.pot` file
    :param translations_dir: path to a directory with babel translations catalogues
    """
    if translations_dir.exists():
        click.secho(f"Updating messages in {translations_dir}", fg="green")
        for catalogue_file in translations_dir.glob("*/LC_MESSAGES/*.po"):
            merge_babel_catalogues(
                messages_pot,
                translations_dir / catalogue_file.relative_to(translations_dir),
            )
    else:
        click.secho(
            f"Cannot update babel translations. Target directory {str(translations_dir)} missing.",
            fg="red",
        )
        sys.exit()


def compile_babel_translations(translations_dir):
    click.secho(f"Compiling messages in {translations_dir}", fg="green")

    CommandLineInterface().run(["pybabel", "compile", "-f", "-d", translations_dir])
    click.secho(f"Done", fg="green")


def merge_babel_catalogues(source_catalogue_file: Path, target_catalogue_file: Path):
    """Merges all entries from a source PO catalogue with entries in a target PO catalogue.

    :param source_catalogue_file: source catalogue pofile
    :param target_catalogue_file: target catalogue pofile
    """
    source_catalogue = polib.pofile(str(source_catalogue_file))
    target_catalogue = polib.pofile(str(target_catalogue_file))
    target_catalogue_by_msgid = {entry.msgid: entry for entry in target_catalogue}

    for entry in source_catalogue:
        if entry.msgid not in target_catalogue_by_msgid:
            target_catalogue.append(entry)
            target_catalogue_by_msgid[entry.msgid] = entry
        elif (
            entry.msgstr
            and entry.msgstr != target_catalogue_by_msgid[entry.msgid].msgstr
        ):
            target_catalogue_by_msgid[entry.msgid].msgstr = entry.msgstr

    target_catalogue.save(str(target_catalogue_file))
    target_catalogue.save_as_mofile(str(target_catalogue_file.with_suffix(".mo")))


def merge_catalogue_dirs(source_translation_dir: Path, target_translation_dir: Path):
    for catalogue_file in source_translation_dir.glob("*/LC_MESSAGES/*.po"):
        click.secho(
            f"Merging {catalogue_file} into {target_translation_dir}", fg="yellow"
        )
        merge_babel_catalogues(
            catalogue_file,
            target_translation_dir / catalogue_file.relative_to(source_translation_dir),
        )
