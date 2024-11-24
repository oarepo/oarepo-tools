#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Check format github action."""

from __future__ import annotations

from typing import Any

from oarepo_tools.source_format.check import check_code
from oarepo_tools.source_format.paths import prepare_paths
from oarepo_tools.workflow.output import output


def oarepo_check_format(
    options: dict[str, Any], variables: dict[str, dict[str, Any]]
) -> None:
    """Check the format of the code."""
    paths, python_package = prepare_paths([], False)

    with output.nested_stdout():
        check_code(
            projectname=python_package.name,
            owner=python_package.owner or "CESNET z.s.p.o.",
            paths=paths,
            ruff=True,
            licenseheaders=True,
            future_annotations=True,
            mypy=True,
            fix=False,
        )
