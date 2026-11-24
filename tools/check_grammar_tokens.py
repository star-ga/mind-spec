#!/usr/bin/env python3
"""Check that every terminal of the syntactic grammar exists in the lexical grammar.

A terminal of grammar-syntax.ebnf (a quoted string) MUST be listed in the Keyword,
ContextualWord, Operator or Punctuation rule of grammar-lexical.ebnf, or be a boolean
literal. Every nonterminal that the syntactic grammar uses MUST be defined in one of
the two files, and no rule is defined in both. Every ContextualWord entry MUST have the shape of an
identifier, because the lexer produces it as an Identifier.

usage: check_grammar_tokens.py [LEXICAL.ebnf SYNTAX.ebnf]
exit status 0 when there is no finding, 1 otherwise.
"""

import re
import sys
from pathlib import Path

TOKEN_RULES = ("Keyword", "ContextualWord", "Operator", "Punctuation", "BooleanLiteral")
IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TOKEN_RE = re.compile(r'"[^"]*"|\'[^\']*\'|\?[^?]*\?|[A-Za-z_][A-Za-z0-9_]*|[=;|,\[\]\(\)\{\}]')


def strip_comments(text: str) -> str:
    out, depth, i = [], 0, 0
    while i < len(text):
        if text.startswith("(*", i):
            depth += 1
            i += 2
        elif text.startswith("*)", i) and depth:
            depth -= 1
            i += 2
        else:
            if depth == 0:
                out.append(text[i])
            i += 1
    return "".join(out)


def parse_rules(text: str) -> dict:
    toks = TOKEN_RE.findall(strip_comments(text))
    rules, i = {}, 0
    while i < len(toks):
        if re.match(r"[A-Za-z_]", toks[i]) and i + 1 < len(toks) and toks[i + 1] == "=":
            name, body = toks[i], []
            i += 2
            while i < len(toks) and toks[i] != ";":
                body.append(toks[i])
                i += 1
            rules[name] = body
        i += 1
    return rules


def terminals(body: list) -> list:
    return [t[1:-1] for t in body if t[0] in "\"'"]


def nonterminals(body: list) -> list:
    return [t for t in body if re.match(r"[A-Za-z_]", t)]


def check(lexical_text: str, syntax_text: str) -> list:
    lex, syn = parse_rules(lexical_text), parse_rules(syntax_text)
    tokens = {t for r in TOKEN_RULES for t in terminals(lex.get(r, []))}
    findings = []
    for word in terminals(lex.get("ContextualWord", [])):
        if not IDENTIFIER_RE.fullmatch(word):
            findings.append("ContextualWord %r is not shaped like an identifier" % word)
    for name, body in syn.items():
        for t in terminals(body):
            if t not in tokens:
                findings.append("terminal %r of %s is not in the lexical grammar" % (t, name))
        for n in nonterminals(body):
            if n not in syn and n not in lex:
                findings.append("%s uses %s, which is not defined" % (name, n))
    findings += ["rule %s is defined in both files" % n for n in syn if n in lex]
    return findings


def main(argv: list) -> int:
    root = Path(__file__).resolve().parent.parent / "spec" / "v1.0"
    lexical = Path(argv[0]) if argv else root / "grammar-lexical.ebnf"
    syntax = Path(argv[1]) if argv else root / "grammar-syntax.ebnf"
    findings = check(lexical.read_text(encoding="utf-8"), syntax.read_text(encoding="utf-8"))
    for f in findings:
        print(f)
    print("findings: %d" % len(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
