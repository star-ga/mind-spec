import unittest
from pathlib import Path

from tools.check_grammar_tokens import check

SPEC = Path(__file__).resolve().parent.parent.parent / "spec" / "v1.0"

LEXICAL = 'Keyword = "fn" ; Operator = "+" | "<<" ; Punctuation = ";" ;'


class TestGrammarTokens(unittest.TestCase):
    def test_spec_grammars_agree(self) -> None:
        lexical = (SPEC / "grammar-lexical.ebnf").read_text(encoding="utf-8")
        syntax = (SPEC / "grammar-syntax.ebnf").read_text(encoding="utf-8")
        self.assertEqual(check(lexical, syntax), [])

    def test_unknown_terminal_is_found(self) -> None:
        # positive control: a token that the lexical grammar lacks must be reported
        findings = check(LEXICAL, 'A = "fn" , "+" , ">>" ;')
        self.assertEqual(len(findings), 1)
        self.assertIn("'>>'", findings[0])

    def test_undefined_nonterminal_is_found(self) -> None:
        findings = check(LEXICAL, 'A = "fn" , B ;')
        self.assertEqual(len(findings), 1)
        self.assertIn("B", findings[0])

    def test_comment_text_is_ignored(self) -> None:
        self.assertEqual(check(LEXICAL, '(* "zzz" *) A = "fn" ;'), [])


if __name__ == "__main__":
    unittest.main()
