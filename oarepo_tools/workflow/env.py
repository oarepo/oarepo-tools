#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Environment variables handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .format import format_value

if TYPE_CHECKING:
    from .base import Environment, Variables


def update_env(
    actual_env: Environment,
    env_definition: Environment,
    variables: Variables,
) -> Environment:
    """Update the environment with the definition."""
    actual_env = {**actual_env}
    variables["env"] = actual_env

    for key, value in env_definition.items():
        if isinstance(value, str):
            actual_env[key] = str(format_value(value, variables))
        else:
            actual_env[key] = value

    return actual_env
