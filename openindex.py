#!/usr/bin/env python3
"""Decide openness ONCE, for the whole corpus, before any engine runs.

Openness has been checked after the fact until now, which spends the expensive half of the
work on conjectures that were already answered -- and worse, it let three papers ship on
28 August whose entries say plainly that Mathar's recurrence "follows easily from" a fact
stated two lines above.

This walks every entry, finds the conjectural recurrences, and records for each whether
anything on the entry (in ANY tag, not just %F) reads as a settlement. The result is a
single index every sweep filters through first. A flag is a reason to read, not a verdict:
26 of 26 flagged papers in the roster audit turned out to be about a different statement,
so the flagged lines are stored alongside for judging.
"""
import json, os, re, sys
sys.path.insert(0, ".")
import conjlines, openness

ROOT = "/home/user/oeis/oeisdata/seq"
OUT = "open_index.json"


def main():
    idx = {"open": {}, "flagged": {}}
    manual = json.load(open("settled-manual.json")) if os.path.exists("settled-manual.json") else {}
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            a = "A" + fn[1:7]
            fl = [re.sub(r"^%.\s+A\d{6}\s*", "", l.rstrip())
                  for l in open(os.path.join(dd, fn), errors="ignore")
                  if len(l) > 3 and l[0] == "%" and l[1] == "F"]
            conj = [l for l in fl if conjlines.is_recurrence(l)]
            if not conj:
                continue
            if a in manual:
                idx["flagged"][a] = {"conj": conj, "why": [manual[a]]}
                continue
            ok, hits = openness.status(a)
            (idx["open"] if ok else idx["flagged"])[a] = (
                {"conj": conj} if ok else {"conj": conj, "why": hits[:3]})
    json.dump(idx, open(OUT, "w"), indent=1)
    print(f"{len(idx['open'])} entries still open, {len(idx['flagged'])} flagged for reading")


if __name__ == "__main__":
    main()
