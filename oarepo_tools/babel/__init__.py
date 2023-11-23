import shutil
import sys
from pathlib import Path
from subprocess import check_output

import click

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


def check_babel_configuration(base_dir, i18n_configuration):
    babel_ini_file = base_dir / "babel.ini"
    # check if babel.ini exists and if it does not, create it
    if not babel_ini_file.exists():
        shutil.copy(Path(__file__).parent / "babel.ini", babel_ini_file)
        click.secho(f"Created babel.ini in {base_dir}", fg="green")


def prepare_babel_translation_dir(base_dir, i18n_configuration) -> Path:
    translations_dir = base_dir / i18n_configuration["babel_output_translations"][0]

    if not translations_dir.exists():
        translations_dir.mkdir(parents=True)
        click.secho(f"Created {translations_dir}", fg="green")

    for language in i18n_configuration.get("languages", ("cs", "en")):
        catalogue_dir = translations_dir / language / "LC_MESSAGES"
        if not catalogue_dir.exists():
            catalogue_dir.mkdir(parents=True)
            click.secho(f"Created {catalogue_dir}", fg="green")
        messages = catalogue_dir / "messages.po"
        if not messages.exists():
            messages.touch()
            click.secho(f"Created {messages}", fg="green")

    return translations_dir


def extract_babel_messages(base_dir, i18n_configuration, translations_dir):
    babel_ini_file = base_dir / "babel.ini"
    # extract messages
    jinjax_extra_source = str(
        translations_dir.relative_to(base_dir) / "jinjax_messages.jinja"
    )

    sources = [
        x
        for x in i18n_configuration["babel_source_paths"] + [jinjax_extra_source]
        if x.strip()
    ]

    translations_file = str(translations_dir / "messages.pot")

    click.secho(
        f"Extracting babel messages from {', '.join(sources)} -> {translations_file}"
    )

    find_jinjax_strings = """grep -E -hori '[^\{]\{\s_\(.*\)\s\}[^\}]'"""
    search_sources = f"{find_jinjax_strings} {' '.join(sources)}"
    reformat_for_babel = """awk '{print "{" substr($0, 2, length($0) - 2) "}"}'"""

    extract_jinjax_strings = (
        f"{search_sources} | {reformat_for_babel} > {jinjax_extra_source}"
    )
    check_output(extract_jinjax_strings, shell=True)

    CommandLineInterface().run(
        [
            "pybabel",
            "extract",
            "-F",
            babel_ini_file,
            "-k",
            "lazy_gettext",
            "-o",
            translations_file,
            *sources,
        ]
    )

    return translations_dir


def update_babel_translations(translations_dir):
    click.secho(f"Updating messages in {translations_dir}", fg="green")
    for catalogue_file in translations_dir.glob("*/LC_MESSAGES/*.po"):
        merge_catalogues(
            translations_dir / "messages.pot",
            translations_dir / catalogue_file.relative_to(translations_dir),
        )


def compile_babel_translations(translations_dir):
    click.secho(f"Compiling messages in {translations_dir}", fg="green")

    CommandLineInterface().run(["pybabel", "compile", "-f", "-d", translations_dir])
    click.secho(f"Done", fg="green")


def merge_catalogues(source_catalogue_file: Path, target_catalogue_file: Path):
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


def merge_catalogues_from_translation_dir(
    source_translation_dir: Path, target_translation_dir: Path
):
    for catalogue_file in source_translation_dir.glob("*/LC_MESSAGES/*.po"):
        click.secho(
            f"Merging {catalogue_file} into {target_translation_dir}", fg="yellow"
        )
        merge_catalogues(
            catalogue_file,
            target_translation_dir / catalogue_file.relative_to(source_translation_dir),
        )
