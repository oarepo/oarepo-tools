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
from typing import TYPE_CHECKING, override

import click

from .base import WorkflowPart
from .output import output

if TYPE_CHECKING:
    from .base import Environment, InputOutputVars
    from .step import Step
    from .workflow import Workflow


class StepRunMixin:
    """Mixin for running steps."""

    def run_steps(self) -> None:
        """Run the step."""
        steps: list[Step] = self.steps  # type: ignore
        for step in steps:
            click.secho(f"Running step {step}", fg="yellow")
            if step.condition():
                with output.nested():
                    step.run()


@dataclasses.dataclass
class Job(WorkflowPart, StepRunMixin):
    """A job."""

    name: str

    @property
    @override
    def workflow(self) -> Workflow:
        return self.parent.workflow

    @cached_property
    def steps(self) -> list[Step]:
        """Return the steps of the job."""
        return [
            self.workflow.action_factory.resolve_step(step_definition, order, self)
            for order, step_definition in enumerate(self.definition.get("steps", []))
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
        click.secho(f"Running job {self.name}", fg="yellow")
        with output.nested():
            self.run_steps()

    @property
    def build_path_name(self) -> str:
        """Return the name of the build path."""
        return self.sanitize_path_name(self.name)

    def __str__(self) -> str:
        """Return the name of the job as its string representation."""
        return self.name
