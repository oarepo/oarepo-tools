#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Workflow step."""

from __future__ import annotations

import abc
import dataclasses
from typing import TYPE_CHECKING, Any, override

from .base import WorkflowPart
from .env import update_env
from .format import format_value

if TYPE_CHECKING:
    from .job import Job
    from .types import Environment, InputOutputVars, Variables
    from .workflow import Workflow


@dataclasses.dataclass()
class Step(WorkflowPart):
    """An abstract workflow job step."""

    definition: dict[str, Any]
    """The definition of the action."""

    job: Job

    @property
    @override
    def inputs(self) -> InputOutputVars:
        """Return the inputs of the workflow part."""
        variables: Variables = {
            "github": self.workflow.github,
            "inputs": self.job.inputs,  # take inputs from job
            "env": self.job.environment,
        }
        return {
            k: format_value(v, variables)
            for k, v in self.definition.get("with", {}).items()
        }

    @property
    @override
    def environment(self) -> Environment:
        """Return the environment of the workflow part."""
        variables: Variables = {
            "github": self.workflow.github,
            "inputs": self.inputs,  # take inputs from this action
            "env": self.job.environment,
        }
        return update_env(
            self.job.environment, self.definition.get("env") or {}, variables=variables
        )

    @property
    @override
    def workflow(self) -> Workflow:
        """Return the workflow."""
        return self.job.workflow

    @abc.abstractmethod
    @override
    def run(self) -> InputOutputVars | None:
        """Run the step."""
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """Return the name of the step."""
        return self.definition.get("name")  # type: ignore

    @property
    def step_type(self) -> str | None:
        """Return the type of the step."""
        if "uses" in self.definition:
            return self.definition["uses"]  # type: ignore
        if "shell" in self.definition:
            return self.definition["shell"]  # type: ignore
        if "run" in self.definition:
            return "shell"
        return None

    def __str__(self) -> str:
        """Return the name of the job as its string representation."""
        name = self.name
        step_type = self.step_type
        if name:
            return f"{name} ({step_type})"
        else:
            return step_type or "<unknown>"


class ActionFactory:
    """An abstract factory for creating actions."""

    def __init__(self, actions: dict[str, type[Step]]):
        """Initialize the factory."""
        self.actions = actions

    def resolve(self, definition: dict[str, Any], job: Job) -> Step:
        """Resolve the action from the definition."""
        match definition:
            case definition if "uses" in definition:
                action_type = definition["uses"]
            case definition if "shell" in definition:
                action_type = definition["shell"]
            case definition if "run" in definition:
                action_type = "bash"
            case _:
                raise ValueError(f"No action type found in definition {definition}")

        if action_type not in self.actions:
            raise ValueError(f"Unknown action type {action_type}")

        return self.actions[action_type](definition=definition, job=job)
