#!/usr/bin/env python3
"""
Add a standard HTML comment header to MIND specification markdown files.

- Adds the header only if it's not already present.
- Skips obvious meta files like README.md and license-related docs.
"""

from pathlib import Path

HEADER = """<!--
Copyright (c) 2025 STARGA Inc.
MIND Language Specification — Community Edition
Licensed under the MIT License. See LICENSE-MIT.
-->

"""

SKIP_NAMES = {
    "README.md",
    "LICENSE.md",
    "LICENSE",
    "LICENSE-MIT",
    "LICENSE-COMMERCIAL",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "STATUS.md",
    "_sidebar.md",
    "changelog.md",
}

SKIP_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
}

def should_skip(path: Path) -> bool:
    name = path.name
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    if name in SKIP_NAMES:
        return True
    # Skip any license-like file in markdown form
    lower = name.lower()
    if "license" in lower or "licence" in lower:
        return True
    return False

def add_header_to_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "MIND Language Specification — Community Edition" in text:
        return

    new_text = HEADER + text
    path.write_text(new_text, encoding="utf-8")
    print(f"Updated: {path}")

def main() -> None:
    root = Path(".").resolve()
    for md in root.rglob("*.md"):
        if should_skip(md):
            continue
        add_header_to_file(md)

if __name__ == "__main__":
    main()

