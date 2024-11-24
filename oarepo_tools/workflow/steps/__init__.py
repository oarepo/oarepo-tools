#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Run actions in the workflow."""

from __future__ import annotations

from .bash import BashAction
from .checkout import CheckoutAction
from .dummy import DummyAction
from .oarepo_check_format import OARepoCheckFormatAction
from .oarepo_test_services import OARepoTestServicesAction
from .trusted import TrustedAction

steps = {
    "actions/checkout@v4": CheckoutAction,
    "oarepo/actions/check-format@1": OARepoCheckFormatAction,
    "oarepo/actions/services@1": OARepoTestServicesAction,
    "oarepo/actions/prepare-test-env@1": TrustedAction,
    "oarepo/actions/python@v1": TrustedAction,
    "oarepo/actions/python-installer@v1": TrustedAction,
    "astral-sh/setup-uv@v3": DummyAction,
    "actions/setup-python@v5": DummyAction,
    "bash": BashAction,
}

__all__ = ["steps"]
