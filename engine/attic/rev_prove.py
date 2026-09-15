#!/usr/bin/env python3
"""Settle recurrence conjectures on entries whose generating function is posted as a
series reversion, by eliminating the reversion and working in the resulting algebraic
function field."""
import json, os, re, signal
import sympy as sp
import reversion as rv
import algfield as af
from prove_rec import parse_conj
from holonomic import taylor

x, y = sp.symbols('x y')
n = sp.Symbol('n')
RES = os.environ.get("RES", "rev-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def branch(P, data, off, N):
    """The root of P whose expansion is the entry's own data."""
    for e in rv.branch_factors(P):
        try:
            roots = sp.solve(sp.Eq(e, 0), y)
        except Exception:
            continue
        for r in roots:
            try:
                base = taylor(r, off + N + 4)
            except Exception:
                continue
            if all(sp.simplify(base[off + k] - data[k]) == 0 for k in range(N + 1)):
                return e, r
    return None, None


def main():
    cache = json.load(open("scan-cache.json"))
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    todo = [(a, v) for a, v in sorted(cache.items())
            if not v["settled"] and any(rv.REV.search(g) for g in v["gfs"])]
    print(f"{len(todo)} entries with a reversion generating function")
    for a, v in todo:
        for ci, conj in enumerate(v["conjs"]):
            key = f"{a}#{ci}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "status": None}
            signal.alarm(int(os.environ.get("PER", "180")))
            try:
                ps = parse_conj(conj)
                off, N = v["offset"], min(len(v["data"]) - 1, 9)
                P = e = root = None
                for g in v["gfs"]:
                    P = rv.parse(g)
                    if P is None:
                        continue
                    e, root = branch(P, v["data"], off, N)
                    if e is not None:
                        rec["gf_src"], rec["gf"] = g, sp.sstr(root)
                        break
                if e is None:
                    rec["status"] = "no reversion branch reproduces the terms"
                else:
                    F = af.Field(e)
                    ok, B = F.is_polynomial(F.residual(sp.Poly(y, y), ps, n))
                    if ok:
                        deg = sp.Poly(B, x).total_degree() if B != 0 else -1
                        rec.update(status="PROVED", B=sp.sstr(B), degree=int(deg),
                                   order=len(ps) - 1, minpoly=sp.sstr(e), mode="ogf")
                        print(f"{key}  PROVED  B={rec['B']}  valid for n>{deg}")
                    else:
                        rec["status"] = "residual not polynomial"
            except _TO:
                rec["status"] = "skip: timeout"
            except Exception as ex:
                rec["status"] = f"skip: {type(ex).__name__}: {str(ex)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"), "of", len(out))


if __name__ == "__main__":
    main()
