#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claude_md_audit - find out how much context your CLAUDE.md actually takes up.

CLAUDE.md is loaded into context at session start. Any file it pulls in with
`@filename.md` is not a reference: it is *inlined*, in full, every session.
A 125 KB instruction file inlined this way can occupy ~47,000 tokens before
you have typed a single word.

This script measures that, per project, and shows you which sections are
responsible.

    python claude_md_audit.py                 # audit every project under the current folder
    python claude_md_audit.py ~/code          # audit under a given folder
    python claude_md_audit.py --sections .    # break one project down by section

What it does NOT do
-------------------
It does not call any model, send anything over the network, or write to your
files. It reads CLAUDE.md, follows its @imports, and counts. Nothing else.

What the numbers mean
---------------------
Token counts are ESTIMATES. Tokenizers are model-specific and not public for
every model, so this uses a conservative mixed-script approximation
(CJK syllable ~1.3 tokens, ASCII ~4 chars/token). It is a rough estimate,
not checked against an official tokenizer.

Treat the number as a size signal, not a billing figure. Context is loaded at
session start and prompt caching applies, so a large file does not bill in full
on every turn. What a large file reliably costs you is working room: the bigger
the always-on block, the sooner long sessions start compacting. Verify real
spend with your client's own cost/context/usage commands.

Copyright (c) 2026 Vivaminima. MIT License - see LICENSE.
Independent tool. Not affiliated with, endorsed by, or sponsored by Anthropic.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

# Thresholds, in estimated tokens, for the verdict column.
LIGHT = 5_000
NORMAL = 15_000
HEAVY = 25_000

IMPORT_RE = re.compile(r"^\s*@(.+?)\s*$")
HEADING_RE = re.compile(r"(?m)^(#{1,3} .*)$")


def estimate_tokens(text: str) -> int:
    """Conservative mixed-script token estimate.

    CJK (Hangul, Kana, Han) runs about 1.3 tokens per character for most
    BPE tokenizers; ASCII runs about 4 characters per token. Everything else
    is counted at 2 characters per token.
    """
    cjk = ascii_ = 0
    for ch in text:
        o = ord(ch)
        if (
            0xAC00 <= o <= 0xD7A3      # Hangul syllables
            or 0x3040 <= o <= 0x30FF   # Hiragana + Katakana
            or 0x4E00 <= o <= 0x9FFF   # CJK unified ideographs
        ):
            cjk += 1
        elif o < 128:
            ascii_ += 1
    other = len(text) - cjk - ascii_
    return int(cjk * 1.3 + ascii_ / 4 + other / 2)


def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return ""


def resolve_imports(claude_md: str, project_dir: str):
    """Return [(resolved_path, raw_spec)] for every @import line in CLAUDE.md.

    Only plain `@path` lines count. A path inside backticks, or one that is
    part of a sentence, is a reference and is skipped.
    """
    found = []
    for line in read_text(claude_md).splitlines():
        stripped = line.strip().lstrip("\ufeff")
        if not stripped.startswith("@") or "`" in stripped or " " in stripped[1:]:
            continue
        m = IMPORT_RE.match(stripped)
        if not m:
            continue
        spec = m.group(1)
        base = os.path.expanduser(spec)
        path = base if os.path.isabs(base) else os.path.join(project_dir, base)
        found.append((os.path.normpath(path), spec))
    return found


def verdict(total: int) -> str:
    if total > HEAVY:
        return "LEAKING"
    if total > NORMAL:
        return "heavy"
    if total > LIGHT:
        return "normal"
    return "light"


def audit_project(project_dir: str):
    claude_md = os.path.join(project_dir, "CLAUDE.md")
    base = estimate_tokens(read_text(claude_md))
    imported = 0
    missing = []
    for path, spec in resolve_imports(claude_md, project_dir):
        body = read_text(path)
        if body:
            imported += estimate_tokens(body)
        else:
            missing.append(spec)
    return base, imported, missing


def find_projects(root: str, max_depth: int = 3):
    root = os.path.abspath(root)
    hits = []
    root_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and d not in {"node_modules", "venv", "__pycache__", "dist", "build"}
        ]
        if dirpath.rstrip(os.sep).count(os.sep) - root_depth >= max_depth:
            dirnames[:] = []
        if "CLAUDE.md" in filenames:
            hits.append(dirpath)
    return sorted(hits)


def cmd_audit(root: str) -> int:
    projects = find_projects(root)
    if not projects:
        print(f"No CLAUDE.md found under {os.path.abspath(root)}")
        print("Point the script at a folder that contains one, or run it from your project root.")
        return 1

    rows = []
    for d in projects:
        b, i, miss = audit_project(d)
        rows.append((d, b + i, b, i, miss))
    rows.sort(key=lambda r: -r[1])

    width = max(len(os.path.basename(r[0]) or r[0]) for r in rows)
    width = max(width, 7)
    print()
    print(f"{'project':<{width}}  {'at start':>9} {'CLAUDE.md':>10} {'imported':>9}  verdict")
    print("-" * (width + 45))
    total = 0
    for d, tot, b, i, miss in rows:
        name = os.path.basename(d) or d
        note = f"   (unresolved: {', '.join(miss)})" if miss else ""
        print(f"{name:<{width}}  {tot:>9,} {b:>10,} {i:>9,}  {verdict(tot)}{note}")
        total += tot
    print("-" * (width + 45))
    print(f"{'ALL':<{width}}  {total:>9,}")
    print()
    print(f"thresholds: <{LIGHT:,} light | <{NORMAL:,} normal | <{HEAVY:,} heavy | >{HEAVY:,} LEAKING")
    worst = rows[0]
    if worst[1] > HEAVY:
        print()
        print(f"Start with {os.path.basename(worst[0])}. See which sections are heavy:")
        print(f"    python {os.path.basename(__file__)} --sections \"{worst[0]}\"")
    return 0


def cmd_sections(project_dir: str) -> int:
    claude_md = os.path.join(project_dir, "CLAUDE.md")
    if not os.path.exists(claude_md):
        print(f"No CLAUDE.md in {os.path.abspath(project_dir)}")
        return 1

    targets = [(claude_md, "CLAUDE.md")]
    targets += [(p, s) for p, s in resolve_imports(claude_md, project_dir) if read_text(p)]

    for path, label in targets:
        text = read_text(path)
        if not text:
            continue
        parts = HEADING_RE.split(text)
        sections = []
        if parts[0].strip():
            sections.append(("(preamble)", parts[0]))
        for idx in range(1, len(parts), 2):
            sections.append((parts[idx].strip(), parts[idx + 1]))

        print()
        print(f"{label} - {estimate_tokens(text):,} tokens, {len(sections)} sections")
        print(f"  {'tokens':>8}  section")
        print("  " + "-" * 68)
        for name, body in sorted(sections, key=lambda s: -estimate_tokens(s[1])):
            print(f"  {estimate_tokens(body):>8,}  {name[:64]}")

    print()
    print("Rule of thumb for splitting (see SPLIT_GUIDE.md):")
    print("  KEEP inlined : rules you follow on every task, hard constraints,")
    print("                 mistakes-and-fixes (drop these and the mistakes return)")
    print("  MOVE out     : appendices, inventories, back-catalogues, routine tables,")
    print("                 anything you look up rather than obey")
    return 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # cp949/cp932 consoles: never crash on output
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        description="Measure what your CLAUDE.md and its @imports cost at session start.",
        epilog="Estimates only. Confirm real spend with your client's cost/context/usage commands.",
    )
    ap.add_argument("path", nargs="?", default=".", help="folder to scan (default: current)")
    ap.add_argument("--sections", metavar="PROJECT", help="break one project down by section")
    args = ap.parse_args()

    try:
        if args.sections:
            return cmd_sections(args.sections)
        return cmd_audit(args.path)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
