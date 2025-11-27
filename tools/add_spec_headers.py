#!/usr/bin/env python3
"""
Add a standard HTML comment header to MIND specification markdown files.

- Adds the header only if it's not already present.
- Skips obvious meta files like README.md and license-related docs.
"""

from pathlib import Path

HEADER = """<!--
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

MIND Language Specification — Community Edition
-->

"""

HEADER_MARKER = "Licensed under the Apache License, Version 2.0"

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

    # Already marked—nothing to do
    if HEADER_MARKER in text:
        return

    new_text = HEADER + text
    try:
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated: {path}")
    except OSError as e:
        print(f"Error writing {path}: {e}")

def main() -> None:
    root = Path(".").resolve()
    for md in root.rglob("*.md"):
        if should_skip(md):
            continue
        add_header_to_file(md)

if __name__ == "__main__":
    main()

