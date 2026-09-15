#!/usr/bin/env python3
"""Programs as the known side.

The limit on everything so far has not been the engines, it has been the KNOWN side: 1,417
of 1,457 empirical candidates had no independent fact to argue from. But 12,937 entries
carrying a conjecture also carry a program, and a program is a definition -- it is what the
b-file was computed from.

Only a small part of that is usable. A brute-force search program defines the sequence but
says nothing a symbolic engine can hold. What is usable is a program whose body is an
explicit formula in n, or an explicit series expansion of a generating function.

The circularity trap is severe here and is the same one that nearly cost 21 false proofs:
Colin Barker posts his empirical g.f. AND a PARI Vec() of that same g.f., so the program
would "confirm" the conjecture by restating it. Any program whose expression matches a
conjectural line of the same entry is therefore refused, and so is every g.f. expansion
whose g.f. does not appear on a line stated as fact.

This file only measures. The engine is separate.
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)", re.I)
MMA_TABLE = re.compile(r"Table\[(.+),\s*\{\s*n\s*,", re.S)
MMA_SERIES = re.compile(r"CoefficientList\[\s*Series\[", re.I)
MMA_LINREC = re.compile(r"LinearRecurrence\[\s*\{([^}]*)\}\s*,\s*\{([^}]*)\}", re.I)
MMA_RSOLVE = re.compile(r"RecurrenceTable\[|RSolve\[", re.I)
PARI_A = re.compile(r"\ba\s*\(\s*n\s*\)\s*=\s*(.+)$")
PARI_VEC = re.compile(r"\bVec\s*\(", re.I)

cnt, ex = Counter(), {}
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        a = "A" + fn[1:7]
        lines = [l.rstrip("\n") for l in open(os.path.join(dd, fn), errors="ignore")
                 if len(l) > 3 and l[0] == "%"]
        body = {}
        for l in lines:
            body.setdefault(l[1], []).append(re.sub(r"^%.\s+A\d{6}\s*", "", l))
        conj = [b for b in body.get("F", []) + body.get("C", []) if MARK.match(b)]
        if not conj:
            continue
        progs = body.get("t", []) + body.get("o", []) + body.get("p", [])
        if not progs:
            continue
        kinds = set()
        for p in progs:
            if MMA_LINREC.search(p):
                kinds.add("Mathematica LinearRecurrence")
            elif MMA_SERIES.search(p) or PARI_VEC.search(p):
                kinds.add("a series expansion (circularity risk)")
            elif MMA_RSOLVE.search(p):
                kinds.add("RecurrenceTable / RSolve")
            elif MMA_TABLE.search(p):
                kinds.add("Mathematica Table[formula]")
            elif PARI_A.search(p):
                kinds.add("PARI a(n) = formula")
        for k in kinds:
            cnt[k] += 1
            ex.setdefault(k, []).append((a, next(p for p in progs if k.split()[0].lower() in p.lower() or True)[:100]))
        if not kinds:
            cnt["nothing an engine can read"] += 1

for k, v in cnt.most_common():
    print(f"{v:7d}  {k}")
print()
for k in ("Mathematica LinearRecurrence", "Mathematica Table[formula]", "PARI a(n) = formula"):
    print("---", k)
    for a, p in ex.get(k, [])[:6]:
        print(f"  {a}  {p}")
