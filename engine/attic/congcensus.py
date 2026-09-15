#!/usr/bin/env python3
"""How are the congruence, divisibility and periodicity conjectures actually written?

Three times now a refusal rate near 90% turned out to be notation rather than
mathematics, and twice the fix was cheap. So the wording gets read before the parser is
written, not after.
"""
import os, re
from collections import Counter
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
TOPIC = re.compile(r"\bmod\b|\(mod|congruen|divisib|divides|\bperiod", re.I)

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
            if not CONJ.match(l) or SETTLED.search(l) or not TOPIC.search(l):
                continue
            b = re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", l, flags=re.I)
            if re.search(r"\bperiod", b, re.I):
                k = "eventual periodicity"
            elif re.search(r"a\(n\)\s*(==|=|\\equiv|is congruent)", b) and \
                    re.search(r"\(mod\s+\d+\)|mod\s+\d+", b):
                k = "a(n) == c (mod fixed number)"
            elif re.search(r"a\(n\)\s*(==|=)", b) and re.search(r"mod\s+[a-zA-Z]", b):
                k = "a(n) == c (mod something symbolic)"
            elif re.search(r"a\(p\)|prime p|prime\b", b, re.I):
                k = "about a(p) for p prime"
            elif re.search(r"\bdivides\b|divisible by", b, re.I):
                k = "divisibility, in words"
            elif re.search(r"\bmod\b|\(mod", b):
                k = "mod appears, other shape"
            else:
                k = "other"
            cnt[k] += 1
            ex.setdefault(k, []).append((a, b[:135]))
for k, c in cnt.most_common():
    print(f"{c:5d}  {k}")
    for a, b in ex[k][:3]:
        print(f"         {a}  {b}")
print("\ntotal", sum(cnt.values()))
