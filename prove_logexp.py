#!/usr/bin/env python3
"""Settle recurrence conjectures whose generating function is transcendental,
by working in the differential module Q(x)[log(u), exp(g)] instead of a field.
"""
import json, os, re, signal, sys
import sympy as sp
import logexp as le
from prove_rec import parse_gf, parse_conj

x, n = sp.symbols('x n')
RES = "logexp-results.json"


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def taylor_egf(A, N):
    s = sp.series(A, x, 0, N + 2).removeO()
    e = sp.expand(s)
    return [sp.nsimplify(e.coeff(x, k)) * sp.factorial(k) for k in range(N + 1)]


def taylor_ogf(A, N):
    s = sp.series(A, x, 0, N + 2).removeO()
    e = sp.expand(s)
    return [sp.nsimplify(e.coeff(x, k)) for k in range(N + 1)]


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "egf"
    cache = json.load(open("egf-cache.json" if which == "egf" else "rec-cache.json"))
    if which != "egf":
        cache = {a: v for a, v in cache["seen"].items() if v}
    prev = json.load(open(RES)) if os.path.exists(RES) else {}
    todo = [a for a, v in cache.items() if not v.get("proof") and a not in prev]
    print(f"{len(todo)} to attempt ({which})")
    for a in todo:
        v = cache[a]
        rec = {"anum": a, "mode": which, "status": None}
        signal.alarm(int(os.environ.get("PER", "30")))
        try:
            A = None
            off = v["offset"]
            N = min(len(v["data"]) - 1, 9)
            tay = taylor_egf if which == "egf" else taylor_ogf
            for src in v["gfs"]:
                try:
                    cand = parse_gf(src, 'x', raw=src)
                    if not (cand.has(sp.log) or cand.has(sp.exp)):
                        continue          # algebraic: already handled elsewhere
                    t = tay(cand, off + N + 2)
                    if all(sp.simplify(t[off + k] - v["data"][k]) == 0 for k in range(N + 1)):
                        A = cand
                        rec["gf_src"] = src
                        break
                except Exception:
                    continue
            if A is None:
                rec["status"] = "no transcendental g.f. reproduces the terms"
            else:
                m = le.to_module(A)
                if m is None:
                    rec["status"] = "not in Q(x)[log,exp]"
                else:
                    coeffs, u, g = m
                    ps = parse_conj(v["conj"])
                    B = (le.residual_egf if which == "egf" else le.residual_ogf)(
                        coeffs, u, g, ps, n)
                    ok, P = le.is_polynomial(B)
                    if ok:
                        deg = sp.Poly(P, x).total_degree() if P != 0 else 0
                        rec.update(status="PROVED", B=sp.sstr(P), degree=int(deg),
                                   order=len(ps) - 1, gf=sp.sstr(A))
                    else:
                        rec["status"] = "residual not polynomial"
            print(f"{a}  {rec['status']}" +
                  (f"  B={rec.get('B')}" if rec["status"] == "PROVED" else ""))
        except _TO:
            rec["status"] = "skip: timeout"
            print(f"{a}  timeout")
        except Exception as e:
            rec["status"] = f"skip: {type(e).__name__}: {str(e)[:50]}"
            print(f"{a}  {rec['status']}")
        finally:
            signal.alarm(0)
            prev[a] = rec
            json.dump(prev, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in prev.values() if r["status"] == "PROVED"), "of", len(prev))


if __name__ == "__main__":
    main()
