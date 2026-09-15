#!/usr/bin/env python3
"""Assign paper numbers to the results the full sweep found that no paper covers yet.

Withdrawn slots are refilled first, so the numbering stays contiguous, and only then
does the roster extend.
"""
import glob, json, os, re, sys

FREE = [n for n in range(1, 400)
        if not os.path.exists(f"papers/{n}-PROOF.pdf")
        and not os.path.exists(f"papers/{n}-DISPROOF.pdf")]


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def main():
    used = set(json.load(open("paper-map.json")).values())
    fresh = {}
    for f in glob.glob("scan-results-*.json"):
        try:
            fresh.update(json.load(open(f)))
        except Exception:
            pass
    seen, out = set(), []
    for r in sorted(fresh.values(), key=lambda r: (r["anum"], r["conj"])):
        if r["status"] != "PROVED" or r["anum"] in used:
            continue
        k = (r["anum"], norm(r["conj"]))
        if k in seen:
            continue
        seen.add(k)
        out.append({"anum": r["anum"], "conj": r["conj"], "mode": r.get("mode", "ogf"),
                    "gf_src": r.get("gf_src")})
    open_ = json.load(open("open-check.json")) if os.path.exists("open-check.json") else {}
    for i, s in enumerate(out):
        s["num"] = FREE[i]
    json.dump(out, open("new-spec.json", "w"), indent=1)
    print(f"{len(out)} results to place; numbers {out[0]['num']}..{out[-1]['num']}"
          if out else "nothing to place")


if __name__ == "__main__":
    main()
