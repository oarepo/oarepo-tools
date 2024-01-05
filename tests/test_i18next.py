import json
import os
import polib
from oarepo_tools.i18next import (
    ensure_i18next_entrypoint,
    extract_i18next_messages,
    merge_catalogues_from_i18next_translation_dir,
    merge_i18next_catalogues,
)

jsstrings = ["jsstring1", "jsstring2"]


def test_ensure_i18next_entrypoint(app, db, cache, base_dir, i18n_configuration):
    i18next_output_translations = i18n_configuration.get(
        "i18next_output_translations", []
    )

    i18next_dir = base_dir / i18next_output_translations[0]
    ensure_i18next_entrypoint(i18next_dir)

    assert i18next_dir.exists()
    assert (i18next_dir / "i18next.js").exists()
    assert os.path.getsize(str(i18next_dir / "i18next.js"))


def test_extract_i18next_messages(app, db, cache, base_dir, i18n_configuration):
    i18next_translations_dir = (
        base_dir / i18n_configuration.get("i18next_output_translations", [])[0]
    )

    extract_i18next_messages(base_dir, i18n_configuration, i18next_translations_dir)

    # Check that files got created correctly
    paths = [
        i18next_translations_dir / "messages" / "cs/LC_MESSAGES/messages.po",
        i18next_translations_dir / "messages" / "en/LC_MESSAGES/messages.po",
        i18next_translations_dir / "messages" / "da/LC_MESSAGES/messages.po",
    ]
    assert all([path.exists() for path in paths])

    # And has correct contents
    for fpath in paths:
        po_file = polib.pofile(str(fpath))
        entries = {entry.msgid: entry for entry in po_file}
        assert all(
            [key in entries.keys() and entries[key].msgstr == "" for key in jsstrings]
        )


def test_merge_i18next_catalogues(
    app, db, cache, base_dir, i18n_configuration, translations_dir, pofile
):
    source_path = translations_dir / "test_source.json"
    target_path = translations_dir / "test_target.po"

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

    source_path.write_text(json.dumps(source_entries))
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
    app, db, cache, base_dir, i18n_configuration
):
    i18next_translations_dir = (
        base_dir / i18n_configuration.get("i18next_output_translations", [])[0]
    )

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
