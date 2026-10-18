from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

from .core import analyze, render_json, render_markdown


def _write_stdout(rendered: str) -> None:
    # Write real descriptors directly: buffered failures otherwise escape at shutdown.
    try:
        descriptor = sys.stdout.fileno()
    except (AttributeError, io.UnsupportedOperation):
        sys.stdout.write(rendered)
        sys.stdout.flush()
        return
    pending = rendered.encode(sys.stdout.encoding or "utf-8", sys.stdout.errors or "strict")
    while pending:
        written = os.write(descriptor, pending)
        if written <= 0:
            raise OSError("stdout accepted no report bytes")
        pending = pending[written:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic, reviewable report from explicit JSON input."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = analyze(data)
        rendered = render_json(report) if args.format == "json" else render_markdown(report)
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        else:
            _write_stdout(rendered)
    except (OSError, UnicodeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
