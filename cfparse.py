#!/usr/bin/env python3
"""Read an OEIS closed-form line "a(n) = <expression in n>" into a sympy expression.

Only what is needed for the hypergeometric-term test: factorials written postfix (n!,
(n-1)!, (2*n)!), binomials in either spelling, powers, and polynomials. Anything with a
summation, another sequence, a floor, or a back-reference to a(n-i) is refused, because
those are somebody else's engine.
"""
import re
import sympy as sp

n = sp.Symbol('n')
LOCALS = {'binomial': sp.binomial, 'C': sp.binomial, 'factorial': sp.factorial,
          'gamma': sp.gamma, 'Gamma': sp.gamma, 'Pochhammer': sp.rf, 'n': n}

REFUSE = re.compile(
    r"Sum_|Product_|\bA\d{6}\b|floor|ceiling|\bmod\b|hypergeom|Integral|sqrt|"
    r"\ba\(n\s*-|\ba\(n\s*\+|~|\.\.\.|Stirling|\bround\b|\bif\b|\botherwise\b|"
    r"\blog\b|\bexp\b|Bessel|\bPi\b|\be\^|\bO\(", re.I)


def _postfix_factorials(s):
    """(expr)! and token! -> factorial(expr).  Applied innermost-first, repeatedly."""
    prev = None
    while prev != s:
        prev = s
        # a parenthesised group followed by !
        m = re.search(r"\(([^()]*)\)\s*!", s)
        if m:
            s = s[:m.start()] + f"factorial({m.group(1)})" + s[m.end():]
            continue
        # a bare token followed by !  (n!, 2!, k!) but not != and not !!
        m = re.search(r"(?<![!\w)])([A-Za-z_]\w*|\d+)\s*!(?!=)(?!!)", s)
        if m:
            s = s[:m.start()] + f"factorial({m.group(1)})" + s[m.end():]
    return s


def _ready(s):
    s = s.replace("^", "**")
    s = _postfix_factorials(s)
    s = re.sub(r"(\d)\s*\(", r"\1*(", s)
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"\)\s*([A-Za-z])", r")*\1", s)
    s = re.sub(r"(\d)\s*([A-Za-z])\b", r"\1*\2", s)
    # a name immediately followed by ( is a call, everything else is multiplication
    return s


def parse(line, rounding=False):
    """The right-hand side of a(n) = ..., or None.

    rounding=True additionally admits floor and ceiling. They are NOT a closed form on
    their own -- hyperterm.py cannot take a shift quotient through them -- so the default
    keeps refusing them. But parity.py resolves them exactly by substituting n = 2m and
    n = 2m+1, and 116 entries state their known side as C(n+3, ceiling(n/2))*... or as a
    two-branch a(2n) = ..., a(2n+1) = ... . Those are reachable, and were being refused
    here before any engine saw them.
    """
    m = re.match(r"\s*a\(n\)\s*=\s*(.+)$", line.strip(), re.I)
    if not m:
        return None
    b = m.group(1).split(" - _")[0]
    b = re.sub(r"\.?\s*\(\s*End[^()]*\)\s*$", "", b, flags=re.I)
    b = re.sub(r",?\s*\bfor\b\s+n\s*[<>=].*$", "", b, flags=re.I)
    b = re.sub(r",?\s*\bwith\b\s+a\(.*$", "", b, flags=re.I)
    b = re.sub(r",?\s*\bwhere\b\s.*$", "", b, flags=re.I)
    b = re.sub(r"\s*\[.*?\]\s*$", "", b)
    b = re.sub(r"\s*-\s+[A-Z][A-Za-z.'\- ]{2,30}(\([^)]*\))?,?\s*"
               r"([A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4})?\s*$", "", b)
    b = b.strip().rstrip(".").strip().rstrip(",").strip()
    # REFUSE blocks floor and ceiling before the KNOWN check ever runs, so lifting the
    # guard alone changed nothing; the words have to be exempted here too.
    bad = REFUSE.search(b)
    if rounding and bad and bad.group(0).lower() in ("floor", "ceiling"):
        bad = re.search(r"Sum_|Product_|\bA\d{6}\b|\bmod\b|hypergeom|Integral|sqrt"
                        r"|\ba\(n\s*-|\ba\(n\s*\+|~|\.\.\.|Stirling|\bround\b", b)
    if not b or bad:
        return None
    # a chained "a(n) = X = Y" states two formulas; take the first right-hand side
    parts = re.split(r"(?<![<>=!])=(?!=)", b)
    if len(parts) > 1:
        b = parts[0]
    try:
        e = sp.sympify(_ready(b), locals=dict(LOCALS))
    except Exception:
        return None
    if not isinstance(e, sp.Expr) or e.free_symbols - {n}:
        return None
    # an unknown function is not a closed form. sympify turns denominator(...),
    # numerator(...), sigma(...), pi(...) and anything else it does not recognise into an
    # undefined Function whose free symbols are just n, so the symbol check above lets
    # them through and the engine then reports "does not satisfy the recurrence" for a
    # conjecture it was never able to read in the first place.
    KNOWN = (sp.binomial, sp.factorial, sp.gamma, sp.rf, sp.ff, sp.Abs)
    if rounding:
        KNOWN = KNOWN + (sp.floor, sp.ceiling)
    for f in e.atoms(sp.Function):
        if not isinstance(f, KNOWN):
            return None
    if e.has(sp.Function('a')):
        return None
    return e


def matches(e, data, off, npts=8):
    """The formula must reproduce the entry's own terms before it is used."""
    seen = 0
    for i in range(min(len(data), npts + 4)):
        m = off + i
        try:
            v = sp.nsimplify(sp.simplify(e.subs(n, m)), rational=True)
        except Exception:
            return False
        if not v.is_number or v.has(sp.zoo, sp.nan, sp.oo):
            continue                     # a formula stated only for large n
        if sp.simplify(v - data[i]) != 0:
            return False
        seen += 1
    return seen >= 5


def align(e, data, off, span=4, npts=8):
    """e(n-s) for the shift s that reproduces the entry's terms, or None.

    OEIS formula lines are not always written in the entry's own indexing: A005560 has
    offset 2 and a formula whose value at n is a(n+2). Testing the formula as written
    would reject it, and using it as written would prove something about a different
    sequence, so the shift is searched for and then fixed.
    """
    for s in range(-span, span + 1):
        cand = e.subs(n, n - s) if s else e
        if matches(cand, data, off, npts):
            return cand, s
    return None, None


def first_valid(e, data, off, npts=14):
    """The smallest index from which the formula is defined and correct throughout.

    matches() tolerates indices where the formula is undefined, which is right -- entries
    often post a formula valid only from n = 1 while the offset is 0. But a theorem that
    claims the recurrence from n = offset + order onward reaches back to a(offset), so the
    builder needs to know where the formula actually starts being usable, not merely that
    it agrees somewhere.
    """
    good = None
    for i in range(min(len(data), npts) - 1, -1, -1):
        m = off + i
        try:
            v = sp.nsimplify(sp.simplify(e.subs(n, m)), rational=True)
        except Exception:
            break
        if not v.is_number or v.has(sp.zoo, sp.nan, sp.oo):
            break
        if sp.simplify(v - data[i]) != 0:
            break
        good = m
    return good
