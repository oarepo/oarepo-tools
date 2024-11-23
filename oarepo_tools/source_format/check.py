#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Code checker for OArepo codebase, built on top of ruff and mypy."""

from __future__ import annotations

from pathlib import Path

import click

from oarepo_tools.source_format.future_annotations import (
    check_future_annotations,
)
from oarepo_tools.source_format.license import check_license_headers
from oarepo_tools.source_format.mypy import check_mypy
from oarepo_tools.source_format.ruff import check_ruff


def check_code(
    *,
    projectname: str,
    owner: str,
    paths: list[str],
    ruff: bool,
    licenseheaders: bool,
    future_annotations: bool,
    mypy: bool,
    fix: bool,
) -> None:
    """Check code at given paths.

    If --fix is provided, tools that can fix the code will do so.
    """
    click.secho(
        f"Checking code at {', '.join(paths)} with ruff={ruff}, licenseheaders={licenseheaders}, "
        f"future_annotations={future_annotations}, mypy={mypy}, fix={fix}",
        fg="yellow",
    )

    current_file_path = Path(__file__)
    data_path = current_file_path.parent / "data"
    license_config = data_path / "license.tmpl"
    ruff_config = data_path / "ruff.toml"
    mypy_config = data_path / "mypy.ini"

    if future_annotations:
        check_future_annotations(paths)

    if licenseheaders:
        check_license_headers(paths, license_config)

    if ruff:
        check_ruff(paths, ruff_config)

    if mypy:
        check_mypy(paths, mypy_config)
