#!/usr/bin/env python3
"""Entries the equate engine can actually work on.

The first version of this counted 1214 entries and the engine could use almost none of
them: the filter matched "a(n) == 2 (mod n^3)" as a closed form (because "a(n) =" is a
prefix of "a(n) =="), matched floor formulas, and matched cross-entry identities that
need a second entry's generating function. Counting a pool the engine cannot touch is
worse than counting nothing, so this checks parseability and the presence of a usable
known side before including an entry.
"""
import json, os, re
import sympy as sp
import cfparse, gfclean
from ore_prove import PROVEN
from regf import entry, GFL, EGFL
from prove_rec import parse_gf

CONJ_GF = re.compile(r"^\s*Conjectur\w*\s*[:.]?\s*(o\.?g\.?f\.?|g\.?f\.?|e\.?g\.?f\.?)"
                     r"\s*[:.]", re.I)
# "a(n) =" but not "a(n) ==", and not a recurrence
CONJ_CF = re.compile(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*a\(n\)\s*=(?!=)", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct|sumrecursion|"
                     r"can be obtained|Zeilberger", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|it seems|probably", re.I)
ROOT = "/home/user/oeis/oeisdata/seq"


def strip_conj(l):
    return re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", l, flags=re.I)


def usable(a):
    try:
        F, data, off, name = entry(a)
    except Exception:
        return None
    if len(data) < 8:
        return None
    conj_cf = [l for l in F if CONJ_CF.match(l) and not SETTLED.search(l)
               and "a(n-" not in l.replace(" ", "")]
    conj_gf = [l for l in F if CONJ_GF.match(l) and not SETTLED.search(l)]
    good_cf = [l for l in conj_cf if cfparse.parse(strip_conj(l)) is not None]
    good_gf = []
    for l in conj_gf:
        for c in gfclean.candidates(strip_conj(l)):
            try:
                parse_gf(c, 'x', raw=c)
                good_gf.append(l)
                break
            except Exception:
                pass
    if not (good_cf or good_gf):
        return None
    # a known side: a stated recurrence, a posted g.f., or a posted closed form
    has_rec = any(PROVEN.match(l) and not GUESS.search(l)
                  and ("a(n-" in l.replace(" ", "") or "a(n+" in l.replace(" ", ""))
                  for l in F)
    has_gf = any((GFL.match(l) or EGFL.match(l)) and not GUESS.search(l) for l in F)
    has_cf = any(re.match(r"\s*a\(n\)\s*=(?!=)", l) and not GUESS.search(l)
                 and cfparse.parse(l) is not None for l in F)
    if not (has_rec or has_gf or has_cf):
        return None
    return {"anum": a, "conj_cf": len(good_cf), "conj_gf": len(good_gf),
            "known": ("recurrence" if has_rec else "g.f." if has_gf else "closed form")}


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
            if "Conjectur" not in txt:
                continue
            u = usable("A" + fn[1:7])
            if u:
                out.append(u)
    json.dump([u["anum"] for u in out], open("equate-todo.json", "w"), indent=1)
    json.dump(out, open("equate-cands.json", "w"), indent=1)
    from collections import Counter
    print(f"{len(out)} entries the engine can actually work on")
    print("known side:", Counter(u["known"] for u in out))
    print("conjectured closed forms:", sum(u["conj_cf"] for u in out),
          " conjectured g.f.s:", sum(u["conj_gf"] for u in out))


if __name__ == "__main__":
    main()
