#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run supporting services (such as opensearch, redis, ...)."""

from __future__ import annotations

import click

from ..step import Step


class OARepoTestServicesAction(Step):
    """Run supporting services (such as opensearch, redis, ...)."""

    def run(self) -> None:
        """Run supporting services (such as opensearch, redis, ...)."""
        services_to_run = ", ".join(k for k, v in self.inputs.items() if v)
        click.secho(
            f"Supposing the following services are running: {services_to_run}",
            fg="green",
        )
