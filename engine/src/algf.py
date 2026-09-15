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
# A generating function the entry HEDGES is a conjecture whether or not it uses the word:
#
#     A075045  G.f.: seems to be (3*g-1)^(-2)*(1-g)^(-3) where g*(1-g)^2 = x.
#
# Proving one conjecture from another is not a proof, so the hedges belong here with
# `conjectural' and `empirical'. This was a soundness gap, not a missed read -- once the
# implicit-clause path below could parse that line, nothing else would have refused it.
CONJ = re.compile(r'conjectur|empirical|seems to be|appears to be|apparently|probably',
                  re.I)
# `O.g.f.' is the same line as `G.f.', and the corpus writes the separator as `=' as often
# as `:' -- A171853 is `G.f.=z^3*g/[...]', whose body then began with an equals sign and
# could not be parsed at all.
GF = re.compile(r'^\s*(?:o\.)?g\.f\.\s*[:=]?\s*(.*)$', re.I)
ATTR = re.compile(r'\s*[-—]\s*_[^_]+_,.*$')
LEAD = re.compile(r'^\s*[A-Za-z]\s*\(\s*[xz]\s*\)\s*=\s*')
OUT = re.compile(r'A\d{6}|Sum_|Prod_|satisf|continued fraction|Integral|\bE\(|hypergeom', re.I)


def _brackets(s):
    """[...] and {...} are GROUPING in this corpus, not a list and not a set.

    A171853 writes `z^3*g/[(1 + z)(1 - z + z^2 - 2z^2*g)(1 - z)^2]'. sympify reads that as a
    list and the line is refused for a reason that has nothing to do with the mathematics.
    Only converted when the brackets balance, so a genuine interval or index stays untouched.
    """
    if s.count('[') != s.count(']') or s.count('{') != s.count('}'):
        return s
    return s.replace('[', '(').replace(']', ')').replace('{', '(').replace('}', ')')


def _implicit(s):
    """the corpus's multiplication, written out"""
    s = _brackets(s)
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


# ---------------------------------------------------------------------------
# An entry sometimes states its g.f. at a DIFFERENT index origin from its own offset:
#
#     A026110, offset 4:  G.f.: z(1-z)M^5, with M the g.f. of the Motzkin numbers (A001006).
#
# That series is 1,4,15,50,... from z^1, and the entry's a(4) is 1 -- the function is right and
# the indexing is by three. Every consumer of this module assumes coefficient of x^n IS a(n),
# so the shift has to be removed here or the g.f. is unusable. It is not guessed: the shift is
# the one that reproduces the whole published run, which is the same evidence the exact check
# demands, so a misparse cannot survive it any more than before. When no shift fits, the
# expression is returned untouched and the caller's own data check records the refusal.

def _shift(A, data, N=9, W=6):
    """the exponent at which the published run begins, or None"""
    try:
        e = sp.expand(sp.series(A, x, 0, N + W + 1).removeO())
    except Exception:
        return None
    n = min(N, len(data))
    if not n:
        return None
    for sh in range(W + 1):
        try:
            if all(sp.simplify(sp.nsimplify(e.coeff(x, sh + k), rational=True) - data[k]) == 0
                   for k in range(n)):
                return sh
        except Exception:
            continue
    return None


def _normalize(A, data, offset):
    """A re-indexed so that the coefficient of x^n is a(n), or A unchanged"""
    if _series_ok(A, data, offset):
        return A
    sh = _shift(A, data)
    if sh is None or sh == offset:
        return A
    return sp.together(A * x ** (offset - sh))


def read(e, _depth=0):
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
        # "with p(x) = sqrt(...)" is the same clause as "where ...", and only `where` was
        # recognised. That mattered once the body was split on `=`: with the clause still
        # attached, the split offered `sqrt((1-x-4*x^2)/(1-x))` -- the DEFINITION of p -- as
        # the generating function, and on A026571 it was accepted as one. The data check
        # caught it, but the clause must be removed before the split, not after.
        mm = re.search(r',?\s*(?:where|with)\s+(.*)$', body, re.I)
        if mm:
            body = body[:mm.start()].strip().rstrip(',')
            for part in re.split(r',\s*(?=[A-Za-z]\w*\s*=)', mm.group(1)):
                # the abbreviation is often written as a function: "with p(x) = sqrt(...)"
                q = re.match(r'\s*([A-Za-z]\w*)\s*(?:\(\s*[xz]\s*\))?\s*=\s*(.*?)\s*\.?\s*$',
                             part)
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
        # An entry often gives two equal forms on one line:
        #     G.f.: A(x) = (1 - 4*x)^(-1/2) = 1F0(1/2;;4x).
        # The first is exactly what is wanted and the second is hypergeometric notation this
        # module does not read, and rejecting the LINE threw the first away with the second.
        # A000984 is cited three times by other entries and was unreachable for that reason.
        A = None
        for piece in body.split('='):
            piece = piece.strip()
            if not piece:
                continue
            # an abbreviation defined as p(x) appears in the body as p(x) too, which is an
            # application and not a product
            s = _implicit(piece)
            for nm_ in sub_exprs:
                s = re.sub(r'\b%s\s*\(\s*[xz]\s*\)' % re.escape(nm_), nm_, s)
            known = set(loc) | {'sqrt'}
            if set(re.findall(r'[A-Za-z]\w*', s)) - known:
                continue
            try:
                A = sp.sympify(s, locals=loc)
            except Exception:
                A = None
                continue
            break
        if A is None:
            continue
        # A `where' definition can be SELF-REFERENTIAL -- "where g = 1 + x*g^6" -- and
        # substituting it once leaves g free. The name check above passes because g is a key
        # of the substitution table, so the result looked like a generating function and was
        # then recorded as "the entry's stated g.f. does not generate its DATA", which blamed
        # A386368 for a defect of mine. Nothing with a free symbol other than x is a g.f.
        if A.free_symbols - {x}:
            continue
        if not A.has(x):
            continue
        _d = [int(v) for v in e['data'].split(',') if v.strip()]
        return _normalize(A, _d, int(e['offset'].split(',')[0]))
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
    # a g.f. written in terms of ANOTHER sequence's g.f., cited by A-number
    if not _depth:
        for L in e['formula'] + e['comment']:
            t = ' '.join(L.split())
            if CONJ.search(t):
                continue
            m = GF.match(t)
            if not m:
                continue
            body = ATTR.sub('', m.group(1)).strip().rstrip(';').rstrip('.')
            sub = cited(body)
            if not sub:
                continue
            main = re.split(r',?\s+(?:where|with)\b|,\s*(?=[A-Za-z]\s*\([xz]\)\s*g\.f\.)',
                            body, maxsplit=1)[0].strip().rstrip(',')
            # "6/(...)=1/(1-2*x-x*F(x))": the entry gives two equal forms; the one naming the
            # cited symbol is the one this path is for
            for part in reversed(main.split('=')):
                part = LEAD.sub('', part.strip())
                if not part or not any(k in part for k in sub):
                    continue
                loc = {'x': x, 'z': x, 'sqrt': sp.sqrt}
                loc.update(sub)
                # `S(-x)` is COMPOSITION, not a product: the cited g.f. evaluated at -x.
                # Treating it as multiplication -- which is what the corpus's implicit
                # notation looks like everywhere else -- silently gives a different function.
                ss, extra = _apply(_implicit(part), sub)
                if ss is None:
                    continue
                loc = dict(loc)
                loc.update(extra)
                if set(re.findall(r'[A-Za-z]\w*', ss)) - set(loc) - {'sqrt'}:
                    continue
                try:
                    A = sp.sympify(ss, locals=loc)
                except Exception:
                    continue
                if A.free_symbols - {x} or not A.has(x):
                    continue
                A = _normalize(A, d, off)
                if _series_ok(A, d, off):
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
    # Branch selection asks this question once per root, and all but one root is WRONG, so the
    # cost of the whole path is the cost of saying no. `simplify` on a cubic radical takes
    # minutes to say no; thirty digits says it in milliseconds. A numeric answer is only ever
    # used to REJECT -- acceptance still goes through the exact test below -- so nothing is
    # decided by floating point.
    try:
        for k in range(N):
            if abs(complex(sp.N(got[k] - data[k], 30))) > 1e-20:
                return False
    except Exception:
        pass
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


# A `where' clause that DEFINES the abbreviation by an equation rather than in closed form is
# the same object as `satisfies', and was refused for a notational reason only:
#
#     G.f.: z^3*g/[...], where g=g(z) satisfies g=1+zg+z^2*g(g-1).    -- read
#     G.f.: z^3*g/[...], where g=1+zg+z^2*g(g-1)                      -- refused
#     G.f.: (3*g-1)^(-2)*(1-g)^(-3) where g*(1-g)^2 = x               -- refused
#
# The second and third are algebraic equations for g exactly as the first is. The test for
# "this clause defines g implicitly" is not whether it says `satisfies': it is that g survives
# on BOTH sides of the `=', or that the left side is not g alone. Refusing them was the same
# defect as A386368 -- substituting such a clause once leaves g free, the result was rejected
# for having a free symbol, and the entry took the blame for the reader. Branch chosen by the
# entry's own published terms, like every other generating function this module admits.

CLAUSE = re.compile(r',?\s*(?:where|with)\s+(.+?)\s*\.?\s*$', re.I)
INITCOND = re.compile(r',\s*[A-Za-z]\w*\s*\(\s*0\s*\)\s*=\s*[^,]*$')


def _defining_equation(body):
    """(symbol, equation, main) for a `where'-clause that defines its symbol implicitly"""
    m = CLAUSE.search(body)
    if not m:
        return None
    clause = INITCOND.sub('', m.group(1)).strip().rstrip(',')
    main = LEAD.sub('', body[:m.start()].strip().rstrip(',')).strip()
    if not main or 'satisf' in clause.lower():
        return None            # `satisfies' is SATISFIES's business, not this one
    parts = [q.strip() for q in clause.split('=')]
    if len(parts) < 2 or not all(parts[:2]):
        return None
    lhs, rhs = parts[0], parts[1]
    q = re.match(r'\s*([A-Za-z]\w*)', lhs)
    if not q:
        return None
    sym = q.group(1)
    if sym in ('x', 'z') or sym not in main:
        return None
    if sym not in set(re.findall(r'[A-Za-z]\w*', rhs)) and lhs.strip() == sym:
        return None            # a closed-form definition; the ordinary path handles it
    return sym, f'{lhs}={rhs}', main


def implicit(body, data, offset):
    """a g.f. whose abbreviation is defined by an algebraic equation, or None.

    The branch is chosen by the entry's published terms; if none of the branches reproduces
    them, the answer is None rather than a guess.
    """
    m = SATISFIES.search(body)
    if m:
        sym, eq = m.group(1), m.group(2)
        main = LEAD.sub('', body[:m.start()].strip().rstrip(',')).strip()
    else:
        got = _defining_equation(body)
        if not got:
            return None
        sym, eq, main = got
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
    # Degree in g is the whole cost of this path. At 2 it is the quadratic formula and the
    # branch test is arithmetic; at 3 sympy spends minutes building Cardano radicals and then
    # minutes more deciding which one matches, and `holonomic.quadratic` -- the only route fast
    # enough to use the answer -- refuses anything but degree 2 regardless. So the cap costs no
    # result that could have been proved, and it is what keeps an entry from becoming a step
    # longer than the sweep's own alarm (defect 25).
    try:
        P = sp.Poly(sp.numer(sp.together(E)), g)
    except Exception:
        return None
    if P.degree() > 2:
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
        if A.free_symbols - {x}:
            continue
        if _series_ok(A, data, offset):
            return A
    return None


# ---------------------------------------------------------------------------
# 146 of the entries this reader refuses cite ANOTHER sequence's generating function:
#
#     G.f.: (1-x*S(-x))*x*S(-x), where S(x) is the g.f. of the large Schroeder numbers A006318.
#     G.f.: c(x)B(x)/(1+x), c(x) g.f. of A000108, B(x) g.f. of A000984.
#
# A hand table would reach the common ones and stop. `of` resolves the reference properly: the
# standard table first, then the cited entry's OWN g.f. read by this same module. Either way
# the result is verified against the CITED entry's published terms before it is used, so a
# wrong table row or a misparsed reference cannot become the premise of a proof -- which is
# the whole lesson of A116388.
#
# Depth 1 only. A chain of citations is a chain of opportunities to be wrong, and there is no
# evidence in this pool that it would pay.

REF = re.compile(
    r'\b([A-Za-z])\s*(?:\(\s*[xz]\s*\))?\s*(?:=|is)?\s*(?:the\s+)?(?:o\.)?g\.f\.\s*'
    r'(?:of|for)?\s*(?:the\s+)?(?:[a-z\s(]{0,40}?)\b(A\d{6})\b', re.I)


def of(anum, _depth=0):
    """the algebraic g.f. of `anum`, verified against its own published terms, or None"""
    A = standard(anum)
    if A is not None:
        return A
    if _depth:
        return None
    import localentry as _LE
    e = _LE.get(anum)
    if not e:
        return None
    A = read(e, _depth=1)
    if A is None:
        return None
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    return A if _series_ok(A, d, off) else None


def _apply(s, sub):
    """substitute each cited g.f. where it is APPLIED: S(-x) -> (S with x replaced by -x).

    Returns (string, extra locals). The substituted VALUE is carried out of band, as a fresh
    placeholder symbol per occurrence -- named gph1, gph2, ... and NOT _c1, because the
    leftover-name check scans for `[A-Za-z]\\w*` and reads `_c1` as `c1`, which is in no
    locals table and rejected every line this path produced. It was: round-tripping it back through a string introduced
    sympy's own constructor names -- Symbol, Add, Rational -- into the expression, and the
    leftover-name check that keeps foreign functions out then rejected every line this path
    was built to read.
    """
    extra = {}
    k = 0
    for name, A in sub.items():
        while True:
            m = re.search(r'\b%s\s*\(' % re.escape(name), s)
            if not m:
                break
            i = m.end() - 1
            depth, j = 0, i
            while j < len(s):
                if s[j] == '(':
                    depth += 1
                elif s[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j >= len(s):
                return None, None
            arg = s[m.end():j]
            try:
                val = A.subs(x, sp.sympify(arg, locals={'x': x, 'z': x, 'sqrt': sp.sqrt}))
            except Exception:
                return None, None
            k += 1
            ph = f'gph{k}'
            extra[ph] = val
            s = s[:m.start()] + ph + s[j + 1:]
        # a bare mention with no argument means the g.f. in x
        if re.search(r'\b%s\b' % re.escape(name), s):
            k += 1
            ph = f'gph{k}'
            extra[ph] = A
            s = re.sub(r'\b%s\b' % re.escape(name), ph, s)
    return s, extra


def cited(body):
    """{symbol: expression} for every 'S(x) is the g.f. of A######' in the line, or None"""
    out = {}
    for sym, anum in REF.findall(body):
        A = of(anum)
        if A is None:
            return None
        out[sym] = A
    return out or None
