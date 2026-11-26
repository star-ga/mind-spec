"""The lookahead budget of the grammar (DN-86) and the reserved word list (DN-75, DN-87).

The lint runs on the three grammar files with k up to 3. At most three decisions may stay undecided by every k up
to 3, and each of them MUST be one of the three named decisions: the tail of a block (`Block`), a record body
against the brace of a head (`NamePath`) and the reading of a statement start (`Statement`). A fourth one is a red
gate. The reserved word list of lexical.md and the `Keyword` rule of grammar-lexical.ebnf MUST hold the same words.
"""
import functools
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tools import ebnf_lint

SPEC = Path(__file__).resolve().parent.parent.parent / "spec" / "v1.0"
NAMED = {"Block", "NamePath", "Statement"}
BUDGET = 3
K = 3


def read(name: str) -> str:
    return (SPEC / name).read_text(encoding="utf-8")


@functools.lru_cache(maxsize=1)
def spec_lint():
    syntax = ebnf_lint.full_lint(read("grammar-lexical.ebnf"), read("grammar-syntax.ebnf"), K, read("lexical.md"))
    _g, _f, ir_conflicts, _k = ebnf_lint.ir_lint(read("grammar-ir.ebnf"), K)
    return syntax, ir_conflicts


def budget_findings(syntax_conflicts, ir_conflicts) -> list:
    paths = ebnf_lint.unbounded(syntax_conflicts) + ["IR:" + p for p in ebnf_lint.unbounded(ir_conflicts)]
    findings = []
    if len(paths) > BUDGET:
        findings.append("%d undecided choices, the budget is %d: %s" % (len(paths), BUDGET, paths))
    for path in paths:
        if path.split(".")[0] not in NAMED:
            findings.append("undecided choice %s is not one of the named decisions" % path)
    return findings


def reserved_findings(lint_result) -> list:
    return [row for row in lint_result["lexical"] if row[0] == "reserved-list-mismatch"]


class TestGrammarLint(unittest.TestCase):
    def test_selftest(self) -> None:
        with redirect_stdout(io.StringIO()):
            self.assertEqual(ebnf_lint.selftest(), 0)

    def test_lookahead_budget(self) -> None:
        syntax, ir_conflicts = spec_lint()
        self.assertEqual(syntax["ll_k"], K)  # positive control: every k up to 3 was tested
        self.assertGreater(len(syntax["ll"]), 0)  # positive control: the lint found the decided conflicts too
        self.assertEqual(budget_findings(syntax["ll"], ir_conflicts), [])

    def test_reserved_list_equals_keyword_rule(self) -> None:
        syntax, _ = spec_lint()
        reserved = ebnf_lint.parse_reserved(read("lexical.md"))
        self.assertIsNotNone(reserved)
        self.assertGreater(len(reserved), 20)  # positive control: the list was read
        self.assertEqual(reserved_findings(syntax), [])

    def test_fourth_undecided_choice_is_found(self) -> None:
        # control: a grammar with a common prefix of any length before the deciding token
        text = 'S = A , "c" | B , "d" ; A = { "a" } ; B = { "a" } ;'
        g, lx = ebnf_lint.Grammar(text), ebnf_lint.Grammar(ebnf_lint.LEXT)
        rules = {n: ebnf_lint.inline(a, set(g.rules), lx) for n, a in g.rules.items()}
        conflicts, _ = ebnf_lint.ll_conflicts(rules, {"S"}, K)
        findings = budget_findings(conflicts, [])
        self.assertTrue(any("not one of the named decisions" in f for f in findings), findings)
        syntax, ir_conflicts = spec_lint()
        over = budget_findings(syntax["ll"] + conflicts, ir_conflicts)
        self.assertTrue(any("the budget is 3" in f for f in over), over)

    def test_reserved_list_mismatch_is_found(self) -> None:
        md = ebnf_lint.MDT.replace("fn let", "fn")
        result = ebnf_lint.full_lint(ebnf_lint.LEXT, 'S = "fn" , "let" , Identifier ;', 2, md, "S", ("SourceFile",))
        self.assertEqual([row[1] for row in reserved_findings(result)], ["let"])


if __name__ == "__main__":
    unittest.main()
