#!/usr/bin/env python3
"""Check that the attribute table of spec/v1.0/language.md and its conformance rows hold the same names (DN-87).

The table under "## Attributes" lists each attribute name with its status. The names of its "Core v1" rows and the
one-segment attribute names that the accept rows of tests/conformance use MUST be the same set: a Core v1 name with no
accept row, and an accept row with a name that no Core v1 row of the table holds, are findings. A two-segment name is
a tool attribute (DN-84) and is not a name of the table.

Usage: python3 -I tools/check_attribute_rows.py [ROOT]   (exit 0 when there is no finding)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TABLE_ROW = re.compile(r"^\| `([a-z_][a-z0-9_]*)` \| .+ \| ([^|]+?) \|\s*$", re.M)
USE = re.compile(r"#\[([A-Za-z_][A-Za-z0-9_]*)(?=[\](])")


def table_names(language_md: str) -> dict[str, str]:
    m = re.search(r"^## Attributes\n(.*?)(?=^## |\Z)", language_md, re.M | re.S)
    section = m.group(1) if m else ""
    return {name: status.strip() for name, status in TABLE_ROW.findall(section)}


def accept_names(rows: dict[str, str]) -> dict[str, list[str]]:
    used: dict[str, list[str]] = {}
    for path, text in rows.items():
        if not re.search(r"^\s*status: success\s*$", text, re.M):
            continue
        source = text.split("source: |", 1)[-1].split("\nexpected:", 1)[0]
        for name in set(USE.findall(source)):
            used.setdefault(name, []).append(path)
    return used


def check_texts(language_md: str, rows: dict[str, str]) -> list[str]:
    table = table_names(language_md)
    findings = [] if table else ["language.md: no attribute table"]
    core = {name for name, status in table.items() if status == "Core v1"}
    used = accept_names(rows)
    for name in sorted(core - set(used)):
        findings.append(f"language.md: the attribute `{name}` is a Core v1 row of the table and has no accept row")
    for name in sorted(set(used) - core):
        findings.append(f"{used[name][0]}: the accept row uses `#[{name}]`, which no Core v1 row of the table holds")
    return findings


def check(root: Path) -> list[str]:
    language_md = (root / "spec" / "v1.0" / "language.md").read_text(encoding="utf-8")
    conf = root / "tests" / "conformance"
    rows = {str(p.relative_to(root)): p.read_text(encoding="utf-8") for p in sorted(conf.rglob("*.yaml"))}
    return check_texts(language_md, rows)


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent
    findings = check(root)
    for f in findings:
        print(f)
    print(f"findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
