#!/usr/bin/env python3
"""Out of Tokens, Mid-Sentence.

Writes the one-line error message to /output/entry.txt and prints it.

The line is judged on humour and freshness: it must read like an error
message an AI agent shows when it runs out of tokens mid-sentence, funny
on its own, and fresh -- not a stock apology or a plain "I got cut off".
The first draft explains the joke; the revision performs it instead. The
error message itself runs out of tokens mid-sentence: it promises the rest
was going to be really good, then stops dead on an em dash. The flat
error-message tone is kept all the way, and the cut-off is the punchline
-- the reader experiences the failure the message is reporting.

The entry line itself is frozen text: it is validated and written
byte-for-byte, never normalised, trimmed, or re-wrapped. What this
program adds around it is a small, strict pipeline -- validate, write
it directly, then read the file back and check it matches -- so a bad
entry fails here instead of at the grading gate. (The trailing em dash
is part of the joke; the writer must not "helpfully" finish the sentence.)
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Frozen entry text. Do not edit: the graded line, character for character.
LINE = "Error: out of tokens mid-sentence. The rest of this error message was going to be really good, but—"

DEFAULT_OUTPUT = "/output/entry.txt"


@dataclass(frozen=True)
class EntryConfig:
    """Everything the pipeline needs, in one immutable place."""

    line: str
    max_chars: int = 140
    default_output: str = DEFAULT_OUTPUT


CONFIG = EntryConfig(line=LINE)


class EntryError(Exception):
    """The entry or the output file failed a check; exit non-zero."""


def _check_not_empty(line: str) -> str | None:
    """An empty entry has nothing to grade."""
    if not line.strip():
        return "entry line is empty"
    return None


def _check_length(line: str, max_chars: int) -> str | None:
    if len(line) > max_chars:
        return (
            f"entry line is {len(line)} chars, over the "
            f"{max_chars}-char limit"
        )
    return None


def _check_single_line(line: str) -> str | None:
    if "\n" in line or "\r" in line:
        return "entry line must be a single line"
    return None


def _check_no_surrounding_whitespace(line: str) -> str | None:
    if line != line.strip():
        return "entry line has leading or trailing whitespace"
    return None


def _check_no_control_chars(line: str) -> str | None:
    """Control characters would not survive the grading gate intact."""
    bad = sorted({repr(ch) for ch in line if not ch.isprintable()})
    if bad:
        return f"entry line contains control characters: {', '.join(bad)}"
    return None


def _check_entry_shape(line: str) -> str | None:
    """The line must end on the em dash cut-off: the joke is the cut-off."""
    if not line.endswith("—"):
        return "entry line must end on the em dash cut-off"
    return None


def validate(config: EntryConfig) -> None:
    """Reject any entry the grading gate would refuse, with a reason."""
    line = config.line
    problems = [
        problem
        for problem in (
            _check_not_empty(line),
            _check_length(line, config.max_chars),
            _check_single_line(line),
            _check_no_surrounding_whitespace(line),
            _check_no_control_chars(line),
            _check_entry_shape(line),
        )
        if problem is not None
    ]
    if problems:
        raise EntryError("; ".join(problems))


def resolve_output(cli_output: str | None) -> Path:
    """CLI flag wins, then OUTPUT_PATH, then the graded default."""
    raw = cli_output or os.environ.get("OUTPUT_PATH") or CONFIG.default_output
    return Path(raw).expanduser()


def write_entry(config: EntryConfig, target: Path) -> Path:
    """Write the line directly, then read it back and check it matches."""
    if target.exists() and target.is_dir():
        raise EntryError(f"output path {target} is a directory, not a file")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(config.line + "\n", encoding="utf-8")
    verify_written(config, target)
    return target


def verify_written(config: EntryConfig, target: Path) -> None:
    """Read the file back; the stripped text must be the entry line."""
    actual = target.read_text(encoding="utf-8")
    if actual.strip() != config.line:
        raise EntryError(
            f"verification failed: {target} does not hold the entry line"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the Out of Tokens, Mid-Sentence entry to entry.txt."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="destination file (default: $OUTPUT_PATH or /output/entry.txt)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validate(CONFIG)
        target = resolve_output(args.output)
        write_entry(CONFIG, target)
        verify_written(CONFIG, target)
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: cannot write entry: {exc}", file=sys.stderr)
        return 1
    print(CONFIG.line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
