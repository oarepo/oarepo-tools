#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Python package utilities."""

from __future__ import annotations

from pathlib import Path

from oarepo_tools.module_config import PythonPackage


def prepare_paths(
    paths: list[str], with_tests: bool, package_path: str | None = None
) -> tuple[list[str], PythonPackage]:
    """Prepare paths and parse python package's configuration in the top path."""
    paths = list(paths)
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
        while common_path and not (common_path / "setup.cfg").exists() and not (
            common_path / "pyproject.toml"
        ).exists():
            common_path = common_path.parent
        if not common_path:
            raise ValueError("No setup.cfg or pyproject.toml found in paths.")
        python_package = PythonPackage(common_path)
    else:
        python_package = PythonPackage(package_path or ".")
        paths = python_package.top_level_source_directories
    if with_tests:
        paths += python_package.top_level_test_directories
    return paths, python_package
