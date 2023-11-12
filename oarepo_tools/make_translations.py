from pathlib import Path

import click
import configparser

from .babel import check_babel_configuration, extract_babel_messages, update_babel_translations, \
    compile_babel_translations, prepare_babel_translation_dir, merge_catalogues_from_translation_dir


@click.command(help="Generates and compiles localization messages. "
                    "Reads configuration from setup.cfg and uses it to call babel and i18next. "
                    "Expects setup.cfg in the current directory or you may pass the path to it as an argument.")
@click.argument("setup_cfg", default="setup.cfg")
def main(setup_cfg):
    base_dir = Path(setup_cfg).resolve().parent

    configuration = configparser.ConfigParser()
    configuration.read([setup_cfg])
    i18n_configuration = {
        k: [vv.strip() for vv in v.split('\n') if vv.strip()] for k, v in dict(configuration["oarepo.i18n"]).items()
    }
    print(i18n_configuration)

    check_babel_configuration(base_dir, i18n_configuration)

    translations_dir = prepare_babel_translation_dir(base_dir, i18n_configuration)

    extract_babel_messages(base_dir, i18n_configuration, translations_dir)

    update_babel_translations(translations_dir)

    for extra_translations in i18n_configuration.get('babel_input_translations', []):
        merge_catalogues_from_translation_dir(Path(extra_translations), translations_dir)

    # TODO: add javascript here

    compile_babel_translations(translations_dir)
