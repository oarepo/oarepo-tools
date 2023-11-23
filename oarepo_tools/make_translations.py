import configparser
import os
import sys
from pathlib import Path

import click
import yaml

from .babel import (
    check_babel_configuration,
    compile_babel_translations,
    extract_babel_messages,
    merge_catalogues_from_translation_dir,
    prepare_babel_translation_dir,
    update_babel_translations,
)
from .i18next import (
    compile_i18next_translations,
    ensure_i18next_entrypoint,
    extract_i18next_messages,
    merge_catalogues_from_i18next_translation_dir,
)


@click.command(
    help="Generates and compiles localization messages. "
    "Reads configuration from setup.cfg and uses it to call babel and i18next. "
    "Expects setup.cfg or oarepo.yaml in the current directory or you may pass "
    "the path to it as an argument."
)
@click.argument("setup_cfg", required=False)
def main(setup_cfg):
    if not setup_cfg:
        setup_cfg = Path.cwd() / "setup.cfg"
        if not setup_cfg.exists():
            setup_cfg = Path.cwd() / "oarepo.yaml"
    else:
        setup_cfg = Path(setup_cfg)

    base_dir = setup_cfg.resolve().parent
    os.chdir(base_dir)

    i18n_configuration = read_configuration(setup_cfg)

    check_babel_configuration(base_dir, i18n_configuration)

    translations_dir = prepare_babel_translation_dir(base_dir, i18n_configuration)

    extract_babel_messages(base_dir, i18n_configuration, translations_dir)

    update_babel_translations(translations_dir)

    for extra_translations in i18n_configuration.get("babel_input_translations", []):
        merge_catalogues_from_translation_dir(
            base_dir / extra_translations, translations_dir
        )

    for extra_i18next_translations in i18n_configuration.get(
        "i18next_input_translations", []
    ):
        merge_catalogues_from_i18next_translation_dir(
            base_dir / extra_i18next_translations, translations_dir
        )

    i18next_translations_dir = None
    i18next_output_translations = i18n_configuration.get("i18next_output_translations", [])

    if i18next_output_translations:
        i18next_translations_dir = i18next_output_translations[0]
        if len(i18next_output_translations) > 1:
            click.secho(
                f"Multiple i18next_output_translations are not supported, using {i18next_translations_dir}",
                fg="yellow",
            )

    if i18next_translations_dir:
        for extra_i18next_translations in i18n_configuration.get("i18next_input_translations", []):
            merge_catalogues_from_i18next_translation_dir(
                base_dir / extra_i18next_translations, translations_dir
            )

        extract_i18next_messages(base_dir, i18n_configuration, i18next_translations_dir)
        merge_catalogues_from_translation_dir(
            base_dir / i18next_translations_dir / "messages", translations_dir
        )

    compile_babel_translations(translations_dir)

    if i18next_translations_dir:
        compile_i18next_translations(
            translations_dir, i18n_configuration, base_dir / i18next_translations_dir
        )
        ensure_i18next_entrypoint(base_dir / i18next_translations_dir)


def read_configuration(setup_cfg):
    try:
        return read_configuration_from_setup_cfg(setup_cfg)
    except Exception as config_ex:
        try:
            return read_configuration_from_yaml(setup_cfg)
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
    i18n_configuration = {
        k: [vv.strip() for vv in v.split("\n") if vv.strip()]
        for k, v in dict(configuration["oarepo.i18n"]).items()
    }
    return i18n_configuration


def read_configuration_from_yaml(yaml_file: Path):
    with yaml_file.open() as f:
        configuration = yaml.safe_load(f)
    return configuration.get("i18n", {})


if __name__ == "__main__":
    main()
