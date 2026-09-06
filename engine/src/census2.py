#!/usr/bin/env python3
"""Where the remaining open recurrence conjectures actually live.

For every entry carrying a "Conjecture: ... a(n-i) ... = 0" line that no engine has
settled, classify what the entry gives us to work with. The point is to aim the next
engine at the biggest pile, not the most interesting one.
"""
import json, os, re
from collections import Counter
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(
    r"\bproof\b|prove[sndg]?\b|proving|\bproven\b|is true|has been shown|\bshown\b|"
    r"\bshows\b|follows from|confirm\w*|verif\w*|checked using|establish\w*|settled|"
    r"is correct|are correct|follows easily|follows at once|follows immediately|"
    r"derives from|is a consequence|sumrecursion|Zeilberger", re.I)

def has(pats, lines):
    return any(any(re.search(p, l, re.I) for p in pats) for l in lines)

cnt = Counter(); ex = {}
tot = 0
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        txt = open(os.path.join(dd, fn), errors="ignore").read()
        if "Conjectur" not in txt or "a(n-" not in txt:
            continue
        F = [re.sub(r"^A\d{6}\s*", "", l[3:].strip())
             for l in txt.split("\n") if l[:2] in ("%F", "%C", "%e")]
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        if not conjs:
            continue
        # skip entries where any conjecture line already carries settlement wording
        if any(SETTLED.search(c) for c in conjs):
            continue
        tot += 1
        a = "A" + fn[1:7]
        gf   = has([r"^G\.f\.", r"^O\.g\.f\.", r"g\.f\.\s*:"], F)
        egf  = has([r"^E\.g\.f\.", r"e\.g\.f\.\s*:"], F)
        summ = has([r"^a\(n\)\s*=\s*Sum_", r"=\s*Sum_\{k"], F)
        binm = has([r"binomial\(", r"C\(n", r"\bfactorial\b|\bn!\b"], F)
        prod = has([r"^a\(n\)\s*=\s*Product_"], F)
        rec  = any(("a(n-" in l.replace(" ", "") or "a(n+" in l.replace(" ", ""))
                   and "=" in l and not CONJ.match(l) for l in F)
        if gf: k = "g.f. posted"
        elif egf: k = "e.g.f. posted"
        elif summ and binm: k = "SUM with binomials/factorials (telescoping)"
        elif summ: k = "SUM, no binomials"
        elif prod: k = "product formula"
        elif rec: k = "another recurrence posted (Ore division)"
        else: k = "nothing parseable"
        cnt[k] += 1
        ex.setdefault(k, []).append(a)
print(f"{tot} entries with an open conjectured recurrence\n")
for k, c in cnt.most_common():
    print(f"{c:6d}  {k}")
    print(f"          e.g. {' '.join(ex[k][:6])}")
json.dump({k: v for k, v in ex.items()}, open("census2.json", "w"), indent=1)
