#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""MyPy check."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from pathlib import Path


def check_mypy(paths: list[str], mypy_config: Path) -> None:
    """Check code with mypy and raise subprocess.CalledProcessError in case of errors."""
    click.secho("mypy: ", fg="yellow", nl=False)
    subprocess.check_call(
        ["mypy", "--strict", "--config-file", str(mypy_config)] + paths
    )
