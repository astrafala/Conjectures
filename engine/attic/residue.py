#!/usr/bin/env python3
"""The residue: open conjectures whose entry states facts NO parser here can read.

The pattern of every gain today is the same -- the mathematics was never the bottleneck,
the parsers were. 376 candidates were hidden by one regex; 18 came from never reading the
entry's name; 69 came from a mistyped "G.f f:" prefix. So the job is not to invent methods
but to drive this residue to nothing.

For every open conjectural recurrence, every fact line is offered to every parser in the
project. What no parser accepts is printed and classified, and the classification is what
says where to look next.
"""
import json, os, re, sys
sys.path.insert(0, ".")
from collections import Counter
import blocks, fsplit, cfparse, gfclean, sumparse, fzparse, diagonal, hypconv, xref
import universal

GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)
FINITE = re.compile(r"for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b|\bverified for\b|\bup to\b\s+n", re.I)
ATTRIB = re.compile(r"\s+-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d.*$")
GF = re.compile(r"^\s*(o\.|e\.)?g\.f\.\s*[:=]", re.I)
ROOT = "/home/user/oeis/oeisdata/seq"


def readable(q, data, off):
    """The name of the first parser that accepts this line, or None."""
    try:
        if cfparse.parse(q) is not None:
            return "closed form"
        if cfparse.parse(q, rounding=True) is not None:
            return "closed form (rounding)"
        if GF.match(q) and gfclean.candidates(q):
            return "generating function"
        if sumparse.parse(q) is not None:
            return "sum"
        if fzparse.parse(q, data, off) is not None:
            return "g.f. as f(z)"
        if diagonal.parse_extraction(q) is not None:
            return "coefficient extraction"
        if hypconv.parse(q) is not None:
            return "hypergeometric value"
        if xref.resolve(q) is not None:
            return "resolved through another entry"
        if universal._implicit(q, data, off) is not None:
            return "an algebraic relation for the g.f."
        if cfparse.parse(q, rounding=True) is not None:
            return "closed form (rounding)"
    except Exception:
        return None
    return None


def main():
    idx = json.load(open("open_index.json"))["open"]
    cnt = Counter()
    residue = []
    for a in sorted(idx):
        p = os.path.join(ROOT, a[:4], a + ".seq")
        if not os.path.exists(p):
            continue
        lines = [l for l in open(p, errors="ignore") if len(l) > 3 and l[0] == "%"]
        fn = [re.sub(r"^%.\s+A\d{6}\s*", "", l.rstrip()) for l in lines if l[1] in "FN"]
        try:
            data = [int(t) for t in
                    re.sub(r"^%.\s+A\d{6}\s*", "", next(l for l in lines if l[1] == "S")
                           .rstrip()).split(",") if t.strip()]
        except Exception:
            data = []
        off = 0
        for l in lines:
            if l[1] == "O":
                try:
                    off = int(re.sub(r"^%.\s+A\d{6}\s*", "", l.rstrip()).split(",")[0])
                except Exception:
                    pass
        cj = blocks.conjectured_lines(fn)
        known = [ATTRIB.sub("", l) for l in fn
                 if l.strip() not in cj and not GUESS.search(l) and not FINITE.search(l)]
        if not known:
            cnt["no fact line at all"] += 1
            continue
        parts = [q for l in known for q in [l] + fsplit.split(l)]
        hit = None
        for q in parts:
            hit = readable(q, data, off)
            if hit:
                break
        if hit:
            cnt["READABLE: " + hit] += 1
        else:
            cnt["residue: nothing any parser reads"] += 1
            residue.append({"anum": a, "known": known[:4], "conj": idx[a]["conj"][:2]})
    for k, v in cnt.most_common():
        print(f"{v:7d}  {k}")
    json.dump(residue, open("residue.json", "w"), indent=1)
    print(f"\nresidue written: {len(residue)} entries")


if __name__ == "__main__":
    main()
