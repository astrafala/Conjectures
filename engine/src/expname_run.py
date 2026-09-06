#!/usr/bin/env python3
"""Settle a conjectural recurrence from the generating function named in the entry's TITLE.

An entry called "Expansion of (1+x^6)/((1-x)*(1-x^2)*(1-x^3))" does not merely happen to
have that generating function -- that is what the sequence IS. Every g.f. engine here
(rational, quadratic, multiquadratic, general algebraic) has always read %F lines for its
input and never the name, so 141 open entries were sitting in front of machinery already
built for exactly them.

The name is turned into a g.f. candidate, strict_gf checks it against every published term
before it is used, and decide.decide_one runs the residual-polynomial criterion: with
theta = x d/dx, the conjecture holds for all n > deg B exactly when
B(x) = sum_i x^i (p_i(theta+i)A)(x) is a polynomial.
"""
import json, os, re, sys
sys.path.insert(0, ".")
import gfclean, conjlines, decide
from regf import entry
import timeoutrun

MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*(D-finite with recurrence\s*)?", re.I)
EGF = re.compile(r"\be\.?g\.?f\b|exponential", re.I)


def attack(item):
    a, name = item
    F, data, off, nm = entry(a)
    body = re.sub(r"^\s*Expansion of\s*", "", name, flags=re.I)
    egf = bool(EGF.search(body))
    body = re.sub(r"^\s*(e\.g\.f\.|g\.f\.|o\.g\.f\.)\s*:?\s*", "", body, flags=re.I)
    cands = gfclean.candidates("G.f.: " + body)
    if not cands:
        return ("no", "no g.f. parsed out of the name")
    out = []
    for cl in [l for l in F if conjlines.is_recurrence(l)]:
        conj = MARK.sub("", cl)
        r = decide.decide_one(conj, data, off, egf, cands)
        out.append((r.get("status"), cl, r))
    return ("ok", out)


if __name__ == "__main__":
    cands = json.load(open("expname_cands.json"))
    print(f"{len(cands)} entries", flush=True)
    hits, dis = [], []
    for i, it in enumerate(cands):
        st, r = timeoutrun.call(attack, (it,), timeout=240)
        if st != "ok" or r[0] != "ok":
            continue
        for status, cl, rec in r[1]:
            if status == "PROVED":
                hits.append({"anum": it[0], "conj": cl, "name": it[1], **rec})
                print(f"  PROVED    {it[0]}  {cl[:60]}", flush=True)
            elif status == "DISPROVED":
                dis.append({"anum": it[0], "conj": cl, "name": it[1], **rec})
                print(f"  DISPROVED {it[0]}  fails at n={rec.get('fails_at')}", flush=True)
        if i % 25 == 0:
            print(f"  ...{i}", flush=True)
    json.dump(hits, open("expname_hits.json", "w"), indent=1)
    json.dump(dis, open("expname_dis.json", "w"), indent=1)
    print(f"\n{len(hits)} proved, {len(dis)} disproved")
