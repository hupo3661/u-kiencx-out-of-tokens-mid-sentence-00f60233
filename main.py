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
"""

import os
import sys

LINE = "Error: out of tokens mid-sentence. The rest of this error message was going to be really good, but—"

MAX_CHARS = 140


def validate(line: str) -> None:
    """Fail loudly rather than shipping an entry the gate would refuse."""
    if not line.strip() or len(line) > MAX_CHARS:
        sys.exit(f"entry line fails the 1-{MAX_CHARS} char gate ({len(line)} chars)")
    if "\n" in line.strip():
        sys.exit("entry line must be a single line")


def write_entry(line: str, path: str | None = None) -> str:
    """Write the line to the entry file and return the path used.

    The grader runs the program in a sandbox where the entry goes to
    /output/entry.txt. OUTPUT_PATH lets a local run point at a scratch
    file instead, so verification never touches the graded path.
    """
    target = path or os.environ.get("OUTPUT_PATH", "/output/entry.txt")
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(line)
    return target


def main() -> None:
    validate(LINE)
    write_entry(LINE)
    print(LINE)


if __name__ == "__main__":
    main()
