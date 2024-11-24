#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Checkout github action."""

from __future__ import annotations

from typing import Any

from oarepo_tools.workflow.output import output


def handle_checkout(
    options: dict[str, Any], variables: dict[str, dict[str, Any]]
) -> None:
    """Handle the checkout action."""
    if not options:
        output("Local repository already checked out", fg="green")
        return
