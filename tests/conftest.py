# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""
import shutil
import sys
from pathlib import Path
import polib
import pytest
import requests
from invenio_app.factory import create_app as _create_app
from requests.exceptions import ConnectionError

from oarepo_tools.babel import prepare_babel_translation_dir

pytest_plugins = ("celery.contrib.pytest",)

try:
    import pytest_docker
except ImportError:
    # Do nothing docker-compose-related in Github Action env
    @pytest.fixture(scope="session")
    def docker_services():
        return

    @pytest.fixture(scope="session")
    def docker_ip():
        return ""


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def search_service(docker_ip, docker_services):
    """Ensure that OpenSearch service is up and responsive."""
    if not docker_services:
        return

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("search", 9200)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=60.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="module")
def i18n_configuration():
    """Mocked i18n configuration object"""
    return {
        "babel_input_translations": [],
        "babel_output_translations": ["mock_module/translations"],
        "babel_source_paths": ["mock_module/"],
        "i18next_input_translations": [],
        "i18next_output_translations": [
            "mock_module/theme/assets/semantic-ui/translations/mock_module"
        ],
        "i18next_source_paths": ["mock_module/theme/assets/semantic-ui/js"],
        "languages": ["cs", "en", "da"],
    }


def _clear_translations(config):
    babel_output_translations: Path = (
        Path(__file__).parent / config.get("babel_output_translations", ["None"])[0]
    )
    shutil.rmtree(str(babel_output_translations), ignore_errors=True)
    babel_output_translations.mkdir()

    i18next_output_translations = (
        Path(__file__).parent / config.get("i18next_output_translations", ["None"])[0]
    )
    shutil.rmtree(str(i18next_output_translations), ignore_errors=True)


@pytest.fixture(scope="module")
def h():
    """Accept JSON headers."""
    return {"accept": "application/json"}


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {"invenio_i18n.translations": {"mock_module = tests.mock_module"}}


@pytest.fixture(scope="module")
def app_config(app_config, search_service):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config["BABEL_DEFAULT_LOCALE"] = "en"
    app_config["I18N_LANGUAGES"] = [("da", "Danish"), ("cs", "Czech")]
    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"

    # disable redis cache
    app_config["CACHE_TYPE"] = "SimpleCache"  # Flask-Caching related configs

    app_config["APP_THEME"] = ["semantic-ui"]
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command.

    Scope: module

    .. code-block:: python

        def test_cmd(cli_runner):
            result = cli_runner(mycmd)
            assert result.exit_code == 0
    """

    def cli_invoke(command, input=None, *args):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


@pytest.fixture(scope="module")
def base_dir():
    return Path(__file__).parent


@pytest.fixture(scope="module")
def translations_dir(i18n_configuration, base_dir):
    return prepare_babel_translation_dir(base_dir, i18n_configuration)


@pytest.fixture()
def fake_manifest(app):
    python_path = Path(sys.executable)
    invenio_instance_path = python_path.parent.parent / "var" / "instance"
    manifest_path = invenio_instance_path / "static" / "dist"
    manifest_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        Path(__file__).parent / "manifest.json", manifest_path / "manifest.json"
    )


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
