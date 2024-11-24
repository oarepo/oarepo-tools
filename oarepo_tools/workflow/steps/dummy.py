#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Dummy action."""

from __future__ import annotations

import click

from ..step import Step


class DummyAction(Step):
    """Bash action."""

    def run(self) -> None:
        """Check the format of the code."""
        if 'uses' in self.definition:
            click.secho(f"Noop implementation of {self.definition['uses']}", fg="green")
