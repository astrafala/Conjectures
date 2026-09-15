#!/usr/bin/env python3
"""Collect everything papers 32-51 need, straight from the live entries."""
import json, re, subprocess

ORDER = ["A000670", "A002050", "A004123", "A006531", "A052895", "A064618",
         "A080253", "A162314", "A167137", "A259533", "A301921", "A305550",
         "A306082", "A316142", "A316143", "A316144", "A320352", "A354242",
         "A354253", "A355409"]


def fetch(anum):
    out = subprocess.run(
        ["curl", "-sS", "-A", "Mozilla/5.0",
         f"https://oeis.org/search?q=id:{anum}&fmt=json"],
        capture_output=True, text=True, timeout=90).stdout
    return json.loads(out)[0]


def conj_line(r):
    """The labelled conjecture, verbatim, plus its attribution if present."""
    best = None
    for k in ("comment", "formula", "example"):
        for l in r.get(k) or []:
            if re.search(r"period.{0,60}phi\(k\)", l, re.I) and re.match(r"\s*Conjecture", l, re.I):
                if best is None or len(l) > len(best):
                    best = l
    return best


def egf_line(r):
    for l in r.get("formula") or []:
        if re.match(r"\s*E\.?g\.?f", l, re.I):
            return l
    for l in (r.get("comment") or []) + [r["name"]]:
        if re.search(r"[Ee]\.g\.f", l):
            return l
    return None


out = {}
for a in ORDER:
    r = fetch(a)
    out[a] = {
        "name": r["name"],
        "offset": int(r["offset"].split(",")[0]),
        "data": [int(x) for x in r["data"].split(",")],
        "time": r["time"][:10],
        "created": r["created"][:10],
        "revision": r["revision"],
        "author": r.get("author", ""),
        "conjecture": conj_line(r),
        "egf": egf_line(r),
    }
    print(f"{a}  off={out[a]['offset']}  mod={out[a]['time']}  rev={out[a]['revision']}")
    print(f"   egf: {str(out[a]['egf'])[:110]}")
    print(f"   conj: {str(out[a]['conjecture'])[:110]}")

with open("entries.json", "w") as fh:
    json.dump(out, fh, indent=1)
print(f"\nwrote entries.json with {len(out)} entries")
