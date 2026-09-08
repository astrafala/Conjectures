"""Explicit closed forms, as opposed to recurrences.

Many entries state ``Empirical: a(n) = (1/24)*n^4 - (1/12)*n^3 + ... '' or
``Empirical: a(n) = 16*7^n'' -- a formula for a(n), not a recurrence relating consecutive
terms. Such a claim is settled by the same residual test the recurrence papers use, because
every function of the form sum_j p_j(n) lambda_j^n satisfies a monic linear recurrence: the
one whose characteristic polynomial is prod_j (x - lambda_j)^(deg p_j + 1). So:

  1. read the closed form, and read off that annihilating polynomial q;
  2. prove the model satisfies q from some index on (Cayley--Hamilton, exactly as before);
  3. check a(n) = f(n) at deg(q) consecutive indices past that point.

Two sequences that satisfy the same monic recurrence and agree on deg(q) consecutive terms
agree from there on, since the recurrence determines every later term. Both steps are finite
and exact, so the claim is decided rather than tested.
"""
import re
from fractions import Fraction
import sympy

n = sympy.Symbol('n')
x = sympy.Symbol('x')

LINE = re.compile(r'^(?:Conjecture|Empirical)[^:]*:\s*a\(n\)\s*=\s*([^=]+)$', re.I)


def parse_line(L):
    """the closed form and the range the entry claims for it, or None."""
    t = L.strip()
    m = LINE.match(t)
    if not m:
        return None
    body = m.group(1).strip()
    if 'a(n' in body or 'a(k' in body or not re.search(r'\bn\b', body):
        return None
    body = re.sub(r'\s*-\s*_[^_]+_,.*$', '', body)          # attribution
    # An editorial note can also follow the formula as a SENTENCE rather than after a dash:
    # "Empirical: a(n) = (84 + 149*n + 36*n^2 + n^3) / 6. Corrected by _Colin Barker_, ..."
    # The formula there is perfectly readable; only the note made it unparsable, and the
    # entry was refused with "no readable closed form".
    body = re.sub(r'\.\s*(?:Corrected|Edited|Added|Amended|Rewritten|Simplified|Verified|'
                  r'Formula|Offset)\b.*$', '', body, flags=re.I)
    body = re.sub(r'\.\s*\(End\)\s*$', '', body).strip().rstrip('.')
    claimed = None
    m2 = re.search(r'\bfor\s+n\s*(>=|>)\s*(\d+)\s*$', body)
    if m2:
        claimed = int(m2.group(2)) + (0 if m2.group(1) == '>' else -1)
        body = body[:m2.start()].strip().rstrip(',').rstrip('.')
    m3 = re.match(r'^\(for\s+n\s*(>=|>)\s*(\d+)\):\s*(.*)$', t, re.I)
    # anything alphabetic other than the variable itself -- an A-number, floor, mod, sqrt --
    # is out of scope; an earlier version tested for two consecutive letters and so let
    # ``A000788(n-1)'' through, which then blew up inside the annihilator
    if re.search(r'[A-Za-z]', re.sub(r'\bn\b', '', body)):
        return None
    body = body.replace('^', '**')
    try:
        expr = sympy.sympify(body, locals={'n': n}, rational=True)
    except Exception:
        return None
    if not expr.has(n):
        return None
    return expr, claimed


def bases(expr):
    """{lambda: degree of its polynomial coefficient} for f = sum_j p_j(n) lambda_j^n."""
    e = sympy.expand(expr)
    mult = {}
    for t in sympy.Add.make_args(e):
        base, rest = sympy.Integer(1), sympy.Integer(1)
        for f in sympy.Mul.make_args(t):
            if f.is_Pow and f.exp.has(n):
                p = sympy.Poly(sympy.expand(f.exp), n)
                if p.degree() != 1:
                    return None
                a1 = p.all_coeffs()[0]
                if not (a1.is_Integer and a1 > 0):
                    return None
                b = f.base ** int(a1)
                if not b.is_Integer:
                    return None
                base *= b
            else:
                rest *= f
        if not rest.is_polynomial(n):
            return None
        d = sympy.Poly(rest, n).degree() if rest.has(n) else 0
        mult[base] = max(mult.get(base, -1), d)
    return mult


def annihilator(expr):
    """the monic polynomial q with q(shift) f = 0, as a list of integer recurrence
    coefficients [c_1..c_r] meaning a(m) = sum_i c_i a(m-i); None if not of the right shape."""
    mult = bases(expr)
    if mult is None:
        return None
    q = sympy.Integer(1)
    for b, d in mult.items():
        q *= (x - b) ** (d + 1)
    P = sympy.Poly(sympy.expand(q), x)
    co = P.all_coeffs()
    if co[0] != 1:
        return None
    if any(not c.is_Integer for c in co):
        return None
    r = len(co) - 1
    return {i: -int(co[i]) for i in range(1, r + 1)}, r


def value(expr, m):
    v = expr.subs(n, m)
    v = sympy.nsimplify(v) if not v.is_Rational else v
    return Fraction(int(sympy.numer(v)), int(sympy.denom(v)))
