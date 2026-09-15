#!/usr/bin/env python3
"""Extract recurrence conjectures whose entry gives an E.g.f. but no G.f."""
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
            path = os.path.join(dd, fn)
            f = parse(path)
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
            egfs = [re.match(r"E\.g\.f\.\s*:?\s*(.+)", l.strip(), re.I).group(1).strip()
                    for l in f.get("F", []) if re.match(r"E\.g\.f\.", l.strip(), re.I)]
            if not egfs:
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            off = (f.get("O") or ["0"])[0].split(",")[0]
            proof = None
            for tag in ("C", "F", "H"):
                for l in f.get(tag, []):
                    if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I):
                        proof = l[:140]
            out["A" + fn[1:7]] = {
                "name": (f.get("N") or [""])[0], "offset": int(off) if off.lstrip('-').isdigit() else 0,
                "data": terms, "conj": conj, "gfs": egfs, "egf": True,
                "proof": proof, "time": "", "revision": 0}
    json.dump(out, open("egf-cache.json", "w"), indent=1, sort_keys=True)
    print("e.g.f.-only recurrence conjectures:", len(out),
          "| without a proof marker:", sum(1 for v in out.values() if not v["proof"]))


if __name__ == "__main__":
    main()
