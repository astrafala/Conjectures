#!/usr/bin/env python3
"""Regenerate the ledger's RESULTS HELD table from rank-map.json.

The table is derived, never edited by hand: it drifted to 456 rows once because it was
appended to instead of rebuilt.
"""
import json, re

BESPOKE = "a separate argument for that one problem"
SHARED = "one theorem, proved once and applied to twenty entries"
DESC = {k.split('|')[0] + '|' + k.split('|')[1]: v
        for k, v in json.load(open("engine_desc.json")).items()}

rm = json.load(open("rank-map.json"))
cls = json.load(open("paper-classes.json"))
bespoke, shared = set(cls["bespoke"]), set(cls["shared"])
rows = []
for m in rm:
    if m["was"] in bespoke:
        d = BESPOKE
    elif m["was"] in shared:
        d = SHARED
    else:
        d = DESC.get(f"{m['engine']}|{m['verdict']}", "conjectured recurrence proved")
    rows.append(f"| {m['rank']} | {m['verdict']} | {m['anum']} | {d} |")

txt = open("LEDGER.md").read()
lines = txt.split("\n")
first = next(i for i, l in enumerate(lines) if l.startswith("| 1 | PROOF | A063305"))
last = first
while last + 1 < len(lines) and re.match(r"^\| \d+ \| (PROOF|DISPROOF) \| A\d+ \|", lines[last + 1]):
    last += 1
open("LEDGER.md", "w").write("\n".join(lines[:first] + rows + lines[last + 1:]))
print(f"table rebuilt: {len(rows)} rows (was {last - first + 1})")
