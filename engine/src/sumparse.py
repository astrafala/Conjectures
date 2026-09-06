#!/usr/bin/env python3
"""Read an OEIS summation formula into (summand, lo, hi) with k as the index.

Three quarters of the creative-telescoping attempts died at "no usable hypergeometric
sum formula", and a census of what was thrown away showed most of it was notation, not
mathematics: the index is called i or j or m, the range is written "k>=0" or
"k, 0<=k<=n" or "i=0..n/2", or the line ends in "for n>0, with a(0)=1".

Nothing here decides anything. A formula that gets through is still checked against the
entry's own terms and the certificate is still verified, so a permissive parser can only
add candidates, never answers.
"""
import re
import sympy as sp

n, k = sp.symbols('n k')
LOCALS = {'binomial': sp.binomial, 'C': sp.binomial, 'factorial': sp.factorial,
          'gamma': sp.gamma, 'floor': sp.floor, 'ceiling': sp.ceiling,
          'n': n, 'k': k, 'oo': sp.oo}

# these cannot be hypergeometric in the summation variable, so they are refused in the
# summand -- but floor in the *range* is ordinary and stays allowed
BODY_REJECT = re.compile(
    r"Sum_|Product_|Stirling|A\d{6}|\bmod\b|!!|hypergeom|Integral|"
    r"\bprime\b|sigma\(|phi\(|tau\(|numdiv|floor|ceiling|\babs\b|\bsign\b|"
    r"Fibonacci|Lucas|Bernoulli|Euler\(|LambertW|\bround\b", re.I)

IDX = r"([a-zA-Z])"


def _falling(a, b):
    """P(n,k), the OEIS spelling of the falling factorial n(n-1)...(n-k+1)."""
    return sp.gamma(a + 1) / sp.gamma(a - b + 1)


def _clean(body):
    b = body.split(" - _")[0]
    b = re.sub(r"\.?\s*\(\s*End[^()]*\)\s*$", "", b, flags=re.I)
    # trailing conditions and initial-value clauses: "for n>0, with a(0)=1."
    b = re.sub(r",?\s*\bfor\b\s+n\s*[<>=].*$", "", b, flags=re.I)
    b = re.sub(r",?\s*\bwith\b\s+a\(.*$", "", b, flags=re.I)
    b = re.sub(r",?\s*\bwhere\b\s.*$", "", b, flags=re.I)
    b = re.sub(r"\s*\[.*?\]\s*$", "", b)
    return b.strip().rstrip('.').strip().rstrip(',').strip()


def _sympy_ready(s):
    s = s.replace("^", "**")
    s = re.sub(r"(\d)\s*\(", r"\1*(", s)
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"\)\s*([a-zA-Z])", r")*\1", s)
    s = re.sub(r"(\d)\s*([a-zA-Z])\b", r"\1*\2", s)
    return s


def _range(spec):
    """The index spec inside Sum_{...}: return (index letter, lo, hi) as strings."""
    spec = spec.strip()
    m = re.fullmatch(rf"{IDX}\s*=\s*(.+?)\s*\.\.\s*(.+)", spec)
    if m:
        return m.group(1), m.group(2), m.group(3)
    m = re.fullmatch(rf"{IDX}\s*>=\s*(.+)", spec)
    if m:
        return m.group(1), m.group(2), "oo"
    m = re.fullmatch(rf"{IDX}\s*>\s*(.+)", spec)
    if m:
        return m.group(1), f"({m.group(2)})+1", "oo"
    # "k, 0<=k<=n"  /  "k, k>=0"
    m = re.fullmatch(rf"{IDX}\s*,\s*(.+)", spec)
    if m:
        i, cond = m.group(1), m.group(2).strip()
        c = re.fullmatch(rf"(.+?)\s*<=\s*{re.escape(i)}\s*<=\s*(.+)", cond)
        if c:
            return i, c.group(1), c.group(2)
        c = re.fullmatch(rf"{re.escape(i)}\s*>=\s*(.+)", cond)
        if c:
            return i, c.group(1), "oo"
    return None


def parse(src):
    """(F, lo, hi) with the index renamed to k, or None."""
    m = re.match(r"a\(n\)\s*=\s*Sum_\{([^{}]*)\}\s*(.+)$", src.strip(), re.I)
    if not m:
        return None
    rng = _range(m.group(1))
    if rng is None:
        return None
    idx, lo_s, hi_s = rng
    if idx == 'n':
        return None
    body = _clean(m.group(2))
    if not body or BODY_REJECT.search(body):
        return None
    # a second Sum_ further along the line means a double sum, not our business
    if re.search(r"\bSum_", body, re.I):
        return None
    i = sp.Symbol(idx)
    loc = dict(LOCALS)
    loc[idx] = i
    loc['P'] = sp.Function('P')
    try:
        F = sp.sympify(_sympy_ready(body), locals=loc)
        # P(a,b) is the falling factorial in OEIS formula lines
        F = F.replace(sp.Function('P'), _falling)
        # OEIS writes an integer-division upper limit as n/2, meaning floor(n/2)
        lo = sp.sympify(_sympy_ready(lo_s), locals=loc)
        hi = sp.sympify(_sympy_ready(hi_s), locals=loc)
    except Exception:
        return None
    if not all(isinstance(e, sp.Expr) for e in (F, lo, hi)):
        return None          # e.g. a comma inside the range spec sympifies to a list
    # OEIS writes an integer-division limit as n/2, meaning floor(n/2); a limit that is
    # already an integer polynomial in n is left alone
    def _int_limit(e):
        if e in (sp.oo, -sp.oo):
            return e
        try:
            p = sp.Poly(e, n)
        except sp.PolynomialError:
            return sp.floor(e)
        return e if all(c.is_Integer for c in p.all_coeffs()) else sp.floor(e)
    hi, lo = _int_limit(hi), _int_limit(lo)
    if F.free_symbols - {n, i} or (lo.free_symbols | hi.free_symbols) - {n}:
        return None
    if i not in F.free_symbols:
        return None
    if i != k:
        F, lo, hi = (e.subs(i, k) for e in (F, lo, hi))
    if F.has(sp.floor) or F.has(sp.ceiling):
        return None
    return F, lo, hi


def evaluate(F, lo, hi, nn, cap=400):
    """The sum at n = nn, as an exact rational, or None.

    An unbounded upper limit is allowed only when the terms actually stop: the tail is
    required to be identically zero past the last nonzero term, which is what makes the
    sum finite and the telescoping legitimate.
    """
    try:
        k0 = int(lo.subs(n, nn))
    except Exception:
        return None
    if hi == sp.oo:
        tot, zeros, kk = sp.Integer(0), 0, k0
        while kk < k0 + cap and zeros < 12:
            try:
                v = sp.nsimplify(sp.simplify(F.subs({n: nn, k: kk})), rational=True)
            except Exception:
                return None
            if not v.is_number:
                return None
            tot += v
            zeros = zeros + 1 if v == 0 else 0
            kk += 1
        return tot if zeros >= 12 else None
    try:
        k1 = int(hi.subs(n, nn))
    except Exception:
        return None
    if k1 - k0 > cap:
        return None
    tot = sp.Integer(0)
    for kk in range(k0, k1 + 1):
        try:
            v = F.subs({n: nn, k: kk})
        except Exception:
            return None
        tot += v
    return sp.nsimplify(sp.simplify(tot), rational=True)
