import os
import polib
from oarepo_tools.i18next import ensure_i18next_entrypoint, extract_i18next_messages

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
