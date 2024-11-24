#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Format a string with variables."""

from __future__ import annotations

import re
from typing import Any


def format_value(value: Any, variables: dict[str, dict[str, Any]]) -> Any:
    """Format a string with variables."""

    def value_replacement(match: re.Match[str]) -> str:
        """Replace a variable with its value."""
        variable_name = match.group(1).strip()
        grp, name = variable_name.split(".", 1)
        return str(variables[grp][name])

    if not isinstance(value, str):
        return value
    return re.sub(r"\${{([^}]+)}}", value_replacement, value)
