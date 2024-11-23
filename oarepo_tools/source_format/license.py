#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""License headers management."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import click


def add_license_headers_to_paths(license_config: Path, owner: str, paths: list[str], projectname: str) -> None:
    """Add license headers to files in given paths."""
    for path in paths:
        click.secho(f"License headers in {path}: ", fg="yellow", nl=False)
        subprocess.check_call(
            [
                "python",
                "-m",
                "licenseheaders",
                "-t",
                str(license_config),
                "-cy",
                "-o",
                owner,
                "-n",
                projectname,
                "-d",
                path,
            ]
        )
        click.secho("done")


def check_license_headers(paths: list[str], license_config: Path) -> None:
    """Check license headers in files in given paths.

    Raises subprocess.CalledProcessError in case of errors.
    """
    click.secho("Checking license headers: ", fg="yellow", nl=False)
    license_text = license_config.read_text()
    license_lines = [
        chunk
        for line in license_text.splitlines()
        for chunk in re.split(r"\${[^}]+}", line)
    ]
    license_lines = [line for line in license_lines if line.strip()]

    errors = False
    for parent_path in paths:
        for path in Path(parent_path).rglob("*.py"):
            with path.open() as f:
                content = f.read()
                for ll in license_lines:
                    if ll not in content:
                        click.secho(
                            f"Missing or incorrect license header in {path}", fg="red"
                        )
                        errors = True
                        break
    if errors:
        raise subprocess.CalledProcessError(1, "check-license", "Licenses are missing.")
    click.secho("done", fg="green")
