#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""YAML loader that converts int keys to strings."""

from __future__ import annotations

from typing import Any

import yaml


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
