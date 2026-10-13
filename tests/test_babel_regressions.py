"""Regression tests for babel extraction and catalogue merging.

Self-contained (tmp_path only), so they also run without the invenio app
fixtures: ``pytest --noconftest tests/test_babel_regressions.py``.
"""

import polib

from oarepo_tools.babel import (
    ensure_babel_configuration,
    extract_babel_messages,
    merge_babel_catalogues,
)


def _write_po(path, entries):
    po = polib.POFile()
    po.metadata = {"Content-Type": "text/plain; charset=utf-8"}
    for entry in entries:
        po.append(entry)
    po.save(str(path))


def test_extract_from_source_path_named_templates(tmp_path):
    page = tmp_path / "templates" / "semantic-ui" / "app" / "page.html"
    page.parent.mkdir(parents=True)
    page.write_text("<h1>{{ _('toplevel template string') }}</h1>\n")
    output_dir = tmp_path / "translations"
    output_dir.mkdir()

    messages_pot = extract_babel_messages(
        tmp_path,
        ensure_babel_configuration(tmp_path),
        output_dir,
        {"babel_source_paths": ["templates"]},
    )

    msgids = {entry.msgid for entry in polib.pofile(str(messages_pot))}
    assert "toplevel template string" in msgids


def test_merge_revives_obsolete_entry(tmp_path):
    source, target = tmp_path / "messages.pot", tmp_path / "messages.po"
    _write_po(
        source, [polib.POEntry(msgid="Welcome", occurrences=[("page.html", "3")])]
    )
    _write_po(
        target, [polib.POEntry(msgid="Welcome", msgstr="Vítejte", obsolete=True)]
    )

    merge_babel_catalogues(source, target)

    merged = [e for e in polib.pofile(str(target)) if e.msgid == "Welcome"]
    assert len(merged) == 1
    assert not merged[0].obsolete
    assert merged[0].msgstr == "Vítejte"
    assert merged[0].occurrences == [("page.html", "3")]


def test_merge_prefers_active_over_obsolete_duplicate(tmp_path):
    source, target = tmp_path / "messages.pot", tmp_path / "messages.po"
    _write_po(source, [polib.POEntry(msgid="Welcome", msgstr="Vítejte")])
    # active entry first, obsolete duplicate last (the order pybabel writes)
    _write_po(
        target,
        [
            polib.POEntry(msgid="Welcome", msgstr="Zdravím"),
            polib.POEntry(msgid="Welcome", msgstr="Old", obsolete=True),
        ],
    )

    merge_babel_catalogues(source, target)

    active = [
        e for e in polib.pofile(str(target)) if e.msgid == "Welcome" and not e.obsolete
    ]
    assert [e.msgstr for e in active] == ["Vítejte"]
