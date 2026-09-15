#!/usr/bin/env python3
"""Recurrence conjectures whose generating function is stated in the entry NAME.

Many entries have no %F G.f. line but are named "Expansion of <expression>", which is
the same information. This pulls those out in the shape prove_rec already consumes.
"""
import json, os, re
from local_extract import parse, REC, PROOF

ROOT = "/home/user/oeis/oeisdata/seq"


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
            if any(re.match(r"G\.f\.", l.strip(), re.I) for l in f.get("F", [])):
                continue
            name = (f.get("N") or [""])[0]
            m = re.match(r"\s*Expansion of\s+(.+)", name, re.I)
            if not m:
                continue
            gf = m.group(1).strip()
            gf = re.split(r'\s+in powers of|\s*\.\s*$', gf)[0].strip().rstrip('.')
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
                off = int((f.get("O") or ["0"])[0].split(",")[0])
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            proof = None
            for tag in ("C", "F", "H"):
                for l in f.get(tag, []):
                    if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I):
                        proof = l[:140]
            out["A" + fn[1:7]] = {"name": name, "offset": off, "data": terms,
                                  "conj": conj, "gfs": [gf], "proof": proof,
                                  "time": "", "revision": 0}
    json.dump(out, open("name-cache.json", "w"), indent=1, sort_keys=True)
    print("entries with the g.f. in the name:", len(out),
          "| without a proof marker:", sum(1 for v in out.values() if not v["proof"]))


if __name__ == "__main__":
    main()
