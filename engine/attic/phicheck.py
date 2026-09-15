#!/usr/bin/env python3
"""Test the Bala family "a(n) mod k is (eventually) periodic with period dividing phi(k)".

The claim, for a given k, is a(n+phi(k)) == a(n) (mod k) for all n in range. A single
failure inside the published terms is a counterexample -- to the PURE form immediately,
and to the EVENTUAL form only if failures persist to the end of the data (an eventual
claim tolerates any finite prefix). Both verdicts are reported separately and neither is
guessed at.
"""
import json, re
from sympy import totient
import entry

PURE = re.compile(r"purely periodic|is periodic", re.I)


def terms(anum):
    e = entry.get(anum)
    off = int(e["offset"].split(",")[0])
    d = [int(x) for x in e["data"].split(",")]
    return off, d


def test(anum, kmax=64):
    off, d = terms(anum)
    N = len(d)
    out = []
    for k in range(2, kmax + 1):
        p = int(totient(k))
        if p >= N - 2:                      # too few terms to test this k at all
            continue
        bad = [n for n in range(off, off + N - p) if (d[n - off] - d[n + p - off]) % k]
        if not bad:
            continue
        last = bad[-1]
        # an eventual claim survives failures confined to a prefix; require the last
        # failure to sit in the final quarter of what the data can test
        end = off + N - p - 1
        eventual = last >= off + 3 * (end - off) // 4
        out.append({"k": k, "phi": p, "nbad": len(bad), "first": bad[0],
                    "last": last, "end": end, "kills_eventual": eventual})
    return out


def main():
    rows = json.load(open("periodic-phi.json"))
    res = {}
    for r in rows:
        a = r["anum"]
        pure = bool(PURE.search(r["conj"])) and "eventually" not in r["conj"].lower()
        try:
            hits = test(a)
        except Exception as e:
            res[a] = {"error": str(e)}
            continue
        res[a] = {"pure": pure, "hits": hits, "nterms": len(terms(a)[1])}
    json.dump(res, open("phicheck_results.json", "w"), indent=1)
    for a, v in sorted(res.items()):
        if v.get("error"):
            print(f"{a}  ERROR {v['error']}")
            continue
        h = v["hits"]
        ev = [x for x in h if x["kills_eventual"]]
        tag = ""
        if v["pure"] and h:
            tag = "  <-- kills PURE form"
        if ev:
            tag += "  <-- kills EVENTUAL form"
        print(f"{a}  terms={v['nterms']:3d}  pure={v['pure']}  failing k: "
              f"{[x['k'] for x in h][:8]}{tag}")


if __name__ == "__main__":
    main()
