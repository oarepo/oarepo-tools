#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""A workflow job implementation."""

from __future__ import annotations

import dataclasses
from functools import cached_property
from typing import TYPE_CHECKING, Any, override

from .base import WorkflowPart
from .output import output

if TYPE_CHECKING:
    from .step import Step
    from .types import Environment, InputOutputVars
    from .workflow import Workflow


@dataclasses.dataclass
class Job(WorkflowPart):
    """A job."""

    name: str
    parent_workflow: Workflow
    definition: dict[str, Any]

    @property
    @override
    def workflow(self) -> Workflow:
        return self.parent_workflow

    @cached_property
    def steps(self) -> list[Step]:
        """Return the steps of the job."""
        return [
            self.workflow.action_factory.resolve(step_definition, self)
            for step_definition in self.definition.get("steps", [])
        ]

    @property
    @override
    def inputs(self) -> InputOutputVars:
        """Return the inputs of the job."""
        # job does not have any inputs, so just defer to the workflow
        return self.workflow.inputs

    @property
    @override
    def environment(self) -> Environment:
        """Return the environment of the job."""
        # job does not have any environment, so just defer to the workflow
        return self.workflow.environment

    @override
    def run(self) -> None:
        """Run a single job."""
        output(f"Running job {self.name}", fg="yellow")
        for step in self.steps:
            output.enter()
            output(f"Running step {step}", fg="yellow")
            step.run()
            output.exit()

    def __str__(self) -> str:
        """Return the name of the job as its string representation."""
        return self.name
