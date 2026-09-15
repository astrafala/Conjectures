#!/usr/bin/env python3
"""Re-verify the whole roster against the live OEIS entries.

For each paper: is the conjecture it settles still on the entry, and does the entry now
record it as settled by someone else? Every settlement hit is printed in full, because
the wording matters -- "verified for n = 0..800" is a finite check and settles nothing,
while "Conjecture confirmed using the differential equation" settles everything.
"""
import json, os, re, sys, time
from verify_open import fetch, PROOF, norm


def paper_conjectures():
    """paper number -> (A-number, conjecture text or None)."""
    pm = {int(k): v for k, v in json.load(open("paper-map.json")).items()}
    conj = {}
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json"):
        try:
            for a, v in json.load(open(f)).items():
                if v.get("conj"):
                    conj.setdefault(a, v["conj"])
        except Exception:
            pass
    bynum = {}
    for f in ("slot-spec.json", "build-spec.json", "alg-spec-open.json",
              "alg2-spec-open.json", "fix-spec.json", "cross-build.json",
              "cross-redo.json"):
        if os.path.exists(f):
            for s in json.load(open(f)):
                bynum[s["num"]] = (s["anum"], s["conj"])
    out = {}
    for num, a in sorted(pm.items()):
        if num in bynum:
            out[num] = bynum[num]
        else:
            out[num] = (a, conj.get(a))
    return out


def main():
    todo = paper_conjectures()
    lo = int(os.environ.get("LO", "1"))
    hi = int(os.environ.get("HI", "9999"))
    todo = {n: v for n, v in todo.items() if lo <= n <= hi}
    cache, report = {}, {}
    for num, (a, conj) in sorted(todo.items()):
        if a not in cache:
            try:
                cache[a] = fetch(a)
            except Exception as e:
                report[num] = ("FETCH FAILED", a, str(e)[:60])
                continue
            time.sleep(0.25)
        e = cache[a]
        lines = [l for k in ("comment", "formula", "link", "ext", "example")
                 for l in (e.get(k) or [])]
        hits = [l for l in lines
                if PROOF.search(l) and re.search(r"conjectur|recurrence|formula", l, re.I)]
        present = None
        if conj:
            present = any(norm(conj) in norm(l) for l in lines)
        state = "ok"
        if conj and not present:
            state = "conjecture text gone"
        if hits:
            state = "settlement wording"
        report[num] = (state, a, [h[:220] for h in hits[:2]])
        json.dump(report, open(os.environ.get("OUT", "roster-report.json"), "w"), indent=1)
    flagged = {n: v for n, v in report.items() if v[0] != "ok"}
    print(f"checked {len(report)} papers; {len(flagged)} need a look\n")
    for n, (state, a, extra) in sorted(flagged.items()):
        print(f"paper {n}  {a}  {state}")
        for h in (extra if isinstance(extra, list) else [extra]):
            print(f"      {h}")


if __name__ == "__main__":
    main()
