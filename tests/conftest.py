# SPDX-FileCopyrightText: 2024-2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Pytest configuration."""

from __future__ import annotations

import shutil
from pathlib import Path

import polib
import pytest

from oarepo_tools.babel import (
    ensure_babel_configuration,
    ensure_babel_output_translations,
)


@pytest.fixture(scope="module")
def i18n_configuration():
    """Return a mocked i18n configuration object."""
    return {
        "babel_input_translations": [],
        "babel_output_translations": "mock_module/translations",
        "babel_source_paths": ["mock_module/"],
        "i18next_input_translations": [],
        "i18next_output_translations": "mock_module/theme/assets/semantic-ui/translations/mock_module",
        "i18next_source_paths": ["mock_module/theme/assets/semantic-ui/js"],
        "languages": ["cs", "en", "da"],
    }


def _clear_translations(config):
    babel_output_translations: Path = Path(__file__).parent / config.get("babel_output_translations", None)
    if babel_output_translations:
        shutil.rmtree(str(babel_output_translations), ignore_errors=True)
        babel_output_translations.mkdir()

    i18next_output_translations = Path(__file__).parent / config.get("i18next_output_translations", None)
    if i18next_output_translations:
        shutil.rmtree(str(i18next_output_translations), ignore_errors=True)


@pytest.fixture(scope="module")
def base_dir():
    return Path(__file__).parent


@pytest.fixture(scope="module")
def babel_ini_file(base_dir):
    return ensure_babel_configuration(base_dir)


@pytest.fixture(scope="module")
def babel_output_translations(base_dir, i18n_configuration):
    return ensure_babel_output_translations(base_dir, i18n_configuration)


@pytest.fixture(scope="module")
def pofile():
    def _create(entries, filename):
        po = polib.POFile()
        po.metadata = {
            "Project-Id-Version": "1.0",
            "Report-Msgid-Bugs-To": "you@example.com",
            "POT-Creation-Date": "2007-10-18 14:00+0100",
            "PO-Revision-Date": "2007-10-18 14:00+0100",
            "Last-Translator": "you <you@example.com>",
            "Language-Team": "English <yourteam@example.com>",
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
        }
        [po.append(entry) for entry in entries]
        po.save(filename)
        return po

    return _create


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown(i18n_configuration):
    _clear_translations(i18n_configuration)
    yield
    _clear_translations(i18n_configuration)


@pytest.fixture
def extra_translations_dir(base_dir):
    extra_path = base_dir / "extra_translations"

    yield extra_path

    shutil.rmtree(str(extra_path))
