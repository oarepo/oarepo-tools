from pathlib import Path


def add_future_annotations_to_module(path: Path):
    # for each python file
    for file in path.rglob("*.py"):
        add_future_annotations_to_file(file)


def future_annotation_exists(lines):
    for line in lines:
        if "from __future__ import annotations" in line:
            return True
    return False

def find_import_position(lines):
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            return i
    return None


def add_future_annotations_to_file(file: Path):
    # read the file
    with open(file, "r") as f:
        lines = f.readlines()

    if future_annotation_exists(lines):
        return

    import_position = find_import_position(lines)
    if import_position is None:
        return

    lines.insert(import_position, "from __future__ import annotations\n")

    with open(file, "w") as f:
        f.writelines(lines)