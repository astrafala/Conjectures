#!/usr/bin/env python3
"""Sub-classify the 7,959 conjecture lines the first census could only call "other".

It is the largest bucket by a wide margin and completely unexamined. Anything mechanical
hiding in it is worth more than another corner of the shapes already worked.
"""
import os, re
from collections import Counter
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
KNOWN = re.compile(r"a\(n-|=\s*0\s*$|\bmod\b|\(mod|congruen|divisib|divides|"
                   r"~|asymptot|\blim\b|period|G\.f\.|generating function|"
                   r"^a\(n\)\s*=", re.I)

cnt, ex = Counter(), {}
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
        a = "A" + fn[1:7]
        for line in txt.split("\n"):
            if line[:2] not in ("%C", "%F", "%e"):
                continue
            l = re.sub(r"^A\d{6}\s*", "", line[3:].strip())
            if not CONJ.match(l) or SETTLED.search(l):
                continue
            b = re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", l, flags=re.I).strip()
            if KNOWN.search(b):
                continue
            if re.match(r"\(?Start\)?|from\s+_", b, re.I) or len(b) < 12:
                k = "a heading for a block of statements"
            elif re.search(r"^(the |this |every |all |no |there )", b, re.I):
                k = "an English sentence about the sequence"
            elif re.search(r"\bT\(n,\s*k\)|A\(n,\s*k\)|row |column |triangle", b, re.I):
                k = "about a triangle or array"
            elif re.search(r"\bnumber of\b|\bcounts?\b", b, re.I):
                k = "a combinatorial interpretation"
            elif re.search(r"a\(n\)\s*(<|>|<=|>=)", b):
                k = "an inequality on a(n)"
            elif re.search(r"^a\(", b):
                k = "starts with a(...), some other shape"
            elif re.search(r"\bx\^|\bpolynomial|\birreducib", b, re.I):
                k = "about polynomials"
            elif re.search(r"\bdigit|\bbase\b", b, re.I):
                k = "about digits or a base"
            elif re.search(r"=", b):
                k = "an equation not starting with a(n)"
            else:
                k = "unclassified prose"
            cnt[k] += 1
            ex.setdefault(k, []).append((a, b[:120]))
for k, c in cnt.most_common():
    print(f"{c:6d}  {k}")
    for a, b in ex[k][:3]:
        print(f"          {a}  {b}")
print("\ntotal", sum(cnt.values()))
