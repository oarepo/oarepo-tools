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
from pathlib import Path

import click

from oarepo_tools.module_config import PythonPackage
from oarepo_tools.source_format.check import check_code
from oarepo_tools.source_format.format import format_code


@click.command("check")
@click.argument("paths", required=False, nargs=-1)
@click.option("--ruff/--no-ruff", default=True)
@click.option("--licenseheaders/--no-licenseheaders", default=True)
@click.option("--future-annotations/--no-future-annotations", default=True)
@click.option("--with-tests/--without-tests", default=False)
@click.option("--mypy/--no-mypy", default=True)
@click.option("--fix/--no-fix", default=False)
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
    ruff: bool,
    licenseheaders: bool,
    with_tests: bool,
    project_name: str | None,
    owner: str | None,
    future_annotations: bool,
    mypy: bool,
    fix: bool,
) -> None:
    """Check code if it adheres to the CESNET OARepo style guide.

    If you do not pass any paths, they will be automatically detected from the package.
    """
    paths, python_package = prepare_paths(paths, with_tests)

    try:
        if fix:
            format_code(
                projectname=project_name or python_package.name,
                owner=owner or python_package.owner or "CESNET z.s.p.o.",
                paths=paths,
                ruff_format=ruff,
                licenseheaders=licenseheaders,
                add_future_annotations=future_annotations,
            )

        check_code(
            projectname=project_name or python_package.name,
            owner=owner or python_package.owner or "CESNET z.s.p.o.",
            paths=paths,
            ruff=ruff,
            licenseheaders=licenseheaders,
            future_annotations=future_annotations,
            mypy=mypy,
            fix=fix,
        )
    except subprocess.CalledProcessError as e:
        # click.secho(str(e), fg="red")
        raise click.Abort() from e


def prepare_paths(paths: list[str], with_tests: bool) -> tuple[list[str], PythonPackage]:
    """Prepare paths and parse python package's configuration in the top path."""
    if paths:
        # get the common top-level directory of paths
        common_path = Path(paths[0])
        if not common_path.is_dir():
            common_path = common_path.parent

        for path in paths[1:]:
            pth = Path(path)
            if not pth.is_dir():
                pth = pth.parent
            while common_path not in pth.parents:
                common_path = common_path.parent
            if not common_path:
                raise ValueError("Paths do not have a common top-level directory.")
        python_package = PythonPackage(common_path)
    else:
        python_package = PythonPackage(".")
        paths = PythonPackage(".").top_level_source_directories
    if with_tests:
        paths += python_package.top_level_test_directories
    return paths, python_package
