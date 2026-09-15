#!/usr/bin/env python3
"""What is being refused by "not a plain shifted combination of other entries"?

1112 of 1250 cross-entry conjectures died there. The last two times a refusal rate looked
like that -- the summation formulas, the generating-function lines -- it was notation
rather than mathematics. Same question, asked the same way.
"""
import json, re
from collections import Counter
import cross as C

res = json.load(open("cross-results.json"))
bad = [(k, v) for k, v in res.items()
       if v["status"].startswith("not a plain shifted")]
cnt, ex = Counter(), {}
for k, v in bad:
    b = v["conj"]
    b = re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", b, flags=re.I)
    b = b.split(" - _")[0].strip()
    lhs = b.split("=")[0].strip() if "=" in b else ""
    refs = re.findall(r"A\d{6}", b)
    if "=" not in b:
        r = "no equation at all"
    elif lhs != "a(n)":
        r = f"left side is not a(n): {lhs[:24]}"
    elif not refs:
        r = "no A-number on the right"
    elif re.search(r"Sum_|Product_", b):
        r = "a sum or product over the other sequence"
    elif re.search(r"A\d{6}\s*\([^()]*,", b):
        r = "a triangle reference A######(n,k)"
    elif re.search(r"A\d{6}\s*\(\s*\d*\s*\*?\s*n\s*[-+*/]", b):
        r = "the reference is at a scaled or shifted index"
    elif len(set(refs)) > 1 and re.search(r"A\d{6}[^)]*\)\s*\*\s*A\d{6}", b):
        r = "a product of two entries"
    elif re.search(r"\bmod\b|floor|ceiling|\babs\b", b, re.I):
        r = "mod / floor / abs"
    else:
        r = "something else"
    cnt[r] += 1
    ex.setdefault(r, (k, b[:130]))
for r, c in cnt.most_common(14):
    print(f"{c:5d}  {r}")
    print(f"        {ex[r][0]}  {ex[r][1]}")
print("\ntotal", sum(cnt.values()))
