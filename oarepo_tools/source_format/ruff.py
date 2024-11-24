#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Code formatter for OArepo codebase, built on top of ruff."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from pathlib import Path


def format_with_ruff(paths: list[str], ruff_config: Path) -> None:
    """Format code with ruff and raise subprocess.CalledProcessError in case of errors."""
    click.secho("ruff format: ", fg="yellow", nl=False)
    subprocess.check_call(
        ["ruff", "format", "--config", str(ruff_config), "--"] + paths
    )
    click.secho("ruff isort: ", fg="yellow", nl=False)
    subprocess.check_call(
        ["ruff", "check", "--fix", "--select", "I", "--config", str(ruff_config), "--"]
        + paths
    )


def check_ruff(paths: list[str], ruff_config: Path) -> None:
    """Check code with ruff and raise subprocess.CalledProcessError in case of errors."""
    click.secho("ruff: ", fg="yellow", nl=False)
    subprocess.check_call(
        ["ruff", "check", "--fix", "--config", str(ruff_config), "--"] + paths
    )
