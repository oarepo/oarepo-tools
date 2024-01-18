import os
import shutil
from pathlib import Path

import polib

from oarepo_tools.babel import (
    compile_babel_translations,
    ensure_babel_configuration,
    ensure_babel_output_translations,
    extract_babel_messages,
    merge_babel_catalogues,
    merge_catalogue_dirs,
    update_babel_translations,
)
from tests.conftest import _clear_translations

jinjax_strings = ["jinjaxstring1"]
jinjax_extras = ["jinjaxstring2"]
python_strings = ["pythonstring1", "pythonstring2"]
html_strings = ["htmlstring1", "htmlstring2"]


def test_check_babel_configuration(app, db, cache, i18n_configuration, base_dir):
    babel_file = base_dir / "babel.ini"
    created_babel_file = ensure_babel_configuration(base_dir)

    assert str(created_babel_file) == str(babel_file)
    assert created_babel_file.exists()


def test_ensure_babel_output_translations(app, db, cache, i18n_configuration, base_dir):
    # Test create when missing
    config = i18n_configuration.copy()
    translations_dir = ensure_babel_output_translations(base_dir, config)
    assert translations_dir == base_dir / "mock_module/translations"
    # Check that files got created correctly
    paths = [
        translations_dir,
        translations_dir / "cs/LC_MESSAGES/messages.po",
        translations_dir / "en/LC_MESSAGES/messages.po",
        translations_dir / "da/LC_MESSAGES/messages.po",
    ]
    assert all([path.exists() for path in paths])

    # Test translations dir update
    config["languages"] = ["cs", "en", "da", "de"]
    translations_dir = ensure_babel_output_translations(base_dir, config)
    assert all(
        [
            path.exists()
            for path in paths + [translations_dir / "de/LC_MESSAGES/messages.po"]
        ]
    )

    # Test that with missing output config we bail out
    # TODO: need to use i18n_configuration copy here!!!
    del config["babel_output_translations"]
    try:
        translations_dir = ensure_babel_output_translations(base_dir, config)
    except SystemExit:
        pass


def test_extract_messages(
    app,
    db,
    cache,
    i18n_configuration,
    base_dir,
    babel_ini_file,
    babel_output_translations,
):
    messages_pot = extract_babel_messages(
        base_dir, babel_ini_file, babel_output_translations, i18n_configuration
    )

    assert messages_pot.exists()

    # Check if extra Jinjax strings got picked up
    # jinjax_messages = (tmpdir / "jinjax_messages.jinja").read_text(None)
    # assert all([f"{{{{ _('{js}') }}}}" in jinjax_messages for js in jinjax_extras])

    # Check all translation strings got extracted to POT file
    messages_catalogue = polib.pofile(str(messages_pot))
    entries = {entry.msgid: entry for entry in messages_catalogue}
    assert all(
        [
            key in entries.keys() and entries[key].msgstr == ""
            for key in jinjax_strings + jinjax_extras
        ]
    )
    assert all(
        [key in entries.keys() and entries[key].msgstr == "" for key in python_strings]
    )
    assert all(
        [key in entries.keys() and entries[key].msgstr == "" for key in html_strings]
    )

    # Ensure all translation strings are empty after extraction
    assert all([entry.msgstr == "" for entry in entries.values()])


def test_update_babel_translations(
    app,
    db,
    cache,
    i18n_configuration,
    base_dir,
    babel_ini_file,
    tmpdir,
    babel_output_translations,
):
    messages_pot = extract_babel_messages(
        base_dir, babel_ini_file, babel_output_translations, i18n_configuration
    )

    paths = [
        babel_output_translations / "cs/LC_MESSAGES/messages.po",
        babel_output_translations / "en/LC_MESSAGES/messages.po",
        babel_output_translations / "da/LC_MESSAGES/messages.po",
    ]
    assert all([os.path.getsize(str(path)) == 0 for path in paths])

    update_babel_translations(messages_pot, babel_output_translations)

    # Check all translation strings got propagated to language catalogs
    assert all([os.path.getsize(str(path)) > 0 for path in paths])
    for fpath in paths:
        po_file = polib.pofile(str(fpath))
        entries = {entry.msgid: entry for entry in po_file}

        assert all(
            [
                string in entries.keys()
                for string in jinjax_extras
                + jinjax_strings
                + html_strings
                + python_strings
            ]
        )

        # Check translations strings are initially empty
        assert all([entry.msgstr == "" for entry in entries.values()])


def test_compile_babel_translations(
    app,
    db,
    cache,
    i18n_configuration,
    babel_ini_file,
    tmpdir,
    base_dir,
    babel_output_translations,
):
    messages_pot = extract_babel_messages(
        base_dir, babel_ini_file, tmpdir, i18n_configuration
    )
    update_babel_translations(messages_pot, babel_output_translations)

    # Check that all .mo files got created
    compile_babel_translations(babel_output_translations)

    paths = [
        babel_output_translations / "cs/LC_MESSAGES/messages.mo",
        babel_output_translations / "en/LC_MESSAGES/messages.mo",
        babel_output_translations / "da/LC_MESSAGES/messages.mo",
    ]
    assert all([path.exists() and os.path.getsize(str(path)) > 0 for path in paths])


def test_merge_babel_catalogues(
    app, db, cache, i18n_configuration, base_dir, babel_output_translations, pofile
):
    source_path = babel_output_translations / "test_source.po"
    target_path = babel_output_translations / "test_target.po"

    # Simple addition
    source_entries = [
        polib.POEntry(
            msgid="Welcome",
            msgstr="Vitejte",
            occurrences=[("welcome.py", "12"), ("anotherfile.py", "34")],
        )
    ]
    target_entries = [
        polib.POEntry(
            msgid="Other",
            msgstr="Ostatni",
            occurrences=[("welcome.py", "2"), ("anotherfile.py", "3")],
        )
    ]

    pofile(source_entries, str(source_path))
    pofile(target_entries, str(target_path))

    merge_babel_catalogues(source_path, target_path)

    merged_catalogue = polib.pofile(target_path)
    merged_entries = {entry.msgid: entry for entry in merged_catalogue}
    assert all(
        [
            entry.msgid in merged_entries.keys()
            and merged_entries[entry.msgid].msgstr == entry.msgstr
            for entry in source_entries + target_entries
        ]
    )

    source_path.unlink()
    target_path.unlink()

    # Merge update
    source_entries = [
        polib.POEntry(
            msgid="Welcome",
            msgstr="Vitejte",
            occurrences=[("welcome.py", "12"), ("anotherfile.py", "34")],
        )
    ]
    target_entries = [
        polib.POEntry(
            msgid="Welcome",
            msgstr="Zdravim",
            occurrences=[("welcome.py", "12"), ("anotherfile.py", "34")],
        )
    ]
    pofile(source_entries, str(source_path))
    pofile(target_entries, str(target_path))

    merge_babel_catalogues(source_path, target_path)

    merged_catalogue = polib.pofile(target_path)
    merged_entries = {entry.msgid: entry for entry in merged_catalogue}
    assert all(
        [
            entry.msgid in merged_entries.keys()
            and merged_entries[entry.msgid].msgstr == entry.msgstr
            for entry in source_entries
        ]
    )

    source_path.unlink()
    target_path.unlink()
    target_path.with_suffix(".mo").unlink()


def test_merge_catalogue_dirs(
    app,
    db,
    cache,
    base_dir,
    babel_ini_file,
    babel_output_translations,
    i18n_configuration,
    extra_translations_dir,
):
    _clear_translations(i18n_configuration)
    messages_pot = extract_babel_messages(
        base_dir, babel_ini_file, babel_output_translations, i18n_configuration
    )
    update_babel_translations(messages_pot, babel_output_translations)

    target_translation_dir = ensure_babel_output_translations(
        extra_translations_dir, i18n_configuration
    )

    merge_catalogue_dirs(babel_output_translations, target_translation_dir)

    for catalogue_file in babel_output_translations.glob("*/LC_MESSAGES/*.po"):
        source_catalogue = polib.pofile(catalogue_file)
        merged_catalogue = polib.pofile(
            target_translation_dir
            / catalogue_file.relative_to(babel_output_translations)
        )
        source_entries = {entry.msgid: entry for entry in source_catalogue}
        merged_entries = {entry.msgid: entry for entry in merged_catalogue}
        assert all(
            [
                entry.msgid in merged_entries.keys()
                and merged_entries[entry.msgid].msgstr == entry.msgstr
                for entry in source_entries.values()
            ]
        )
