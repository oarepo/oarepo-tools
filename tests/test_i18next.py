import os
from oarepo_tools.i18next import ensure_i18next_entrypoint


def test_ensure_i18next_entrypoint(app, db, cache, base_dir, i18n_configuration):
    i18next_output_translations = i18n_configuration.get(
        "i18next_output_translations", []
    )

    i18next_dir = base_dir / i18next_output_translations[0]
    ensure_i18next_entrypoint(i18next_dir)

    assert i18next_dir.exists()
    assert (i18next_dir / "i18next.js").exists()
    assert os.path.getsize(str(i18next_dir / "i18next.js"))
