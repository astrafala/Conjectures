#!/usr/bin/env python3
"""The generating function an entry states as FACT, when it is an explicit algebraic one.

This is what `holonomic.prove` needs: it turns a conjectured P-recursive recurrence into an
identity of functions, which is a proof rather than a check -- but only if the generating
function is known and algebraic. The corpus writes those as

    G.f.: (1-x-sqrt(1-6x+x^2))/(2x(1+x));
    G.f.: g(z)=(1+z)(z^4+2z^3+2z^2-1+Q)/(2z(1-z-z^2-z^3)), where Q = sqrt((1-z^2)(...))

so three things have to be handled and each defeated an earlier filter: the variable may be z
rather than x; a named abbreviation may be defined in a trailing `where' clause and has to be
substituted, not refused; and implicit multiplication is everywhere -- `2x(1+x)', `1-6x',
`(1-z^2)(1-z)'.

A g.f. the entry marks as conjectural is NOT used: proving one conjecture from another is not
a proof. Neither is one that names another sequence, or is given as a functional equation, a
continued fraction, or a sum -- those are real work and are refused here rather than guessed at.
"""
import re

import sympy as sp

x = sp.Symbol('x')
CONJ = re.compile(r'conjectur|empirical', re.I)
GF = re.compile(r'^\s*G\.f\.\s*:?\s*(.*)$', re.I)
ATTR = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')
LEAD = re.compile(r'^\s*[A-Za-z]\s*\(\s*[xz]\s*\)\s*=\s*')
OUT = re.compile(r'A\d{6}|Sum_|Prod_|satisf|continued fraction|Integral|\bE\(|hypergeom', re.I)


def _implicit(s):
    """the corpus's multiplication, written out"""
    s = s.replace('^', '**')
    s = re.sub(r'(\d)\s*(?=[A-Za-z(])', r'\1*', s)          # 2x, 6x^2, 2(1+x)
    s = re.sub(r'(\))\s*(?=[A-Za-z(])', r'\1*', s)          # (1-z)(1+z), (1-z)Q
    s = re.sub(r'\b([xz])\s*(?=\()', r'\1*', s)             # z(1+z)
    s = re.sub(r'\b([xz])\s*(?=[A-Za-z])', r'\1*', s)       # zQ
    return s


NAME = re.compile(r'^\s*(?:Expansion of|Generating function(?: for)?)\s*[:]?\s*(.*)$', re.I)
INNER = re.compile(r'^\s*(?:g\.f\.|ordinary generating function)\s*[:]?\s*', re.I)
EGF = re.compile(r'\be\.g\.f\.|exponential generating', re.I)


def from_name(e):
    """the g.f. the entry's own NAME gives, when the name IS the definition.

    This is a stronger source than the formula section, and A116388 is why: its `G.f.:` line,
    stated as fact, does not generate the terms the entry publishes -- the first eight are
    2, 0, 10, 12, ... against a published 1, 1, 4, 10, ... -- while the expression in its name
    reproduces them exactly. An erroneous formula line is a fact about that entry and the
    sweep records it; it must never become the premise of a proof.

    An EXPONENTIAL generating function is a different object -- theta acts on it differently --
    and is refused rather than read as an ordinary one.
    """
    nm = ' '.join(e['name'].split())
    m = NAME.match(nm)
    if not m:
        return None
    body = m.group(1).strip().rstrip('.')
    if EGF.search(nm):
        return None
    body = INNER.sub('', body).strip()
    if OUT.search(body) or re.search(r'\bwhere\b|satisf|,', body, re.I):
        return None
    return _parse(body)


def _parse(body):
    var = 'z' if ('z' in body and 'x' not in body) else 'x'
    loc = {var: x, 'sqrt': sp.sqrt}
    s = _implicit(body)
    if set(re.findall(r'[A-Za-z]\w*', s)) - set(loc) - {'sqrt'}:
        return None
    try:
        A = sp.sympify(s, locals=loc)
    except Exception:
        return None
    return A if A.has(x) else None


def read(e):
    """the g.f. as a sympy expression in x, or None."""
    for L in e['formula'] + e['comment']:
        t = ' '.join(L.split())
        if CONJ.search(t):
            continue
        m = GF.match(t)
        if not m:
            continue
        body = ATTR.sub('', m.group(1)).strip().rstrip(';').rstrip('.')
        if OUT.search(body):
            continue
        # a trailing "where Q = ..." defines an abbreviation; substitute it
        subs = {}
        mm = re.search(r',?\s*where\s+(.*)$', body, re.I)
        if mm:
            body = body[:mm.start()].strip().rstrip(',')
            for part in re.split(r',\s*(?=[A-Za-z]\w*\s*=)', mm.group(1)):
                q = re.match(r'\s*([A-Za-z]\w*)\s*=\s*(.*?)\s*\.?\s*$', part)
                if q:
                    subs[q.group(1)] = q.group(2)
        body = LEAD.sub('', body).strip()
        if not body:
            continue
        var = 'z' if ('z' in body and 'x' not in body) else 'x'
        loc = {var: x, 'sqrt': sp.sqrt}
        try:
            sub_exprs = {k: sp.sympify(_implicit(v), locals=loc) for k, v in subs.items()}
        except Exception:
            continue
        loc.update(sub_exprs)
        s = _implicit(body)
        # after substitution nothing alphabetic may remain but the variable and the names
        known = set(loc) | {'sqrt'}
        names = set(re.findall(r'[A-Za-z]\w*', s))
        if names - known:
            continue
        try:
            A = sp.sympify(s, locals=loc)
        except Exception:
            continue
        if not A.has(x):
            continue
        return A
    # a g.f. whose abbreviation is defined by an algebraic equation rather than in closed form
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    for L in e['formula'] + e['comment']:
        t = ' '.join(L.split())
        if CONJ.search(t):
            continue
        m = GF.match(t)
        if not m:
            continue
        body = ATTR.sub('', m.group(1)).strip().rstrip(';').rstrip('.')
        # NOT the full OUT test here: it rejects anything containing "satisf", which is
        # precisely the shape this path exists to read
        if re.search(r'A\d{6}|Sum_|Prod_|Integral|hypergeom', body, re.I):
            continue
        A = implicit(body, d, off)
        if A is not None:
            return A
    return from_name(e)


# ---------------------------------------------------------------------------
# Two widenings, measured over the 380 P-recursive candidates: 146 of the refusals reference
# another sequence's generating function by A-number, and 44 carry a g.f. line the reader
# refuses -- several of those defining an abbreviation IMPLICITLY:
#
#     G.f.: z^3*g^2/((1+z+z^2)(1-3z+z^2)), where g=g(z) satisfies g = 1 + zg + z^2*g(g - 1).
#
# That g is still algebraic; it is just not written in closed form. Solving for it gives
# several branches and only one is the generating function, so the branch is chosen by the
# entry's own published terms -- which is the same check that has to be made anyway before any
# g.f. is used as a premise, and is what caught A116388.

SATISFIES = re.compile(
    r',?\s*where\s+([A-Za-z]\w*)\s*(?:=\s*\1\s*\([xz]\)\s*)?\s*satisfies\s*:?\s*(.+?)\s*\.?\s*$',
    re.I)

# Standard algebraic generating functions, by the A-number the corpus cites. Every one is
# VERIFIED against that entry's own published terms before use -- a table of constants written
# from memory is exactly the kind of thing this project has been burned by.
STANDARD = {
    'A000108': '(1-sqrt(1-4*x))/(2*x)',            # Catalan
    'A001006': '(1-x-sqrt(1-2*x-3*x**2))/(2*x**2)',  # Motzkin
    'A006318': '(1-x-sqrt(1-6*x+x**2))/(2*x)',     # large Schroeder
    'A001003': '(1+x-sqrt(1-6*x+x**2))/(4*x)',     # little Schroeder
    'A000045': 'x/(1-x-x**2)',                     # Fibonacci
    'A001764': None,                               # ternary trees: cubic, left out on purpose
}


def _series_ok(A, data, offset, N=10):
    try:
        s = sp.series(A, x, 0, N + offset + 1).removeO()
        e = sp.expand(s)
        got = [sp.nsimplify(e.coeff(x, k), rational=True) for k in range(offset, offset + N)]
    except Exception:
        return False
    if len(data) < N:
        N = len(data)
        got = got[:N]
    return all(sp.simplify(got[k] - data[k]) == 0 for k in range(N))


def standard(anum):
    """the standard g.f. for `anum`, verified against that entry's own terms, or None"""
    s = STANDARD.get(anum)
    if not s:
        return None
    import localentry as _LE
    e = _LE.get(anum)
    if not e:
        return None
    A = sp.sympify(s, locals={'x': x, 'sqrt': sp.sqrt})
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    return A if _series_ok(A, d, off) else None


def implicit(body, data, offset):
    """a g.f. whose abbreviation is defined by an algebraic equation, or None.

    The branch is chosen by the entry's published terms; if none of the branches reproduces
    them, the answer is None rather than a guess.
    """
    m = SATISFIES.search(body)
    if not m:
        return None
    sym, eq = m.group(1), m.group(2)
    main = body[:m.start()].strip().rstrip(',')
    main = LEAD.sub('', main).strip()
    if not main or OUT.search(main):
        return None
    g = sp.Symbol('_g')
    var = 'z' if ('z' in eq and 'x' not in eq) else 'x'
    loc = {var: x, sym: g, 'sqrt': sp.sqrt}
    if '=' not in eq:
        return None
    lhs, rhs = eq.split('=', 1)
    def prep(t):
        # the abbreviation juxtaposed with a bracket is MULTIPLICATION, not a function call:
        # "z^2*g(g - 1)" is z^2 * g * (g-1). sympify reads g(...) as a call and the equation
        # becomes nonsense, which is why every one of these was refused.
        return re.sub(r'\b%s\s*(?=\()' % re.escape(sym), sym + '*', _implicit(t))

    try:
        E = sp.sympify(prep(lhs), locals=loc) - sp.sympify(prep(rhs), locals=loc)
        M = sp.sympify(prep(main), locals=loc)
    except Exception:
        return None
    try:
        roots = sp.solve(sp.together(E), g)
    except Exception:
        return None
    for rt in roots:
        try:
            A = sp.simplify(M.subs(g, rt))
        except Exception:
            continue
        if _series_ok(A, data, offset):
            return A
    return None
