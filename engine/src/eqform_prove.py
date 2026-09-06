#!/usr/bin/env python3
"""Settle equation-form recurrence conjectures with the residual method.

"a(n) = RHS" is the same statement as "a(n) - RHS = 0", so once the equation is moved
to one side the existing machinery applies unchanged. Ordinary g.f. and exponential
g.f. are both handled; for an e.g.f. the shift a(n-i) becomes an i-fold derivative.
"""
import json, os, re, signal
import sympy as sp
from prove_rec import parse_gf, residual_poly
from holonomic import taylor
import logexp as le

x, n = sp.symbols('x n')
A_ = sp.Function('a')


def parse_eq(b):
    b = b.replace('^', '**')
    b = re.sub(r'(\d)\s*\(', r'\1*(', b)
    b = re.sub(r'(\d)\s*n\b', r'\1*n', b)
    b = re.sub(r'\)\s*\*?\s*a\(', r')*a(', b)
    b = re.sub(r'\)\s*\(', r')*(', b)
    b = re.sub(r'\bn\s*\(', r'n*(', b)
    lhs, rhs = b.split('=', 1)
    expr = sp.expand(sp.sympify(f'({lhs})-({rhs})', locals={'a': A_, 'n': n}))
    shifts = sorted({int(sp.simplify(n - f.args[0])) for f in expr.atoms(sp.Function)})
    if min(shifts) < 0:
        M = -min(shifts)
        expr = sp.expand(expr.subs(n, n - M))
        shifts = [s + M for s in shifts]
    order = max(shifts)
    ps = [sp.expand(expr.coeff(A_(n - i))) for i in range(order + 1)]
    rest = sp.expand(expr - sum(ps[i] * A_(n - i) for i in range(order + 1)))
    if sp.simplify(rest) != 0:
        raise ValueError('unparsed remainder')
    return ps


def egf_residual(A, ps):
    """Residual for an e.g.f.: re-index n = m+r so every shift becomes a derivative."""
    m = le.to_module(A)
    if m is None:
        return None, None
    coeffs, u, g = m
    B = le.residual_egf(coeffs, u, g, ps, n)
    ok, P = le.is_polynomial(B)
    if not ok:
        return None, None
    return (sp.Poly(P, x).total_degree() if P != 0 else 0), P


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def main():
    cache = json.load(open("eqform-cache.json"))
    out = json.load(open("eqform-results.json")) if os.path.exists("eqform-results.json") else {}
    for a, v in sorted(cache.items()):
        if a in out or not (v["gfs"] or v["egfs"]):
            continue
        raw, body = v["conjs"][0]
        rec = {"anum": a, "conj": raw, "status": None}
        signal.alarm(int(os.environ.get("PER", "120")))
        try:
            ps = parse_eq(body)
            off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
            A, mode = None, None
            for src, kind in [(s, "ogf") for s in v["gfs"]] + \
                             [(s, "egf") for s in v["egfs"]]:
                try:
                    G = parse_gf(src, 'x', raw=src)
                    base = taylor(G, off + N0 + 6)
                except Exception:
                    continue
                if kind == "egf":
                    base = [c * sp.factorial(k) for k, c in enumerate(base)]
                for sh in (0, 1, 2, -1, -2):
                    idx = [off + k - sh for k in range(N0 + 1)]
                    if any(i < 0 or i >= len(base) for i in idx):
                        continue
                    if all(sp.simplify(base[i] - v["data"][k]) == 0
                           for k, i in enumerate(idx)):
                        A = sp.together(x ** sh * G) if kind == "ogf" else G
                        if kind == "egf" and sh != 0:
                            continue
                        rec["shift"], rec["gf_src"], mode = sh, src, kind
                        break
                if A is not None:
                    break
            if A is None:
                rec["status"] = "no posted g.f. parses and matches the terms"
            else:
                deg, B = (residual_poly(A, ps) if mode == "ogf" else egf_residual(A, ps))
                if deg is None:
                    rec["status"] = "residual not polynomial"
                else:
                    rec.update(status="PROVED", degree=int(deg), B=sp.sstr(B),
                               order=len(ps) - 1, gf=sp.sstr(A), mode=mode)
            print(f"{a}  {rec['status']}" +
                  (f"  B={rec['B']}  valid for n>{rec['degree']}"
                   if rec["status"] == "PROVED" else ""))
        except _TO:
            rec["status"] = "skip: timeout"
            print(f"{a}  timeout")
        except Exception as e:
            rec["status"] = f"skip: {type(e).__name__}: {str(e)[:60]}"
            print(f"{a}  {rec['status']}")
        finally:
            signal.alarm(0)
            out[a] = rec
            json.dump(out, open("eqform-results.json", "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"), "of", len(out))


if __name__ == "__main__":
    main()
