#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Input loader for workflows."""

from __future__ import annotations

from typing import Any


def load_inputs(inputs: dict[str, Any] | None) -> dict[str, Any]:
    """Load inputs from the workflow configuration.

    :param inputs: inputs from the workflow configuration
    :return: loaded inputs
    """
    ret: dict[str, Any] = {}
    if not inputs:
        return ret
    for input_name, input_def in inputs.items():
        if "default" in input_def:
            ret[input_name] = input_def["default"]
    return ret
