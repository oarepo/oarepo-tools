#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Check format github action."""

from __future__ import annotations

from typing import cast

from oarepo_tools.source_format.check import check_code
from oarepo_tools.source_format.paths import prepare_paths

from ..output import output
from ..step import Step


class OARepoCheckFormatAction(Step):
    """Action to check the format of the code."""

    def run(self) -> None:
        """Check the format of the code."""
        paths, python_package = prepare_paths(
            [],
            False,
            package_path=cast(str, self.workflow.github["workspace"]),
        )

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
