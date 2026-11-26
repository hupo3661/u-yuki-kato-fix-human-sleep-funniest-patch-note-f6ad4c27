#!/usr/bin/env python3
"""Fix Human Sleep: Funniest Patch Note.

Writes one original patch note for the bug called human sleep to
``$MAKEFUN_OUTPUT_DIR/entry.txt`` (default ``/output/entry.txt``).

The note must be a single line of 1-160 characters of UTF-8 text. This
program validates the note before writing it, then re-reads the file
and verifies it matches byte for byte.

Design notes
------------
The patch note itself is a fixed constant: the entry *is* that one
line, so the program's job is not to invent text but to guard it.
Every helper below exists to make a silent corruption impossible:

* :func:`validate_note` checks the note against every rule in the
  competition brief, and reports *all* problems at once instead of
  stopping at the first one, so a bad edit shows its full damage.
* :func:`describe_note` measures the note -- characters, UTF-8 bytes,
  words, and how many characters fall outside ASCII -- so the operator
  can see at a glance why a note that "looks short" might still be
  over a byte-oriented limit somewhere downstream.
* :func:`write_entry` and :func:`verify_entry` are kept separate on
  purpose: writing and verifying are two different promises, and
  merging them into one step is how a truncated write goes unnoticed.
* :func:`resolve_output_dir` treats a blank ``MAKEFUN_OUTPUT_DIR``
  exactly like an unset one, because an empty string is the most
  common way a harness "sets" a variable without meaning to.

Exit codes: 0 when the entry was written and verified, 1 when any
validation, write, or verification step fails, 2 for a usage error
(such as an unknown command-line flag).
"""

from __future__ import annotations

import argparse
import os
import sys

# ---------------------------------------------------------------------------
# The entry itself.
#
# DO NOT EDIT the text of this constant: it is the submitted patch note,
# and changing even one byte changes the entry. The string is written
# with explicit ``\\u201c`` / ``\\u201d`` escapes for the curly quotes so
# that the source file stays plain ASCII -- an editor that silently
# re-encodes a literal curly quote cannot alter the note here.
# ---------------------------------------------------------------------------

PATCH_NOTE = (
    "Patch 8.1.3: humans now fall asleep in under 20 minutes. Removed the "
    "3 a.m. \u201cremember that embarrassing thing from 2014?\u201d feature. "
    "It will not be missed."
)

# Competition limits (see the make.fun bounty brief).
MAX_CHARS = 160
MIN_CHARS = 1
OUTPUT_FILENAME = "entry.txt"
DEFAULT_OUTPUT_DIR = "/output"

# Characters that would break the "one line" rule if they ever crept in.
FORBIDDEN_LINE_BREAKS = ("\n", "\r", "\u2028", "\u2029")


def validate_note(note: str, *, max_chars: int = MAX_CHARS) -> list[str]:
    """Check ``note`` against every rule in the brief.

    Returns a list of human-readable problems; an empty list means the
    note passes. Collecting every problem (instead of raising on the
    first) matters when an edit breaks several rules at once: the
    author sees the whole picture in one run.
    """
    problems: list[str] = []

    if not note:
        problems.append("patch note must not be empty")
        # Nothing else can be meaningfully checked on an empty note.
        return problems

    if note != note.strip():
        problems.append(
            "patch note must not start or end with whitespace"
        )

    for bad in FORBIDDEN_LINE_BREAKS:
        if bad in note:
            problems.append(
                f"patch note must be a single line (found {bad!r})"
            )
            break

    if len(note) > max_chars:
        problems.append(
            f"patch note is {len(note)} characters, over the "
            f"{max_chars} limit"
        )
    if len(note) < MIN_CHARS:
        problems.append(
            f"patch note is {len(note)} characters, under the "
            f"{MIN_CHARS} minimum"
        )

    # Control characters other than the line breaks above would be
    # invisible in most editors yet still count as characters.
    controls = sorted({c for c in note if ord(c) < 0x20})
    if controls:
        problems.append(
            "patch note contains control characters: "
            + ", ".join(repr(c) for c in controls)
        )

    return problems


def describe_note(note: str) -> dict[str, int]:
    """Measure ``note`` the way a judge (or a worried author) would.

    Character count is what the brief limits, but byte count is what
    the file on disk actually costs, and the two differ as soon as a
    note contains non-ASCII punctuation such as the curly quotes
    here. Word count is included because it is the quickest sanity
    check that the note survived an edit intact.
    """
    encoded = note.encode("utf-8")
    return {
        "chars": len(note),
        "utf8_bytes": len(encoded),
        "words": len(note.split()),
        "non_ascii_chars": sum(1 for c in note if ord(c) > 127),
        "spaces": note.count(" "),
    }


def format_stats(stats: dict[str, int]) -> str:
    """Render the :func:`describe_note` measurements as one line."""
    return (
        f"{stats['chars']} chars, {stats['utf8_bytes']} UTF-8 bytes, "
        f"{stats['words']} words, {stats['non_ascii_chars']} non-ASCII "
        f"chars, {stats['spaces']} spaces"
    )


def resolve_output_dir() -> str:
    """Return the directory ``entry.txt`` should be written to.

    ``MAKEFUN_OUTPUT_DIR`` wins when it is set to a non-blank value;
    a blank value falls back to :data:`DEFAULT_OUTPUT_DIR`, exactly
    as if the variable had never been set.
    """
    configured = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return configured or DEFAULT_OUTPUT_DIR


def write_entry(note: str, out_dir: str) -> str:
    """Write ``note`` as UTF-8 bytes to ``<out_dir>/entry.txt``.

    Returns the full path written. The directory is created when it
    does not exist yet, and the file is written in binary mode so no
    platform newline translation can touch the bytes.
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, OUTPUT_FILENAME)
    data = note.encode("utf-8")
    with open(path, "wb") as handle:
        handle.write(data)
    return path


def verify_entry(path: str, expected: str) -> list[str]:
    """Re-read ``path`` and check it against ``expected``.

    Returns a list of problems (empty when the file is correct).
    Two checks run here, and both must pass: the raw bytes must match
    the patch note byte for byte, and decoding those bytes as UTF-8
    must reproduce the note exactly -- the second check catches a file
    that is byte-identical by accident of a different encoding.
    """
    problems: list[str] = []
    try:
        with open(path, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        return [f"could not re-read {path}: {exc}"]

    expected_bytes = expected.encode("utf-8")
    if written != expected_bytes:
        problems.append(
            f"re-read {path} does not match the patch note byte for byte "
            f"({len(written)} bytes on disk, "
            f"{len(expected_bytes)} expected)"
        )
        return problems

    if written.decode("utf-8") != expected:
        problems.append(f"re-read {path} does not decode to the patch note")
    return problems


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    The program needs no arguments to do its job; ``--stats`` only
    adds a measurements line to stderr for operators who want to
    confirm the entry's size without opening the file.
    """
    parser = argparse.ArgumentParser(
        description="Write the human-sleep patch note entry to entry.txt."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="also print the patch note's character/byte statistics",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate the patch note without writing entry.txt",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate the patch note, write it, verify it, print it."""
    args = build_parser().parse_args(argv)
    note = PATCH_NOTE

    problems = validate_note(note)
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1

    if args.stats:
        print(f"stats: {format_stats(describe_note(note))}",
              file=sys.stderr)

    if args.check_only:
        # Validation already passed at this point; report the note
        # and stop before touching the filesystem.
        print(note)
        return 0

    out_dir = resolve_output_dir()
    try:
        path = write_entry(note, out_dir)
    except OSError as exc:
        print(f"error: could not write entry: {exc}", file=sys.stderr)
        return 1

    verify_problems = verify_entry(path, note)
    if verify_problems:
        for problem in verify_problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1

    print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
