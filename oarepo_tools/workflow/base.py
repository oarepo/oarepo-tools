#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Base classes for workflows."""

from __future__ import annotations

import abc
import dataclasses
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from .workflow import Workflow


type InputOutputVars = dict[str, str | bool | int | float]
type Variables = dict[str, dict[str, Any]]
type Environment = dict[str, str]


@dataclasses.dataclass
class LocalAction:
    """Local action."""

    owner: str
    """The owner of the repository."""

    repo: str
    """The repository name."""

    path: Path
    """The path to the repository."""


@dataclasses.dataclass
class WorkflowPart(abc.ABC):
    """A workflow part."""

    order: int
    parent: WorkflowPart
    definition: dict[str, Any]

    @property
    @abc.abstractmethod
    def inputs(self) -> InputOutputVars:
        """Return the inputs of the workflow part."""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def environment(self) -> Environment:
        """Return the environment of the workflow part."""
        raise NotImplementedError()

    @abc.abstractmethod
    def run(self) -> InputOutputVars | None:
        """Run the workflow part.

        Returns output of the part, if any
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def workflow(self) -> Workflow:
        """Return the workflow."""
        raise NotImplementedError()

    @property
    def build_path_name(self) -> str:
        """Return the name of the build path."""
        uses: str | None = self.definition.get("uses")
        name: str | None = self.definition.get("name")
        if name:
            return self.sanitize_path_name(name)
        if uses:
            uses = uses.replace('/', '-').split('@')[0]
            return str(self.order) + "-" + uses
        return str(self.order)

    def sanitize_path_name(self, name):
        return re.sub('[^a-zA-Z0-9-]', '', name.replace(" ", "-")).lower()[:40]

    @property
    def relative_build_path(self) -> Path:
        """Return the path to the workflow."""
        return self.parent.relative_build_path / self.build_path_name
