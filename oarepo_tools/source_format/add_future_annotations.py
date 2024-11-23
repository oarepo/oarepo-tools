#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from pathlib import Path


def add_future_annotations_to_module(path: Path) -> None:
    # for each python file
    for file in path.rglob("*.py"):
        add_future_annotations_to_file(file)


def future_annotation_exists(lines: list[str]) -> bool:
    for line in lines:
        if "from __future__ import annotations" in line:
            return True
    return False


def find_import_position(lines: list[str]) -> int | None:
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
    if future_annotation_exists(lines):
        return lines

    import_position = find_import_position(lines)
    if import_position is None:
        return lines

    lines.insert(import_position, "from __future__ import annotations")
    return lines


def add_future_annotations_to_file(file: Path) -> None:
    # read the file
    with open(file, "r") as f:
        lines = f.readlines()
    lines_length = len(lines)

    add_future_annotations_to_lines(lines)

    if len(lines) != lines_length:
        with open(file, "w") as f:
            lines = [line if line.endswith("\n") else line + "\n" for line in lines]
            f.writelines(lines)
