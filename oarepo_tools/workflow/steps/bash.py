#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Bash action."""

from __future__ import annotations

import subprocess
from ..step import Step
from ..base import Environment


class BashAction(Step):
    """Bash action."""

    def run(self) -> Environment | None:
        """Check the format of the code."""
        run = self.definition.get("run", "")
        if not run:
            return None
        bash_file = self.relative_build_path.with_suffix(".sh")
        github_output = self.relative_build_path.with_suffix(".out")
        bash_file.parent.mkdir(parents=True, exist_ok=True)
        with bash_file.open("w") as f:
            for k, v in self.environment.items():
                f.write(f"export {k}=\"{v}\"\n")
            f.write(f"export GITHUB_OUTPUT=\"{github_output}\"\n")
            f.write("\n\n")
            f.write(run)

        subprocess.check_call(["bash", str(bash_file)])

        # read variables from the output file
        if github_output.exists():
            env = {}
            with github_output.open() as f:
                for line in f:
                    key, value = line.strip().split("=", 1)
                    env[key] = value.strip('"').strip("'")
            return env
        return None