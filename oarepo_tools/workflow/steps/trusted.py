#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""A trusted action from github or elsewhere."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, override

from oarepo_tools.workflow.step import Step

from ..base import Environment, InputOutputVars, WorkflowPart
from ..job import StepRunMixin
from ..output import output

if TYPE_CHECKING:
    from ..workflow import Workflow


class TrustedAction(Step):
    """A trusted action from github or elsewhere."""

    @override
    def run(self) -> InputOutputVars | None:
        """Run the trusted action."""
        if "uses" in self.definition:
            action_to_run = self.definition["uses"]
            action_definition = self.workflow.get_action_definition(action_to_run)
            runs: dict[str, Any] | None = action_definition.get("runs")
            if not runs:
                raise ValueError(
                    f"Action {action_to_run} does not have 'runs' defined."
                )
            using = runs.get("using")
            if not using:
                raise ValueError(
                    f"Action {action_to_run} does not have 'using' defined on <runs> element."
                )
            match using:
                case "composite":
                    runner = CompositeRunner(action_definition, self)
                case _:
                    raise NotImplementedError(
                        f"Running action of type {using} is not implemented yet"
                    )

            return runner.run()

        raise NotImplementedError("Only 'uses' is supported in trusted actions.")


class CompositeRunner(WorkflowPart, StepRunMixin):
    """Runner of composite actions."""

    def __init__(self, definition: dict[str, Any], step: Step):
        """Initialize the runner."""
        self.definition = definition
        self.parent = step
        self.order = 0

    @property
    def step(self):
        return self.parent

    @property
    def inputs(self) -> InputOutputVars:
        """Filter inputs to those defined in here."""
        ret: InputOutputVars = {}
        for k, v in self.definition.get("inputs", {}).items():
            if k in self.step.inputs:
                ret[k] = self.step.inputs[k]
            elif "default" in v:
                ret[k] = v["default"]
            else:
                raise Exception(
                    f"Variable {k} not passed to runner nor has a default value"
                )
        return ret

    @property
    def environment(self) -> Environment:
        """Return the environment of the workflow part."""
        return self.step.environment

    @cached_property
    def steps(self) -> list[Step]:
        """Return the steps of the job/composite action."""
        step_definitions = self.definition["runs"]["steps"]
        return [
            self.workflow.action_factory.resolve_step(x, order, self)
            for order, x in enumerate(step_definitions)
        ]

    def run(self) -> InputOutputVars | None:
        """Run the workflow part.

        Returns output of the part, if any
        """
        self.run_steps()
        return None

    @property
    def workflow(self) -> Workflow:
        """Return the workflow."""
        return self.step.workflow
