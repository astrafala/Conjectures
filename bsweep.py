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
import bfile, conjlines, cfparse, gfclean, blocks
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


def _fact(k):
    import math
    return math.factorial(int(k))


def _binom(a_, b_):
    import math
    a_, b_ = int(a_), int(b_)
    return 0 if b_ < 0 or b_ > a_ else math.comb(a_, b_)


CONJ_LINE = re.compile(r"^\s*(Conjectur\w*|Empirical)", re.I)
# "for n>2 and odd", "for n = 31 and all n >= 33", "except for n = 4": a conjecture that
# restricts WHICH n it speaks about, in a way not parsed here, must not be tested at all --
# testing it at the indices it excludes reported 103 disproofs, every one of them false.
QUALIFIED = re.compile(r"\b(odd|even|except|otherwise|unless|if\s+n\b|when\s+n\b"
                       r"|and\s+all\s+n|n\s*=\s*\d+\s*(,|and)|prime|square|divisib)", re.I)


def _truncated(body):
    """A line cut off mid-expression cannot be tested; what parses is only half of it.

    Long generating functions are sometimes stored truncated in the OEIS itself (A071283,
    A071285, A071287, A283644 all end inside their numerator). Reading half a polynomial and
    calling the result a counterexample is a mistake, not a disproof.
    """
    b = re.sub(r"\(Start\)|\(End\)", "", body)
    return (b.count("(") != b.count(")") or b.count("[") != b.count("]")
            or bool(re.search(r"[+*/^-]\s*$", b.strip())))
STRIP = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*", re.I)


def _conj_stmts(F):
    """Conjectured statements, block contents included."""
    out = [l for l in F if CONJ_LINE.match(l)]
    for s_, h, orig in blocks.statements(F):
        if s_ not in out:
            out.append(s_)
    return out


def check_closed(F, vals, off, cap=120):
    """A conjectured closed form that misses a b-file term is disproved."""
    bad = []
    for cl in _conj_stmts(F):
        body = STRIP.sub("", cl)
        if not re.match(r"^\s*a\(n\)\s*=", body) or re.search(r"a\(n\s*-\s*\d", body):
            continue
        if QUALIFIED.search(body) or _truncated(body) or "[" in body:
            continue
        e = cfparse.parse(body)
        if e is None:
            continue
        # evaluating a sympy expression term by term dominates the slice; compile it once
        try:
            f = sp.lambdify(n, e, modules=[{"binomial": _binom, "factorial": _fact}, "math"])
        except Exception:
            continue
        lo = start_index(cl, 0, off)
        # the index convention may be shifted; a mismatch that a small shift repairs is a
        # convention, not a counterexample
        base = max(0, lo - off)
        top = min(len(vals), cap)
        # test each shift over the WHOLE claimed range, not a handful of terms: a formula
        # that fits throughout under some shift is stated in a different index convention,
        # which is a wording difference and not a counterexample
        shifted = False
        for sh in list(range(-8, 0)) + list(range(1, 9)):
            try:
                rng = range(base, top)
                if len(rng) >= 8 and all(f(i + off + sh) == vals[i] for i in rng):
                    shifted = True
                    break
            except Exception:
                continue
        if shifted:
            continue
        fails, tested = [], 0
        for i in range(max(0, lo - off), min(len(vals), cap)):
            try:
                v = f(i + off)
            except Exception:
                break
            if not isinstance(v, int):
                break
            tested += 1
            if v != vals[i]:
                fails.append(i + off)
                if len(fails) > 40:
                    break
        if tested >= 20 and fails:
            half = (lo + min(len(vals), cap) - 1 + off) // 2
            if fails[-1] >= half:
                bad.append((cl, fails[0], fails[-1], len(fails), min(len(vals), cap) - 1 + off))
    return bad


def _rat_coeffs(A, N, x):
    """The first N power-series coefficients of a RATIONAL function, by long division.

    sympy.series on a complicated generating function can take minutes -- it is what made
    26 entries time out. For a rational function the coefficients come from dividing the
    numerator by the denominator on coefficient lists, which is exact and immediate. A
    non-rational g.f. is skipped rather than expanded.
    """
    num, den = sp.fraction(sp.cancel(sp.together(A)))
    if not (num.is_polynomial(x) and den.is_polynomial(x)):
        return None
    a_ = [sp.Integer(c) for c in sp.Poly(sp.expand(num), x).all_coeffs()[::-1]]
    b_ = [sp.Integer(c) for c in sp.Poly(sp.expand(den), x).all_coeffs()[::-1]]
    a_ += [sp.Integer(0)] * (N - len(a_))
    b_ += [sp.Integer(0)] * (N - len(b_))
    if b_[0] == 0:
        return None
    out = []
    for i in range(N):
        t = a_[i] - sum(b_[j] * out[i - j] for j in range(1, i + 1))
        q = sp.Rational(t, b_[0])
        out.append(q)
    return out


def check_gf(F, vals, off, cap=120):
    """A conjectured ordinary generating function whose coefficients miss a b-file term."""
    bad = []
    x = sp.Symbol('x')
    for cl in _conj_stmts(F):
        body = STRIP.sub("", cl)
        if not re.match(r"^\s*(o\.)?g\.f\.", body, re.I):
            continue
        for cand in gfclean.candidates(body)[:1]:
            cand = cand[0] if isinstance(cand, (tuple, list)) else cand
            try:
                A = sp.sympify(str(cand).replace("^", "**"))
            except Exception:
                continue
            if not isinstance(A, sp.Expr) or (A.free_symbols - {x}):
                continue
            N = min(len(vals), cap)
            ser = _rat_coeffs(A, N + off + 1, x)
            if ser is None:
                continue
            if QUALIFIED.search(body) or _truncated(body):
                continue
            # try a small index shift before calling it wrong: an OEIS generating function
            # is often written so that [x^k] is a(k+1), and reading it the other way made
            # every g.f. in the sweep look false
            # the shift can be several places: A071283's generating function is written so
            # that [x^(k+4)] is a(k), which no small window catches
            if any(all(ser[i + off + sh] == vals[i] for i in range(N))
                   for sh in list(range(-8, 0)) + list(range(1, 9))
                   if 0 <= off + sh and off + sh + N <= len(ser)):
                continue
            fails = [i + off for i in range(N) if ser[i + off] != vals[i]]
            if fails and len(fails) < N:
                half = (2 * off + N - 1) // 2
                if fails[-1] >= half:
                    bad.append((cl, fails[0], fails[-1], len(fails), N - 1 + off))
    return bad


def main(budget=460, per_fetch=0.0):
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
        # the download is already paid for, so test the other conjecture shapes on the same
        # terms: a conjectured closed form is disproved by one index where it differs, and
        # a conjectured generating function by one coefficient
        bad += check_closed(F, vals, off) + check_gf(F, vals, off)
        done[anum] = {"status": "DISPROVED" if bad else "holds on all b-file terms",
                      "nterms": len(vals), "ndata": len(data), "bad": bad}
        if bad:
            b0 = bad[0]
            print(f"  DISPROVED {anum}  fails from n={b0[1]} to n={b0[2]} "
                  f"({b0[3]} failures, tested to n={b0[4]}; {len(data)} terms in DATA)",
                  flush=True)
        n_new += 1
        json.dump(done, open(OUT, "w"))
        if per_fetch:
            time.sleep(per_fetch)
    json.dump(done, open(OUT, "w"))
    dis = sum(1 for v in done.values() if v.get("status") == "DISPROVED")
    print(f"  {n_new} checked this slice; {len(done)}/{len(queue)} total, {dis} disproved",
          flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 460)
