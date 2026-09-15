#!/usr/bin/env python3
"""Rank newly built papers into the set rather than appending them.

New results are given a temporary number at the end, described in paper-engines.json so
the ranking knows what tier they belong to, and then the whole roster is re-ranked. The
old numbering is preserved in rank-map.json each time.
"""
import json, os, re, shutil, sys


def main(newdir, engine, spec_file):
    eng = {int(k): v for k, v in json.load(open("paper-engines.json")).items()}
    spec = {s["num"]: s for s in json.load(open(spec_file))}
    nxt = max(eng) + 1
    added = []
    for f in sorted(os.listdir(newdir), key=lambda s: int(s.split("-")[0])):
        if not f.endswith(".pdf"):
            continue
        old = int(f.split("-")[0])
        s = spec[old]
        shutil.copy(f"{newdir}/{f}", f"papers/{nxt}-PROOF.pdf")
        eng[nxt] = {"engine": engine, "order": s.get("order_conj", 0),
                    "degree": s.get("order_derived", 0), "anum": s["anum"],
                    "disproof": False}
        added.append((nxt, s["anum"]))
        nxt += 1
    json.dump({str(k): v for k, v in eng.items()},
              open("paper-engines.json", "w"), indent=1, sort_keys=True)
    print(f"{len(added)} papers added at temporary numbers: {added}")


if __name__ == "__main__":
    main(*sys.argv[1:])
