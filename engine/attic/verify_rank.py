#!/usr/bin/env python3
"""Nothing may be lost or duplicated by the renumbering: check A-numbers set-wise."""
import json, os, re
from collections import Counter
from pdfminer.high_level import extract_text


def amap(d):
    out = {}
    for f in sorted(os.listdir(d), key=lambda s: int(s.split("-")[0])):
        t = extract_text(f"{d}/{f}", maxpages=2)
        a = re.findall(r"A\d{6}", t)
        out[int(f.split("-")[0])] = a[0] if a else None
    return out


new, old = amap("papers"), amap("papers-old-numbering")
rm = {m["rank"]: m for m in json.load(open("rank-map.json"))}
bad = [r for r, a in new.items() if rm[r]["anum"] != a]
print("rank entries disagreeing with the map:", bad or "none")
print("same multiset of A-numbers:", Counter(new.values()) == Counter(old.values()))
json.dump({str(k): v for k, v in new.items()}, open("paper-map.json", "w"),
          indent=1, sort_keys=True)
