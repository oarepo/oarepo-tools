#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Local github actions runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oarepo_tools.workflow.actions import actions
from oarepo_tools.workflow.step import ActionFactory
from oarepo_tools.workflow.workflow import Workflow

if TYPE_CHECKING:
    from pathlib import Path

    from .types import InputOutputVars


def load_and_run_workflow(
    workflow_file: Path,
    local_oarepo_actions_path: Path | None,
    overridden_inputs: InputOutputVars,
    temporary_dir: Path,
) -> None:
    """Load and run a workflow."""
    workspace = str(workflow_file.parent.parent.parent)

    action_factory = ActionFactory(actions)

    workflow = Workflow(
        workflow_file=workflow_file,
        inputs=overridden_inputs,
        environment={"GITHUB_WORKSPACE": workspace},
        github={
            "workspace": workspace,
        },
        action_factory=action_factory,
    )
    workflow.run()
