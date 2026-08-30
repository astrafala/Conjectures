#!/usr/bin/env python3
"""Entries with an open, decidable congruence or divisibility conjecture."""
import json, os, re
import congparse
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
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
        F = [re.sub(r"^A\d{6}\s*", "", l[3:].strip())
             for l in txt.split("\n") if l[:2] in ("%F", "%C", "%e")]
        if any(CONJ.match(l) and not SETTLED.search(l) and congparse.parse(l) is not None
               for l in F):
            out.append("A" + fn[1:7])
json.dump(out, open("cong-todo.json", "w"), indent=1)
print(len(out), "entries with a decidable congruence conjecture")
print("e.g.", out[:14])
