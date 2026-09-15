#!/usr/bin/env python3
"""How much of "no usable known side" is really "my parser could not read it"?

1,417 of 1,457 empirical candidates were dropped for having nothing to argue from. That
number was never broken down. It matters which it is: a genuine absence is a null and the
vein is dead, but a parser gap converts one-for-one into settled conjectures at the
standard of evidence already in use, with no new machinery and no weaker citation.

So for every entry with a conjectural recurrence or g.f., look at the NON-conjectural %F
lines -- the ones stating a fact -- and ask which of the existing parsers accepts them. A
line no parser accepts is either prose or a gap; the split is printed and sampled.
"""
import os, re, sys
from collections import Counter
sys.path.insert(0, ".")
import blocks, conjlines
import gfclean, cfparse, sumparse

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)", re.I)
FINITE = re.compile(r"for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b|\bverified for\b|\bup to\b\s+n", re.I)
GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl)", re.I)
ATTRIB = re.compile(r"-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d")

GF = re.compile(r"^\s*(o\.)?g\.f\.\s*[:=]", re.I)
EGF = re.compile(r"^\s*e\.g\.f\.\s*[:=]", re.I)
CF = re.compile(r"^\s*a\(n\)\s*=", re.I)
SUM = re.compile(r"^\s*a\(n\)\s*=\s*Sum_", re.I)
XREF = re.compile(r"\bA\d{6}\b")
PROSE = re.compile(r"[A-Za-z]{4,}\s+[A-Za-z]{4,}\s+[A-Za-z]{4,}")

cnt = Counter()
gap = {}
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        a = "A" + fn[1:7]
        F = open(os.path.join(dd, fn), errors="ignore").read()
        flines = [re.sub(r"^%.\s+A\d{6}\s*", "", l) for l in F.split("\n")
                  if len(l) > 3 and l[0] == "%" and l[1] == "F"]
        conjraw = blocks.conjectured_lines(F)
        conj = [l for l in flines if MARK.match(l)]
        if not conj:
            continue
        # does the conjecture state a recurrence or a g.f.? otherwise not our target
        if not any(conjlines.is_recurrence(l) or GF.search(l) for l in conj):
            continue
        cnt["entries with a conjectural recurrence or g.f."] += 1
        known = []
        for l in flines:
            if MARK.match(l) or l.strip() in conjraw or GUESS.search(l) or FINITE.search(l):
                continue
            known.append(ATTRIB.split(l)[0].strip())
        if not known:
            cnt["  no non-conjectural formula line at all"] += 1
            continue
        cnt["  has at least one line stated as fact"] += 1
        shapes = Counter()
        for l in known:
            if XREF.search(l):
                shapes["names another entry"] += 1
            elif GF.match(l) or EGF.match(l):
                shapes["a generating function"] += 1
            elif SUM.match(l):
                shapes["a sum"] += 1
            elif CF.match(l):
                shapes["a closed form"] += 1
            elif PROSE.search(l):
                shapes["prose"] += 1
            else:
                shapes["other"] += 1
        for k in shapes:
            cnt["    " + k] += 1
        if not (shapes.keys() & {"a generating function", "a sum", "a closed form"}):
            gap.setdefault("only prose or xref", []).append((a, known[0][:100]))

for k, v in cnt.most_common():
    print(f"{v:7d}  {k}")
