#!/usr/bin/env python3
"""Harvest recurrence conjectures that ride along for free.

An OEIS entry often carries several conjectured recurrences. A paper settles one of
them; the others sit on the same generating function and the same argument applies
verbatim, but they were never counted. This collects, for every entry we have a paper
on, the conjecture lines we did NOT use.
"""
import json, os, re

ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"Conjecture", re.I)


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def lines_of(a):
    p = f"{ROOT}/{a[:4]}/{a}.seq"
    out = []
    if not os.path.exists(p):
        return out
    for l in open(p, errors="ignore"):
        if l[:2] == "%C" or l[:2] == "%F" or l[:2] == "%e":
            out.append(re.sub(r"^A\d{6}\s*", "", l[3:].strip()))
    return out


def main():
    pmap = {int(k): v for k, v in json.load(open("paper-map.json")).items()}
    used_conj = {}
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json"):
        if os.path.exists(f):
            for a, v in json.load(open(f)).items():
                if v.get("conj"):
                    used_conj.setdefault(a, set()).add(norm(v["conj"]))
    for f in ("rec-cache.json",):
        c = json.load(open(f))["seen"]
        for a, v in c.items():
            if v and v.get("conj"):
                used_conj.setdefault(a, set()).add(norm(v["conj"]))
    for f in ("egf-cache.json",):
        for a, v in json.load(open(f)).items():
            if v and v.get("conj"):
                used_conj.setdefault(a, set()).add(norm(v["conj"]))

    out = {}
    mine = {num: a for num, a in pmap.items() if num >= 29}
    for num, a in sorted(mine.items()):
        others = []
        for l in lines_of(a):
            if not CONJ.search(l):
                continue
            if "a(n-" not in l.replace(" ", ""):
                continue
            if "=0" not in l.replace(" ", ""):
                continue
            if norm(l) in used_conj.get(a, set()):
                continue
            if any(norm(l) == norm(o) for o in others):
                continue
            others.append(l)
        if others:
            out.setdefault(a, {"papers": [], "others": others})["papers"].append(num)
    json.dump(out, open("extra2-conj.json", "w"), indent=1, sort_keys=True)
    tot = sum(len(v["others"]) for v in out.values())
    print(f"{len(out)} entries carry {tot} uncounted recurrence conjectures")


if __name__ == "__main__":
    main()
