from oarepo_tools.source_format.future_annotations import add_future_annotations_to_lines


def test_missing_with_import():

    assert add_future_annotations_to_lines([
        "# something here",
        "import blah"
    ]) == [
        "# something here",
        "from __future__ import annotations",
        "import blah"
    ]

def test_missing_with_from_import():

        assert add_future_annotations_to_lines([
            "# something here",
            "from blah import something"
        ]) == [
            "# something here",
            "from __future__ import annotations",
            "from blah import something"
        ]

def test_missing_with_initial_license():
    assert add_future_annotations_to_lines([
        "# License: MIT",
        "#",
        "def blah(): ..."
    ]) == [
        "# License: MIT",
        "#",
        "from __future__ import annotations",
        "def blah(): ..."
    ]

def test_missing_with_module_docstring():
    assert add_future_annotations_to_lines([
        '"""Module docstring"""',
        'def blah(): ...'
    ]) == [
        '"""Module docstring"""',
        'from __future__ import annotations',
        'def blah(): ...'
    ]

def test_missing_with_module_multiline_docstring():
    assert add_future_annotations_to_lines([
        '"""Module docstring',
        'on multiple lines"""',
        'def blah(): ...'
    ]) == [
        '"""Module docstring',
        'on multiple lines"""',
        'from __future__ import annotations',
        'def blah(): ...'
    ]

def test_missing_with_module_multiline_docstring_and_license():
    assert add_future_annotations_to_lines([
        '# License: MIT',
        '"""Module docstring',
        'on multiple lines"""',
        'def blah(): ...'
    ]) == [
        '# License: MIT',
        '"""Module docstring',
        'on multiple lines"""',
        'from __future__ import annotations',
        'def blah(): ...'
    ]

def test_empty_file():
    assert add_future_annotations_to_lines([]) == []

def test_empty_file_with_license():
    assert add_future_annotations_to_lines([
        '# License: MIT'
    ]) == [
        '# License: MIT'
    ]