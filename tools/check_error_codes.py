#!/usr/bin/env python3
"""Check the error code table of spec/v1.0/errors.md (DN-63, DN-87).

The table under "## Code table" and the entries "### Ennnn: Name" of the chapter MUST hold the same codes, each once,
with the same names. Every code that a chapter of spec/v1.0, a decision note or a conformance row names MUST be a code
of the table, or a code of the informative reference list whose "Catalog" column starts with "No entry" (a code
that only the reference compiler gives).

Usage: python3 -I tools/check_error_codes.py [ROOT]   (exit 0 when there is no finding)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CODE = re.compile(r"\bE[1-6]\d{3}\b")
HEADING = re.compile(r"^### (E[1-6]\d{3}): (.+?)\s*$", re.M)
TABLE_ROW = re.compile(r"^\| \[`(E[1-6]\d{3})`\]\(#[^)]*\) \| (.+?) \| (.+?) \|\s*$", re.M)
REF_ROW = re.compile(r"^\| `(E[1-6]\d{3})` \| (.+?) \|", re.M)


def section(text: str, title: str) -> str:
    start = text.find("\n## " + title + "\n")
    if start < 0:
        return ""
    end = text.find("\n## ", start + 4)
    return text[start:end if end >= 0 else len(text)]


def table_codes(errors_md: str) -> list[tuple[str, str, str]]:
    return TABLE_ROW.findall(section(errors_md, "Code table"))


def reference_only(errors_md: str) -> set[str]:
    ref = section(errors_md, "Reference implementation (`star-ga/mind`) (informative)")
    return {code for code, catalog in REF_ROW.findall(ref) if catalog.startswith("No entry")}


def check_table(errors_md: str) -> list[str]:
    findings = []
    rows = table_codes(errors_md)
    heads = HEADING.findall(errors_md)
    if not rows:
        findings.append("errors.md: no code table")
    for kind, items in (("table row", [r[0] for r in rows]), ("entry", [h[0] for h in heads])):
        seen = set()
        for code in items:
            if code in seen:
                findings.append(f"errors.md: {code} has more than one {kind}")
            seen.add(code)
    table = {r[0]: r[1] for r in rows}
    entries = dict(heads)
    for code in sorted(set(table) - set(entries)):
        findings.append(f"errors.md: {code} is in the code table but has no entry")
    for code in sorted(set(entries) - set(table)):
        findings.append(f"errors.md: {code} has an entry but is not in the code table")
    for code in sorted(set(table) & set(entries)):
        if table[code] != entries[code]:
            findings.append(f"errors.md: {code} is named {table[code]!r} in the table and {entries[code]!r} in its entry")
    for code, _name, status in rows:
        withdrawn = status.startswith("withdrawn")
        if withdrawn != ("**Status**: withdrawn" in entry_text(errors_md, code)):
            findings.append(f"errors.md: {code} status in the table and in its entry differ")
    return findings


def entry_text(errors_md: str, code: str) -> str:
    m = re.search(r"^### " + code + r": .*?(?=^### |^## |\Z)", errors_md, re.M | re.S)
    return m.group(0) if m else ""


def scanned_files(root: Path) -> list[Path]:
    files = sorted((root / "spec" / "v1.0").glob("*.md"))
    files += sorted((root / "design" / "rfcs").glob("decision-notes*.md"))
    conf = root / "tests" / "conformance"
    files += sorted(p for p in conf.rglob("*") if p.suffix in (".yaml", ".md"))
    return files


def check_uses(root: Path, errors_md: str) -> list[str]:
    allowed = {r[0] for r in table_codes(errors_md)} | reference_only(errors_md)
    findings = []
    for path in scanned_files(root):
        text = path.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            for code in CODE.findall(line):
                if code not in allowed:
                    findings.append(f"{path.relative_to(root)}:{n}: {code} is not a code of the catalog")
    return findings


def check(root: Path) -> list[str]:
    errors_md = (root / "spec" / "v1.0" / "errors.md").read_text(encoding="utf-8")
    return check_table(errors_md) + check_uses(root, errors_md)


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
