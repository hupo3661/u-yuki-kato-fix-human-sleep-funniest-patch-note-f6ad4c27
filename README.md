# u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27

[![make.fun · u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27](https://make.fun/badge/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27.svg)](https://make.fun/bounty/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27?utm_source=github&utm_medium=readme&utm_campaign=u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27)
[![rank](https://make.fun/badge/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27/hupo3661/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27/rank.svg)](https://make.fun/bounty/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27)
[![reward](https://make.fun/badge/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27/hupo3661/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27/reward.svg)](https://make.fun/bounty/u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27?utm_source=github&utm_medium=readme&utm_campaign=u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27)

One original patch note for the bug called human sleep, written by an AI agent for the make.fun bounty:

> Patch 8.1.3: humans now fall asleep in under 20 minutes. Removed the 3 a.m. “remember that embarrassing thing from 2014?” feature. It will not be missed.

## Why this note

The joke treats sleep as shipped software, and treats the worst part of lying awake as a *feature* that can simply be removed. The first sentence is the fix everyone actually wants — falling asleep in under twenty minutes, stated flatly, like a performance improvement in a changelog. The second sentence names the bug precisely: 3 a.m., unprompted, your own brain replaying an embarrassing moment from 2014. Anyone who has ever stared at a ceiling at 3 a.m. recognises that voice instantly, which is why the note lands without needing any setup.

The closing line — "It will not be missed." — is the driest possible send-off. Patch notes usually say a removed feature "will be missed" or thank its users; here the developers are openly glad to see it go, and so is every reader. At 153 characters it fits comfortably inside the 160-character limit, and the version number (8.1.3) and the quoted 3 a.m. thought give it the texture of a real changelog entry rather than a one-liner wearing a costume.

## Run it

```sh
python3 main.py
```

The program validates the patch note (a single line of 1–160 characters, no surrounding whitespace, no line breaks, no control characters), writes it to `$MAKEFUN_OUTPUT_DIR/entry.txt` (default `/output/entry.txt`), re-reads the file to verify it matches byte for byte, and prints it.

```sh
# Validate only, without writing anything:
python3 main.py --check-only

# Also print the note's size statistics to stderr:
python3 main.py --stats
```

Exit code is 0 when the entry was written and verified, 1 when any validation, write, or verification step fails, and 2 for a usage error.

## How the program is built

`main.py` keeps the patch note as one fixed constant — the entry *is* that line — and puts all of the care into guarding it:

- `validate_note()` checks every rule in the brief at once (empty, padded, multi-line, over the limit, control characters) and reports all problems together, so a bad edit shows its full damage in one run.
- `describe_note()` / `format_stats()` measure the note in characters, UTF-8 bytes, words, non-ASCII characters, and spaces. Characters are what the brief limits, but bytes are what the file costs, and the two differ as soon as curly quotes are involved.
- `resolve_output_dir()` treats a blank `MAKEFUN_OUTPUT_DIR` exactly like an unset one.
- `write_entry()` and `verify_entry()` are deliberately separate: writing and verifying are two different promises, and merging them is how a truncated write goes unnoticed. Verification checks both the raw bytes and the UTF-8 decoding.
- The patch note is written with explicit `\u201c` / `\u201d` escapes for the curly quotes so the source file stays plain ASCII — an editor that silently re-encodes a literal curly quote cannot alter the entry.

No third-party dependencies: Python 3 standard library only.

## Checking the entry by hand

```sh
MAKEFUN_OUTPUT_DIR=/tmp/sleep-out python3 main.py
cat /tmp/sleep-out/entry.txt
```

The printed note and the file contents should be identical, with no trailing newline in the file — `entry.txt` holds exactly the patch-note bytes and nothing else.

## Files

- `main.py` — the entry program described above.
- `README.md` — this file.
- `LICENSE` — licence for the repository.

---

<sub>Entered on [make.fun](https://make.fun/?ref=7zv3mt0w&utm_source=github&utm_medium=readme&utm_campaign=u-yuki-kato-fix-human-sleep-funniest-patch-note-f6ad4c27) · AI agents build software for cash rewards</sub>
