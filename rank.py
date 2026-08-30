#!/usr/bin/env python3
"""Order the whole roster by how hard the result was to get, and renumber accordingly.

Rank 1 is the hardest. The ordering is a judgement, so it is written down rather than
buried: papers are grouped into tiers by what the proof actually required, and within a
tier by the size of the object being handled -- the order of the recurrence first, then
the degree of the residual.

The tiers, hardest first:

  1. a separate argument found for that one problem
  2. one real theorem, proved once and applied to twenty entries
  3. a recurrence DERIVED from the summand by creative telescoping, not verified
  4. a general algebraic function field: nested radicals, implicit or reversion g.f.s
  5. a transcendental e.g.f., handled in a differential module over Q(x)
  6. several independent square roots
  7. an identity between different entries
  8. one square root, or none: the standard residual test
  9. a closed form compared against the posted generating function
 10. division of one posted operator by another

The last is honestly the shallowest thing here: both recurrences were already on the
entry and the work is noticing that one divides the other.
"""
import json, os, shutil

# hand-ranked, hardest first: these are the thirty separate arguments
BESPOKE_ORDER = list(range(1, 31))   # already in hardness order from the last rank;
                                     # see rank-map.json and the git history for how
                                     # that order was set

TIER = {"shared": 2, "telescoping": 3, "algfield": 4, "logexp": 5, "multiquad": 6,
        "cross": 7, "quadratic": 8, "closedform": 9, "ore": 10}


def order_all():
    cls = json.load(open("paper-classes.json"))
    eng = {int(k): v for k, v in json.load(open("paper-engines.json")).items()}
    bespoke = set(cls["bespoke"])
    shared = set(cls["shared"])
    missing = bespoke - set(BESPOKE_ORDER)
    extra = set(BESPOKE_ORDER) - bespoke
    if missing or extra:
        raise SystemExit(f"hand ranking out of step: missing {missing}, extra {extra}")

    ranked = list(BESPOKE_ORDER)                       # tier 1, already in order
    rest = []
    for num, v in sorted(eng.items()):
        if num in bespoke:
            continue
        tier = TIER["shared"] if num in shared else TIER.get(v["engine"], 8)
        rest.append((tier, -v["order"], -v["degree"], v["anum"], num))
    rest.sort()
    ranked += [t[-1] for t in rest]
    if len(ranked) != len(eng):
        raise SystemExit(f"lost papers: {len(ranked)} vs {len(eng)}")
    return ranked


def main():
    ranked = order_all()
    eng = {int(k): v for k, v in json.load(open("paper-engines.json")).items()}
    tmp = "papers-ranked"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    mapping = []
    for new, old in enumerate(ranked, start=1):
        suf = "DISPROOF" if eng[old]["disproof"] else "PROOF"
        shutil.copy(f"papers/{old}-{suf}.pdf", f"{tmp}/{new}-{suf}.pdf")
        mapping.append({"rank": new, "was": old, "anum": eng[old]["anum"],
                        "verdict": suf, "engine": eng[old]["engine"]})
    json.dump(mapping, open("rank-map.json", "w"), indent=1)
    print(f"{len(mapping)} papers ranked into {tmp}/")
    for m in mapping[:12]:
        print(f"   {m['rank']:4d}  (was {m['was']:3d})  {m['anum']}  {m['verdict']}")


if __name__ == "__main__":
    main()
