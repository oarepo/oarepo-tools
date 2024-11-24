#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Local github actions runner."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

from oarepo_tools.workflow.actions import run_action
from oarepo_tools.workflow.dict_utils import dict_get
from oarepo_tools.workflow.env import update_env
from oarepo_tools.workflow.inputs import load_inputs
from oarepo_tools.workflow.output import output

if TYPE_CHECKING:
    from pathlib import Path


class StringKeyLoader(yaml.SafeLoader):  # type: ignore
    """YAML loader that converts int keys to strings."""

    def construct_mapping(self, *args: Any, **kwargs: Any) -> Any:
        """Construct a mapping."""
        mapping = super().construct_mapping(*args, **kwargs)

        for key in list(mapping.keys()):
            if isinstance(key, bool):
                if key:
                    mapping["on"] = mapping.pop(key)
                else:
                    mapping["off"] = mapping.pop(key)
            elif isinstance(key, (int, float)):
                mapping[str(key)] = mapping.pop(key)

        return mapping


def load_and_run_workflow(
    workflow_file: Path,
    local_oarepo_actions_path: Path | None,
    overriden_inputs: dict[str, str],
    temporary_dir: Path,
) -> None:
    """Load and run a workflow."""
    with open(workflow_file) as file:
        workflow = yaml.load(file, Loader=StringKeyLoader)

    inputs = load_inputs(
        dict_get(workflow, "on", "workflow_call", "inputs", default={})
    )
    inputs.update(overriden_inputs)

    env: dict[str, str] = {}
    if "env" in workflow:
        env = update_env(
            env,
            dict_get(workflow, "env", default={}) or {},
            variables=dict(inputs=inputs, env=env),
        )

    run_jobs(workflow.get("jobs"), variables=dict(inputs=inputs, env=env))


def run_jobs(jobs: dict[str, Any], variables: dict[str, Any]) -> None:
    """Run jobs from the workflow file."""
    output.enter()
    for job_name, job_definition in jobs.items():
        run_job(job_name, job_definition, variables)
    output.exit()


def run_job(
    job_name: str, job_definition: dict[str, Any], variables: dict[str, Any]
) -> None:
    """Run a single job."""
    output(f"Running job {job_name}", fg="yellow")
    for step in job_definition.get("steps", []):
        output.enter()
        run_step(step, variables)
        output.exit()


def step_name(step: dict[str, Any]) -> str:
    """Get the name of the step for printing."""
    if "name" in step:
        return step["name"]  # type: ignore
    if "uses" in step:
        return step["uses"]  # type: ignore
    return ""


def run_step(step: dict[str, Any], variables: dict[str, Any]) -> None:
    """Run a single step."""
    output(f"Running step {step_name(step)}", fg="yellow")
    if "uses" in step:
        output.enter()
        run_action(step["uses"], step, variables)
        output.exit()
