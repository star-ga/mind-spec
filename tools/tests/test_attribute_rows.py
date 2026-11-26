import unittest
from pathlib import Path

from tools.check_attribute_rows import check, check_texts, table_names

ROOT = Path(__file__).resolve().parent.parent.parent

TABLE = """## Attributes

| Name | Item | Argument form | Meaning | Status |
|------|------|---------------|---------|--------|
| `test` | a function | none | a test | Core v1 |
| `repr` | a `struct` | `(C)` | layout | extension |

## Raw memory
"""
ACCEPT = "input:\n  source: |\n    #[test]\n    fn t() { }\nexpected:\n  status: success\n"
REJECT = "input:\n  source: |\n    #[fast]\n    fn f() { }\nexpected:\n  status: error\n"


class TestAttributeRows(unittest.TestCase):
    def test_repository_is_clean(self) -> None:
        self.assertEqual(check(ROOT), [])

    def test_repository_table_is_read(self) -> None:
        text = (ROOT / "spec" / "v1.0" / "language.md").read_text(encoding="utf-8")
        names = table_names(text)
        self.assertIn("raw_memory", names)  # positive control: the table was read
        self.assertEqual(names["raw_memory"], "Core v1")

    def test_sample_is_clean(self) -> None:
        self.assertEqual(check_texts(TABLE, {"a.yaml": ACCEPT, "b.yaml": REJECT}), [])

    def test_core_name_without_accept_row_is_found(self) -> None:
        findings = check_texts(TABLE, {"b.yaml": REJECT})
        self.assertEqual(findings, ["language.md: the attribute `test` is a Core v1 row of the table and has no accept row"])

    def test_accept_row_with_name_outside_table_is_found(self) -> None:
        bad = ACCEPT.replace("#[test]", "#[test]\n    #[fast]")
        findings = check_texts(TABLE, {"a.yaml": bad})
        self.assertTrue(any("`#[fast]`" in f for f in findings), findings)

    def test_accept_row_with_extension_name_is_found(self) -> None:
        bad = ACCEPT.replace("#[test]", "#[test]\n    #[repr(C)]")
        findings = check_texts(TABLE, {"a.yaml": bad})
        self.assertTrue(any("`#[repr]`" in f for f in findings), findings)

    def test_tool_attribute_is_not_a_table_name(self) -> None:
        tool = ACCEPT.replace("#[test]", "#[test]\n    #[fmt.skip]")
        self.assertEqual(check_texts(TABLE, {"a.yaml": tool}), [])


if __name__ == "__main__":
    unittest.main()
