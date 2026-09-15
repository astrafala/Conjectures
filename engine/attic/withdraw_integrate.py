#!/usr/bin/env python3
"""Withdraw six papers whose conjectures turn out to be settled, and add the six
coefficient-extraction results.

The six withdrawals were found by re-running the settlement scan with a pattern that
matches "verifies" and "proves", not only "verified" and "proved". Each hit was read
before acting on it; the ones kept are recorded in the ledger with the wording that
was judged not to settle anything.
"""
import json, os, shutil

WITHDRAW = {                     # paper number in the pre-rank numbering -> why
    86:  ("A081923", "P. Bala, Sep 25 2013: Zeilberger's algorithm on Walsh's sum gives "
                     "a first-order recurrence, from which 'it is easy to verify that "
                     "a(n) satisfies the second-order recurrence ... conjectured above'"),
    250: ("A162477", "E. Munarini, Aug 31 2017: gives the closed g.f. and states that "
                     "'using this form of the g.f., it is straightforward to prove the "
                     "above conjectured recurrence'"),
    287: ("A093387", "the entry carries a full proof of Mathar's conjecture from the "
                     "two recursions, worked through both parities"),
    333: ("A106272", "P. Hadjicostas, Jul 15 2019: generating-function proof on the "
                     "entry, ending 'which proves the conjecture'"),
    380: ("A106271", "P. Hadjicostas, Jul 15 2019: generating-function proof on the "
                     "entry, ending 'which proves the conjecture'"),
    391: ("A155587", "P. Hadjicostas, Aug 03 2020: derives the recurrence from the "
                     "Catalan relation, 'implies R. J. Mathar's conjecture'"),
}

# A156894 paper 3 of the extraction build is dropped for the same reason: P. Bala,
# Oct 05 2015, "the Maple command sumrecursion ... verifies this recurrence".
DIAG_SKIP = {3}


def main():
    eng = {int(k): v for k, v in json.load(open("paper-engines.json")).items()}
    cls = json.load(open("paper-classes.json"))

    shutil.rmtree("papers", ignore_errors=True)
    shutil.copytree("papers-old-numbering", "papers")

    for num, (a, why) in sorted(WITHDRAW.items()):
        assert eng[num]["anum"] == a, (num, eng[num]["anum"], a)
        suf = "DISPROOF" if eng[num]["disproof"] else "PROOF"
        os.remove(f"papers/{num}-{suf}.pdf")
        del eng[num]
        print(f"withdrawn {num:4d}  {a}")
    cls["mechanical"] = [n for n in cls["mechanical"] if n not in WITHDRAW]

    spec = {s["num"]: s for s in json.load(open("diag-build.json"))}
    nxt = max(eng) + 1
    for f in sorted(os.listdir("papers-new"), key=lambda s: int(s.split("-")[0])):
        old = int(f.split("-")[0])
        if old in DIAG_SKIP:
            print(f"not added  {spec[old]['anum']}  settled on the entry")
            continue
        s = spec[old]
        shutil.copy(f"papers-new/{f}", f"papers/{nxt}-PROOF.pdf")
        eng[nxt] = {"engine": "diagonal", "order": s["order"], "degree": s["degree"],
                    "anum": s["anum"], "disproof": False}
        cls["mechanical"].append(nxt)
        print(f"added     {nxt:4d}  {s['anum']}")
        nxt += 1

    json.dump({str(k): v for k, v in eng.items()},
              open("paper-engines.json", "w"), indent=1, sort_keys=True)
    json.dump(cls, open("paper-classes.json", "w"), indent=1)
    print(f"\nroster now {len(eng)} papers")


if __name__ == "__main__":
    main()
