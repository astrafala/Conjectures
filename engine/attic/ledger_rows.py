#!/usr/bin/env python3
"""Regenerate the RESULTS HELD table from what the papers directory actually holds."""
import json, os, re, sys

DESC = {"ogf": "conjectured P-recursive recurrence",
        "egf": "conjectured P-recursive recurrence (e.g.f.)"}


def contributor(conj):
    m = re.search(r"- _([^_]+)_", conj or "")
    if not m:
        return "Mathar"
    who = m.group(1).strip()
    return who.split()[-1] if who else "Mathar"


def main(specs, out):
    rows = {}
    for f in specs:
        if not os.path.exists(f):
            continue
        for s in json.load(open(f)):
            num = s["num"]
            if not os.path.exists(f"papers/{num}-PROOF.pdf"):
                continue
            d = DESC.get(s.get("mode", "ogf"), DESC["ogf"])
            if s.get("gf_from_name"):
                d += ", g.f. from the entry name"
            rows[num] = f"| {num} | PROOF | {s['anum']} | {d} | {contributor(s['conj'])} |"
    with open(out, "w") as fh:
        json.dump([rows[n] for n in sorted(rows)], fh, indent=1)
    print(f"{len(rows)} rows written to {out}")


if __name__ == "__main__":
    main(sys.argv[2:], sys.argv[1])
