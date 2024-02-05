import configparser
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import click
import yaml

from .babel import (
    compile_babel_translations,
    ensure_babel_configuration,
    ensure_babel_output_translations,
    extract_babel_messages,
    merge_babel_catalogues,
    merge_catalogue_dirs,
    update_babel_translations,
)
from .i18next import (
    compile_i18next_translations,
    ensure_i18next_output_translations,
    extract_i18next_messages,
    merge_catalogues_from_i18next_translation_dir,
)


@click.command(
    help="Generates and compiles localization messages. "
    "Reads configuration from setup.cfg and uses it to call babel and i18next. "
    "Expects setup.cfg or oarepo.yaml in the current directory or you may pass "
    "the path to it as an argument."
)
@click.argument("config_path", required=False)
def main(config_path):
    config_path = Path(config_path or Path.cwd())
    base_dir = (config_path if config_path.is_dir() else config_path.parent).resolve()
    os.chdir(base_dir)

    i18n_configuration = read_configuration(config_path)

    babel_ini_file = ensure_babel_configuration(base_dir)
    babel_translations_dir = ensure_babel_output_translations(
        base_dir, i18n_configuration
    )
    babel_messages_pot = extract_babel_messages(
        base_dir, babel_ini_file, babel_translations_dir, i18n_configuration
    )

    i18n_translations_dir = ensure_i18next_output_translations(
        base_dir, i18n_configuration
    )

    with tempfile.TemporaryDirectory() as i18n_temp:
        i18n_messages_pot = extract_i18next_messages(
            base_dir, Path(i18n_temp), i18n_configuration
        )
        merge_babel_catalogues(i18n_messages_pot, babel_messages_pot)

    update_babel_translations(babel_messages_pot, babel_translations_dir)

    for extra_babel_translations in i18n_configuration.get(
        "babel_input_translations", []
    ):
        merge_catalogue_dirs(
            base_dir / extra_babel_translations, babel_translations_dir
        )

    for extra_i18next_translations in i18n_configuration.get(
        "i18next_input_translations", []
    ):
        merge_catalogues_from_i18next_translation_dir(
            base_dir / extra_i18next_translations, babel_translations_dir
        )

    compile_babel_translations(babel_translations_dir)

    compile_i18next_translations(
        babel_translations_dir, i18n_translations_dir, i18n_configuration
    )


def read_configuration(config_path: Path):
    try:
        return read_configuration_from_setup_cfg(
            config_path if config_path.is_file() else config_path / "setup.cfg"
        )
    except Exception as config_ex:
        try:
            return read_configuration_from_yaml(
                config_path if config_path.is_file() else config_path / "oarepo.yaml"
            )
        except Exception as yaml_ex:
            click.secho(
                "Could not read configuration from setup.cfg or oarepo.yaml", fg="red"
            )
            click.secho(f"setup.cfg error: {config_ex}", fg="red")
            click.secho(f"oarepo.yaml error: {yaml_ex}", fg="red")
            sys.exit(1)


def read_configuration_from_setup_cfg(setup_cfg):
    configuration = configparser.ConfigParser()
    configuration.read([str(setup_cfg)])

    def _parse_value(v):
        if "\n" not in v:
            return v

        return [line.strip() for line in v.split("\n") if line.strip()]

    i18n_configuration = {
        k: _parse_value(v) for k, v in dict(configuration["oarepo.i18n"]).items()
    }
    return i18n_configuration


def read_configuration_from_yaml(yaml_file: Path):
    with yaml_file.open() as f:
        configuration = yaml.safe_load(f)
    return configuration.get("i18n", {})


if __name__ == "__main__":
    main()
