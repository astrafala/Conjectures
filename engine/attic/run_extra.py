#!/usr/bin/env python3
"""Prove the SECOND, still-open recurrence conjecture on entries whose first one
we already settled. Same machinery, different conjecture line."""
import json, sys
from local_extract import entry as lentry
import prove_rec
prove_rec._save = lambda d: None   # the extra conjectures must not overwrite the main results file

EXTRA = json.load(open("extra-conj.json"))
ents = {}
for a, meta in EXTRA.items():
    r = lentry(f"/home/user/oeis/oeisdata/seq/{a[:4]}/{a}.seq")
    if r is None:
        print(f"{a}: local_extract returned nothing"); continue
    v = dict(r[1])
    v["conj"] = meta["others"][0]
    ents[a] = v
sel = sys.argv[1:]
if sel:
    ents = {a: v for a, v in ents.items() if a in sel}
res = prove_rec.run(ents, per_entry=300)
json.dump(res, open("extra-results.json", "w"), indent=1, sort_keys=True)
