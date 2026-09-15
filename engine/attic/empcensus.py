#!/usr/bin/env python3
"""What shape are the 23,322 "Empirical:" statements?

"Empirical" is the OEIS's usual label for a formula found by fitting and not proved --
Colin Barker's generating functions and recurrences above all. There are more of them than
there are lines saying "Conjecture", and this project has never read one. If they are the
same shapes the engines already settle, that is the largest opportunity here by a wide
margin.
"""
import os, re
from collections import Counter
ROOT = "/home/user/oeis/oeisdata/seq"
EMP = re.compile(r"^\s*Empirical\s*[:.]?\s*", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
HEAD = re.compile(r"\(\s*Start\s*\)\s*$", re.I)
END = re.compile(r"\(\s*End\s*\)", re.I)

cnt, ex = Counter(), {}
entries = set()
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        txt = open(os.path.join(dd, fn), errors="ignore").read()
        if "mpirical" not in txt:
            continue
        a = "A" + fn[1:7]
        F = [re.sub(r"^%.\s+A\d{6}\s*", "", l)
             for l in txt.split("\n") if len(l) > 3 and l[1] in "FCe"]
        inside = False
        for l in F:
            body = None
            if EMP.match(l):
                if HEAD.search(l):
                    inside = True
                    continue
                body = EMP.sub("", l).strip()
            elif inside:
                body = END.sub("", l).strip()
                if END.search(l):
                    inside = False
            if not body or SETTLED.search(body) or len(body) < 8:
                continue
            entries.add(a)
            nb = body.replace(" ", "")
            if re.match(r"(o\.?)?g\.?f\.?\s*[:.]", body, re.I):
                k = "a generating function"
            elif re.match(r"e\.?g\.?f\.?\s*[:.]", body, re.I):
                k = "an exponential generating function"
            elif "a(n-" in nb and "=0" in nb:
                k = "a linear recurrence, = 0"
            elif re.match(r"a\(n\)\s*=", body) and "a(n-" in nb:
                k = "a linear recurrence, a(n) = ..."
            elif re.match(r"a\(n\)\s*=", body):
                k = "a closed form for a(n)"
            elif re.search(r"\bmod\b|\(mod", body, re.I):
                k = "a congruence"
            elif re.search(r"~|asymptot", body):
                k = "asymptotics"
            else:
                k = "something else"
            cnt[k] += 1
            ex.setdefault(k, []).append((a, body[:120]))
print(f"{len(entries)} entries carry an empirical statement; "
      f"{sum(cnt.values())} statements\n")
for k, c in cnt.most_common():
    print(f"{c:7d}  {k}")
    for a, b in ex[k][:3]:
        print(f"           {a}  {b}")
