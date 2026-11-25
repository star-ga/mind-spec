import json
import shutil
import subprocess
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parent.parent / "site-links.js"

ROOT_FILES = ["STATUS.md", "design/rfcs/0024-impl-forms.md"]

# (page under docs/, body, expected body after the rewrite of the site build)
CASES = [
    ("rfcs/a.md", "[x](../../spec/v1.0/ir.md#core-ir)", "[x](../spec/v1.0/ir.md#core-ir)"),
    ("rfcs/a.md", "[x](../../design/rfcs/0024-impl-forms.md)", "[x](../design/rfcs/0024-impl-forms.md)"),
    ("rfcs/a.md", "[x](../../tests/conformance/syntax/README.md)", "[x](../tests/conformance/syntax/README.md)"),
    ("changelog.md", "[x](../STATUS.md) [y](../spec/v1.0/ir.md)", "[x](STATUS.md) [y](spec/v1.0/ir.md)"),
    # not published from outside docs/: unchanged
    ("rfcs/a.md", "[x](../../design/rfcs/0099-other.md)", "[x](../../design/rfcs/0099-other.md)"),
    ("changelog.md", "[x](../README.md)", "[x](../README.md)"),
    # stays inside docs/, or leaves the repository: unchanged
    ("rfcs/a.md", "[x](../design/compiler.md) [y](./active.md)", "[x](../design/compiler.md) [y](./active.md)"),
    ("rfcs/a.md", "[x](../../../spec/v1.0/ir.md)", "[x](../../../spec/v1.0/ir.md)"),
    # a link inside docs/ whose rest, after as many characters as the prefix that leaves docs/, names a published file
    ("rfcs/a.md", "[x](sub/a/spec/v1.0/ir.md)", "[x](sub/a/spec/v1.0/ir.md)"),
    # a fenced code block is not changed
    ("rfcs/a.md", "```text\n[x](../../spec/v1.0/ir.md)\n```", "```text\n[x](../../spec/v1.0/ir.md)\n```"),
]

SCRIPT = """
const { makeIsPublished, rewriteDocsPage } = require(process.argv[1]);
const [rootFiles, cases] = JSON.parse(process.argv[2]);
const isPublished = makeIsPublished(rootFiles);
process.stdout.write(JSON.stringify(cases.map(([page, body]) => rewriteDocsPage(body, page, isPublished))));
"""


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class TestSiteLinks(unittest.TestCase):
    def test_docs_links_are_rewritten_to_the_published_place(self) -> None:
        arg = json.dumps([ROOT_FILES, [[page, body] for page, body, _ in CASES]])
        run = subprocess.run(["node", "-e", SCRIPT, str(MODULE), arg], capture_output=True, text=True, check=True)
        got = json.loads(run.stdout)
        for (page, body, want), have in zip(CASES, got):
            with self.subTest(page=page, body=body):
                self.assertEqual(have, want)


if __name__ == "__main__":
    unittest.main()
