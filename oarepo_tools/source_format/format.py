#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Code formatter for OArepo codebase, built on top of ruff and mypy."""

from __future__ import annotations

from pathlib import Path

import click

from oarepo_tools.source_format.future_annotations import (
    add_future_annotations_to_paths,
)
from oarepo_tools.source_format.license import add_license_headers_to_paths
from oarepo_tools.source_format.ruff import format_with_ruff


def format_code(
    *,
    projectname: str,
    owner: str,
    paths: list[str],
    ruff_format: bool,
    licenseheaders: bool,
    add_future_annotations: bool,
) -> None:
    """Format code at given paths."""
    click.secho(
        f"Formatting code at {', '.join(paths)} with ruff_format={ruff_format}, "
        f"licenseheaders={licenseheaders}, add_future_annotations={add_future_annotations}",
        fg="yellow",
    )

    current_file_path = Path(__file__)
    data_path = current_file_path.parent / "data"
    license_config = data_path / "license.tmpl"
    ruff_config = data_path / "ruff.toml"

    if add_future_annotations:
        add_future_annotations_to_paths(paths)

    if licenseheaders:
        add_license_headers_to_paths(license_config, owner, paths, projectname)

    if ruff_format:
        format_with_ruff(paths, ruff_config)
