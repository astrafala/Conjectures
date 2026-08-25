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

A_ = sp.Function('a')


def catalan(t):
    return (1 - sp.sqrt(1 - 4 * t)) / (2 * t)


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
    s = s.strip().rstrip('.').strip()
    for cut in (' where ', ', where', ' - _', ';', ' for ', ' with ', ' and ', ' is ',
                ' satisfies', ' see ', ' Cf.'):
        s = s.split(cut)[0]
    s = split_top_comma(s)
    # drop a leading "A(x) =" / "G(x) =" style label, keep the last right-hand side
    parts = re.split(r'(?<![<>=!])=(?!=)', s)
    if len(parts) > 1:
        cand = [q for q in parts if re.search(r'[xt]', q)]
        s = cand[-1] if cand else parts[-1]
    s = s.strip()
    s = s.replace('^', '**').replace('[', '(').replace(']', ')')
    s = s.replace(' ', '')
    # implicit multiplication, in safe patterns only
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)      # 2x -> 2*x ,  2( -> 2*(
    s = re.sub(r'\)([a-zA-Z0-9(])', r')*\1', s)       # )x  )2  )(  )sqrt
    s = re.sub(r'\*\*\*', '**', s)
    s = re.sub(r'([xt])([a-zA-Z_])', lambda m: m.group(0)
               if m.group(0) in ('sq',) else m.group(1) + '*' + m.group(2), s)
    s = s.replace('s*qrt', 'sqrt').replace('sq*rt', 'sqrt')
    return s


def parse_gf(s, var):
    s = normalise(s)
    if re.search(r'sum|prod|integral|series_reversion|d/dx|\.\.\.', s, re.I):
        raise ValueError('non-closed-form g.f.')
    loc = {'sqrt': sp.sqrt, 'c': catalan, var: x, 'x': x, 't': x}
    e = sp.sympify(s, locals=loc, rational=True)
    e = sp.nsimplify(e, rational=True) if e.atoms(sp.Float) else e
    if e.free_symbols - {x}:
        raise ValueError(f'unresolved symbols {e.free_symbols}')
    return e


def parse_conj(s):
    body = re.sub(r'^\s*Conjecture[:.]\s*', '', s, flags=re.I)
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
    if q is None:
        raise ValueError("g.f. not in a single quadratic extension of Q(x)")
    r = qf.residual(q, ps, n)
    ok, poly = qf.is_polynomial(r)
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
            for gf_src in v["gfs"]:
                var = 't' if re.search(r'\bt\b', gf_src) and 'x' not in gf_src else 'x'
                try:
                    cand = parse_gf(gf_src, var)
                except Exception:
                    continue
                off0 = v["offset"]
                N0 = min(len(v["data"]) - 1, 12)
                try:
                    tt = taylor(cand, N0 + max(off0, 0) + 2)
                    vals = tt[off0:off0 + N0 + 1]
                    if all(sp.simplify(vals[k] - v["data"][k]) == 0 for k in range(N0 + 1)):
                        A = cand
                        break
                except Exception:
                    continue
            if A is None:
                rec["status"] = "no posted g.f. parses and matches the terms"
                results[a] = rec
                if verbose:
                    print(f"{a}  SKIP  {rec['status']}")
                continue
            ok, bad, got = None, None, None
            off = v["offset"]
            N = min(len(v["data"]) - 1, 14)
            t = taylor(A, N + max(off, 0) + 2)
            series_vals = [sp.simplify(u) for u in t[off:off + N + 1]] if off >= 0 else None
            ok = series_vals is not None and all(
                sp.simplify(series_vals[k] - v["data"][k]) == 0 for k in range(N + 1))
            if not ok:
                rec["status"] = "gf does not match published terms"
                results[a] = rec
                if verbose:
                    print(f"{a}  SKIP  {rec['status']}")
                continue
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
