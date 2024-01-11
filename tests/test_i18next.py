import json
import os
from pathlib import Path
import shutil
import polib
from oarepo_tools.i18next import (
    generate_pot_from_i18next_translations,
    install_i18next,
    extract_i18next_messages,
    merge_catalogues_from_i18next_translation_dir,
    merge_i18next_catalogues,
)

jsstrings = ["jsstring1", "jsstring2"]


def test_install_i18next(app, db, cache, base_dir, i18n_configuration):
    i18next_output_translations = i18n_configuration.get(
        "i18next_output_translations", []
    )

    i18next_dir = base_dir / i18next_output_translations[0]
    install_i18next(i18next_dir)

    assert i18next_dir.exists()
    assert (i18next_dir / "i18next.js").exists()
    assert os.path.getsize(str(i18next_dir / "i18next.js"))


def test_extract_i18next_messages(app, db, cache, base_dir, tmpdir, i18n_configuration):
    working_dir = extract_i18next_messages(base_dir, Path(tmpdir), i18n_configuration)

    # Check that files got created correctly
    paths = [
        working_dir / "extracted-messages.json",
    ]
    assert all([path.exists() for path in paths])

    # And has correct contents
    for fpath in paths:
        translations = json.loads(fpath.read_text(None))
        assert all([k in jsstrings and v == "" for k, v in translations.items()])


def test_generate_pot_from_i18next_translations(
    app, db, cache, base_dir, tmpdir, i18n_configuration
):
    working_dir = extract_i18next_messages(base_dir, Path(tmpdir), i18n_configuration)

    pot_file = generate_pot_from_i18next_translations(working_dir)

    # Check that file got created correctly
    path = working_dir / "messages.pot"

    assert pot_file == path
    assert pot_file.exists()

    pot_catalogue = polib.POFile(pot_file)
    pot_entries = {entry.msgid: entry for entry in pot_catalogue}
    assert all(
        [entry.msgid in jsstrings and entry.msgstr == "" for entry in pot_entries]
    )


def test_merge_i18next_catalogues(
    app, db, cache, base_dir, tmpdir, i18n_configuration, translations_dir, pofile
):
    source_path = Path(tmpdir) / "test_source.json"
    target_path = Path(tmpdir) / "test_target.po"

    # Simple addition
    source_entries = {
        "Welcome": "Vitejte",
    }
    target_entries = [
        polib.POEntry(
            msgid="Other",
            msgstr="Ostatni",
            occurrences=[("welcome.py", "2"), ("anotherfile.py", "3")],
        )
    ]

    source_path.write_text(json.dumps(source_entries), "utf-8")
    pofile(target_entries, str(target_path))

    merge_i18next_catalogues(source_path, target_path)

    merged_catalogue = polib.pofile(target_path)
    merged_entries = {entry.msgid: entry for entry in merged_catalogue}
    assert all(
        [
            msgid in merged_entries.keys() and merged_entries[msgid].msgstr == msgstr
            for msgid, msgstr in [[k, v] for k, v in source_entries.items()]
            + [[e.msgid, e.msgstr] for e in target_entries]
        ]
    )

    source_path.unlink()
    target_path.unlink()

    # Merge update
    source_entries = {
        "Welcome": "Vitejte",
    }
    target_entries = [
        polib.POEntry(
            msgid="Welcome",
            msgstr="Zdravim",
            occurrences=[("welcome.py", "12"), ("anotherfile.py", "34")],
        )
    ]
    source_path.write_text(json.dumps(source_entries))
    pofile(target_entries, str(target_path))

    merge_i18next_catalogues(source_path, target_path)

    merged_catalogue = polib.pofile(target_path)
    merged_entries = {entry.msgid: entry for entry in merged_catalogue}
    assert all(
        [
            msgid in merged_entries.keys() and merged_entries[msgid].msgstr == msgstr
            for msgid, msgstr in [[k, v] for k, v in source_entries.items()]
        ]
    )

    source_path.unlink()
    target_path.unlink()


def test_merge_catalogues_from_i18next_translation_dir(
    app, db, cache, tmpdir, base_dir, i18n_configuration
):
    i18next_translations_dir = (
        base_dir / i18n_configuration.get("i18next_output_translations", [])[0]
    )
    working_dir = extract_i18next_messages(base_dir, Path(tmpdir), i18n_configuration)

    pot_file = generate_pot_from_i18next_translations(working_dir)

    source_translations_dir = base_dir / "test_i18next_translations"
    (source_translations_dir / "cs").mkdir(exist_ok=True, parents=True)
    (source_translations_dir / "en").mkdir(exist_ok=True, parents=True)
    (source_translations_dir / "da").mkdir(exist_ok=True, parents=True)
    (source_translations_dir / "en/translations.json").write_text(
        json.dumps({"jsstring2": "test", "jsstring3": ""})
    )
    (source_translations_dir / "cs/translations.json").write_text(
        json.dumps({"jsstring2": "test", "jsstring3": ""})
    )
    (source_translations_dir / "da/translations.json").write_text(
        json.dumps({"jsstring2": "test", "jsstring3": ""})
    )

    extract_i18next_messages(base_dir, i18n_configuration, i18next_translations_dir)

    merge_catalogues_from_i18next_translation_dir(
        source_translations_dir, i18next_translations_dir
    )

    # Check that files got created correctly
    paths = [
        i18next_translations_dir / "messages" / "cs/LC_MESSAGES/messages.po",
        i18next_translations_dir / "messages" / "en/LC_MESSAGES/messages.po",
        i18next_translations_dir / "messages" / "da/LC_MESSAGES/messages.po",
    ]
    assert all([path.exists() for path in paths])

    expected = {"jsstring1": "", "jsstring2": "test", "jsstring3": ""}

    shutil.rmtree(source_translations_dir, ignore_errors=True)

    # And has correct contents
    for fpath in paths:
        po_file = polib.pofile(str(fpath))
        entries = {entry.msgid: entry for entry in po_file}
        assert all(
            [
                key in entries.keys() and entries[key].msgstr == value
                for key, value in expected.items()
            ]
        )
