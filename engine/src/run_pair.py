#!/usr/bin/env python3
"""Settle a named conjecture line on a named entry, without touching the main results."""
import json, sys
import sympy as sp
from local_extract import entry as lentry
import prove_rec
prove_rec._save = lambda d: None

todo = json.load(open(sys.argv[1]))     # {anum: [conj, ...]}
out = {}
for a, conjs in sorted(todo.items()):
    r = lentry(f"/home/user/oeis/oeisdata/seq/{a[:4]}/{a}.seq")
    if r is None:
        print(f"{a}: no local entry"); continue
    for j, conj in enumerate(conjs):
        v = dict(r[1]); v["conj"] = conj
        res = prove_rec.run({a: v}, per_entry=300)
        out[f"{a}#{j}"] = {**res[a], "conj": conj}
json.dump(out, open("pair-results.json", "w"), indent=1, sort_keys=True)
