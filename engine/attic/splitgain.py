#!/usr/bin/env python3
"""How much fact side does splitting multi-formula lines recover?

A %F line often carries several statements separated by full stops. Parsers read the line
whole and reject it. This counts, over every entry with a conjectural recurrence, the
entries that gain a parseable closed form or generating function purely from the split --
no new mathematics, only punctuation.
"""
import os, re, sys
sys.path.insert(0, ".")
from collections import Counter
import blocks, conjlines, cfparse, gfclean, fsplit

ROOT = "/home/user/oeis/oeisdata/seq"
GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)
FINITE = re.compile(r"for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b|\bverified for\b|\bup to\b\s+n", re.I)
ATTRIB = re.compile(r"\s+-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d.*$")
GF = re.compile(r"^\s*(o\.)?g\.f\.\s*[:=]", re.I)

cnt = Counter()
gained = []
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        a = "A" + fn[1:7]
        flines = [re.sub(r"^%.\s+A\d{6}\s*", "", l.rstrip("\n"))
                  for l in open(os.path.join(dd, fn), errors="ignore")
                  if len(l) > 3 and l[0] == "%" and l[1] == "F"]
        if not any(conjlines.is_recurrence(l) for l in flines):
            continue
        cnt["entries with a conjectural recurrence"] += 1
        conjraw = blocks.conjectured_lines(flines)
        known = [ATTRIB.sub("", l) for l in flines
                 if l.strip() not in conjraw and not GUESS.search(l) and not FINITE.search(l)]
        def usable(items):
            for l in items:
                if cfparse.parse(l) is not None:
                    return "closed form"
                if GF.match(l) and gfclean.candidates(l):
                    return "g.f."
            return None
        before = usable(known)
        after = before or usable([p for l in known for p in fsplit.split(l)])
        if before:
            cnt["  a parser already read one"] += 1
        elif after:
            cnt["  GAINED from the split: " + after] += 1
            gained.append((a, after))
        else:
            cnt["  still nothing"] += 1

for k, v in cnt.most_common():
    print(f"{v:7d}  {k}")
print("\nfirst gained:", " ".join(a for a, _ in gained[:30]))
import json; json.dump([a for a, _ in gained], open("splitgain.json", "w"))
