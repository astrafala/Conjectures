#!/usr/bin/env python3
"""Decide congruence and divisibility conjectures with a fixed modulus.

The sequence's recurrence comes from whatever the entry gives: one it states outright,
or one derived from its generating function or closed form (equate.py). Modulo a fixed k
the state space is finite, so the sequence is eventually periodic with a computable
pre-period and period (modper.py), and the conjecture is then decided by inspecting one
period -- proved or refuted, never left open.
"""
import json, os, re, sys
import sympy as sp
import congparse, equate, equate_run, modper, ore, timeoutrun
from equate import n
from regf import entry
from ore_prove import coeffs as rec_coeffs, PROVEN

RES = os.environ.get("RES", "cong-results.json")
CONJ = re.compile(r"^\s*Conjectur", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|probably", re.I)


def operator_for(a, F, data, off):
    """(coefficients of N^0.., description) for a recurrence the entry supports."""
    for l in F:
        if not PROVEN.match(l) or GUESS.search(l):
            continue
        if "a(n-" not in l.replace(" ", "") and "a(n+" not in l.replace(" ", ""):
            continue
        try:
            ps = rec_coeffs(l)
            L = ore.to_operator(ps)
        except Exception:
            continue
        r = len(L) - 1
        if r < 1:
            continue
        ok = True
        for m in range(off + r, min(off + len(data), off + r + 8)):
            tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * data[m - i - off]
                      for i, p in enumerate(ps) if p != 0)
            if tot != 0:
                ok = False
                break
        if ok:
            return L, ("a recurrence the entry states", l)
    got = equate_run.work(a)          # reuse its search for a derivable recurrence
    if isinstance(got, dict) and got.get("operator"):
        return [sp.sympify(t) for t in got["operator"]], ("a derived recurrence",
                                                          got.get("known_src", ""))
    return None, None


def decide(a):
    F, data, off, name = entry(a)
    conjs = [l for l in F if CONJ.match(l) and not SETTLED.search(l)
             and congparse.parse(l) is not None]
    if not conjs:
        return {"status": "no decidable congruence conjecture"}
    L, desc = operator_for(a, F, data, off)
    if L is None:
        return {"status": "no recurrence available for this entry"}
    r = len(L) - 1
    if len(data) < r:
        return {"status": "not enough published terms to start the recurrence"}
    out = []
    for l in conjs:
        c, k, n_from, residues, m = congparse.parse(l)
        if k < 2 or k > 5000:
            out.append((l, "modulus out of range"))
            continue
        per = modper.eventual_period(L, data[:r], off, k)
        if per is None or (isinstance(per, tuple) and per[0] == "not invertible"):
            out.append((l, f"the leading coefficient is not invertible mod {k}"
                           if per else "could not compute the period"))
            continue
        start, period = per
        vals = modper.values(L, data[:r], off, k, start + 2 * period + r + 2)
        if vals is None:
            out.append((l, "could not tabulate the residues"))
            continue
        lo = max(off, n_from if n_from is not None else off, start)
        idx = range(lo, start + period + max(0, lo - start))
        bad = []
        for mm in idx:
            if mm - off >= len(vals):
                break
            if residues and (mm % m) not in [rr % m for rr in residues]:
                continue
            if vals[mm - off] % k != c % k:
                bad.append(mm)
        if bad:
            out.append((l, f"FALSE: fails at n={bad[:4]}"))
        else:
            out.append((l, f"PROVED: a(n) mod {k} is eventually periodic from n={start} "
                           f"with period {period}, and the residue is {c % k} throughout "
                           f"the claimed range"))
    return {"status": "done", "operator": [sp.sstr(t) for t in L],
            "known": desc[0], "known_src": desc[1],
            "results": [{"conj": l, "verdict": v} for l, v in out]}


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    per = int(os.environ.get("PER", "150"))
    for a in todo:
        if a in out:
            continue
        st, val = timeoutrun.call(decide, (a,), timeout=per)
        rec = {"anum": a}
        rec.update(val if st == "ok" else {"status": st})
        for r_ in rec.get("results", []):
            if r_["verdict"].startswith(("PROVED", "FALSE")):
                print(f"{a}  {r_['verdict'][:70]}", flush=True)
        out[a] = rec
        json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    from collections import Counter
    print(Counter(v["status"][:40] for v in out.values()))


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
