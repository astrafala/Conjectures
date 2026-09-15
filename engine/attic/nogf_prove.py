#!/usr/bin/env python3
"""Settle recurrence conjectures on entries that post no G.f. line but whose NAME is
"Expansion of <expr>".

For such an entry the generating function is not a claim to be checked: it is the
definition of the sequence. So the residual test applies with nothing assumed.
"""
import json, os, re, signal
import sympy as sp
from prove_rec import parse_gf, parse_conj, residual_poly
from holonomic import taylor
import logexp as le

x, n = sp.symbols('x n')
RES = os.environ.get("RES", "nogf-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def main():
    cache = json.load(open("nogf-cache.json"))
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    todo = [(f"{a}#{j}", a, c, v) for a, v in sorted(cache.items())
            for j, c in enumerate(v["conjs"]) if f"{a}#{j}" not in out]
    shard, nshard = int(os.environ.get("SHARD", "0")), int(os.environ.get("NSHARD", "1"))
    if nshard > 1:
        todo = [t for i, t in enumerate(todo) if i % nshard == shard]
    print(f"{len(todo)} conjectures to attempt")
    for key, a, conj, v in todo:
        rec = {"anum": a, "conj": conj, "name": v["name"], "status": None}
        signal.alarm(int(os.environ.get("PER", "60")))
        try:
            ps = parse_conj(conj)
            G = parse_gf(v["src"], 'x', raw=v["src"])
            off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
            base = taylor(G, off + N0 + 6)
            if v["egf"]:
                base = [c * sp.factorial(k) for k, c in enumerate(base)]
                shifts = (0,)
            else:
                shifts = (0, 1, 2, -1, -2, 3, -3)
            A = None
            for sh in shifts:
                idx = [off + k - sh for k in range(N0 + 1)]
                if any(i < 0 or i >= len(base) for i in idx):
                    continue
                if all(sp.simplify(base[i] - v["data"][k]) == 0
                       for k, i in enumerate(idx)):
                    A = sp.together(x ** sh * G) if not v["egf"] else G
                    rec["shift"] = sh
                    break
            if A is None:
                rec["status"] = "name expression does not reproduce the terms"
            elif not v["egf"]:
                deg, B = residual_poly(A, ps)
                if deg is None:
                    rec["status"] = "residual not polynomial"
                else:
                    rec.update(status="PROVED", degree=int(deg), B=sp.sstr(B),
                               order=len(ps) - 1, gf=sp.sstr(A), mode="ogf",
                               gf_src=v["src"])
            else:
                m = le.to_module(A)
                if m is None:
                    rec["status"] = "e.g.f. not in Q(x)[log,exp]"
                else:
                    coeffs, u, g = m
                    ok, P = le.is_polynomial(le.residual_egf(coeffs, u, g, ps, n))
                    if ok:
                        rec.update(status="PROVED", B=sp.sstr(P), mode="egf",
                                   degree=int(sp.Poly(P, x).total_degree()) if P != 0 else 0,
                                   order=len(ps) - 1, gf=sp.sstr(A), gf_src=v["src"])
                    else:
                        rec["status"] = "residual not polynomial"
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
