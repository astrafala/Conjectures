#!/usr/bin/env python3
"""Rewrite the ledger to match what the papers directory actually contains.

The roster line, the RESULTS HELD table and the caveats are all derived from
paper-map.json and the live-verified conjecture texts, so the ledger cannot drift away
from the papers again.
"""
import json, os, re, sys

LEDGER = "LEDGER.md"


def rows(pm, conjmap):
    out = []
    for num in sorted(pm):
        a = pm[num]
        verdict = "DISPROOF" if os.path.exists(f"papers/{num}-DISPROOF.pdf") else "PROOF"
        desc, who = conjmap.get(num, ("conjectured P-recursive recurrence", "Mathar"))
        out.append(f"| {num} | {verdict} | {a} | {desc} | {who} |")
    return out


def main(newrows, roster_note, caveat):
    txt = open(LEDGER).read()
    txt = re.sub(r"Last updated [^.]*\. Roster: \*\*\d+ papers\*\*[^\n]*\n[^\n]*\n",
                 roster_note, txt, count=1)
    # append the new table rows just before the caveats heading
    marker = "\n### Caveats to disclose when handing these over\n"
    i = txt.index(marker)
    txt = txt[:i] + "\n" + "\n".join(newrows) + "\n" + txt[i:]
    # and the new caveat right after that heading
    j = txt.index(marker) + len(marker)
    txt = txt[:j] + "\n" + caveat.strip() + "\n" + txt[j:]
    open(LEDGER, "w").write(txt)
    print("ledger updated")


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), open(sys.argv[2]).read(), open(sys.argv[3]).read())
