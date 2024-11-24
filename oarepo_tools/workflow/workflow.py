#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""A workflow class."""

from __future__ import annotations

import subprocess
from functools import cached_property
from typing import TYPE_CHECKING, Any, cast, override

import click
import yaml

from .base import WorkflowPart
from .dict_utils import dict_get
from .env import update_env
from .job import Job
from .output import output
from .yaml_tools import StringKeyLoader

if TYPE_CHECKING:
    from pathlib import Path

    from .base import Environment, InputOutputVars, LocalAction
    from .step import ActionFactory


class Workflow(WorkflowPart):
    """A workflow."""

    def __init__(
        self,
        workflow_file: Path,
        inputs: InputOutputVars,
        environment: Environment,
        github: InputOutputVars,
        action_factory: ActionFactory,
        temporary_dir: Path,
        local_actions: list[LocalAction],
    ):
        """Initialize the workflow."""
        self.workflow_file = workflow_file
        self.workflow_definition = self._load_workflow(workflow_file)
        self.overridden_inputs = inputs
        self.initial_environment = environment
        self.github = github
        self.action_factory = action_factory
        self.temporary_dir = temporary_dir
        self.local_actions = {
            (action.owner, action.repo): action.path for action in local_actions
        }

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
            job_name: Job(order=idx, name=job_name, parent=self, definition=job_def)
            for idx, (job_name, job_def) in enumerate(
                self.workflow_definition.get("jobs", {}).items()
            )
        }

    @override
    def run(self) -> None:
        """Run the workflow."""
        click.secho(f"Running workflow {self.name}", fg="yellow")
        for job in self.jobs.values():
            with output.nested():
                job.run()

    def get_action_definition(self, action: str) -> dict[str, Any]:
        """Clone the action and return path to its action.yml file."""
        action, version = action.split("@", 1) if "@" in action else (action, None)
        split = action.split("/")
        if len(split) < 2:
            raise ValueError(f"Invalid action format: {action}")
        owner = split[0]
        repository = split[1]
        action_within_repository = "/".join(split[2:])

        if (owner, repository) in self.local_actions:
            action_repo_dir = self.local_actions[(owner, repository)]
        else:
            action_repo_dir = self._clone_repository(owner, repository, version)

        if action_within_repository:
            action_repo_dir /= action_within_repository

        action_file = action_repo_dir / "action.yml"

        if not action_file.exists():
            raise ValueError(f"Action {action} does not contain action.yml file")

        with open(action_file) as f:
            return yaml.load(f, Loader=StringKeyLoader)  # type: ignore

    def _clone_repository(
        self, owner: str, repository: str, version: str | None
    ) -> Path:
        """Clone the repository to a temp directory and return path to it."""
        action_repo_dir = (
            self.temporary_dir / "actions" / owner / repository / (version or "main")
        )
        if not action_repo_dir.exists():
            action_repo_dir.mkdir(parents=True)
            if version:
                raise NotImplementedError("Cloning by version is not supported yet")
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    f"https://github.com/{owner}/{repository}",
                    str(action_repo_dir),
                ]
            )
        return action_repo_dir

    @property
    def relative_build_path(self) -> Path:
        """Return the path to the workflow."""
        return self.temporary_dir / "build" / self.workflow_file.stem