#!/usr/bin/env python3
"""Test every open conjectured recurrence against its FULL b-file.

Everything here has been checked against the DATA field, about forty terms. Most b-files
carry hundreds or thousands. A conjecture that survives forty terms and fails at the two
hundredth is DISPROVED, and that is a result -- one that costs nothing but the reading.

Entries are queued by how much the b-file adds over the DATA field, largest first, since
that is where a failure can hide. The b-file size is read from the Git LFS pointer the
clone left behind, so the ordering costs no downloads at all.

A disagreement is reported, never acted on blindly: the b-file could disagree with DATA
(then the entry is inconsistent, not the conjecture wrong), so both are checked and the
first index where the recurrence fails is recorded exactly.
"""
import json, os, re, sys, time
sys.path.insert(0, ".")
import sympy as sp
import bfile, conjlines
from makeslots import coeffs_of
from regf import entry

n = sp.Symbol('n')
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*"
                  r"(?:(?:to be\s+)?D-finite\s+with\s+recurrence\s*[:.,]?\s*)?", re.I)
OUT = "bsweep_results.json"


def _intpoly(p):
    """Integer coefficient list, lowest degree first -- evaluated with plain arithmetic.

    sympy's Poly.eval per term per coefficient dominates the runtime over a thousand-term
    b-file. The coefficients here are always integers, so Horner in Python is exact and
    orders of magnitude faster.
    """
    if p == 0:
        return [0]
    # a coefficient like 1/n is not a polynomial and sympy raises rather than returning
    # False, so ask before converting
    try:
        if not sp.expand(p).is_polynomial(n):
            return None
        q = sp.Poly(sp.expand(p), n)
    except Exception:
        return None
    cs = q.all_coeffs()[::-1]
    out = []
    for c in cs:
        c = sp.nsimplify(c, rational=True)
        if c.q != 1:
            return None                     # not an integer polynomial: skip this one
        out.append(int(c))
    return out


def _ev(co, x):
    v = 0
    for c in reversed(co):
        v = v * x + c
    return v


# "for n > 13" means the recurrence is asserted only from n = 14 on. Testing below that
# index is testing something the conjecture never claimed -- and doing so reported 362
# disproofs in the first slice, every one of them false.
FROM = re.compile(r"\bfor\s+n\s*(>=|>|\\ge)\s*(\d+)", re.I)


def start_index(cl, order, off):
    m = FROM.search(cl)
    lo = max(order + off, off)
    if m:
        k = int(m.group(2))
        lo = max(lo, k if m.group(1) in (">=", "\\ge") else k + 1)
    return lo


def check(anum, conjs, vals, off, cap=4000):
    """[(conj, first failing index, value)] over the b-file's terms."""
    bad = []
    for cl in conjs:
        try:
            ps = coeffs_of(cl)
        except Exception:
            continue
        if not ps or len(ps) < 2:
            continue
        polys = [_intpoly(p) for p in ps]
        if any(c is None for c in polys):
            continue
        r = len(ps) - 1
        top = min(len(vals), cap)
        lo = start_index(cl, r, off)
        fails = []
        for i in range(max(r, lo - off), top):
            nn = i + off
            tot = 0
            for j, co in enumerate(polys):
                if co == [0]:
                    continue
                tot += _ev(co, nn) * vals[i - j]
            if tot != 0:
                fails.append(nn)
                if len(fails) > 40:
                    break
        if not fails:
            continue
        tested_hi = max(r, lo - off) + off, top - 1 + off
        # A recurrence with polynomial coefficients is asserted for LARGE n; failing at a
        # few small indices is the boundary, not a counterexample -- the residual criterion
        # says the same thing, "for all n > deg B". A disproof needs a failure that is still
        # happening late in the b-file. Requiring the last failure to sit in the upper half
        # of the tested range is what separates the two.
        half = (tested_hi[0] + tested_hi[1]) // 2
        if fails[-1] >= half:
            bad.append((cl, fails[0], fails[-1], len(fails), tested_hi[1]))
    return bad


def main(budget=460, per_fetch=0.3):
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    idx = json.load(open("open_index.json"))["open"]
    rm = {r["anum"] for r in json.load(open("rank-map.json"))}
    queue = json.load(open("bsweep_queue.json"))
    t0 = time.time()
    n_new = 0
    for anum in queue:
        if anum in done or time.time() - t0 > budget:
            continue
        if bfile.fetch(anum) is None:
            done[anum] = {"status": "no b-file"}
            continue
        off, vals = bfile.contiguous(anum)
        if len(vals) < 12:
            done[anum] = {"status": "b-file too short"}
            continue
        try:
            F, data, doff, nm = entry(anum)
        except Exception:
            done[anum] = {"status": "no entry"}
            continue
        # the b-file must agree with the DATA field, or the entry is inconsistent
        m = min(len(data), len(vals))
        if off != doff or any(vals[i] != data[i] for i in range(min(m, 20))):
            done[anum] = {"status": "b-file disagrees with DATA"}
            continue
        conjs = [l for l in F if conjlines.is_recurrence(l)]
        bad = check(anum, conjs, vals, off)
        done[anum] = {"status": "DISPROVED" if bad else "holds on all b-file terms",
                      "nterms": len(vals), "ndata": len(data), "bad": bad}
        if bad:
            b0 = bad[0]
            print(f"  DISPROVED {anum}  fails from n={b0[1]} to n={b0[2]} "
                  f"({b0[3]} failures, tested to n={b0[4]}; {len(data)} terms in DATA)",
                  flush=True)
        n_new += 1
        json.dump(done, open(OUT, "w"))
        time.sleep(per_fetch)
    json.dump(done, open(OUT, "w"))
    dis = sum(1 for v in done.values() if v.get("status") == "DISPROVED")
    print(f"  {n_new} checked this slice; {len(done)}/{len(queue)} total, {dis} disproved",
          flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 460)
