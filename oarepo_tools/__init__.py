# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Translation tooling for OARepo packages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import click

if TYPE_CHECKING:
    from pathlib import Path


def validate_output_translations_dir(
    base_dir: Path, i18n_configuration: dict, config_key: str, create_if_missing: bool = False
) -> Path | Literal[False]:
    """Return the output translations directory configured under `config_key`, or False if unusable."""
    babel_output_translations = i18n_configuration.get(config_key)
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
    base_dir: Path,
    i18n_configuration: dict,
    config_key: str,
) -> list[Path] | Literal[False]:
    """Return existing source paths configured under `config_key`, or False if none are configured."""
    source_paths = i18n_configuration.get(config_key, [])
    if not source_paths:
        return False

    sanitized_source_paths = []
    for path in source_paths:
        source_path: Path = base_dir / path.strip()
        if not source_path.exists():
            click.secho(f"Invalid path: {source_path!s}. Skipping...", fg="yellow")
            continue
        sanitized_source_paths.append(source_path)

    return sanitized_source_paths
