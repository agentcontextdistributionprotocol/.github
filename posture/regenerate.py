#!/usr/bin/env python3
"""Regenerate this repo's copy of the posture paragraph from canonical.

The paragraph is copied verbatim and generated mechanically -- never retyped.
Retyping is how the copies diverged in the first place, and a human-retyped
paragraph that is 99% right is worse than an obviously stale one, because the
diff looks like a deliberate edit.

Deliberately shares extract() with check_drift.py: the thing that writes the
copy and the thing that polices it must agree on where the paragraph starts and
ends, or a regenerated file can still fail the check.

Local adaptations preserved: the '**Project status.**' run-in prefix instead of
a heading, and a hard wrap. Both survive the checker's normalisation.

  python3 posture/regenerate.py            # rewrite profile/README.md in place
  python3 posture/regenerate.py --check     # exit 1 if it would change anything
"""

import argparse
import json
import os
import sys
from pathlib import Path

from check_drift import LocalSource, Operational, RemoteSource, Unavailable, extract

HERE = Path(__file__).parent
PREFIX = "**Project status.** "
WIDTH = 81


def wrap(text: str, width: int) -> list[str]:
    """Greedy fill. Matches `fold -s -w 81` rather than GNU fmt's optimal-fit,
    so the output is identical on BSD and GNU boxes."""
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report whether a rewrite is needed; change nothing")
    ap.add_argument("--source", choices=["remote", "local"], default="remote")
    ap.add_argument("--workspace", type=Path, default=HERE.resolve().parents[1])
    args = ap.parse_args()

    manifest = json.loads((HERE / "copies.json").read_text(encoding="utf-8"))
    canon = manifest["canonical"]
    src = (LocalSource(args.workspace) if args.source == "local"
           else RemoteSource(os.environ.get("GITHUB_TOKEN")))
    try:
        text = (src.read(canon["repo"], canon["path"], canon.get("local_dir"))
                if args.source == "local" else src.read(canon["repo"], canon["path"]))
    except Unavailable as e:
        print(f"FATAL: cannot read canonical: {e}", file=sys.stderr)
        return 2
    if text is None:
        print("FATAL: canonical file not found", file=sys.stderr)
        return 2

    para = extract(text, manifest["anchors"]["start"], manifest["anchors"]["end"])
    if para is None:
        print("FATAL: canonical paragraph not found -- anchors may be stale",
              file=sys.stderr)
        return 2

    target = HERE.parent / "profile" / "README.md"
    lines = target.read_text(encoding="utf-8").split("\n")
    starts = [i for i, l in enumerate(lines) if l.startswith(PREFIX)]
    if len(starts) != 1:
        print(f"FATAL: expected exactly 1 line starting {PREFIX!r}, found {len(starts)}",
              file=sys.stderr)
        return 2
    i = starts[0]
    ends = [j for j in range(i, len(lines))
            if manifest["anchors"]["end"].split()[-1] in lines[j]]
    if not ends:
        print("FATAL: could not find the end of the existing paragraph", file=sys.stderr)
        return 2
    j = ends[0]

    new_block = wrap(PREFIX + para, WIDTH)
    if lines[i:j + 1] == new_block:
        print("profile/README.md is already in sync with canonical.")
        return 0
    if args.check:
        print("profile/README.md would change -- run posture/regenerate.py")
        return 1
    target.write_text("\n".join(lines[:i] + new_block + lines[j + 1:]), encoding="utf-8")
    print(f"rewrote profile/README.md lines {i + 1}-{j + 1} "
          f"({j - i + 1} -> {len(new_block)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
