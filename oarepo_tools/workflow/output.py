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
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from collections.abc import Generator


class OutputWriter:
    """Output writer with indentation support."""

    def __init__(self) -> None:
        """Initialize the output writer."""
        self.level = 0
        self.indent = 2

        self.stdout = sys.stdout
        self.stderr = sys.stderr

        sys.stdout = IndentedStream(self.stdout, self)
        sys.stderr = IndentedStream(self.stdout, self, autoflush=True)

    @contextmanager
    def nested(self) -> Generator[None, None, None]:
        """Redirect the output to the indented stream."""
        self.level += 1
        try:
            yield
        finally:
            self.level -= 1


class IndentedStream:
    """Stream with indentation support."""

    def __init__(
        self, stream: TextIO, writer: OutputWriter, autoflush: bool = False
    ) -> None:
        """Initialize the indented stream."""
        self.stream = stream
        self.writer = writer
        self.autoflush = autoflush

    def write(self, data: str | bytes) -> None:
        """Write the data to the stream."""
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        self.stream.write(
            "".join(
                [
                    f"{' ' * self.writer.level * self.writer.indent}{line}"
                    for line in data.splitlines(True)
                ]
            )
        )
        if self.autoflush:
            self.flush()

    def flush(self) -> None:
        """Flush the stream."""
        self.stream.flush()

    def isatty(self) -> bool:
        """Return if the stream is a tty."""
        return self.stream.isatty()


output = OutputWriter()
"""Output writer instance."""
