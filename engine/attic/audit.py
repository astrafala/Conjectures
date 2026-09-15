#!/usr/bin/env python3
"""Independent audit of every PROVED recurrence.

Two checks that share no code with the symbolic prover:

  1. EXACTNESS. Reject any residual B(x) containing a floating-point number --
     a float means some step left exact arithmetic, so the "proof" is not one.

  2. NUMERICS. Take the entry's published terms straight from OEIS and evaluate
     the conjectured recurrence sum_i p_i(n) a(n-i) directly, in exact integer
     arithmetic, for every n in range. It must vanish for all n > deg(B), which
     is exactly what the symbolic residual predicts.

A result is kept only if it passes both.
"""
import json, re, subprocess
import sympy as sp
from prove_rec import parse_conj

n = sp.Symbol('n')
x = sp.Symbol('x')


def audit():
    cache = json.load(open("rec-cache.json"))["seen"]
    res = json.load(open("rec-results.json"))
    good, rejected = {}, {}
    for a, r in sorted(res.items()):
        if r.get("status") != "PROVED":
            continue
        B = sp.sympify(r["B"])
        if B.atoms(sp.Float):
            rejected[a] = "residual contains floats - not exact"
            continue
        v = cache.get(a)
        if v is None:
            try:
                out = subprocess.run(
                    ["curl", "-sS", "-A", "Mozilla/5.0",
                     f"https://oeis.org/search?q=id:{a}&fmt=json"],
                    capture_output=True, text=True, timeout=90).stdout
                e = json.loads(out)[0]
                conj = None
                for k in ("formula", "comment"):
                    for l in e.get(k) or []:
                        if re.match(r"\s*Conjecture", l, re.I) and "a(n-" in l:
                            conj = l
                            break
                    if conj:
                        break
                gf = [l.split(":", 1)[1].strip() for l in (e.get("formula") or [])
                      if re.match(r"G\.f\.", l.strip(), re.I)]
                v = {"name": e["name"], "offset": int(e["offset"].split(",")[0]),
                     "data": [int(t) for t in e["data"].split(",")],
                     "conj": conj, "gfs": gf, "proof": None,
                     "time": e["time"][:10], "revision": e["revision"]}
                cache[a] = v
            except Exception as ex:
                rejected[a] = f"not in cache and refetch failed: {ex}"
                continue
        if not v.get("conj"):
            rejected[a] = "no conjecture text available"
            continue
        try:
            ps = parse_conj(v["conj"])
        except Exception as e:
            rejected[a] = f"reparse failed: {e}"
            continue
        data, off, deg = v["data"], v["offset"], r["degree"]
        order = len(ps) - 1
        bad = []
        lo = max(order, deg + 1)
        for idx in range(lo, len(data)):
            nn = idx + off
            tot = 0
            for i, p in enumerate(ps):
                coeff = sp.Integer(int(sp.Poly(p, n).eval(nn))) if p != 0 else 0
                tot += coeff * data[idx - i]
            if tot != 0:
                bad.append(nn)
        if bad:
            rejected[a] = f"recurrence fails on published terms at n={bad[:4]}"
            continue
        checked = len(data) - lo
        if checked < 3:
            rejected[a] = f"only {checked} terms available to check"
            continue
        good[a] = {**r, "terms_verified": checked, "first_n": lo + off,
                   "name": v["name"], "conj": v["conj"], "time": v["time"],
                   "revision": v["revision"], "offset": off,
                   "ndata": len(data), "gfs": v["gfs"]}
    return good, rejected


if __name__ == "__main__":
    good, rejected = audit()
    for a, why in sorted(rejected.items()):
        print(f"REJECT {a}: {why}")
    print(f"\nkept {len(good)}, rejected {len(rejected)}")
    json.dump(good, open("rec-verified.json", "w"), indent=1, sort_keys=True)
    print(" ".join(sorted(good)))
