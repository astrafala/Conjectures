#!/usr/bin/env python3
"""Fetch OEIS entries in full and print everything needed for Hard Rule 2."""
import json, subprocess, sys

FIELDS = ("comment", "formula", "example", "xref", "link", "reference", "ext")


def get(anum):
    out = subprocess.run(
        ["curl", "-sS", "-A", "Mozilla/5.0",
         f"https://oeis.org/search?q=id:{anum}&fmt=json"],
        capture_output=True, text=True, timeout=90).stdout
    d = json.loads(out)
    return (d[0] if isinstance(d, list) else d["results"][0])


def show(anum, full=True):
    r = get(anum)
    print("=" * 78)
    print(f"{anum} | {r['name']}")
    print(f"OFFSET {r['offset']} | KEYWORDS {r['keyword']} | AUTHOR {r.get('author')}")
    print(f"CREATED {r['created'][:10]} | LAST MODIFIED {r['time'][:10]} | rev {r['revision']}")
    print(f"DATA {r['data'][:150]}")
    for k in FIELDS:
        for l in r.get(k) or []:
            if full or "onjecture" in l:
                print(f"  [{k}] {l[:400]}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        show(a)
