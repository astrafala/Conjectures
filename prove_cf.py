#!/usr/bin/env python3
"""Run the closed-form test over every candidate; save results incrementally."""
import json, os, signal, sys
import sympy as sp
import closed_form as C
from prove_rec import parse_gf
from holonomic import taylor

x, n = sp.symbols('x n')
RES = "cf-results.json"


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def main():
    prev = json.load(open(RES)) if os.path.exists(RES) else {}
    cache = {}
    for a, v in C.entries():
        cache[a] = v
    json.dump(cache, open("cf-cache.json", "w"), indent=1, sort_keys=True)
    todo = [a for a in cache if a not in prev and not cache[a]["proof"]]
    only = [t for t in sys.argv[1:] if t.startswith("A")]
    if only:
        todo = only
    print(f"{len(todo)} to attempt")
    for a in todo:
        v = cache[a]
        rec = {"anum": a, "status": None}
        signal.alarm(int(os.environ.get("PER", "25")))
        try:
            f = C.parse_formula(v["conj"])
            # the entry's g.f., checked against its own published terms first
            A = None
            off = v["offset"]
            N = min(len(v["data"]) - 1, 10)
            for src in v["gfs"]:
                try:
                    cand = parse_gf(src, 'x', raw=src)
                    t = taylor(cand, off + N + 3)
                    if all(sp.simplify(t[off + k] - v["data"][k]) == 0 for k in range(N + 1)):
                        A = cand
                        rec["gf_src"] = src
                        break
                except Exception:
                    continue
            if A is None:
                rec["status"] = "posted g.f. does not reproduce the terms"
            else:
                F = C.gf_of(f, off)
                if sp.simplify(sp.together(F - A)) == 0:
                    rec.update(status="PROVED", formula=sp.sstr(f),
                               gf=sp.sstr(sp.simplify(A)), F=sp.sstr(F))
                else:
                    rec["status"] = "closed form does NOT match the g.f."
            print(f"{a}  {rec['status']}")
        except _TO:
            rec["status"] = "skip: timeout"
            print(f"{a}  timeout")
        except Exception as e:
            rec["status"] = f"skip: {type(e).__name__}: {str(e)[:55]}"
            print(f"{a}  {rec['status']}")
        finally:
            signal.alarm(0)
            prev[a] = rec
            json.dump(prev, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in prev.values() if r["status"] == "PROVED"), "of", len(prev))


if __name__ == "__main__":
    main()
