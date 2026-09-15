#!/usr/bin/env python3
"""How many open recurrence conjectures sit on entries defined by coefficient extraction,
broken down by the shape of the extraction. Decides where the next engine goes."""
import os, re, sys
from collections import Counter
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*(Conjectur)", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|guess|probably", re.I)
EXT = re.compile(r"^a\(n\)\s*=\s*(.*?)(\[\s*x\^\(?([^\]]*?)\)?\s*\]|[Cc]oefficient of x\^\(?([^ ]*?)\)? in)\s*(.+)$")

def shape(pre, idx, body):
    pre = pre.strip().rstrip('*').strip()
    idx = (idx or "").replace(" ", "")
    has_n_exp = re.search(r"\^\(?[^)]*\bn\b", body) is not None
    if idx in ("n",):
        s = "[x^n]"
    elif re.fullmatch(r"\d*\*?n([-+]\d+)?", idx):
        s = "[x^(q*n+r)]"
    else:
        s = f"[x^other:{idx[:12]}]"
    if pre:
        s += "  pre=" + ("n!" if "n!" in pre else "1/(n+..)" if "/" in pre else pre[:14])
    if not has_n_exp:
        s += "  (no n in exponent)"
    return s

cnt, ex = Counter(), {}
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        txt = open(os.path.join(dd, fn), errors="ignore").read()
        if "Conjectur" not in txt or "a(n-" not in txt or "x^" not in txt:
            continue
        F = [re.sub(r"^A\d{6}\s*", "", l[3:].strip())
             for l in txt.split("\n") if l[:2] in ("%F", "%C")]
        if not any(CONJ.match(l) and "a(n-" in l.replace(" ", "")
                   and "=0" in l.replace(" ", "") for l in F):
            continue
        for l in F:
            if CONJ.match(l) or GUESS.search(l):
                continue
            m = EXT.match(l)
            if not m:
                continue
            s = shape(m.group(1), m.group(3) or m.group(4), m.group(5))
            cnt[s] += 1
            ex.setdefault(s, ("A" + fn[1:7], l[:120]))
for s, c in cnt.most_common(28):
    print(f"{c:5d}  {s}")
    print(f"         {ex[s][0]}  {ex[s][1]}")
print("\ntotal", sum(cnt.values()))
