#!/usr/bin/env python3
"""Settle recurrence conjectures on entries whose generating function is derived from a
stated relation to other entries."""
import json, os, re, signal
import sympy as sp
import relgf as R
from relgf import x, n
from prove_rec import parse_conj, residual_poly
from holonomic import taylor
import logexp as le
import algfield as af
import quadfield as qf
import multiquad as mq


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))
RES = os.environ.get("RES", "relgf-results.json")


def main():
    cache = json.load(open("relgf-cache.json"))
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    gcache = {}
    for a, v in sorted(cache.items()):
        for j, conj in enumerate(v["conjs"]):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": v["name"], "status": None}
            signal.alarm(int(os.environ.get("PER", "120")))
            try:
                ps = parse_conj(conj)
                off, N = v["offset"], min(len(v["data"]) - 1, 9)
                A = kind = used = None
                for rel in v["rels"]:
                    cand, k = R.derive(rel, off, gcache)
                    if cand is None:
                        continue
                    try:
                        base = taylor(cand, off + N + 4)
                        if k == "egf":
                            base = [c * sp.factorial(i) for i, c in enumerate(base)]
                    except Exception:
                        continue
                    if all(sp.simplify(base[off + i] - v["data"][i]) == 0
                           for i in range(N + 1)):
                        A, kind, used = cand, k, rel
                        break
                if A is None:
                    rec["status"] = "no relation yields a g.f. reproducing the terms"
                elif kind == "egf":
                    m = le.to_module(A)
                    if m is None:
                        rec["status"] = "derived e.g.f. not in Q(x)[log,exp]"
                    else:
                        ok, B = le.is_polynomial(le.residual_egf(m[0], m[1], m[2], ps, n))
                        if ok:
                            rec.update(status="PROVED", B=sp.sstr(B), mode="egf",
                                       degree=int(sp.Poly(B, x).total_degree()) if B != 0 else 0,
                                       order=len(ps) - 1, gf=sp.sstr(A), relation=used)
                        else:
                            rec["status"] = "residual not polynomial"
                else:
                    if qf.to_quad(A) is None and mq.to_multi(A) is None:
                        F, u = af.from_expr(A)
                        if F is None:
                            rec["status"] = "derived g.f. is not algebraic of low degree"
                        else:
                            ok, B = F.is_polynomial(F.residual(u, ps, n))
                            deg = (int(sp.Poly(B, x).total_degree()) if B != 0 else -1) if ok else None
                    else:
                        deg, B = residual_poly(A, ps)
                    if rec["status"] is None:
                        if deg is None:
                            rec["status"] = "residual not polynomial"
                        else:
                            rec.update(status="PROVED", B=sp.sstr(B), degree=int(deg),
                                       mode="ogf", order=len(ps) - 1, gf=sp.sstr(A),
                                       relation=used)
                if rec["status"] == "PROVED":
                    print(f"{key}  PROVED  B={rec['B']}  valid for n>{rec['degree']}")
            except _TO:
                rec["status"] = "skip: timeout"
            except Exception as e:
                rec["status"] = f"skip: {type(e).__name__}: {str(e)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"), "of", len(out))


if __name__ == "__main__":
    main()
