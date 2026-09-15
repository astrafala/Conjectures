#!/usr/bin/env python3
"""Build papers 101-200, one entry per subprocess so a slow one cannot stall the run.

Numbers are assigned only to entries that actually build, so the run is contiguous.
"""
import json, os, subprocess, sys

SEL = [l.strip() for l in open("new-entries.txt") if l.strip()]
TARGET_LO = int(os.environ.get("LO", "101"))
TARGET_HI = int(os.environ.get("HI", "200"))

CHILD = '''
import os, json, sys
os.environ["START"] = "{num}"
import makerecpapers as M
M.START = {num}
M._sel = ["{anum}"]
M.OPEN = {{k: v for k, v in M.OPEN.items() if k == "{anum}"}}
M.build()
'''


def main():
    num = TARGET_LO
    while num <= TARGET_HI and os.path.exists(f"papers/{num}-PROOF.pdf"):
        num += 1
    assigned = json.load(open("paper-map.json")) if os.path.exists("paper-map.json") else {}
    used = set(assigned.values())
    for anum in SEL:
        if num > TARGET_HI:
            break
        if anum in assigned:
            continue
        if anum in used:
            continue
        try:
            subprocess.run(["python3", "-c", CHILD.format(num=num, anum=anum)],
                           timeout=75, capture_output=True)
        except subprocess.TimeoutExpired:
            print(f"  timeout on {anum}")
            continue
        if os.path.exists(f"papers/{num}-PROOF.pdf"):
            assigned[anum] = num
            print(f"{num:4d}  {anum}")
            num += 1
            json.dump(assigned, open("paper-map.json", "w"), indent=1, sort_keys=True)
        else:
            print(f"  failed {anum}")
    print(f"\nnext free number: {num}")


if __name__ == "__main__":
    main()
