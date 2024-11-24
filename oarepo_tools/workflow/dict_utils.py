#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Dictionary utilities."""

from __future__ import annotations

from typing import Any


def dict_get[T](d: dict[str, Any], *path: str, default: T | None = None) -> T:
    """Get value from nested dictionary using path.

    :param d: dictionary
    :param path: path to the value
    :return: value from the dictionary
    """
    for key in path:
        if key in d:
            d = d[key]
        else:
            return default  # type: ignore
    return d  # type: ignore
