#!/usr/bin/env python3
"""Run the e.g.f. residual test over the e.g.f.-only recurrence conjectures."""
import json, os, re, signal, sys
import sympy as sp
from prove_rec import parse_gf, parse_conj
from egf import residual_egf

x = sp.Symbol('x')
n = sp.Symbol('n')
RES = "egf-results.json"


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def egf_taylor(A, N):
    s = sp.series(A, x, 0, N + 2).removeO()
    e = sp.expand(s)
    return [sp.nsimplify(e.coeff(x, k)) * sp.factorial(k) for k in range(N + 1)]


def main():
    ents = json.load(open("egf-cache.json"))
    prev = json.load(open(RES)) if os.path.exists(RES) else {}
    only = [a for a in sys.argv[1:] if a.startswith("A")]
    todo = only or [a for a, v in ents.items() if not v["proof"] and a not in prev]
    for a in todo:
        v = ents[a]
        rec = {"anum": a, "status": None}
        signal.alarm(int(os.environ.get("PER", "20")))
        try:
            A = None
            off = v["offset"]
            N = min(len(v["data"]) - 1, 10)
            for src in v["gfs"]:
                try:
                    cand = parse_gf(src, 'x', raw=src)
                    t = egf_taylor(cand, off + N + 2)
                    if all(sp.simplify(t[off + k] - v["data"][k]) == 0 for k in range(N + 1)):
                        A = cand
                        rec["gf_src"] = src
                        break
                except Exception:
                    continue
            if A is None:
                rec["status"] = "no e.g.f. reproduces the terms"
            else:
                ps = parse_conj(v["conj"])
                ok, B = residual_egf(A, ps)
                if not ok:
                    rec["status"] = "residual not polynomial"
                else:
                    deg = sp.Poly(B, x).total_degree() if B != 0 else 0
                    rec.update(status="PROVED", B=sp.sstr(B), degree=deg,
                               order=len(ps) - 1, gf=sp.sstr(A), egf=True)
            print(f"{a}  {rec['status']}" + (f"  B={rec.get('B')}" if rec['status'] == 'PROVED' else ''))
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
    print("PROVED", sum(1 for v in prev.values() if v["status"] == "PROVED"), "of", len(prev))


if __name__ == "__main__":
    main()
