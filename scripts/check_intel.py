#!/usr/bin/env python3
"""Validate intel/ front-matter; used by CI and locally.

Checks:
- every intel/**/*.md (except INDEX.md and READMEs) has valid front-matter
- required fields present, type/domain values legal
- writeups must carry a one-line `hint` (anti-anchoring mechanism)
- nothing committed with `embargo: true` (embargoed content must not be in git)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEL = ROOT / "intel"

VALID_TYPE = {"technique", "writeup", "cheatsheet", "playbook"}
VALID_DOMAIN = {"web", "pwn", "crypto", "re", "forensics", "ir", "ai", "osint",
                "defense", "pentest", "misc"}


def parse_front_matter(text: str):
    if not text.startswith("---"):
        return None, "missing front-matter"
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None, "front-matter not closed"
    fm = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip().strip("'\"")
    return fm, None


def main() -> int:
    errors = []
    files = [p for p in INTEL.rglob("*.md")
             if p.name not in ("INDEX.md", "README.md", "EXTERNAL.md")
             and "external" not in p.parts]
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        try:
            fm, err = parse_front_matter(p.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            errors.append(f"{rel}: not valid UTF-8")
            continue
        if err:
            errors.append(f"{rel}: {err}")
            continue
        for key in ("type", "domain", "date"):
            if not fm.get(key):
                errors.append(f"{rel}: missing required field '{key}'")
        if fm.get("type") not in VALID_TYPE:
            errors.append(f"{rel}: illegal type '{fm.get('type')}'")
        if fm.get("domain") not in VALID_DOMAIN:
            errors.append(f"{rel}: illegal domain '{fm.get('domain')}'")
        if fm.get("type") == "writeup" and not fm.get("hint"):
            errors.append(f"{rel}: writeup needs a one-line 'hint' (anti-anchoring)")
        if str(fm.get("embargo", "")).lower() in ("true", "yes"):
            errors.append(f"{rel}: embargo=true content must NOT be committed")
    if errors:
        for e in errors:
            print(f"FAIL {e}")
        return 1
    print(f"intel ok: {len(files)} file(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
