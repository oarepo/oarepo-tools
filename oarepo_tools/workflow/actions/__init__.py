#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run actions in the workflow."""

from __future__ import annotations

from .checkout import CheckoutAction
from .oarepo_check_format import OARepoCheckFormatAction
from .oarepo_test_services import OARepoTestServicesAction

actions = {
    "actions/checkout@v4": CheckoutAction,
    "oarepo/actions/check-format@1": OARepoCheckFormatAction,
    "oarepo/actions/services@1": OARepoTestServicesAction,
}

__all__ = ["actions"]
