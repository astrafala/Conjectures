#!/usr/bin/env python3
"""Re-check a set of papers against the LIVE OEIS, not the local clone.

The clone is a snapshot. Everything harvested on 30 Aug was filtered against a copy from
25 Aug, and this target list is being worked by other people right now -- seven of Tong
Niu's 2026 papers name their entry in the title. A five-day-old snapshot is not good
enough to stand behind a claim of priority, so the check is repeated against the live
entry before delivery.
"""
import json, re, sys, time
from verify_open import fetch, PROOF
from wording_scan import WIDE, norm


def check(spec_files):
    rows = []
    for f in spec_files:
        rows += json.load(open(f))
    seen, out = {}, []
    for v in sorted(rows, key=lambda r: r["num"]):
        a = v["anum"]
        if a not in seen:
            e = None
            for i in range(5):
                try:
                    e = fetch(a); break
                except Exception:
                    time.sleep(3 * (i + 1))
            seen[a] = e
            time.sleep(0.35)
        e = seen[a]
        if e is None:
            out.append((v["num"], a, "FETCH FAILED", []))
            continue
        lines = [l for k in ("comment", "formula", "link", "ext", "example")
                 for l in (e.get(k) or [])]
        present = any(norm(v["conj"]) in norm(l) for l in lines)
        self_hit = [l for l in lines
                    if WIDE.search(l) and norm(v["conj"])[:60] in norm(l)]
        other = [l for l in lines
                 if WIDE.search(l) and re.search(r"conjectur|recurrence", l, re.I)]
        st = ("CONJECTURE GONE FROM THE ENTRY" if not present else
              "SETTLED ON ITS OWN LINE" if self_hit else
              "read: settlement wording elsewhere" if other else "still open")
        out.append((v["num"], a, st, (self_hit or other)[:2]))
    bad = [r for r in out if r[2] != "still open"]
    print(f"{len(out)} papers re-checked live; {len(bad)} need attention\n")
    for num, a, st, hits in bad:
        print(f"--- {num}  {a}  {st}")
        for h in hits:
            print(f"       {h[:200]}")
    print(f"\n{sum(1 for r in out if r[2] == 'still open')} confirmed still open")
    return out


if __name__ == "__main__":
    check(sys.argv[1:])
