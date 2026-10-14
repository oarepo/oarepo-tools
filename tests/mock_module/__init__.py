# SPDX-FileCopyrightText: 2024-2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""A mock module containing various types of translations strings."""

from __future__ import annotations

from oarepo_runtime.i18n import lazy_gettext as _


def use_translated_strings():
    return {
        "section": _("pythonstring1"),
        "fields": [
            {
                "props": {
                    "label": _("pythonstring2"),
                    "icon": "lab",
                },
            }
        ],
    }
