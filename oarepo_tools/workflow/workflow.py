#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""A workflow class."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, cast, override

import yaml

from .base import WorkflowPart
from .dict_utils import dict_get
from .env import update_env
from .job import Job
from .output import output
from .yaml_tools import StringKeyLoader

if TYPE_CHECKING:
    from pathlib import Path

    from .step import ActionFactory
    from .types import Environment, InputOutputVars


class Workflow(WorkflowPart):
    """A workflow."""

    def __init__(
        self,
        workflow_file: Path,
        inputs: InputOutputVars,
        environment: Environment,
        github: InputOutputVars,
        action_factory: ActionFactory,
    ):
        """Initialize the workflow."""
        self.workflow_file = workflow_file
        self.workflow_definition = self._load_workflow(workflow_file)
        self.overridden_inputs = inputs
        self.initial_environment = environment
        self.github = github
        self.action_factory = action_factory

    @classmethod
    def _load_workflow(cls, workflow_file: Path) -> dict[str, Any]:
        """Load the workflow."""
        with open(workflow_file) as file:
            return yaml.load(file, Loader=StringKeyLoader)  # type: ignore

    @property
    def name(self) -> str:
        """Return the name of the workflow."""
        return cast(str, self.workflow_definition.get("name", "<unknown>"))

    @cached_property
    @override
    def inputs(self) -> InputOutputVars:
        """Return the inputs of the workflow."""
        inputs_dict: dict[str, Any] = dict_get(
            self.workflow_definition, "on", "workflow_call", "inputs", default={}
        )

        ret: dict[str, Any] = {}
        for input_name, input_def in inputs_dict.items():
            if "default" in input_def:
                ret[input_name] = input_def["default"]
        ret.update(self.overridden_inputs)
        return ret

    @property
    @override
    def workflow(self) -> Workflow:
        """Return the workflow."""
        return self

    @cached_property
    @override
    def environment(self) -> Environment:
        """Return the environment of the workflow."""
        env: dict[str, str] = {}
        if "env" in self.workflow_definition:
            env = update_env(
                env,
                self.workflow_definition.get("env") or {},
                variables=dict(inputs=self.inputs, env=env),
            )
        return env

    @cached_property
    def jobs(self) -> dict[str, Job]:
        """Return the jobs of the workflow."""
        return {
            job_name: Job(name=job_name, parent_workflow=self, definition=job_def)
            for job_name, job_def in self.workflow_definition.get("jobs", {}).items()
        }

    @override
    def run(self) -> None:
        """Run the workflow."""
        output(f"Running workflow {self.name}")
        for job in self.jobs.values():
            output.enter()
            job.run()
            output.exit()
