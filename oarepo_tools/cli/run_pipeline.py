#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run github pipeline including oarepo/actions locally."""

from __future__ import annotations

import shutil
import traceback
from pathlib import Path
from typing import Any

import click

from oarepo_tools.workflow.base import LocalAction
from oarepo_tools.workflow.local_runner import load_and_run_workflow


@click.command()
@click.option("--workflow-name", default="build.yaml")
@click.option(
    "--local-actions",
    default=None,
    help="Path to local actions, format: owner/repo=<local path>",
    multiple=True,
)
@click.option("--debug/--no-debug", default=False)
def main(workflow_name: str, local_actions: list[str], debug: bool) -> None:
    """Run github pipeline including oarepo/actions locally."""
    if not workflow_name.endswith(".yaml"):
        workflow_name += ".yaml"
    workflow_dir = Path.cwd() / ".github" / "workflows" / workflow_name

    inputs: dict[str, Any] = {}
    temporary_dir = Path.cwd() / ".temp"

    if temporary_dir.exists():
        shutil.rmtree(temporary_dir)

    local_action_list: list[LocalAction] = []
    for act in local_actions:
        owner_repo, local_path = act.split("=")
        owner, repo = owner_repo.split("/")
        local_action_list.append(LocalAction(owner, repo, Path(local_path)))

    try:
        load_and_run_workflow(
            workflow_dir,
            local_action_list,
            inputs,
            temporary_dir,
        )
    except Exception as e:
        click.secho(f"Workflow failed - {type(e).__name__}: {str(e)}", fg="red")
        if debug:
            traceback.print_exc()
        raise click.Abort(str(e)) from e


if __name__ == "__main__":
    main()
