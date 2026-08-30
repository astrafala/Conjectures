#!/usr/bin/env python3
"""Re-check every shipped paper against the LIVE entry for settlement wording.

The local filter that decides whether a conjecture is still open read %F lines only. But an
entry can record a settlement in a comment or a link -- A002627 and A045406 both carry Tong
Niu's arXiv proof as a %H link, and A126674 says "R. J. Mathar's recurrence is correct" in a
%C comment. Five of fourteen fresh results were already settled that way.

Every count in this project has been re-checked live before shipping, and the live check
does read comments and links. This verifies that claim paper by paper rather than trusting
it: for all 526, fetch the entry now and report anything whose text says the conjecture is
answered. Slices are resumable because the run is long and the container sleeps between
turns.
"""
import json, os, re, sys, time
sys.path.insert(0, ".")
from verify_open import fetch

SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
OUT = "roster_audit.json"


def main(budget=500):
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    rm = json.load(open("rank-map.json"))
    anums = sorted({r["anum"] for r in rm})
    t0 = time.time()
    for a in anums:
        if a in done or time.time() - t0 > budget:
            continue
        e = None
        for i in range(4):
            try:
                e = fetch(a); break
            except Exception:
                time.sleep(2 * (i + 1))
        if e is None:
            continue
        fields = (e.get("formula", []) + e.get("comment", []) + e.get("link", [])
                  + e.get("reference", []) + e.get("example", []))
        hits = [f for f in fields if SETTLED.search(f)]
        done[a] = {"time": e["time"][:10], "revision": e["revision"],
                   "settle_wording": hits[:4]}
        json.dump(done, open(OUT, "w"), indent=1)
        time.sleep(0.35)
    flagged = {a: v for a, v in done.items() if v["settle_wording"]}
    print(f"{len(done)}/{len(anums)} checked; {len(flagged)} carry settlement wording")
    return done


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
