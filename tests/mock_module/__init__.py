# A mock module containing various types of translations strings

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
