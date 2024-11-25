#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Python package metadata."""

from __future__ import annotations

import dataclasses
from functools import cached_property
from pathlib import Path

from setuptools.config.pyprojecttoml import (
    read_configuration as pyprojecttoml_read_configuration,
)
from setuptools.config.setupcfg import read_configuration as setupcfg_read_configuration


@dataclasses.dataclass
class PythonPackageMetadata:
    """Python package metadata."""

    name: str
    owner: str | None
    top_level_modules: list[str]


class PythonPackage:
    """Parser of python package directory, extracting metadata from setup.cfg or pyproject.toml."""

    def __init__(self, path: str | Path):
        """Initialize parser with path to the package."""
        self._path = Path(path)

    @cached_property
    def loaded_metadata(self) -> PythonPackageMetadata:
        """Load metadata from setup.cfg or pyproject.toml."""
        setup_cfg_path = self._path / "setup.cfg"
        pyproject_toml_path = self._path / "pyproject.toml"

        if setup_cfg_path.exists():
            return self._load_setup_cfg(setup_cfg_path)
        elif pyproject_toml_path.exists():
            return self._load_pyproject_toml(pyproject_toml_path)
        else:
            raise ValueError(
                f"No setup.cfg or pyproject.toml found inside {self._path}"
            )

    @property
    def top_level_modules(self) -> list[str]:
        """Top level modules of the package."""
        return self.loaded_metadata.top_level_modules

    @property
    def top_level_source_directories(self) -> list[str]:
        """Top level source directories of the package."""
        return [str(self._path / module) for module in self.top_level_modules]

    @property
    def top_level_test_directories(self) -> list[str]:
        """Top level test directories of the package."""
        if (self._path / "tests").exists():
            return [str(self._path / "tests")]
        return []

    @property
    def name(self) -> str:
        """Name of the package."""
        return self.loaded_metadata.name

    @property
    def owner(self) -> str | None:
        """Owner of the package."""
        return self.loaded_metadata.owner

    def _load_setup_cfg(self, setup_cfg_path: Path) -> PythonPackageMetadata:
        config = setupcfg_read_configuration(setup_cfg_path)
        return PythonPackageMetadata(
            top_level_modules=[config["metadata"]["name"].replace("-", "_").lower()],
            name=config["metadata"]["name"],
            owner=None,
        )

    def _load_pyproject_toml(self, pyproject_toml_path: Path) -> PythonPackageMetadata:
        config = pyprojecttoml_read_configuration(pyproject_toml_path)
        return PythonPackageMetadata(
            top_level_modules=[config["project"]["name"].replace("-", "_").lower()],
            name=config["project"]["name"],
            owner=None,
        )
