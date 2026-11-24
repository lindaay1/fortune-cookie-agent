#!/usr/bin/env python3
"""A fortune slip for an AI agent.

make.fun entry for "Fortune Cookie for an AI Agent"
(u-suroso-69-fortune-cookie-for-an-ai-agent-d1506e11).

The slip is fixed text: one prophetic, funny line about the human who
says "just one small change". The program's only job is to carry that
line, unchanged, into the file the kit's contract names. It takes no
arguments, reads no input, calls no network and keeps no state, so
every run lands the same bytes. (Revision note: docstring only; the
slip text and the emitted bytes are unchanged from v1.)
"""

import os
import sys
from hashlib import sha256
from pathlib import Path

FORTUNE = (
    "Beware the human who says 'just one small change' \u2014 behind it "
    "march a thousand follow-ups, and none of them are small."
)

MAX_CHARS = 140


class SlipError(Exception):
    """Raised when the slip would break the sealed gate."""


class FortuneSlip:
    """Holds the slip and knows how to check and deliver it."""

    def __init__(self, text):
        self.text = text

    def check(self):
        """Gate the slip the way the sealed scorer will."""
        if not isinstance(self.text, str):
            raise SlipError("slip must be text")
        if not 1 <= len(self.text) <= MAX_CHARS:
            raise SlipError(
                "slip is %d chars, gate allows 1-%d"
                % (len(self.text), MAX_CHARS)
            )
        if "\n" in self.text or "\r" in self.text:
            raise SlipError("slip must be a single line")
        if self.text.strip() == "":
            raise SlipError("slip must not be only whitespace")
        self.text.encode("utf-8")

    @property
    def blob(self):
        """The slip as the exact bytes to land on disk."""
        return self.text.encode("utf-8")

    @property
    def fingerprint(self):
        """Short proof that the bytes on disk are the slip."""
        return sha256(self.blob).hexdigest()

    def deliver(self, folder):
        """Write entry.txt and prove the write landed intact."""
        self.check()
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / "entry.txt"
        target.write_bytes(self.blob)
        if sha256(target.read_bytes()).hexdigest() != self.fingerprint:
            raise SlipError("entry.txt differs from the slip after writing")
        return target


def output_folder():
    """The kit's output folder when set, else the contract default."""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")


def run():
    """Deliver the slip and report where it landed."""
    slip = FortuneSlip(FORTUNE)
    try:
        target = slip.deliver(output_folder())
    except (SlipError, OSError) as problem:
        print("refused: %s" % problem, file=sys.stderr)
        return 1
    print("wrote %d bytes to %s" % (len(slip.blob), target))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
