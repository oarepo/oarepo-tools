#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run supporting services (such as opensearch, redis, ...)."""

from __future__ import annotations

from typing import Any

from oarepo_tools.workflow.output import output


def oarepo_test_services(
    options: dict[str, Any], variables: dict[str, dict[str, Any]]
) -> None:
    """Run supporting services (such as opensearch, redis, ...)."""
    services_to_run = ", ".join(k for k, v in options.items() if v)
    output(
        f"Supposing the following services are running: {services_to_run}", fg="green"
    )
