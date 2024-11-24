#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Code formatter for OArepo codebase."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from pathlib import Path


def validate_output_translations_dir(
    base_dir: Path,
    i18n_configuration: dict[str, Any],
    config_key: str,
    create_if_missing: bool = False,
) -> Path | None:
    """Validate output translations directory from configuration."""
    babel_output_translations: str | None = i18n_configuration.get(config_key)
    if not babel_output_translations:
        return None

    translations_dir = base_dir / babel_output_translations

    if not translations_dir.exists():
        if create_if_missing:
            translations_dir.mkdir(parents=True)
            click.secho(f"Created {translations_dir}", fg="green")
        else:
            return None

    return translations_dir


def validate_source_paths(
    base_dir: Path,
    i18n_configuration: dict[str, Any],
    config_key: str,
) -> list[Path]:
    """Validate source paths from configuration."""
    source_paths = i18n_configuration.get(config_key, [])
    if not source_paths:
        return []

    sanitized_source_paths = []
    for path in source_paths:
        source_path: Path = base_dir / path.strip()
        if not source_path.exists():
            click.secho(f"Invalid path: {str(source_path)}. Skipping...", fg="yellow")
            continue
        sanitized_source_paths.append(source_path)

    return sanitized_source_paths
