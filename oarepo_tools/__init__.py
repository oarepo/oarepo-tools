from pathlib import Path

import click


def validate_output_translations_dir(
    base_dir, i18n_configuration, config_key, create_if_missing=False
):
    babel_output_translations = i18n_configuration.get(config_key, None)
    if not babel_output_translations:
        return False

    translations_dir = base_dir / babel_output_translations

    if not translations_dir.exists():
        if create_if_missing:
            translations_dir.mkdir(parents=True)
            click.secho(f"Created {translations_dir}", fg="green")
        else:
            return False

    return translations_dir


def validate_source_paths(
    base_dir,
    i18n_configuration,
    config_key,
):
    source_paths = i18n_configuration.get(config_key, [])
    if not source_paths:
        return False

    sanitized_source_paths = []
    for path in source_paths:
        source_path: Path = base_dir / path.strip()
        if not source_path.exists():
            click.secho(f"Invalid path: {str(source_path)}. Skipping...", fg="yellow")
            continue
        sanitized_source_paths.append(source_path)

    return sanitized_source_paths
