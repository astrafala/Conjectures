#!/usr/bin/env python3
"""Live check, one conjecture at a time, that each result in a spec is still open.

Keyed on the conjecture rather than the entry, because several entries here carry more
than one. Any settlement wording anywhere on the entry is printed in full so it can be
read rather than trusted to a regex.
"""
import json, sys, time
from verify_open import fetch, PROOF, norm
import re


def main(path):
    spec = json.load(open(path))
    cache, keep, drop = {}, [], []
    for s in spec:
        a = s["anum"]
        if a not in cache:
            try:
                cache[a] = fetch(a)
            except Exception as e:
                print(f"{a}  FETCH FAILED {e}")
                continue
            time.sleep(0.3)
        e = cache[a]
        lines = [l for k in ("comment", "formula", "link", "ext", "example")
                 for l in (e.get(k) or [])]
        here = [l for l in lines if norm(s["conj"]) in norm(l)]
        if not here:
            drop.append((a, "conjecture no longer on the entry", ""))
            continue
        hits = [l for l in lines if PROOF.search(l) and
                re.search(r"conjectur|recurrence", l, re.I)]
        if hits:
            drop.append((a, "settlement wording on the entry", hits[0][:200]))
            continue
        s["conj"] = here[0]
        keep.append(s)
    for a, why, txt in drop:
        print(f"DROP {a}: {why}")
        if txt:
            print(f"        {txt}")
    json.dump(keep, open(path.replace(".json", "-open.json"), "w"), indent=1)
    print(f"\nstill open: {len(keep)} of {len(spec)}")


if __name__ == "__main__":
    main(sys.argv[1])
