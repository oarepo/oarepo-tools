#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Code formatter and checker for OArepo codebase, built on top of ruff and mypy."""

import subprocess
from pathlib import Path

import click

from oarepo_tools.source_format.add_future_annotations import add_future_annotations_to_module


def format_code(
    *,
    projectname: str,
    owner: str,
    paths: list[str],
    ruff_format: bool,
    licenseheaders: bool,
    add_future_annotations: bool
):
    click.secho(
        f"Formatting code at {paths} with ruff_format={ruff_format}, "
        f"licenseheaders={licenseheaders}",
        fg="yellow",
    )

    current_file_path = Path(__file__)
    data_path = current_file_path.parent / "data"
    license_config = data_path / "license.tmpl"
    ruff_config = data_path / "ruff.toml"

    if ruff_format:
        click.secho("ruff format: ", fg="yellow", nl=False)
        subprocess.check_call(["ruff", "format", "--config", ruff_config, "--"] + paths)
        click.secho("ruff isort: ", fg="yellow", nl=False)
        subprocess.check_call(
            ["ruff", "check", "--fix", "--select", "I", "--config", ruff_config, "--"]
            + paths
        )

    if licenseheaders:
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

    if add_future_annotations:
        for path in paths:
            add_future_annotations_to_module(Path(path))