#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Types for workflow module."""

from __future__ import annotations

from typing import Any

type InputOutputVars = dict[str, str | bool | int | float]
type Variables = dict[str, dict[str, Any]]
type Environment = dict[str, str]
