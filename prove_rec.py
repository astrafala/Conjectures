#!/usr/bin/env python3
"""Run the holonomic argument over every collected recurrence conjecture.

For each entry we
  1. parse the posted G.f. into a sympy expression,
  2. CHECK it against the entry's published terms (a parse error is then caught,
     not silently proved),
  3. parse the conjectured recurrence into coefficients p_i(n),
  4. form the residual B(x) = sum_i x^i (p_i(theta+i) A)(x) and simplify it
     symbolically.

B == 0, or B a polynomial of degree d, proves the recurrence for all n > d.
Anything that does not simplify to a polynomial is reported as unresolved, never
as proved.
"""
import json, re, sys
import sympy as sp
from holonomic import x, n, theta, apply_poly_in_theta, taylor
import quadfield as qf
import multiquad as mq

A_ = sp.Function('a')


def catalan(t):
    return (1 - sp.sqrt(1 - 4 * t)) / (2 * t)


def motzkin(t):
    return (1 - t - sp.sqrt(1 - 2 * t - 3 * t ** 2)) / (2 * t ** 2)


def inline_defs(raw):
    """Pick up 'where C = <expr>' / 'C=(...)' definitions stated next to the g.f."""
    out = {}
    for m in re.finditer(r'\bwhere\s+([A-Za-z])\s*(?:\([a-z]\))?\s*=\s*([^,.;]+)', raw):
        out[m.group(1)] = m.group(2).strip()
    for m in re.finditer(r'\b([A-Z])\s*=\s*(\([^,;]*?\)/\([^,;]*?\))', raw):
        out.setdefault(m.group(1), m.group(2).strip())
    return out


def split_top_comma(s):
    d = 0
    for i, ch in enumerate(s):
        if ch in '([':
            d += 1
        elif ch in ')]':
            d -= 1
        elif ch == ',' and d == 0:
            return s[:i]
    return s


def normalise(s):
    s = s.strip()
    # trailing editorial markers that are not part of the expression
    s = re.sub(r'\.?\s*\(\s*End[^()]*\)\s*$', '', s, flags=re.I)
    s = re.sub(r'\s*\[\s*(From|Added|Corrected)[^\]]*\]\s*$', '', s, flags=re.I)
    s = s.strip().rstrip('.').strip()
    for cut in (' where ', ', where', ' - _', ';', ' for ', ' with ', ' and ', ' is ',
                ' satisfies', ' see ', ' Cf.', '(conjectured', ' conjectured',
                ' (empirical', ' empirical'):
        s = s.split(cut)[0]
    s = split_top_comma(s)
    # drop a leading "A(x) =" / "G(x) =" style label, keep the last right-hand side
    parts = re.split(r'(?<![<>=!])=(?!=)', s)
    if len(parts) > 1:
        cand = [q for q in parts if re.search(r'[xt]', q)]
        s = cand[-1] if cand else parts[-1]
    s = s.strip()
    s = s.replace('^', '**').replace('[', '(').replace(']', ')')
    s = s.replace('{', '(').replace('}', ')')
    s = s.replace(' ', '')
    # implicit multiplication, in safe patterns only
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)      # 2x -> 2*x ,  2( -> 2*(
    s = re.sub(r'\)([a-zA-Z0-9(])', r')*\1', s)       # )x  )2  )(  )sqrt
    s = re.sub(r'\*\*\*', '**', s)
    # protect function names before inserting implicit multiplication, or a rule
    # like "x followed by a letter" will shred exp -> ex*p, next -> ne*x*t, etc.
    FUNCS = ['arcsinh', 'arccosh', 'arctanh', 'arcsin', 'arccos', 'arctan',
             'binomial', 'hypergeom', 'LambertW', 'serreverse', 'Product',
             'ceiling', 'sqrt', 'sinh', 'cosh', 'tanh', 'asin', 'acos', 'atan',
             'floor', 'gamma', 'zeta', 'Sum', 'exp', 'log', 'sin', 'cos', 'tan',
             'abs', 'Pi']
    holes = {}
    for i, fname in enumerate(FUNCS):
        tok = f'@{i}@'
        if fname in s:
            s = s.replace(fname, tok)
            holes[tok] = fname
    s = re.sub(r'([xt])([a-zA-Z_])', r'\1*\2', s)
    for tok, fname in holes.items():
        s = s.replace(tok, fname)
    s = s.strip().rstrip('.').strip()
    while s.count('(') > s.count(')'):
        s += ')'
    while s.count(')') > s.count('(') and s.endswith(')'):
        s = s[:-1]
    return s


def parse_gf(s, var, raw=None):
    raw = raw if raw is not None else s
    defs = inline_defs(raw)
    s = normalise(s)
    # strip a leading parenthetical aside such as "(with offset 0 instead of 1):"
    s = re.sub(r'^\(([^()]*[A-Za-z][^()]*)\)\s*:\s*', '', s)
    if re.search(r'sum|prod|integral|series_reversion|d/dx|\.\.\.', s, re.I):
        raise ValueError('non-closed-form g.f.')
    loc = {'sqrt': sp.sqrt, 'c': catalan, 'C': catalan, var: x, 'x': x, 't': x, 'z': x,
           'exp': sp.exp, 'log': sp.log, 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
           'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh, 'Pi': sp.pi,
           'binomial': sp.binomial, 'floor': sp.floor, 'gamma': sp.gamma}
    if re.search(r'Motzkin', raw, re.I):
        loc['M'] = motzkin
        loc['m'] = motzkin
    for name, body in defs.items():
        try:
            val = sp.sympify(normalise(body), locals=dict(loc), rational=True)
            if not (val.free_symbols - {x}):
                loc[name] = val
        except Exception:
            pass
    e = sp.sympify(s, locals=loc, rational=True)
    e = sp.nsimplify(e, rational=True) if e.atoms(sp.Float) else e
    if e.free_symbols - {x}:
        raise ValueError(f'unresolved symbols {e.free_symbols}')
    return e


def parse_conj(s):
    # OEIS states these under a dozen labels; strip whichever preamble is present.
    # The order matters: the label comes first, the "D-finite with recurrence" phrase
    # after it, and either may be absent.  A stray letter between the two ("Conjecture:b
    # D-finite with recurrence") is a typo on the entry and is tolerated.
    body = s
    for pat in (r'^\s*Conjectur(?:e[sd]?|al)\b\s*\d*\s*(?:to\s+be)?\s*[:.]?\s*',
                r'^\s*[a-z]?\s*(?:Empirical|Conjectured|Conjectural)?\s*'
                r'D-finite\s+with\s+recurrence\s*[:.]?\s*',
                r'^\s*Conjectur(?:e[sd]?|al)\b\s*[:.]?\s*'):
        body = re.sub(pat, '', body, flags=re.I)
    # a stated change of indexing is not something to silently ignore
    if re.match(r'\s*\(\s*with\s+offset', body, re.I):
        raise ValueError('the conjecture restates the offset; indexing not assumed')
    body = body.split(' - _')[0]
    m = re.search(r'(.*?)=\s*0', body, re.S)
    if not m:
        raise ValueError('no "=0"')
    body = m.group(1)
    body = body.replace('^', '**')
    body = re.sub(r'(\d)\s*\(', r'\1*(', body)
    body = re.sub(r'(\d)\s*n\b', r'\1*n', body)
    body = re.sub(r'\)\s*\*?\s*a\(', r')*a(', body)
    body = re.sub(r'\)\s*\(', r')*(', body)
    body = re.sub(r'\bn\s*\(', r'n*(', body)
    expr = sp.expand(sp.sympify(body, locals={'a': A_, 'n': n}))
    order = 0
    for f in expr.atoms(sp.Function):
        d = sp.simplify(n - f.args[0])
        order = max(order, int(d))
    ps = []
    for i in range(order + 1):
        ps.append(sp.expand(expr.coeff(A_(n - i))))
    # nothing else may remain
    rest = sp.expand(expr - sum(ps[i] * A_(n - i) for i in range(order + 1)))
    if sp.simplify(rest) != 0:
        raise ValueError('unparsed remainder in recurrence')
    return ps


def residual_poly(A, ps, maxdeg=8):
    """Exact: returns (degree, B) if the residual is a polynomial, else (None, None)."""
    q = qf.to_quad(A)
    if q is not None:
        r = qf.residual(q, ps, n)
        ok, poly = qf.is_polynomial(r)
    else:
        m = mq.to_multi(A)
        if m is None:
            raise ValueError("g.f. not in a multiquadratic extension of Q(x)")
        coeffs, Ds = m
        r = mq.residual(coeffs, Ds, ps, n)
        ok, poly = mq.is_polynomial(r)
    if not ok:
        return None, None
    poly = sp.expand(poly)
    deg = sp.Poly(poly, x).total_degree() if poly != 0 else -1
    return deg, poly


import signal, os

class _TO(Exception):
    pass

def _alarm(sig, frm):
    raise _TO()

signal.signal(signal.SIGALRM, _alarm)


def _save(results):
    prev = json.load(open("rec-results.json")) if os.path.exists("rec-results.json") else {}
    prev.update(results)
    json.dump(prev, open("rec-results.json", "w"), indent=1, sort_keys=True)


def run(entries, verbose=True, per_entry=40):
    results = {}
    for a, v in sorted(entries.items()):
        rec = {"anum": a, "status": None}
        signal.alarm(per_entry)
        try:
            A = None
            off0 = v["offset"]
            N0 = min(len(v["data"]) - 1, 11)
            for gf_src in v["gfs"]:
                var = 't' if re.search(r'\bt\b', gf_src) and 'x' not in gf_src else 'x'
                try:
                    G = parse_gf(gf_src, var, raw=gf_src)
                except Exception:
                    continue
                try:
                    base = taylor(G, off0 + N0 + 6)      # expanded ONCE
                except Exception:
                    continue
                for sh in (0, 1, 2, -1, -2, 3, -3):
                    idx = [off0 + k - sh for k in range(N0 + 1)]
                    if any(i < 0 or i >= len(base) for i in idx):
                        continue
                    if all(sp.simplify(base[i] - v["data"][k]) == 0
                           for k, i in enumerate(idx)):
                        A = sp.together(x ** sh * G)
                        rec["shift"] = sh
                        rec["gf_src"] = gf_src
                        break
                if A is not None:
                    break
            if A is None:
                rec["status"] = "no posted g.f. parses and matches the terms"
                results[a] = rec
                if verbose:
                    print(f"{a}  SKIP  {rec['status']}")
                continue
            N = N0
            ps = parse_conj(v["conj"])
            deg, B = residual_poly(A, ps)
            if deg is None:
                rec["status"] = "residual not polynomial"
            else:
                rec["status"] = "PROVED"
                rec["degree"] = deg
                rec["B"] = sp.sstr(B)
                rec["order"] = len(ps) - 1
                rec["gf"] = sp.sstr(A)
                rec["terms_checked"] = N + 1
            results[a] = rec
            if verbose:
                extra = f"  B(x)={sp.sstr(B)}  valid for n>{deg}" if deg is not None else ""
                print(f"{a}  {rec['status']}{extra}")
        except _TO:
            rec["status"] = "skip: timeout"
            results[a] = rec
            if verbose:
                print(f"{a}  skip: timeout")
        except Exception as e:
            rec["status"] = f"skip: {type(e).__name__}: {str(e)[:60]}"
            results[a] = rec
            if verbose:
                print(f"{a}  {rec['status']}")
        finally:
            signal.alarm(0)
            _save({a: results.get(a, rec)})
    return results


if __name__ == "__main__":
    cache = json.load(open("rec-cache.json"))
    ents = {a: v for a, v in cache["seen"].items()
            if v and v["gfs"] and not v["proof"]}
    import os
    prev = json.load(open("rec-results.json")) if os.path.exists("rec-results.json") else {}
    args = sys.argv[1:]
    if args and args[0].startswith("--slice"):
        lo, hi = (int(t) for t in args[1].split(":"))
        keys = sorted(ents)[lo:hi]
        ents = {a: ents[a] for a in keys}
    elif args:
        ents = {a: v for a, v in ents.items() if a in args}
    ents = {a: v for a, v in ents.items() if a not in prev}
    res = run(ents)
    prev.update(res)
    res = prev
    json.dump(res, open("rec-results.json", "w"), indent=1, sort_keys=True)
    good = [a for a, r in res.items() if r["status"] == "PROVED"]
    print(f"\nPROVED: {len(good)} of {len(ents)}")
    print(" ".join(sorted(good)))
