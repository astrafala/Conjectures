#!/usr/bin/env python3
"""Entries carrying the "eventually periodic mod k, period dividing phi(k)" conjecture.

This project already holds a proof of that statement for every sequence whose exponential
generating function has the form G(e^x - 1) -- twenty papers rest on it. The census found
129 open conjectures of that shape, so the question is simply how many more entries the
theorem already covers.
"""
import json, os, re
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
SHAPE = re.compile(r"period", re.I)
PHI = re.compile(r"phi\(k\)|A000010\(k\)|totient", re.I)

out, withphi = [], []
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        txt = open(os.path.join(dd, fn), errors="ignore").read()
        if "Conjectur" not in txt or "period" not in txt:
            continue
        F = [re.sub(r"^A\d{6}\s*", "", l[3:].strip())
             for l in txt.split("\n") if l[:2] in ("%F", "%C", "%e")]
        hits = [l for l in F if CONJ.match(l) and SHAPE.search(l)
                and not SETTLED.search(l)]
        if not hits:
            continue
        a = "A" + fn[1:7]
        out.append(a)
        if any(PHI.search(l) for l in hits):
            egf = [l for l in F if re.match(r"\s*E\.g\.f\.", l, re.I)]
            withphi.append({"anum": a, "conj": hits[0][:200],
                            "egf": [e[:150] for e in egf[:2]]})
json.dump(out, open("periodic-todo.json", "w"), indent=1)
json.dump(withphi, open("periodic-phi.json", "w"), indent=1)
print(f"{len(out)} entries with an open periodicity conjecture")
print(f"{len(withphi)} of them say the period divides phi(k)")
for w in withphi[:12]:
    print(f"  {w['anum']}  egf: {w['egf'][0][:100] if w['egf'] else '(none posted)'}")
