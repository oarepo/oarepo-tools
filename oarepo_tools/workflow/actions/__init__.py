#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run actions in the workflow."""

from __future__ import annotations

from typing import Any

from ..format import format_value
from .checkout import handle_checkout
from .oarepo_check_format import oarepo_check_format
from .oarepo_test_services import oarepo_test_services

actions = {
    "actions/checkout@v4": handle_checkout,
    "oarepo/actions/check_format@1": oarepo_check_format,
    "oarepo/actions/services@1": oarepo_test_services,
}


def parse_action_options(
    action: dict[str, Any], variables: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Parse action options."""
    if "with" not in action:
        return {}

    return {k: format_value(v, variables) for k, v in action["with"].items()}


def run_action(
    action_name: str, action: dict[str, Any], variables: dict[str, dict[str, Any]]
) -> None:
    """Run the action."""
    if action_name not in actions:
        raise ValueError(f"Unknown action: {action_name}")

    options = parse_action_options(action, variables)
    actions[action_name](options, variables)
