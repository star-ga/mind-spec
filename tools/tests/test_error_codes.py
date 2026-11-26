import re
import unittest
from pathlib import Path

from tools.check_error_codes import check, check_fix_rows, check_table, table_codes

ROOT = Path(__file__).resolve().parent.parent.parent

SAMPLE = """# Errors

## Code table

| Code | Name | Status | Fix class |
|------|------|--------|-----------|
| [`E1001`](#e1001-a) | A | in force | EXACT |
| [`E1002`](#e1002-b) | B | withdrawn by DN-1; the entry keeps its history | NONE |

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

    def test_fix_class_outside_the_four_is_found(self) -> None:
        bad = SAMPLE.replace("| in force | EXACT |", "| in force | MAYBE |")
        self.assertTrue(any("E1001 has the fix class 'MAYBE'" in f for f in check_table(bad)), check_table(bad))

    def test_exact_row_without_fix_block_is_found(self) -> None:
        row = "expected:\n  status: error\n  error:\n    code: E1001\n"
        self.assertEqual(check_fix_rows({"r.yaml": row}, SAMPLE),
                         ["r.yaml: E1001 has the fix class EXACT, and the row has no fix block"])
        fixed = row + "  fix:\n    class: EXACT\n    source: |\n      fn main() { }\n"
        self.assertEqual(check_fix_rows({"r.yaml": fixed}, SAMPLE), [])

    def test_fix_block_with_another_class_is_found(self) -> None:
        row = "expected:\n  status: error\n  error:\n    code: E1001\n  fix:\n    class: TYPED\n    source: |\n      x\n"
        self.assertTrue(check_fix_rows({"r.yaml": row}, SAMPLE))

    def test_repository_has_fix_rows(self) -> None:
        text = (ROOT / "spec" / "v1.0" / "errors.md").read_text(encoding="utf-8")
        rows = {str(p): p.read_text(encoding="utf-8") for p in (ROOT / "tests" / "conformance").rglob("*.yaml")}
        with_fix = [p for p, t in rows.items() if "\n  fix:\n" in t]
        self.assertGreater(len(with_fix), 20)  # positive control: the fix blocks were read
        self.assertEqual(check_fix_rows(rows, text), [])

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


def distance(a: str, b: str) -> int:
    """Damerau-Levenshtein distance (adjacent transpositions), as E1104 uses it."""
    d = [[i + j if i * j == 0 else 0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def e1104_overlaps(errors_md: str, lexical_md: str) -> list[str]:
    """Words of the E1105 table that E1104 would also take: 3 or more letters at distance 1 from a keyword."""
    block = lexical_md.split("### Keywords", 1)[1].split("```", 2)[1]
    keywords = block.split()
    entry = errors_md.split("### E1105:", 1)[1].split("\n### ", 1)[0]
    rows = [line.split("|")[1] for line in entry.splitlines() if line.startswith("| `")]
    words = [w for row in rows for w in re.findall(r"`([A-Za-z]+)`", row)]
    return [f"{w} ~ {k}" for w in words if len(w) >= 3 for k in keywords if distance(w, k) == 1]


class TestE1104AndE1105(unittest.TestCase):
    def test_no_table_word_is_a_misspelled_keyword(self) -> None:
        errors = (ROOT / "spec" / "v1.0" / "errors.md").read_text(encoding="utf-8")
        lexical = (ROOT / "spec" / "v1.0" / "lexical.md").read_text(encoding="utf-8")
        self.assertEqual(e1104_overlaps(errors, lexical), [])

    def test_overlap_is_found(self) -> None:
        errors = (ROOT / "spec" / "v1.0" / "errors.md").read_text(encoding="utf-8")
        lexical = (ROOT / "spec" / "v1.0" / "lexical.md").read_text(encoding="utf-8")
        bad = errors.replace("| `def`, `func`,", "| `def`, `fun`, `func`,")
        self.assertNotEqual(bad, errors)  # positive control: the table row was found
        self.assertIn("fun ~ fn", e1104_overlaps(bad, lexical))
        self.assertEqual(distance("lett", "let"), 1)
        self.assertEqual(distance("whlie", "while"), 1)
        self.assertEqual(distance("func", "fn"), 2)


if __name__ == "__main__":
    unittest.main()
