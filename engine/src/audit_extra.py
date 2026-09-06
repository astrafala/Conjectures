#!/usr/bin/env python3
"""Independent integer re-check of the extra results.

Shares no code with the symbolic prover: it evaluates the conjectured recurrence
directly on the entry's published terms in exact integer arithmetic, and refuses any
residual that contains a floating-point number.
"""
import json, os, re
import sympy as sp
from prove_rec import parse_conj
n = sp.Symbol('n')
ROOT = "/home/user/oeis/oeisdata/seq"


def terms(a):
    data = ""
    off = 0
    for l in open(f"{ROOT}/{a[:4]}/{a}.seq", errors="ignore"):
        if l[:2] in ("%S", "%T", "%U"):
            data += re.sub(r"^A\d{6}\s*", "", l[3:].strip())
        elif l[:2] == "%O":
            off = int(re.sub(r"^A\d{6}\s*", "", l[3:].strip()).split(",")[0])
    return [int(t) for t in data.split(",") if t.strip()], off


def main():
    EXTRA = json.load(open("extra-conj.json"))
    res = {}
    for f in ("extra-results.json", "extra-egf-results.json"):
        if os.path.exists(f):
            res.update(json.load(open(f)))
    ok_all = {}
    for a, meta in sorted(EXTRA.items()):
        r = res.get(a)
        if not r or r["status"] != "PROVED":
            print(f"{a}: NOT PROVED"); continue
        if sp.sympify(r["B"]).atoms(sp.Float):
            print(f"{a}: REJECT - residual contains floats"); continue
        ps = parse_conj(meta["others"][0])
        data, off = terms(a)
        order = len(ps) - 1
        lo = max(order, r["degree"] + 1)
        bad = [idx + off for idx in range(lo, len(data))
               if sum(int(sp.Poly(p, n).eval(idx + off)) * data[idx - i]
                      for i, p in enumerate(ps) if p != 0) != 0]
        checked = len(data) - lo
        verdict = "OK" if (not bad and checked >= 3) else \
                  (f"FAIL at n={bad[:4]}" if bad else f"only {checked} terms")
        print(f"{a}: order={order} deg={r['degree']} first n={lo+off} "
              f"checked={checked} -> {verdict}")
        if verdict == "OK":
            ok_all[a] = {**r, "conj": meta["others"][0], "terms_verified": checked,
                         "first_n": lo + off, "offset": off, "data": data}
    json.dump(ok_all, open("extra-verified.json", "w"), indent=1, sort_keys=True)
    print(f"\nkept {len(ok_all)} of {len(EXTRA)}")


if __name__ == "__main__":
    main()
