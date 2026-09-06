#!/usr/bin/env python3
"""Entries whose generating function is stated mid-line rather than as a "G.f.:" line.

The extractors all required the formula line to BEGIN with "G.f." Some entries write it
inside a sentence -- "Expansion of (1+x*C^3)*C^4, where C = ... is g.f. for Catalan
numbers", "Theorem: G.f. = ...", "G.f: x^2*M(x)^2/(...)" -- and those were invisible.
"""
import json, os, re

ROOT = "/home/user/oeis/oeisdata/seq"
LABEL = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
GF = re.compile(r"(?:O\.g\.f\.|G\.f\.?|Generating function)\s*[:=]\s*(.+)$", re.I)
EMPIRIC = re.compile(r"empirical|conjectur|guessed|apparent", re.I)


def main():
    have = set(json.load(open("scan-cache.json"))) | set(json.load(open("nogf-cache.json")))
    out = {}
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            a = "A" + fn[1:7]
            if a in have:
                continue
            txt = open(os.path.join(dd, fn), errors="ignore").read()
            if "Conjectur" not in txt or "a(n-" not in txt:
                continue
            F = {}
            for line in txt.split("\n"):
                if line.startswith("%"):
                    F.setdefault(line[1], []).append(
                        re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
            conjs = [l for tag in ("C", "F", "e") for l in F.get(tag, [])
                     if LABEL.match(l) and "a(n-" in l.replace(" ", "")
                     and "=0" in l.replace(" ", "")]
            if not conjs:
                continue
            gfs = []
            for l in F.get("F", []) + F.get("C", []) + F.get("N", []):
                if EMPIRIC.search(l) or LABEL.match(l):
                    continue
                m = GF.search(l)
                if m:
                    gfs.append(m.group(1).strip())
                m2 = re.match(r"Expansion of\s+(.+)$", l, re.I)
                if m2:
                    gfs.append(m2.group(1).strip())
            if not gfs:
                continue
            data = "".join(F.get("S", []) + F.get("T", []) + F.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            out[a] = {"name": (F.get("N") or [""])[0],
                      "offset": int((F.get("O") or ["0"])[0].split(",")[0]),
                      "data": terms, "conjs": conjs, "gfs": gfs, "egfs": [],
                      "settled": None, "time": "", "revision": 0}
    json.dump(out, open("midline-cache.json", "w"), indent=1, sort_keys=True)
    print(f"{len(out)} entries, {sum(len(v['conjs']) for v in out.values())} conjectures")


if __name__ == "__main__":
    main()
