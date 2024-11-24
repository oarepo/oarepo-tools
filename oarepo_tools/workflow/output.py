#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-tools is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Indented output writer."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, TextIO

import click

if TYPE_CHECKING:
    from collections.abc import Generator


class IndentedStream:
    """Stream with indentation support."""

    def __init__(
        self, stream: TextIO, level: int, indent: int, autoflush: bool = False
    ) -> None:
        """Initialize the indented stream."""
        self.stream = stream
        self.level = level
        self.indent = indent
        self.autoflush = autoflush

    def write(self, data: str | bytes) -> None:
        """Write the data to the stream."""
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        self.stream.write(
            "".join(
                [
                    f"{' ' * self.level * self.indent}{line}"
                    for line in data.splitlines(True)
                ]
            )
        )
        if self.autoflush:
            self.flush()

    def flush(self) -> None:
        """Flush the stream."""
        self.stream.flush()


class OutputWriter:
    """Output writer with indentation support."""

    def __init__(self) -> None:
        """Initialize the output writer."""
        self.level = 0
        self.indent = 2

    def enter(self) -> None:
        """Increase the indentation level."""
        self.level += 1

    def exit(self) -> None:
        """Decrease the indentation level."""
        if self.level:
            self.level -= 1

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        """Write the output.

        The signature of this method is the same as click.secho.
        """
        msg = args[0].split("\n")
        msg = "\n".join([f"{' ' * self.level * self.indent}{m}" for m in msg])
        click.secho(msg, *args[1:], **kwargs)

    @contextmanager
    def nested_stdout(self) -> Generator[None, None, None]:
        """Redirect the output to the indented stream."""
        current_stdout = sys.stdout
        current_stderr = sys.stderr
        sys.stdout = IndentedStream(current_stdout, self.level, self.indent)
        sys.stderr = IndentedStream(sys.stderr, self.level, self.indent, autoflush=True)
        try:
            yield
        finally:
            sys.stdout = current_stdout
            sys.stderr = current_stderr


output = OutputWriter()
"""Output writer instance."""
