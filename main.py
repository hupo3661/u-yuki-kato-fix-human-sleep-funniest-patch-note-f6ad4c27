#!/usr/bin/env python3
"""Fix Human Sleep: Funniest Patch Note.

Writes one original patch note for the bug called human sleep to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt).

The note must be a single line of 1-160 characters of UTF-8 text. This
program validates the line before writing it, then re-reads the file and
verifies it matches byte for byte.
"""

import os
import sys

PATCH_NOTE = (
    "Patch 8.1.3: humans now fall asleep in under 20 minutes. Removed the "
    "3 a.m. \u201cremember that embarrassing thing from 2014?\u201d feature. "
    "It will not be missed."
)

MAX_CHARS = 160


def main() -> int:
    note = PATCH_NOTE

    # Validate: single line, 1-160 characters, not only whitespace.
    if not note or note != note.strip():
        print("error: patch note must not be empty or padded with whitespace", file=sys.stderr)
        return 1
    if "\n" in note or "\r" in note:
        print("error: patch note must be a single line", file=sys.stderr)
        return 1
    if len(note) > MAX_CHARS:
        print(f"error: patch note is {len(note)} characters, over the {MAX_CHARS} limit", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip() or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    data = note.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)

    # Re-read and verify byte-for-byte equality.
    with open(path, "rb") as f:
        written = f.read()
    if written != data:
        print("error: re-read entry.txt does not match the patch note byte for byte", file=sys.stderr)
        return 1

    print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
