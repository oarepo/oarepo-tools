import os
import shutil
import polib
from pathlib import Path

from oarepo_tools.babel import (
    check_babel_configuration,
    compile_babel_translations,
    extract_babel_messages,
    merge_catalogues,
    merge_catalogues_from_translation_dir,
    prepare_babel_translation_dir,
    update_babel_translations,
)

jinjax_strings = ["jinjaxstring1"]
jinjax_extras = ["jinjaxstring2"]
python_strings = ["pythonstring1", "pythonstring2"]
html_strings = ["htmlstring1", "htmlstring2"]


def test_check_babel_configuration(app, db, cache, i18n_configuration, base_dir):
    babel_file = base_dir / "babel.ini"
    check_babel_configuration(base_dir)
    assert babel_file.exists()


def test_prepare_translations_dir(
    app, db, cache, i18n_configuration, base_dir, extra_entry_points
):
    # Test create when missing
    translations_dir = prepare_babel_translation_dir(base_dir, i18n_configuration)
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
    i18n_configuration["languages"] = ["cs", "en", "da", "de"]
    translations_dir = prepare_babel_translation_dir(base_dir, i18n_configuration)
    assert all(
        [
            path.exists()
            for path in paths + [translations_dir / "de/LC_MESSAGES/messages.po"]
        ]
    )


def test_extract_messages(
    app,
    db,
    cache,
    i18n_configuration,
    base_dir,
    tmpdir,
    extra_entry_points,
):
    working_dir = extract_babel_messages(base_dir, tmpdir, i18n_configuration)

    assert working_dir == tmpdir

    # Check that files got created correctly
    paths = [
        "messages.pot",
        "jinjax_messages.jinja",
    ]
    assert all([Path(tmpdir / path).exists() for path in paths])

    # Check if extra Jinjax strings got picked up
    jinjax_messages = (tmpdir / "jinjax_messages.jinja").read_text(None)
    assert all([f"{{{{ _('{js}') }}}}" in jinjax_messages for js in jinjax_extras])

    # Check all translation strings got extracted to POT file
    messages_catalogue = polib.pofile(str(tmpdir / "messages.pot"))
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
    app, db, cache, i18n_configuration, base_dir, tmpdir, translations_dir
):
    working_dir = extract_babel_messages(base_dir, tmpdir, i18n_configuration)

    paths = [
        translations_dir / "cs/LC_MESSAGES/messages.po",
        translations_dir / "en/LC_MESSAGES/messages.po",
        translations_dir / "da/LC_MESSAGES/messages.po",
    ]
    assert all([os.path.getsize(str(path)) == 0 for path in paths])

    update_babel_translations(working_dir, translations_dir)

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
    app, db, cache, i18n_configuration, tmpdir, base_dir, translations_dir
):
    working_dir = extract_babel_messages(base_dir, tmpdir, i18n_configuration)
    update_babel_translations(working_dir, translations_dir)

    # Check that all .mo files got created
    compile_babel_translations(translations_dir)

    paths = [
        translations_dir / "cs/LC_MESSAGES/messages.mo",
        translations_dir / "en/LC_MESSAGES/messages.mo",
        translations_dir / "da/LC_MESSAGES/messages.mo",
    ]
    assert all([path.exists() and os.path.getsize(str(path)) > 0 for path in paths])


def test_merge_catalogues(
    app, db, cache, i18n_configuration, base_dir, translations_dir, pofile
):
    source_path = translations_dir / "test_source.po"
    target_path = translations_dir / "test_target.po"

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

    merge_catalogues(source_path, target_path)

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

    merge_catalogues(source_path, target_path)

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


def test_merge_catalogues_from_translation_dir(
    app, db, cache, base_dir, translations_dir, i18n_configuration, tmpdir, pofile
):
    working_dir = extract_babel_messages(base_dir, tmpdir, i18n_configuration)
    update_babel_translations(working_dir, translations_dir)

    target_path = base_dir / "test_translations"
    target_translation_dir = prepare_babel_translation_dir(
        target_path, i18n_configuration
    )

    merge_catalogues_from_translation_dir(translations_dir, target_translation_dir)

    for catalogue_file in translations_dir.glob("*/LC_MESSAGES/*.po"):
        source_catalogue = polib.pofile(catalogue_file)
        merged_catalogue = polib.pofile(
            target_translation_dir / catalogue_file.relative_to(translations_dir)
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

    shutil.rmtree(target_path)
