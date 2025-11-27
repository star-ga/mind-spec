#!/usr/bin/env python3
"""
Add a standard HTML comment header to MIND specification markdown files.

- Adds the header only if it's not already present.
- Skips obvious meta files like README.md and license-related docs.
"""

from pathlib import Path

APACHE_MARKER = "Licensed under the Apache License, Version 2.0"
OLD_MARKER_SPEC = "MIND Language Specification — Community Edition"
OLD_MARKER_MIT = "Permission is hereby granted, free of charge"

HEADER = """<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

"""

SKIP_FILES = {
    "LICENSE",
    "LICENSE-COMMERCIAL",
    "README.md",
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
    # Exact path-part matches, not substrings
    if any(skip_dir in path.parts for skip_dir in SKIP_DIRS):
        return True
    if path.name in SKIP_FILES:
        return True
    return False

def add_header_to_file(path: Path) -> None:
    """Add the spec header to a single markdown file, if not already present."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading {path}: {e}")
        return

    if text.lstrip().startswith(HEADER):
        return

    first_lines = "\n".join(text.splitlines()[:40])

    if OLD_MARKER_SPEC in first_lines or OLD_MARKER_MIT in first_lines:
        text = remove_existing_header(text)
    elif APACHE_MARKER in first_lines:
        # Already on the new header; leave untouched
        return

    new_text = HEADER + text
    try:
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated: {path}")
    except OSError as e:
        print(f"Error writing {path}: {e}")


def remove_existing_header(text: str) -> str:
    """Strip the leading legacy header block to prepare for replacement."""

    marker_positions = [
        text.find(OLD_MARKER_SPEC),
        text.find(OLD_MARKER_MIT),
    ]
    marker_positions = [pos for pos in marker_positions if pos != -1]

    if not marker_positions:
        return text

    marker_index = min(marker_positions)
    comment_start = text.rfind("<!--", 0, marker_index)
    comment_end = text.find("-->", marker_index)

    if comment_start != -1 and comment_end != -1:
        stripped = text[comment_end + len("-->") :]
    else:
        # Fallback: drop everything up to the line containing the marker
        stripped = "\n".join(text.split("\n")[text[:marker_index].count("\n") + 1 :])

    return stripped.lstrip("\n")

def main() -> None:
    root = Path(".").resolve()
    for md in root.rglob("*.md"):
        if should_skip(md):
            continue
        add_header_to_file(md)

if __name__ == "__main__":
    main()
