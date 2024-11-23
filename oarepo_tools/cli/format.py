#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Commandline tool to format and check code according to the CESNET OARepo style guide."""

from __future__ import annotations

import subprocess

import click

from oarepo_tools.module_config import PythonPackage
from oarepo_tools.source_format.format import format_code


@click.command("format")
@click.argument("paths", required=False, nargs=-1)
@click.option("--ruff-format/--no-ruff-format", default=True)
@click.option("--licenseheaders/--no-licenseheaders", default=True)
@click.option("--with-tests/--without-tests", default=False)
@click.option(
    "--project-name",
    default=None,
    help="When not passed, it will be automatically detected.",
)
@click.option(
    "--owner", default=None, help="When not passed, it will be automatically detected."
)
def main(
    paths: list[str],
    ruff_format: bool,
    licenseheaders: bool,
    with_tests: bool,
    project_name: str | None,
    owner: str | None,
):
    """Format code according to the CESNET OARepo style guide.

    If you do not pass any paths, they will be automatically detected from the package.
    """
    if paths:
        python_package = PythonPackage(paths)
    else:
        python_package = PythonPackage(".")
        paths = PythonPackage(".").top_level_source_directories

    if with_tests:
        paths += python_package.top_level_test_directories

    try:
        format_code(
            projectname=project_name or python_package.name,
            owner=owner or python_package.owner or "CESNET z.s.p.o.",
            paths=paths,
            ruff_format=ruff_format,
            licenseheaders=licenseheaders,
        )
    except subprocess.CalledProcessError as e:
        click.secho(str(e), fg="red")
        raise click.Abort()
