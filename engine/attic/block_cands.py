#!/usr/bin/env python3
"""Entries with a conjecture inside a block that the equate engine could reach.

The block contents are conjectural, so they are excluded from the known side; an entry
qualifies only if something OUTSIDE the blocks is stated as fact and can be read.
"""
import json, os, re
import blocks, cfparse, gfclean
from ore_prove import PROVEN
from regf import entry, GFL, EGFL
from prove_rec import parse_gf

ROOT = "/home/user/oeis/oeisdata/seq"
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct|Theorem", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|probably", re.I)
GF = re.compile(r"^\s*(o\.?)?g\.?f\.?\s*[:.]|^\s*e\.?g\.?f\.?\s*[:.]", re.I)
CF = re.compile(r"^\s*a\(n\)\s*=(?!=)")


def usable(a):
    try:
        F, data, off, name = entry(a)
    except Exception:
        return None
    if len(data) < 8:
        return None
    if any(SETTLED.search(l) for l in F):
        return None                      # something on the entry already settles it
    conj = blocks.conjectured_lines(F)
    if not conj:
        return None
    tgt = [s for s in conj
           if (GF.match(s) and any(True for c in gfclean.candidates(s)))
           or (CF.match(s) and "a(n-" not in s.replace(" ", ""))]
    if not tgt:
        return None
    outside = [l for l in F if l.strip() not in conj and not GUESS.search(l)]
    has_rec = any(PROVEN.match(l) and ("a(n-" in l.replace(" ", "")
                                       or "a(n+" in l.replace(" ", ""))
                  for l in outside)
    has_gf = any(GFL.match(l) or EGFL.match(l) for l in outside)
    has_cf = any(CF.match(l) and cfparse.parse(l) is not None for l in outside)
    if not (has_rec or has_gf or has_cf):
        return None
    return {"anum": a, "targets": len(tgt),
            "known": "recurrence" if has_rec else "g.f." if has_gf else "closed form"}


def main():
    out = []
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            txt = open(os.path.join(dd, fn), errors="ignore").read()
            if "Conjectur" not in txt or "Start" not in txt:
                continue
            u = usable("A" + fn[1:7])
            if u:
                out.append(u)
    json.dump([u["anum"] for u in out], open("block-todo.json", "w"), indent=1)
    from collections import Counter
    print(f"{len(out)} entries with a block conjecture and a usable known side")
    print("known side:", Counter(u["known"] for u in out))
    print("conjectured statements to attack:", sum(u["targets"] for u in out))


if __name__ == "__main__":
    main()
