import unittest
from pathlib import Path

from tools.check_error_codes import check, check_table, table_codes

ROOT = Path(__file__).resolve().parent.parent.parent

SAMPLE = """# Errors

## Code table

| Code | Name | Status |
|------|------|--------|
| [`E1001`](#e1001-a) | A | in force |
| [`E1002`](#e1002-b) | B | withdrawn by DN-1; the entry keeps its history |

## E1xxx

### E1001: A
- **Trigger**: a

### E1002: B
- **Status**: withdrawn by DN-1.
"""


class TestErrorCodes(unittest.TestCase):
    def test_repository_is_clean(self) -> None:
        self.assertEqual(check(ROOT), [])

    def test_table_has_every_code_once(self) -> None:
        text = (ROOT / "spec" / "v1.0" / "errors.md").read_text(encoding="utf-8")
        codes = [row[0] for row in table_codes(text)]
        self.assertGreater(len(codes), 90)  # positive control: the table was read
        self.assertEqual(len(codes), len(set(codes)))

    def test_sample_is_clean(self) -> None:
        self.assertEqual(check_table(SAMPLE), [])

    def test_code_twice_in_table_is_found(self) -> None:
        bad = SAMPLE.replace("| [`E1002`](#e1002-b) | B |", "| [`E1001`](#e1001-a) | A |")
        findings = check_table(bad)
        self.assertTrue(any("E1001 has more than one table row" in f for f in findings), findings)

    def test_entry_twice_is_found(self) -> None:
        bad = SAMPLE + "\n### E1001: A\n- **Trigger**: another meaning\n"
        findings = check_table(bad)
        self.assertTrue(any("E1001 has more than one entry" in f for f in findings), findings)

    def test_entry_missing_from_table_is_found(self) -> None:
        bad = SAMPLE + "\n### E1003: C\n- **Trigger**: c\n"
        self.assertIn("errors.md: E1003 has an entry but is not in the code table", check_table(bad))

    def test_name_mismatch_is_found(self) -> None:
        bad = SAMPLE.replace("### E1001: A", "### E1001: Another name")
        findings = check_table(bad)
        self.assertTrue(any("E1001 is named" in f for f in findings), findings)

    def test_status_mismatch_is_found(self) -> None:
        bad = SAMPLE.replace("- **Status**: withdrawn by DN-1.", "- **Trigger**: b")
        self.assertIn("errors.md: E1002 status in the table and in its entry differ", check_table(bad))


if __name__ == "__main__":
    unittest.main()
