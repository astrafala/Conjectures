#!/usr/bin/env python3
"""Settle recurrence conjectures posted in forward-shift form, a(n+k).

The residual method needs the standard backward form sum_i p_i(n) a(n-i). A
conjecture written with forward shifts is the same statement re-indexed: if the
largest shift is M, substituting n -> n - M turns a(n+k) into a(n-(M-k)). This does
the substitution symbolically, so nothing is assumed about how the line was written.
"""
import json, os, re, signal, sys
import sympy as sp
from prove_rec import parse_gf, residual_poly
from holonomic import taylor

x, n = sp.symbols('x n')
A_ = sp.Function('a')


def parse_conj_fwd(s):
    body = re.sub(r'^\s*Conjecture[:.]\s*', '', s, flags=re.I).split(' - _')[0]
    m = re.search(r'(.*?)=\s*0', body, re.S)
    if not m:
        raise ValueError('no "=0"')
    body = m.group(1).replace('^', '**')
    body = re.sub(r'(\d)\s*\(', r'\1*(', body)
    body = re.sub(r'(\d)\s*n\b', r'\1*n', body)
    body = re.sub(r'\)\s*\*?\s*a\(', r')*a(', body)
    body = re.sub(r'\)\s*\(', r')*(', body)
    body = re.sub(r'\bn\s*\(', r'n*(', body)
    expr = sp.expand(sp.sympify(body, locals={'a': A_, 'n': n}))
    shifts = sorted({int(sp.simplify(f.args[0] - n)) for f in expr.atoms(sp.Function)})
    M = max(shifts)
    if M <= 0:
        raise ValueError('not a forward-shift conjecture')
    expr = expr.subs(n, n - M)                       # re-index
    order = M - min(shifts)
    ps = [sp.expand(expr.coeff(A_(n - i))) for i in range(order + 1)]
    rest = sp.expand(expr - sum(ps[i] * A_(n - i) for i in range(order + 1)))
    if sp.simplify(rest) != 0:
        raise ValueError('unparsed remainder')
    return ps, M


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def main():
    cache = json.load(open("fwd-cache.json"))
    out = {}
    for a, v in sorted(cache.items()):
        if not v["gfs"]:
            continue
        for j, conj in enumerate(v["conjs"]):
            key = f"{a}#{j}"
            rec = {"anum": a, "conj": conj, "status": None}
            signal.alarm(int(os.environ.get("PER", "120")))
            try:
                ps, M = parse_conj_fwd(conj)
                A = None
                off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
                for src in v["gfs"]:
                    try:
                        G = parse_gf(src, 'x', raw=src)
                        base = taylor(G, off + N0 + 6)
                    except Exception:
                        continue
                    for sh in (0, 1, 2, -1, -2, 3, -3):
                        idx = [off + k - sh for k in range(N0 + 1)]
                        if any(i < 0 or i >= len(base) for i in idx):
                            continue
                        if all(sp.simplify(base[i] - v["data"][k]) == 0
                               for k, i in enumerate(idx)):
                            A = sp.together(x ** sh * G)
                            rec["shift"], rec["gf_src"] = sh, src
                            break
                    if A is not None:
                        break
                if A is None:
                    rec["status"] = "no posted g.f. parses and matches the terms"
                else:
                    deg, B = residual_poly(A, ps)
                    if deg is None:
                        rec["status"] = "residual not polynomial"
                    else:
                        rec.update(status="PROVED", degree=deg, B=sp.sstr(B),
                                   order=len(ps) - 1, gf=sp.sstr(A), reindex=M)
                print(f"{key}  {rec['status']}" +
                      (f"  B={rec['B']}" if rec["status"] == "PROVED" else ""))
            except _TO:
                rec["status"] = "skip: timeout"
                print(f"{key}  timeout")
            except Exception as e:
                rec["status"] = f"skip: {type(e).__name__}: {str(e)[:60]}"
                print(f"{key}  {rec['status']}")
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open("fwd-results.json", "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"), "of", len(out))


if __name__ == "__main__":
    main()
