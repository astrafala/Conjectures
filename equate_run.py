#!/usr/bin/env python3
"""Sweep the conjectured closed forms and conjectured generating functions.

For each entry: take a description it states as fact, derive a recurrence from it, check
the conjectured description satisfies the same recurrence, and match initial terms. See
equate.py for why that is a proof rather than a check.
"""
import json, os, re, sys
import sympy as sp
import cfparse, equate, gfclean, timeoutrun
from equate import x, n
from regf import entry, GFL, EGFL
from holonomic import taylor
from parity_run import parse_with_rounding
from ore_prove import PROVEN, coeffs as rec_coeffs
import ore

RES = os.environ.get("RES", "equate-results.json")
CONJ = re.compile(r"^\s*Conjectur", re.I)
CONJ_GF = re.compile(r"^\s*Conjectur\w*\s*[:.]?\s*(o\.?g\.?f\.?|g\.?f\.?|e\.?g\.?f\.?)"
                     r"\s*[:.]", re.I)
CONJ_CF = re.compile(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*a\(n\)\s*=", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|it seems|probably", re.I)


def known_sides(F):
    """(generating functions, closed forms) the entry states as fact."""
    gfs, cfs = [], []
    for l in F:
        if GUESS.search(l):
            continue
        if GFL.match(l) or EGFL.match(l):
            gfs.append((("egf" if EGFL.match(l) else "ogf"), l))
        elif re.match(r"\s*a\(n\)\s*=", l):
            cfs.append(l)
    return gfs, cfs


def strip_conj(l):
    return re.sub(r"^\s*Conjectur\w*\s*\d*\s*[:.]?\s*", "", l, flags=re.I)


def work(a):
    F, data, off, name = entry(a)
    gfs, cfs = known_sides(F)
    conj_gfs = [l for l in F if CONJ_GF.match(l)]
    conj_cfs = [l for l in F if CONJ_CF.match(l) and "a(n-" not in l.replace(" ", "")]
    if not (conj_gfs or conj_cfs):
        return {"status": "no conjectured closed form or g.f."}

    # ---- the known side, as an operator ------------------------------------
    L = start = known_desc = None
    # The most direct known side of all: a recurrence the entry states as fact. Deriving
    # one from a generating function is only needed when the entry does not simply give
    # one, and nearly every failure in the first run was "no usable known description"
    # on an entry that had one all along.
    for l in F:
        if not PROVEN.match(l) or GUESS.search(l):
            continue
        if "a(n-" not in l.replace(" ", "") and "a(n+" not in l.replace(" ", ""):
            continue
        try:
            ps_known = rec_coeffs(l)
            cand = ore.to_operator(ps_known)
        except Exception:
            continue
        r_ = len(cand) - 1
        if r_ < 1:
            continue
        ok_ = True
        for m in range(off + r_, min(off + len(data), off + r_ + 8)):
            tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * data[m - i - off]
                      for i, p in enumerate(ps_known) if p != 0)
            if tot != 0:
                ok_ = False
                break
        if ok_:
            L, start, known_desc = cand, off, ("stated recurrence", l)
            break
    for mode, l in gfs:
        for c in gfclean.candidates(l):
            try:
                G = __import__("prove_rec").parse_gf(c, 'x', raw=c)
                base = taylor(G, off + min(len(data), 10) + 4)
                if mode == "egf":
                    base = [t * sp.factorial(i) for i, t in enumerate(base)]
            except Exception:
                continue
            for sh in ((0,) if mode == "egf" else (0, 1, 2, -1, -2)):
                idx = [off + k - sh for k in range(min(len(data), 10))]
                if any(i < 0 or i >= len(base) for i in idx):
                    continue
                try:
                    if not all(sp.simplify(base[i] - data[k]) == 0
                               for k, i in enumerate(idx)):
                        continue
                except Exception:
                    continue
                A = G if mode == "egf" else sp.together(x ** sh * G)
                if mode == "egf":
                    continue                 # the operator route below is for o.g.f.s
                got = equate.operator_from_gf(A)
                if got:
                    L, start = got
                    known_desc = ("generating function", c)
                    break
            if L:
                break
        if L:
            break
    if L is None:
        for l in cfs:
            e = cfparse.parse(l)
            if e is None:
                continue
            e, sh = cfparse.align(e, data, off)
            if e is None:
                continue
            got = equate.operator_from_closed_form(e)
            if got:
                L, start = got
                known_desc = ("closed form", l)
                break
    if L is None:
        return {"status": "no usable non-conjectural description to work from"}

    r = len(L) - 1
    bad = equate.leading_poles(L)
    n0 = max(off, start)
    while n0 in bad:
        n0 += 1
    if n0 + r > off + len(data):
        return {"status": "not enough published terms to pin the initial conditions"}

    # ---- the conjectured side ----------------------------------------------
    for l in conj_cfs:
        e = cfparse.parse(strip_conj(l)) or parse_with_rounding(strip_conj(l))
        if e is None:
            continue
        if not cfparse.matches(e, data, off):
            continue
        info = equate.cf_satisfies(e, L)
        if info is None:
            continue
        return {"status": "PROVED", "kind": "closed form", "conj": l,
                "known": known_desc[0], "known_src": known_desc[1],
                "operator": [sp.sstr(t) for t in L], "order": r,
                "from_n": int(n0), "leading_poles": [int(b) for b in bad]}
    for l in conj_gfs:
        for c in gfclean.candidates(re.sub(r"^\s*Conjectur\w*\s*[:.]?\s*", "", l)):
            try:
                G = __import__("prove_rec").parse_gf(c, 'x', raw=c)
                base = taylor(G, off + min(len(data), 10) + 4)
            except Exception:
                continue
            ok = False
            for sh in (0, 1, 2, -1, -2):
                idx = [off + k - sh for k in range(min(len(data), 10))]
                if any(i < 0 or i >= len(base) for i in idx):
                    continue
                try:
                    if all(sp.simplify(base[i] - data[k]) == 0
                           for k, i in enumerate(idx)):
                        G = sp.together(x ** sh * G)
                        ok = True
                        break
                except Exception:
                    pass
            if not ok:
                continue
            deg = equate.gf_satisfies(G, L)
            if deg is None:
                continue
            return {"status": "PROVED", "kind": "generating function", "conj": l,
                    "known": known_desc[0], "known_src": known_desc[1],
                    "operator": [sp.sstr(t) for t in L], "order": r,
                    "residual_degree": int(deg), "from_n": int(n0),
                    "leading_poles": [int(b) for b in bad]}
    return {"status": "the conjectured description does not satisfy the recurrence"}


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    per = int(os.environ.get("PER", "150"))
    for a in todo:
        if a in out:
            continue
        st, val = timeoutrun.call(work, (a,), timeout=per)
        rec = {"anum": a}
        rec.update(val if st == "ok" else
                   {"status": "timeout" if st == "timeout" else str(val)})
        if rec["status"] == "PROVED":
            print(f"{a}  PROVED  {rec['kind']} from the entry's {rec['known']}",
                  flush=True)
        out[a] = rec
        json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    from collections import Counter
    print(Counter(v["status"][:44] for v in out.values()))


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
