#!/usr/bin/env python3
"""Recurrence conjectures on entries that give an explicit a(n) formula but no g.f.

The formula is accepted as the entry gives it (the same standing the posted G.f. has in
the other runs). If it is a combination of n^k r^n, its generating function is computed
exactly by closed_form.gf_of, and the recurrence is then settled by the usual residual
test. The computed g.f. is checked against the entry's published terms before use, so a
misparsed formula cannot turn into a proof.
"""
import json, os, re
import sympy as sp
from local_extract import parse, REC, PROOF
import closed_form as C

ROOT = "/home/user/oeis/oeisdata/seq"
x, n = sp.symbols('x n')


def main():
    out = {}
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in os.listdir(dd):
            if not fn.endswith(".seq"):
                continue
            f = parse(os.path.join(dd, fn))
            conj = None
            for tag in ("C", "F", "e"):
                for l in f.get(tag, []):
                    if REC.search(l) and ("=0" in l.replace(" ", "") or "= 0" in l):
                        if conj is None or len(l) > len(conj):
                            conj = l
            if not conj:
                continue
            if any(re.match(r"[GE]\.g?\.?f\.", l.strip(), re.I) for l in f.get("F", [])):
                continue
            forms = [l for l in f.get("F", [])
                     if re.match(r"a\(n\)\s*=", l.strip())
                     and not re.match(r"\s*Conjecture", l, re.I)
                     and "a(n-" not in l and "a(n+" not in l]
            if not forms:
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
                off = int((f.get("O") or ["0"])[0].split(",")[0])
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            gfs = []
            for src in forms:
                try:
                    fn_expr = C.parse_formula(src)
                    F = C.gf_of(fn_expr, off)
                    ser = sp.series(F, x, 0, off + 10).removeO()
                    ok = all(sp.simplify(sp.expand(ser).coeff(x, off + k) - terms[k]) == 0
                             for k in range(min(8, len(terms))))
                    if ok:
                        gfs.append(sp.sstr(sp.simplify(F)))
                        break
                except Exception:
                    continue
            if not gfs:
                continue
            proof = None
            for tag in ("C", "F", "H"):
                for l in f.get(tag, []):
                    if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I):
                        proof = l[:140]
            out["A" + fn[1:7]] = {"name": (f.get("N") or [""])[0], "offset": off,
                                  "data": terms, "conj": conj, "gfs": gfs,
                                  "proof": proof, "time": "", "revision": 0}
            print(f'  {"A"+fn[1:7]}  g.f. derived from its a(n) formula')
    json.dump(out, open("formula-cache.json", "w"), indent=1, sort_keys=True)
    print("entries whose g.f. was derived from an explicit a(n) formula:", len(out))


if __name__ == "__main__":
    main()
