#!/usr/bin/env python3
"""What the 268 unreadable entries actually offer, so the next engine has a target."""
import json, re
from collections import Counter
from regf import entry

mine = {r["anum"] for r in json.load(open("rank-map.json"))}
todo = [a for a in json.load(open("census2.json"))["nothing parseable"] if a not in mine]
cnt, ex = Counter(), {}
for a in todo:
    F, data, off, name = entry(a)
    body = " || ".join(F)
    if re.search(r"\bA\d{6}\b", body):
        k = "defined from another sequence"
    elif re.search(r"Sum_|Product_", body):
        k = "sum or product formula"
    elif re.search(r"a\(n\)\s*=.*a\(n-", body):
        k = "another recurrence stated"
    elif not F:
        k = "no formula section at all -- only the name"
    else:
        k = "formula section, nothing recognised"
    cnt[k] += 1
    ex.setdefault(k, []).append(a)
for k, c in cnt.most_common():
    print(f"{c:5d}  {k}\n         e.g. {' '.join(ex[k][:8])}")
json.dump(ex, open("census3.json", "w"), indent=1)

print("\n--- names of the 'only the name' group, for shape:")
for a in ex.get("no formula section at all -- only the name", [])[:14]:
    print(" ", a, entry(a)[3][:100])
