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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Environment, InputOutputVars
    from .workflow import Workflow


class WorkflowPart(abc.ABC):
    """A workflow part."""

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
