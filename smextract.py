#!/usr/bin/env python3
"""Harvest the Sequence Machine's conjectures that this toolkit can actually decide.

The OEIS is not the only place conjectures live. The Sequence Machine (sequencedb.net,
data at github.com/jonmaiga/sequence-machine-data) holds ~1.97 million machine-generated
formulas for OEIS sequences, found by executing generated stack machines and keeping what
matches the published terms. They are conjectural by construction: the README says so.

Most are out of reach for the same reason the OEIS cross-entry vein was -- 65% of them name
another A-number, and resolving those needs the referenced entry to have a closed form of
its own. What is in reach is the class that states a RATIONAL GENERATING FUNCTION,

    A053208:  ogf((3x+x^2)/(1-3x+2x^2))

because a rational g.f. is equivalent to a constant-coefficient linear recurrence, and
deciding whether a sequence with a known closed form satisfies one is exactly what
hyperterm.py does. The OEIS entry supplies the known side; the Sequence Machine supplies
the conjecture.

Only programs that are unproven, not already sourced from the OEIS, and matching at least
200 published terms are kept.
"""
import json, os, re, sys

ROOT = "/home/user/jonmaiga/sequence-machine-data/oeis"
OUT = "sm_ogf.json"
KIND = re.compile(r"^(ogf|egf)\(", re.I)
XREF = re.compile(r"A\d{6}")


def main():
    got = json.load(open(OUT)) if os.path.exists(OUT) else {"done": [], "hits": []}
    done = set(got["done"])
    hits = got["hits"]
    dirs = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    for d in dirs:
        if d in done:
            continue
        dd = os.path.join(ROOT, d)
        for fn in os.listdir(dd):
            if not fn.endswith(".programs.json"):
                continue
            try:
                j = json.load(open(os.path.join(dd, fn)))
            except Exception:
                continue
            a = "A%06d" % j.get("oi", 0)
            for p in j.get("ps", []):
                if "proven" in (p.get("tags") or []) or p.get("s") == "oeis":
                    continue
                if p.get("mt", 0) < 200:
                    continue
                ix = p.get("ix", "")
                if not KIND.match(ix) or XREF.search(ix):
                    continue
                hits.append({"anum": a, "ix": ix, "mt": p["mt"], "date": p.get("d")})
        done.add(d)
        json.dump({"done": sorted(done), "hits": hits}, open(OUT, "w"))
    print(f"{len(done)}/{len(dirs)} directories, {len(hits)} generating-function conjectures")


if __name__ == "__main__":
    main()
