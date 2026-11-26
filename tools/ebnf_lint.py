#!/usr/bin/env python3
"""EBNF text-quality lint for the MIND specification grammars (stdlib only).

Usage:  python3 -I tools/ebnf_lint.py --lex L.ebnf --syn S.ebnf --ir I.ebnf --lexmd lexical.md [--k 3]
        python3 -I tools/ebnf_lint.py --selftest
        python3 -I tools/ebnf_lint.py --help
The report is Markdown on standard output. A decision that no k up to the tested k decides is reported as
"none up to k=K"; tools/tests/test_grammar_lint.py holds the budget of such decisions (DN-86).
Dialect (ISO-like): name = expr ; with "," concat, "|" choice, [ ] optional, { } repeat,
( ) group, "x" or 'x' terminals, ? text ? special sequences, (* comments *).
"""
import re, sys

TOKEN = re.compile(r'''\s+|\(\*.*?\*\)|"[^"]*"|'[^']*'|\?[^?]*\?|[A-Za-z_][A-Za-z_0-9]*|[=,|;\[\]{}()]''', re.S)
EXT_CLASS = {'Identifier': '<Identifier>', 'IntegerLiteral': '<Int>', 'DecimalInteger': '<Int>',
             'FloatingPointLiteral': '<Float>', 'TupleIndexPair': '<Float>', 'StringLiteral': '<Str>'}
SPLIT_DOCUMENTED = {'>>', '>=', '>>=', '::'}   # joins that the grammar comments describe as re-read
CAP = 400000


class Overflow(Exception):
    pass


# ---------------------------------------------------------------- parsing
def lex_tokens(text):
    pos, out = 0, []
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise SyntaxError('bad character %r at line %d' % (text[pos], text.count('\n', 0, pos) + 1))
        s = m.group()
        if not (s.isspace() or s.startswith('(*')):
            out.append((s, text.count('\n', 0, pos) + 1))
        pos = m.end()
    return out


class Parser:
    def __init__(self, text):
        self.t, self.i = lex_tokens(text), 0

    def peek(self):
        return self.t[self.i][0] if self.i < len(self.t) else None

    def take(self, want=None):
        tok = self.t[self.i][0]
        if want and tok != want:
            raise SyntaxError('expected %s got %s at line %d' % (want, tok, self.t[self.i][1]))
        self.i += 1
        return tok

    def rules(self):
        out = []
        while self.peek() is not None:
            line = self.t[self.i][1]
            name = self.take()
            self.take('=')
            out.append((name, self.alt(), line))
            self.take(';')
        return out

    def alt(self):
        items = [self.seq()]
        while self.peek() == '|':
            self.take()
            items.append(self.seq())
        return items[0] if len(items) == 1 else ('alt', tuple(items))

    def seq(self):
        items = [self.factor()]
        while self.peek() == ',':
            self.take()
            items.append(self.factor())
        return items[0] if len(items) == 1 else ('seq', tuple(items))

    def factor(self):
        tok = self.take()
        if tok in '[{(' and len(tok) == 1:
            inner = self.alt()
            self.take({'[': ']', '{': '}', '(': ')'}[tok])
            return {'[': ('opt', inner), '{': ('rep', inner), '(': inner}[tok]
        if tok[0] in '"\'':
            return ('t', tok[1:-1])
        if tok[0] == '?':
            return ('sp', tok.strip('? ').strip())
        if re.match(r'[A-Za-z_]', tok):
            return ('n', tok)
        raise SyntaxError('unexpected %s' % tok)


class Grammar:
    def __init__(self, text):
        self.rules, self.dups, self.line, self.order = {}, [], {}, []
        for name, ast, line in Parser(text).rules():
            if name in self.rules:
                self.dups.append((name, line))
                continue
            self.rules[name], self.line[name] = ast, line
            self.order.append(name)


def walk_nodes(ast):
    yield ast
    if ast[0] in ('seq', 'alt'):
        for a in ast[1]:
            yield from walk_nodes(a)
    elif ast[0] in ('opt', 'rep'):
        yield from walk_nodes(ast[1])


def names_in(ast):
    return {n[1] for n in walk_nodes(ast) if n[0] == 'n'}


def terms_in(ast):
    return {n[1] for n in walk_nodes(ast) if n[0] == 't'}


def inline(ast, own, lex, depth=0):
    """Replace names that the lexical grammar defines by their text (token classes stay classes)."""
    k = ast[0]
    if k == 'n':
        name = ast[1]
        if name in own:
            return ast
        if name in EXT_CLASS:
            return ('t', EXT_CLASS[name])
        if lex is not None and name in lex.rules and depth < 8:
            return inline(lex.rules[name], own, lex, depth + 1)
        return ast
    if k in ('seq', 'alt'):
        return (k, tuple(inline(a, own, lex, depth) for a in ast[1]))
    if k in ('opt', 'rep'):
        return (k, inline(ast[1], own, lex, depth))
    return ast


# ---------------------------------------------------------------- name checks
def reachable(rules, roots):
    seen, todo = set(), list(roots)
    while todo:
        n = todo.pop()
        if n in seen or n not in rules:
            continue
        seen.add(n)
        todo.extend(names_in(rules[n]))
    return seen


def nullable_names(rules):
    nul, changed = set(), True
    while changed:
        changed = False
        for n, a in rules.items():
            if n not in nul and is_nullable(a, nul):
                nul.add(n)
                changed = True
    return nul


def is_nullable(a, nul):
    k = a[0]
    if k == 't' or k == 'sp':
        return False
    if k == 'n':
        return a[1] in nul
    if k == 'seq':
        return all(is_nullable(x, nul) for x in a[1])
    if k == 'alt':
        return any(is_nullable(x, nul) for x in a[1])
    return True


def leftmost(a, nul):
    k = a[0]
    if k == 'n':
        return {a[1]}
    if k == 'alt':
        return set().union(*(leftmost(x, nul) for x in a[1]))
    if k == 'seq':
        out = set()
        for x in a[1]:
            out |= leftmost(x, nul)
            if not is_nullable(x, nul):
                break
        return out
    if k in ('opt', 'rep'):
        return leftmost(a[1], nul)
    return set()


def left_recursion(rules):
    nul = nullable_names(rules)
    edges = {n: leftmost(a, nul) & set(rules) for n, a in rules.items()}
    found = []
    for n in rules:
        stack, seen = list(edges[n]), set()
        while stack:
            m = stack.pop()
            if m in seen:
                continue
            seen.add(m)
            stack.extend(edges.get(m, ()))
        if n in seen:
            direct = n in edges[n]
            found.append((n, 'direct' if direct else 'indirect', sorted(seen & {x for x in rules if n in reach_of(edges, x)})))
    return found


def reach_of(edges, start):
    seen, stack = set(), list(edges.get(start, ()))
    while stack:
        m = stack.pop()
        if m not in seen:
            seen.add(m)
            stack.extend(edges.get(m, ()))
    return seen


def empty_loops(rules):
    nul = nullable_names(rules)
    return sorted({n for n, a in rules.items() for x in walk_nodes(a) if x[0] == 'rep' and is_nullable(x[1], nul)})


# ---------------------------------------------------------------- LL(k)
def concat(A, B, k):
    out = set()
    for a in A:
        if len(a) >= k or (a and a[-1] == '$'):
            out.add(a[:k])
        else:
            for b in B:
                out.add((a + b)[:k])
        if len(out) > CAP:
            raise Overflow()
    return out


class LL:
    def __init__(self, rules, k, seeds, mapped=frozenset()):
        self.rules, self.k, self.mapped = rules, k, mapped
        self.fn = {n: frozenset() for n in rules}
        self.cache = None
        self.fixpoint_first()
        self.cache = {}
        self.follow = {n: set() for n in rules}
        for s in seeds:
            self.follow[s] = {('$',)}
        self.rec = {}
        self.fixpoint_follow()

    def F(self, a):
        if self.cache is not None and id(a) in self.cache:
            return self.cache[id(a)]
        r = self._F(a)
        if self.cache is not None:
            self.cache[id(a)] = r
        return r

    def _F(self, a):
        t, k = a[0], self.k
        if t == 't':
            return {(a[1],)}
        if t == 'sp':
            return {('<?%s>' % a[1][:24],)}
        if t == 'n':
            return self.fn.get(a[1], set())
        if t == 'alt':
            return set().union(*(self.F(x) for x in a[1]))
        if t == 'seq':
            r = {()}
            for x in a[1]:
                r = concat(r, self.F(x), k)
            return r
        if t == 'opt':
            return self.F(a[1]) | {()}
        return self.loop(a[1], {()})

    def loop(self, x, after):
        fx, cur = self.F(x), set(after)
        while True:
            nxt = set(after) | concat(fx, cur, self.k)
            if nxt == cur:
                return cur
            cur = nxt

    def fixpoint_first(self):
        changed = True
        while changed:
            changed = False
            for n, a in self.rules.items():
                v = frozenset(self._F(a))
                if v != self.fn[n]:
                    self.fn[n], changed = v, True

    def fixpoint_follow(self):
        changed = True
        while changed:
            self.changed, self.rec = False, {}
            for n, a in self.rules.items():
                self.walk(a, n, set(self.follow[n]))
            changed = self.changed

    def walk(self, a, path, after):
        t = a[0]
        if t == 'n':
            if a[1] in self.follow and not after <= self.follow[a[1]]:
                self.follow[a[1]] |= after
                self.changed = True
        elif t == 'seq':
            sfx = after
            for i in range(len(a[1]) - 1, -1, -1):
                self.walk(a[1][i], '%s.%d' % (path, i), sfx)
                sfx = concat(self.F(a[1][i]), sfx, self.k)
        elif t == 'alt':
            self.rec[path] = (a, after, None)
            for i, x in enumerate(a[1]):
                self.walk(x, '%s|%d' % (path, i), after)
        elif t == 'opt':
            self.rec[path] = (a, after, None)
            self.walk(a[1], path + '?', after)
        elif t == 'rep':
            L = self.loop(a[1], after)
            self.rec[path] = (a, after, L)
            self.walk(a[1], path + '*', L)
        elif t == 't':
            self.rec.setdefault(('tok', path), (a, after, None))

    def shadow(self, A, B):
        """Strings that match only because a contextual word is also an Identifier."""
        def has(S, f):
            return {s for s in S if f(s)}
        isword = lambda s: any(x in self.mapped for x in s)
        isid = lambda s: '<Identifier>' in s
        mp = lambda S: {tuple('<Identifier>' if x in self.mapped else x for x in s) for s in S}
        return (mp(has(A, isword)) & has(B, isid)) | (has(A, isid) & mp(has(B, isword)))

    def conflicts(self):
        out = []
        for path, (a, after, L) in self.rec.items():
            if isinstance(path, tuple):
                continue
            for (i, j, A, B) in self.choices(a, after, L):
                ex = A & B
                sh = self.shadow(A, B) if self.mapped else set()
                if ex or sh:
                    out.append((path, i, j, ex, sh))
        return out

    def choices(self, a, after, L):
        t, k = a[0], self.k
        if t == 'alt':
            sets = [concat(self.F(x), after, k) for x in a[1]]
            return [(i, j, sets[i], sets[j]) for i in range(len(sets)) for j in range(i + 1, len(sets))]
        if t == 'opt':
            return [(0, 1, concat(self.F(a[1]), after, k), set(after))]
        return [(0, 1, concat(self.F(a[1]), L, k), set(after))]


def decision_text(a, i, j):
    def show(x):
        s = flat(x)
        return s if len(s) < 60 else s[:57] + '...'
    if a[0] == 'alt':
        return 'alt %d [%s] vs alt %d [%s]' % (i, show(a[1][i]), j, show(a[1][j]))
    return '%s [%s] vs what follows' % ('optional' if a[0] == 'opt' else 'repeat', show(a[1]))


def flat(a):
    t = a[0]
    if t == 't':
        return '"%s"' % a[1]
    if t == 'n':
        return a[1]
    if t == 'sp':
        return '?%s?' % a[1]
    if t == 'seq':
        return ' , '.join(flat(x) for x in a[1])
    if t == 'alt':
        return '( ' + ' | '.join(flat(x) for x in a[1]) + ' )'
    return ('[ %s ]' if t == 'opt' else '{ %s }') % flat(a[1])


def ll_conflicts(rules, roots, kmax, mapped=frozenset()):
    """Return conflicts with per-k presence. Result: list of dict."""
    seeds = set(roots) | {n for n in rules if n not in reachable(rules, roots)}
    byk, last_ok = {}, 0
    for k in range(1, kmax + 1):
        try:
            ll = LL(rules, k, seeds, mapped)
            byk[k] = (ll, ll.conflicts())
            last_ok = k
        except Overflow:
            break
    res = {}
    for k, (ll, cs) in byk.items():
        for path, i, j, ex, sh in cs:
            d = res.setdefault((path, i, j), {'path': path, 'i': i, 'j': j, 'exact': {}, 'shadow': {},
                                              'node': ll.rec[path][0]})
            if ex:
                d['exact'][k] = ex
            if sh:
                d['shadow'][k] = sh
    for d in res.values():
        for key in ('exact', 'shadow'):
            ks = d[key]
            d[key + '_k'] = None if not ks else (None if last_ok in ks else max(ks) + 1)
            d[key + '_present'] = bool(ks)
    return list(res.values()), last_ok


# ---------------------------------------------------------------- lexical cross checks
def terminals_of(lex, names):
    out = set()
    for n in names:
        if n in lex.rules:
            out |= terms_in(lex.rules[n])
    return out


def is_word(s):
    return bool(re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', s))


def lexical_checks(syn, lex, reserved, reach):
    keyword = terminals_of(lex, ['Keyword'])
    ctx = terminals_of(lex, ['ContextualWord'])
    produced = keyword | ctx | terminals_of(lex, ['Operator', 'Punctuation', 'BooleanLiteral'])
    used_all = set().union(*(terms_in(a) for a in syn.rules.values()))
    used_reach = set().union(*(terms_in(syn.rules[n]) for n in reach if n in syn.rules))
    f = []
    for t in sorted(used_all - produced):
        f.append(('terminal-not-producible', t, 'syntax spells "%s"; the lexical grammar cannot produce it' % t))
    for t in sorted(w for w in used_all if is_word(w) and w not in keyword and w not in ctx):
        if t not in terminals_of(lex, ['BooleanLiteral']):
            f.append(('word-used-not-reserved', t, 'syntax spells word "%s"; it is not reserved and not listed contextual' % t))
    for t in sorted(keyword - used_all):
        f.append(('keyword-reserved-not-used', t, '"%s" is reserved; no syntax rule spells it' % t))
    for t in sorted((keyword & used_all) - used_reach):
        f.append(('keyword-only-unreachable', t, '"%s" is reserved and spelled only in rules not reachable from the start' % t))
    for t in sorted(used_all & ctx - used_reach):
        f.append(('contextual-only-unreachable', t, '"%s" is contextual and spelled only in rules not reachable from the start' % t))
    for t in sorted(ctx - used_all):
        f.append(('contextual-not-used', t, 'contextual word "%s" is spelled by no syntax rule' % t))
    for t in sorted(terminals_of(lex, ['Operator', 'Punctuation']) - used_all):
        f.append(('token-lexed-not-used', t, 'token "%s" is lexed but no syntax rule spells it' % t))
    if reserved is not None:
        for t in sorted(set(reserved) - keyword):
            f.append(('reserved-list-mismatch', t, '"%s" is in lexical.md reserved list, not in Keyword rule' % t))
        for t in sorted(keyword - set(reserved)):
            f.append(('reserved-list-mismatch', t, '"%s" is in Keyword rule, not in lexical.md reserved list' % t))
    for t in sorted(terminals_of(lex, ['BooleanLiteral'])):
        if reserved is not None and t not in reserved:
            f.append(('literal-word-not-reserved', t, 'literal word "%s" is not reserved; Identifier can spell it' % t))
    return f


def adjacency_checks(ll, lex):
    joined = terminals_of(lex, ['Operator', 'Punctuation'])
    out = {}
    for path, (a, after, _) in ll.rec.items():
        if isinstance(path, tuple) and a[0] == 't':
            for s in after:
                if s[0] != '$' and a[1] + s[0] in joined:
                    out.setdefault((a[1], s[0]), []).append(path[1])
    return out


# ---------------------------------------------------------------- driver
def name_findings(g, roots, extra_defs=()):
    f = []
    for n, line in g.dups:
        f.append(('defined-twice', n, 'line %d redefines %s (first at line %d)' % (line, n, g.line[n])))
    defined = set(g.rules) | set(extra_defs)
    for n in g.order:
        for u in sorted(names_in(g.rules[n]) - defined):
            f.append(('undefined-name', u, 'used in %s (line %d), defined nowhere' % (n, g.line[n])))
    reach = reachable(g.rules, roots)
    for n in g.order:
        if n not in reach:
            f.append(('defined-not-reached', n, 'line %d: not reachable from %s' % (g.line[n], ','.join(sorted(roots)))))
    for n, kind, cyc in left_recursion(g.rules):
        f.append(('left-recursion', n, '%s left recursion through %s' % (kind, ','.join(cyc))))
    for n in empty_loops(g.rules):
        f.append(('empty-loop', n, 'a repeat in %s can match the empty string' % n))
    return f, reach


def parse_reserved(md):
    m = re.search(r'reserved and MAY NOT be used as identifiers:\s*```[^\n]*\n(.*?)```', md, re.S)
    return m.group(1).split() if m else None


def full_lint(lex_t, syn_t, kmax=2, md=None, start='Module', lex_roots=('SourceFile',)):
    lex, syn = Grammar(lex_t), Grammar(syn_t)
    res = {}
    res['syn_names'], reach = name_findings(syn, {start}, set(lex.rules))
    used_by_syn = names_in_all(syn) & set(lex.rules)
    res['lex_names'], _ = name_findings(lex, set(lex_roots) | used_by_syn)
    reserved = parse_reserved(md) if md else None
    res['lexical'] = lexical_checks(syn, lex, reserved, reach)
    rules = {n: inline(a, set(syn.rules), lex) for n, a in syn.rules.items()}
    ctxw = terminals_of(lex, ['ContextualWord']) | {'_'}
    res['ll'], res['ll_k'] = ll_conflicts(rules, {start}, kmax, frozenset(ctxw))
    ll1 = LL(rules, 1, {start} | {n for n in rules if n not in reach})
    res['adj'] = adjacency_checks(ll1, lex)
    res['grammars'] = (lex, syn, rules, reach)
    return res


def names_in_all(g):
    return set().union(*(names_in(a) for a in g.rules.values()))


def ir_lint(ir_t, kmax=2):
    g = Grammar(ir_t)
    f, reach = name_findings(g, {'IRModule'})
    ll, lk = ll_conflicts(g.rules, {'IRModule'}, kmax)
    return g, f, ll, lk


# ---------------------------------------------------------------- report
def sample(S, n=4):
    return ', '.join(' '.join(s) for s in sorted(S)[:n])


def kmsg(kk, last):
    return 'none up to k=%d' % last if kk is None else 'k=%d' % kk


def unbounded(conflicts):
    """Rule paths of the exact conflicts that no tested k decides."""
    return sorted(d['path'] for d in conflicts if d['exact_present'] and d['exact_k'] is None)


def print_report(args):
    rd = lambda p: open(p, encoding='utf-8').read()
    lex_t, syn_t, ir_t = rd(args['lex']), rd(args['syn']), rd(args['ir'])
    md = rd(args['lexmd']) if 'lexmd' in args else None
    k = int(args.get('k', 3))
    r = full_lint(lex_t, syn_t, k, md)
    lex, syn, rules, reach = r['grammars']
    print('# Lint output\n')
    print('syntax rules: %d, lexical rules: %d, reachable from Module: %d\n' % (len(syn.rules), len(lex.rules), len(reach)))
    for title, key in (('Names, lexical grammar', 'lex_names'), ('Names, syntax grammar', 'syn_names')):
        print('## %s\n\n| check | name | detail |\n|---|---|---|' % title)
        for c, n, d in r[key]:
            print('| %s | %s | %s |' % (c, n, d))
        print()
    print('## Lexical cross-check\n\n| check | word | detail |\n|---|---|---|')
    for c, n, d in r['lexical']:
        print('| %s | `%s` | %s |' % (c, n, d))
    print('\n## Adjacent syntax tokens that the lexer joins (context-dependent tokens)\n')
    print('| pair | joined token | rule-paths | documented split rule |\n|---|---|---|---|')
    for (a, b), ps in sorted(r['adj'].items()):
        print('| `%s` then `%s` | `%s` | %s | %s |' % (a, b, a + b, ', '.join(sorted(set(p.split('.')[0].split('|')[0] for p in ps))[:5]),
                                                     'yes' if a + b in SPLIT_DOCUMENTED and all(p.split('.')[0].split('|')[0] in ('CloseAngle', 'SliceColon') for p in ps) else 'NO'))
    print('\n## LL(k) conflicts, syntax (k tested 1..%d)\n' % r['ll_k'])
    print_ll(r['ll'], r['ll_k'])
    g, f, ll, lk = ir_lint(ir_t, k)
    print('\n## Names, IR grammar\n\n| check | name | detail |\n|---|---|---|')
    for c, n, d in f:
        print('| %s | %s | %s |' % (c, n, d))
    print('\n## LL(k) conflicts, IR (k tested 1..%d)\n' % lk)
    print_ll(ll, lk)


def print_ll(cs, last):
    print('| id | rule path | decision | kind | k that decides | tokens at k=1 |\n|---|---|---|---|---|---|')
    for n, d in enumerate(sorted(cs, key=lambda d: d['path']), 1):
        for key in ('exact', 'shadow'):
            if not d[key + '_present']:
                continue
            ks = d[key]
            sm = sample(ks[min(ks)])
            print('| C%02d%s | %s | %s | %s | %s | %s |' % (n, '' if key == 'exact' else 's', d['path'],
                  decision_text(d['node'], d['i'], d['j']).replace('|', '/'), key, kmsg(d[key + '_k'], last), sm))


# ---------------------------------------------------------------- selftest
LEXT = '''Keyword = "fn" | "let" ; ContextualWord = "tensor" | "in" ;
Operator = ">" | ">>" | "+" ; Punctuation = "(" | ")" ; BooleanLiteral = "true" | "false" ;
Identifier = "x" ; IntegerLiteral = "1" ; SourceFile = Identifier ;'''
MDT = 'The following keywords are reserved and MAY NOT be used as identifiers:\n\n```\nfn let\n```\n'


def selftest():
    cases = [
        ('clean', 'S = "fn" , Identifier , "let" ;', [], 'S'),
        ('undefined-name', 'S = A ;', ['undefined-name'], 'S'),
        ('defined-not-reached', 'S = "fn" ; B = "let" ;', ['defined-not-reached'], 'S'),
        ('defined-twice', 'S = "fn" ; S = "let" ;', ['defined-twice'], 'S'),
        ('left-recursion direct', 'S = S , "fn" | "let" ;', ['left-recursion'], 'S'),
        ('left-recursion indirect', 'S = A , "fn" | "let" ; A = S , "let" ;', ['left-recursion'], 'S'),
        ('empty-loop', 'S = { [ "fn" ] } , "let" ;', ['empty-loop'], 'S'),
        ('terminal-not-producible', 'S = "fn" , "zz" ;', ['terminal-not-producible'], 'S'),
        ('word-used-not-reserved', 'S = "fn" , "foo" ;', ['word-used-not-reserved'], 'S'),
        ('keyword-reserved-not-used', 'S = "fn" ;', ['keyword-reserved-not-used'], 'S'),
        ('adjacent join', 'S = "fn" , ">" , ">" , "let" ;', ['adjacent'], 'S'),
    ]
    bad = 0
    for name, syn, want, start in cases:
        got = set(selftest_run(syn, start))
        if name == 'clean':
            ok = not got
        else:
            ok = all(w in got for w in want)
        print('%-28s %s %s' % (name, 'PASS' if ok else 'FAIL', sorted(got)))
        bad += not ok
    bad += selftest_ll()
    print('selftest %s' % ('FAILED' if bad else 'OK'))
    return 1 if bad else 0


def selftest_run(syn, start):
    r = full_lint(LEXT, syn, 2, MDT, start, ('SourceFile',))
    got = [c for c, _, _ in r['syn_names']] + [c for c, _, _ in r['lexical']]
    got = [c for c in got if c not in ('token-lexed-not-used', 'contextual-not-used', 'literal-word-not-reserved')]
    if r['adj']:
        got.append('adjacent')
    return got


def selftest_ll():
    tests = [
        ('first-first, decided at k=2', 'S = "a" , "b" | "a" , "c" ;', 'exact', 2),
        ('first-follow optional', 'S = [ "a" ] , "a" ;', 'exact', 2),
        ('first-follow repeat', 'S = { "a" } , "a" ;', 'exact', 2),
        ('unbounded prefix', 'S = A , "c" | B , "d" ; A = { "a" } ; B = { "a" } ;', 'exact', None),
        ('identifier shadow', 'S = Identifier | "tensor" ;', 'shadow', None),
        ('no conflict control', 'S = "a" , "b" | "c" , "d" ;', None, 0),
    ]
    bad = 0
    for name, text, kind, want in tests:
        g, lx = Grammar(text), Grammar(LEXT)
        rules = {n: inline(a, set(g.rules), lx) for n, a in g.rules.items()}
        cs, last = ll_conflicts(rules, {'S'}, 3, frozenset({'tensor', 'in', '_'}))
        if kind is None:
            ok = not cs
        else:
            ok = any(c[kind + '_present'] and c[kind + '_k'] == want for c in cs)
        print('%-28s %s' % ('ll: ' + name, 'PASS' if ok else 'FAIL'))
        bad += not ok
    return bad


def main(argv):
    if '--selftest' in argv:
        return selftest()
    if '--help' in argv or '-h' in argv or len(argv) % 2:
        print(__doc__)
        return 0 if ('--help' in argv or '-h' in argv) else 2
    args, i = {}, 0
    while i < len(argv):
        args[argv[i].lstrip('-')] = argv[i + 1]
        i += 2
    if not all(x in args for x in ('lex', 'syn', 'ir')):
        print(__doc__)
        return 2
    print_report(args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
