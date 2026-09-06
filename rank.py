#!/usr/bin/env python3
"""Order the whole roster by how hard the result was to get, and renumber accordingly.

Rank 1 is the hardest. The ordering is a judgement, so it is written down rather than
buried: papers are grouped into tiers by what the proof actually required, and within a
tier by the size of the object being handled -- the order of the recurrence first, then
the degree of the residual.

The tiers, hardest first:

  1. a separate argument found for that one problem
  2. one real theorem, proved once and applied to twenty entries -- and, at the same
     level, the reduction of a Stirling-transform sequence modulo k to an integer
     combination of the functions n -> i^n, which settles a periodicity conjecture that
     no amount of computing terms can settle
  3. a conjectured CLOSED FORM or GENERATING FUNCTION, proved by deriving a recurrence
     from what the entry asserts and showing the conjectured description satisfies it
  4. a conjecture shown FALSE, with the recurrence that holds instead derived and
     proved -- ranked here for what the result is, not for the machinery: the residual
     test returning a negative is no harder than returning a positive, but the paper
     carries a correction nobody had
  5. a recurrence derived from the summand by telescoping over a range whose summand
     does NOT vanish at the ends, so the boundary and range corrections are carried
     through and the resulting inhomogeneity cleared
  5. a recurrence DERIVED from the summand by creative telescoping, not verified
  6. the generating function itself DERIVED from a coefficient-extraction definition,
     by Lagrange inversion and elimination -- the entry posts no g.f. at all
  6. a general algebraic function field: nested radicals, implicit or reversion g.f.s
  7. a transcendental e.g.f., handled in a differential module over Q(x)
  8. a posted closed form, split on the parity of n, then decided by the theory of
     hypergeometric terms -- again no generating function anywhere
  9. the same without the parity split
 10. several independent square roots
 11. an identity between different entries
 12. one square root, or none: the standard residual test
 13. a closed form compared against the posted generating function
 14. division of one posted operator by another

The last is honestly the shallowest thing here: both recurrences were already on the
entry and the work is noticing that one divides the other.
"""
import json, os, shutil

# hand-ranked, hardest first: these are the thirty separate arguments
BESPOKE_ORDER = list(range(1, 31))   # already in hardness order from the last rank;
                                     # see rank-map.json and the git history for how
                                     # that order was set

TIER = {"shared": 2, "stirling-phi": 2, "gauss-congruence": 2, "equate": 3, "disproof": 4, "section": 3, "funceq-mod": 3, "transfer-matrix": 6, "subblock-3x3": 6, "king-move": 6, "neighbour-set": 6, "reciprocal-link": 6, "pattern-neighbour": 5, "pattern-subblock": 5, "subblock-matrix": 5, "index-change": 4, "relabelling": 5, "circular-coloring": 5, "global-count": 5, "budget": 4, "order-flag": 5, "order-cond": 5, "common-sum": 5, "order-statistic": 6, "monotone-subblock": 6, "subblock-coloring": 6, "subblock-difference": 6, "matrix-subblock": 6, "commuting-subblock": 6, "edge-count": 6, "perimeter-cycle": 6, "edge-count-pattern": 5, "subblock-neighbour": 5, "cell-condition": 6, "cell-condition-pattern": 5, "defective": 4, "image-count": 4, "occupancy-image": 4, "occupancy-turn": 4, "consecutive-triple": 5, "monotone-statistic": 6, "clashing-pair": 5, "pattern-avoidance": 6, "all-values-subblock": 5, "self-count": 5, "digit-divisibility": 5, "ray-sum": 5, "modular-neighbour": 5, "offset-inequality": 5, "repeated-value": 5, "forbidden-run": 6, "subblock-line-sum": 6, "adjacency-precedence": 6, "value-neighbour": 6, "capped-pair-count": 5, "pair-sum-order": 5, "distance-inequality": 5, "clockwise-perimeter": 6, "lex-subblock-statistic": 5, "graph-adjacency-array": 5, "graph-array-lumped": 4, "neighbour-arithmetic": 5, "chessboard-colour-class": 4, "symmetric-sum-zero": 3, "neighbour-existential": 5, "subblock-statistic-neighbour": 6, "array-permutation": 5, "minmax-median": 6, "subblock-content": 6, "table-column": 5, "walk-closed-form": 5, "telescoping-boundary": 5,
        "telescoping": 6, "diagonal": 7, "algfield": 8, "logexp": 9, "parity": 10,
        "closedform-direct": 11, "holonomic": 11, "gf-implies-rec": 12, "order-recovery": 4, "table-order-recovery": 4, "multiquad": 12, "cross": 13, "quadratic": 14,
        "closedform": 15, "ore-complete": 16, "ore": 17,
        # the known side is the entry's NAME rather than a formula line. The mathematics is
        # hyperterm's, so the tier is closedform's; what differs is where the input came
        # from, not how hard the argument is.
        "closedform-name": 15}


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
        tier = TIER["shared"] if num in shared else TIER.get(v["engine"], 14)
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
        # read from the was-keyed master, not from papers/, which after the first ranking
        # holds the RANK numbering: reading it here would copy whatever paper happens to
        # sit at that rank now.
        shutil.copy(f"papers-old-numbering/{old}-{suf}.pdf", f"{tmp}/{new}-{suf}.pdf")
        mapping.append({"rank": new, "was": old, "anum": eng[old]["anum"],
                        "verdict": suf, "engine": eng[old]["engine"]})
    json.dump(mapping, open("rank-map.json", "w"), indent=1)
    print(f"{len(mapping)} papers ranked into {tmp}/")
    for m in mapping[:12]:
        print(f"   {m['rank']:4d}  (was {m['was']:3d})  {m['anum']}  {m['verdict']}")


if __name__ == "__main__":
    main()
