#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Future annotations check and adding."""
from __future__ import annotations

import subprocess
from pathlib import Path

import click


def add_future_annotations_to_module(path: Path) -> None:
    """Add future annotations to all python files in the given path."""
    for file in path.rglob("*.py"):
        add_future_annotations_to_file(file)


def check_future_annotations_in_module(path: Path) -> bool:
    """Check if all python files in the given path have future annotations."""
    ok = True
    for file in path.rglob("*.py"):
        if not check_future_annotations_in_file(file):
            ok = False
            click.secho(f"Missing future annotations in {file}", fg="red")
    return ok


def future_annotation_exists(lines: list[str]) -> bool:
    """Check if future annotations are already present in the given lines."""
    return any(line.startswith("from __future__ import annotations") for line in lines)


def find_import_position(lines: list[str]) -> int | None:
    """Find the position where from __future__ import ... should be added."""
    state = "initial"
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        match state:
            case "initial":
                if line.startswith("from ") or line.startswith("import "):
                    return i
                if line.startswith("#"):
                    continue
                if line.startswith('"""') or line.startswith("'''"):
                    # single-line docstring
                    if line.endswith('"""') or line.endswith("'''"):
                        continue
                    # multi-line docstring
                    state = "docstring"
                    continue
                return i
            case "docstring":
                if '"""' in line or "'''" in line:
                    state = "initial"
                continue
    return None


def add_future_annotations_to_lines(lines: list[str]) -> list[str]:
    """Add future annotations to the given lines if they are missing."""
    if future_annotation_exists(lines):
        return lines

    import_position = find_import_position(lines)
    if import_position is None:
        return lines

    lines.insert(import_position, "from __future__ import annotations")
    return lines


def add_future_annotations_to_file(file: Path) -> None:
    """Add future annotations to the given file."""
    # read the file
    with open(file) as f:
        lines = f.readlines()
    lines_length = len(lines)

    add_future_annotations_to_lines(lines)

    if len(lines) != lines_length:
        with open(file, "w") as f:
            lines = [line if line.endswith("\n") else line + "\n" for line in lines]
            f.writelines(lines)


def check_future_annotations_in_file(file: Path) -> bool:
    """Check if future annotations are present in the given file."""
    with open(file) as f:
        lines = f.readlines()
    if future_annotation_exists(lines):
        return True
    import_position = find_import_position(lines)
    return import_position is None


def check_future_annotations(paths: list[str]) -> None:
    """Check if all python files in the given paths have future annotations.

    If not, raise subprocess.CalledProcessError.
    """
    click.secho("Checking future annotations: ", fg="yellow", nl=False)
    for path in paths:
        if not check_future_annotations_in_module(Path(path)):
            raise subprocess.CalledProcessError(
                1, "check-future-annotations", "Future annotations are missing."
            )
    click.secho("Success", fg="green")


def add_future_annotations_to_paths(paths: list[str]) -> None:
    """Add future annotations to all python files in the given paths."""
    click.secho("Adding future annotations: ", fg="yellow", nl=False)
    for path in paths:
        add_future_annotations_to_module(Path(path))
    click.secho("done", fg="green")
