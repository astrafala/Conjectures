#!/usr/bin/env python3
"""What is actually being thrown away by "no usable hypergeometric sum formula".

Three quarters of the telescoping attempts died there, so the reason each candidate
formula was refused is worth more than another engine.
"""
import json, os, re
from collections import Counter
import sympy as sp
from zeil_run import candidates, parse_sum, LOCALS, SUMF, CONJ, GUESS
from zeil import n, k

REJECT = [
    (r"Sum_", "nested Sum"), (r"Product_", "Product"), (r"Stirling", "Stirling"),
    (r"A\d{6}", "refers to another sequence"), (r"floor|ceiling", "floor/ceiling"),
    (r"\bmod\b", "mod"), (r"!!", "double factorial"), (r"hypergeom", "hypergeom"),
]

cnt, ex = Counter(), {}
res = {}
for f in ("zeil-0.json", "zeil-1.json", "zeil-2.json"):
    res.update(json.load(open(f)))
bad = {kk.split("#")[0] for kk, v in res.items()
       if isinstance(v, dict) and v.get("status") == "no usable hypergeometric sum formula"}

for a, conjs, sums, data, off, name in candidates():
    if a not in bad:
        continue
    for src in sums:
        m = re.match(r"a\(n\)\s*=\s*Sum_\{\s*k\s*=\s*([^.]+?)\.\.\s*([^}]+?)\s*\}\s*(.+)$",
                     src.strip(), re.I)
        if not m:
            m2 = re.match(r"a\(n\)\s*=\s*Sum_\{([^}]*)\}", src.strip(), re.I)
            r = f"index spec not 'k=lo..hi': {m2.group(1)[:26] if m2 else '?'}"
        else:
            body = m.group(3).split(" - _")[0]
            r = None
            for pat, label in REJECT:
                if re.search(pat, body, re.I):
                    r = "body has " + label
                    break
            if r is None:
                try:
                    b = body.strip().rstrip('.').replace("^", "**")
                    b = re.sub(r"(\d)\s*\(", r"\1*(", b)
                    b = re.sub(r"\)\s*\(", r")*(", b)
                    b = re.sub(r"(\d)\s*([nk])\b", r"\1*\2", b)
                    e = sp.sympify(b, locals=LOCALS)
                    extra = e.free_symbols - {n, k}
                    r = f"free symbols {sorted(map(str, extra))}" if extra else "PARSES?"
                except Exception as ex_:
                    r = f"sympify fails: {str(ex_)[:40]}"
        cnt[r] += 1
        ex.setdefault(r, (a, src[:130]))
for r, c in cnt.most_common(22):
    print(f"{c:5d}  {r}")
    print(f"         {ex[r][0]}  {ex[r][1]}")
print("\ntotal rejected formula lines:", sum(cnt.values()))
