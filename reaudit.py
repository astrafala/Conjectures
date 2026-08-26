#!/usr/bin/env python3
"""Re-derive every shipped paper's result from scratch and compare.

The full sweep re-attempts every conjecture with the current code, so it doubles as an
independent re-run of work done earlier under earlier versions of the parser and of the
field reductions. Anything a paper claims that the fresh run does not reproduce is
flagged for inspection rather than quietly kept.
"""
import glob, json, re
import sympy as sp

x = sp.Symbol('x')


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def main():
    fresh = {}
    for f in glob.glob("scan-results-*.json"):
        try:
            fresh.update(json.load(open(f)))
        except Exception:
            pass
    byconj = {}
    for k, r in fresh.items():
        byconj[(r["anum"], norm(r["conj"]))] = r

    pm = {int(k): v for k, v in json.load(open("paper-map.json")).items()}
    claims = {}
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json"):
        try:
            for a, v in json.load(open(f)).items():
                if v.get("conj"):
                    claims.setdefault(a, []).append(v["conj"])
        except Exception:
            pass
    res = {}
    for f in ("rec-results.json", "egf-results.json", "logexp-results.json"):
        try:
            res.update(json.load(open(f)))
        except Exception:
            pass

    agree = disagree = absent = 0
    problems = []
    for num, a in sorted(pm.items()):
        if num < 29:
            continue                     # papers 1-28 were not produced here
        for conj in claims.get(a, []):
            key = (a, norm(conj))
            fr = byconj.get(key)
            if fr is None:
                absent += 1
                continue
            if fr["status"] != "PROVED":
                disagree += 1
                problems.append((num, a, fr["status"]))
                continue
            old = res.get(a, {})
            if old.get("B") is not None and fr.get("B") is not None:
                if sp.expand(sp.sympify(old["B"]) - sp.sympify(fr["B"])) != 0:
                    disagree += 1
                    problems.append((num, a, f"residual differs: {old['B']} vs {fr['B']}"))
                    continue
            agree += 1
    print(f"re-derived and agreeing: {agree}")
    print(f"not covered by the sweep: {absent}")
    print(f"DISAGREEING: {disagree}")
    for p in problems:
        print("  ", p)


if __name__ == "__main__":
    main()
