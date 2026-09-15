#!/usr/bin/env python3
"""Gather every proved conjecture from every engine, drop what a paper already covers,
and assign the free paper numbers.

Withdrawn slots are refilled before the roster extends, so the numbering stays
contiguous.
"""
import glob, json, os, re


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


SOURCES = (glob.glob("scan-results-*.json")
           + ["nogf-results.json", "eqform-results.json",
              "extra-results.json", "extra-egf-results.json", "pair-results.json"])


def covered():
    """(anum, conjecture) pairs a paper already settles."""
    out = set()
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json"):
        try:
            for a, v in json.load(open(f)).items():
                if v.get("conj"):
                    out.add((a, norm(v["conj"])))
        except Exception:
            pass
    for f in glob.glob("*spec*.json") + glob.glob("*build*.json") + ["cross-redo.json"]:
        if not os.path.exists(f):
            continue
        try:
            rows = json.load(open(f))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for s in rows:
            if not isinstance(s, dict) or "num" not in s or "conj" not in s:
                continue
            if os.path.exists(f"papers/{s['num']}-PROOF.pdf"):
                out.add((s["anum"], norm(s["conj"])))
    return out


def main():
    have = covered()
    nogf = json.load(open("nogf-cache.json")) if os.path.exists("nogf-cache.json") else {}
    found, seen = [], set()
    for f in SOURCES:
        if not os.path.exists(f):
            continue
        for k, r in json.load(open(f)).items():
            if not isinstance(r, dict) or r.get("status") != "PROVED":
                continue
            a = r.get("anum") or k.split("#")[0]
            if not r.get("conj"):
                continue          # older result files did not record the text
            key = (a, norm(r["conj"]))
            if key in have or key in seen:
                continue
            seen.add(key)
            found.append({"anum": a, "conj": r["conj"], "mode": r.get("mode", "ogf"),
                          "gf_src": r.get("gf_src"),
                          "gf_from_name": f == "nogf-results.json",
                          "degree": r.get("degree")})
    free = [n for n in range(1, 500)
            if not os.path.exists(f"papers/{n}-PROOF.pdf")
            and not os.path.exists(f"papers/{n}-DISPROOF.pdf")]
    found.sort(key=lambda s: (s["anum"], s["conj"]))
    for i, s in enumerate(found):
        s["num"] = free[i]
    json.dump(found, open("new-spec.json", "w"), indent=1)
    print(f"{len(found)} results with no paper yet")
    if found:
        print(f"numbers {found[0]['num']} .. {found[-1]['num']}")


if __name__ == "__main__":
    main()
