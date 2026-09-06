#!/usr/bin/env python3
"""Rebuild the ledger's RESULTS HELD table from the papers themselves.

Rows 1-28 came from the original hand-written ledger and are kept verbatim; everything
from 29 on is derived from the built PDFs, so the table cannot drift away from what the
directory actually holds.
"""
import json, os, re
import paperpath

LEDGER = "LEDGER-CLAUDE-CODE.md"

KIND = [
    (r"conjectured recurrence", "conjectured P-recursive recurrence"),
    (r"periodicity modulo m", "eventual periodicity mod m, period dividing phi(m)"),
    (r"conjectured closed form", "conjectured closed form"),
    (r"conjectured identity", "identity between OEIS entries"),
    (r"gcd-sum", "gcd-sum evaluation"),
    (r"convergent series", "sequence equals a convergent infinite series"),
]


def who(conj):
    m = re.search(r"- _([^_]+)_", conj or "")
    return (m.group(1).strip().split()[-1] if m else "Mathar")


def main():
    pm = {int(k): v for k, v in json.load(open("paper-map.json")).items()}
    titles = {int(k): v for k, v in json.load(open("paper-titles.json")).items()}
    conjs = {}
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json"):
        try:
            for a, v in json.load(open(f)).items():
                if v.get("conj"):
                    conjs[a] = v["conj"]
        except Exception:
            pass
    import glob
    for f in sorted(set(glob.glob("*spec*.json") + glob.glob("*build*.json"))):
        if os.path.exists(f):
            for s in json.load(open(f)):
                if s.get("anum") and s.get("conj"):
                    conjs.setdefault(s["anum"], s["conj"])

    txt = open(LEDGER).read()
    lines = txt.split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("| 1 | "))
    # the table ends at the first line that is not one of its rows. Taking the LAST
    # matching line in the whole file instead was catastrophic: the census tables added
    # later have rows of the same shape, so everything between the two got replaced by
    # the rebuilt rows and four hundred lines of notes were deleted in one run.
    last = first
    while last + 1 < len(lines) and re.match(r"^\| \d+ \| ", lines[last + 1]):
        last += 1
    keep = [l for l in lines[first:last + 1] if re.match(r"^\| (1?[0-9]|2[0-8]) \| ", l)]

    rows = list(keep)
    for num in sorted(pm):
        if num < 29:
            continue
        a = pm[num]
        title = titles.get(num, "")
        kind = "conjectured P-recursive recurrence"
        for pat, name in KIND:
            if re.search(pat, title, re.I):
                kind = name
                break
        verdict = ("DISPROOF" if os.path.exists(paperpath.path(num, "DISPROOF"))
                   else "PROOF")
        rows.append(f"| {num} | {verdict} | {a} | {kind} | {who(conjs.get(a))} |")

    out = lines[:first] + rows + lines[last + 1:]
    open(LEDGER, "w").write("\n".join(out))
    print(f"table rebuilt: {len(rows)} rows, papers 1..{max(pm)}")


if __name__ == "__main__":
    main()
