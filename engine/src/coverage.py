#!/usr/bin/env python3
"""What conjectural statements exist that the word "Conjecture" would never find?

Three blind spots to measure, not guess at:

  1. TAGS. Everything here reads %F, %C and %e. Conjectures could also sit in %N (the
     name), %D or %H.
  2. WRAPPING. OEIS breaks long lines across several records with the same tag. Half a
     conjecture read as a whole one is worse than none.
  3. WORDING. "Conjecture" is not the only way to say it. "Empirical g.f.:",
     "It appears that", "Apparently", "Probably", "seems to be" are all used, and Colin
     Barker's thousands of fitted generating functions are labelled "Empirical".
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
MARKERS = [
    (re.compile(r"^\s*Conjectur", re.I), "Conjecture..."),
    (re.compile(r"^\s*Empirical", re.I), "Empirical..."),
    (re.compile(r"^\s*(It )?appears that", re.I), "(It) appears that"),
    (re.compile(r"^\s*Apparently\b", re.I), "Apparently"),
    (re.compile(r"^\s*Probably\b", re.I), "Probably"),
    (re.compile(r"^\s*It seems", re.I), "It seems"),
    (re.compile(r"^\s*(Presumably|Seemingly)\b", re.I), "Presumably / Seemingly"),
    (re.compile(r"\bempirical", re.I), "empirical, not at the start"),
    (re.compile(r"\bconjectur", re.I), "conjectur, not at the start"),
]
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)

tagcnt, markcnt, ex = Counter(), Counter(), {}
wrapped = 0
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        txt = open(os.path.join(dd, fn), errors="ignore").read()
        a = "A" + fn[1:7]
        prev_tag, prev_open = None, False
        for line in txt.split("\n"):
            if len(line) < 4 or line[0] != "%":
                continue
            tag = line[1]
            body = re.sub(r"^%.\s+A\d{6}\s*", "", line)
            # a line that ends mid-expression and is followed by the same tag is a wrap
            if prev_open and tag == prev_tag:
                wrapped += 1
            prev_open = (body.count("(") > body.count(")")) or body.rstrip().endswith(",")
            prev_tag = tag
            if SETTLED.search(body):
                continue
            for pat, name in MARKERS:
                if pat.search(body):
                    markcnt[name] += 1
                    tagcnt[(name, tag)] += 1
                    ex.setdefault(name, []).append((a, tag, body[:120]))
                    break
print("BY WORDING (settled ones removed):")
for name, c in markcnt.most_common():
    print(f"{c:7d}  {name}")
    for a, t, b in ex[name][:2]:
        print(f"           %{t} {a}  {b}")
print("\nBY TAG, for each wording:")
for (name, t), c in sorted(tagcnt.items(), key=lambda kv: -kv[1])[:16]:
    print(f"{c:7d}  {name:32s} in %{t}")
print(f"\nlines that continue an unclosed previous line of the same tag: {wrapped}")
