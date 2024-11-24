#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Checkout github action."""

from __future__ import annotations

from ..output import output
from ..step import Step


class CheckoutAction(Step):
    """Checkout action."""

    def run(self) -> None:
        """Checkout the repository."""
        if not self.inputs:
            output("Local repository already checked out", fg="green")
            return
        raise NotImplementedError(
            "Checkout action for secondary repository not yet implemented"
        )
