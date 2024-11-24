#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run github pipeline including oarepo/actions locally."""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any

import click

from oarepo_tools.workflow.local_runner import load_and_run_workflow


@click.command()
@click.option("--workflow-name", default="build.yaml")
@click.option(
    "--local-oarepo-actions-path",
    default=None,
    help="Path to local oarepo/actions repository.",
)
@click.option("--debug/--no-debug", default=False)
def main(
    workflow_name: str, local_oarepo_actions_path: str | None, debug: bool
) -> None:
    """Run github pipeline including oarepo/actions locally."""
    if not workflow_name.endswith(".yaml"):
        workflow_name += ".yaml"
    workflow_dir = Path.cwd() / ".github" / "workflows" / workflow_name

    inputs: dict[str, Any] = {}
    temporary_dir = Path.cwd() / ".temp"

    try:
        load_and_run_workflow(
            workflow_dir,
            Path(local_oarepo_actions_path) if local_oarepo_actions_path else None,
            inputs,
            temporary_dir,
        )
    except Exception as e:
        click.secho(f"Workflow failed - {type(e).__name__}: {str(e)}", fg="red")
        if debug:
            traceback.print_exc()
        raise click.Abort(str(e)) from e
