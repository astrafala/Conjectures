#!/usr/bin/env python3
"""Run the residual criterion as a DECISION procedure over every open conjecture.

The criterion is an equivalence: with B(x) = sum_i x^i (p_i(theta+i)A)(x), the coefficient
of x^n in B is exactly sum_i p_i(n) a(n-i). So B polynomial of degree d proves the
recurrence for n > d, and B not polynomial DISPROVES it for infinitely many n. Both
answers are results.

Every earlier sweep recorded only the first as a finding and logged the second as a
failure, which is why four disproofs sat unnoticed in the result files. This runs the
same computation over the whole open set and keeps both.

For a disproof the standard is higher than for a proof, so:
  * the generating function must reproduce EVERY published term, not a sample;
  * a smallest explicit counterexample is computed and recorded;
  * the conjecture must fail under every joint re-indexing in a small window, since a
    recurrence stated against a since-changed offset is a slip, not a false statement.
"""
import json, os, re, sys
import sympy as sp
import gfclean
import algfield as af
import quadfield as qf, multiquad as mq, logexp as le
from regf import entry, CONJ, GFL, EGFL
from prove_rec import parse_gf, parse_conj
from holonomic import taylor

x, n = sp.symbols('x n')
RES = os.environ.get("RES", "decide-results.json")


import timeoutrun


def strict_gf(cands, data, off, egf, extra=30):
    """A g.f. reproducing EVERY published term, with its coefficient list."""
    N = off + len(data) + extra
    for c in cands:
        try:
            G = parse_gf(c, 'x', raw=c)
            base = taylor(G, N)
            if egf:
                base = [t * sp.factorial(i) for i, t in enumerate(base)]
        except Exception:
            continue
        for sh in ((0,) if egf else (0, 1, 2, 3, -1, -2, -3)):
            idx = [off + k - sh for k in range(len(data))]
            if any(i < 0 or i >= len(base) for i in idx):
                continue
            A = G if egf else sp.together(x ** sh * G)
            try:
                co = taylor(A, N) if not egf else base
            except Exception:
                continue
            try:
                if all(sp.simplify(co[off + k] - data[k]) == 0
                       for k in range(len(data))):
                    return c, A, co, []
            except Exception:
                continue
            # a posted g.f. that is right from some index on but wrong at the first term
            # or two is an offset convention, not a different sequence. Adding the
            # correcting polynomial keeps A algebraic and shifts the residual by a
            # polynomial, so the criterion still applies -- and the paper says so.
            fix = gfclean.polynomial_correction(co, data, off)
            if fix is None:
                continue
            diffs, _ = fix
            if not diffs:
                return c, A, co, []
            corr = sum(v * x ** i for i, v in diffs)
            A2 = sp.together(A + corr)
            co2 = list(co)
            for i, v in diffs:
                co2[i] = sp.nsimplify(co[i] + v, rational=True)
            if all(sp.simplify(co2[off + k] - data[k]) == 0 for k in range(len(data))):
                return c, A2, co2, diffs
    return None, None, None, []


def malformed(conj):
    """A conjecture whose written form is suspect: a repeated or missing shift.

    A202020 posts "... + 4*(11-14n)*a(n-4) + 12*(n-1)*a(n-4) = 0" -- a(n-4) twice and no
    a(n-3). Parsing merges the duplicates and the result fails on the entry's own terms,
    which looks exactly like a disproof and is not one: replacing the second a(n-4) with
    a(n-3) makes it hold at every published index. It is a transcription slip on the
    entry.

    Returns a reason string when the shifts are not a contiguous run, each appearing
    once, and None when they are.
    """
    from collections import Counter
    body = conj.split(" - _")[0]
    shifts = [int(m) for m in re.findall(r"a\(n\s*-\s*(\d+)\)", body)]
    shifts += [0] * len(re.findall(r"a\(n\)(?!\s*-)", body))
    if not shifts:
        return "no terms parsed"
    c = Counter(shifts)
    dup = sorted(k for k, v in c.items() if v > 1)
    gaps = [k for k in range(max(shifts) + 1) if k not in c]
    if dup:
        return f"the shift a(n-{dup[0]}) appears more than once"
    if gaps and len(gaps) < len(c):
        return f"no a(n-{gaps[0]}) term between the others"
    return None


def reindexable(ps, data, off, span=5):
    """True if some joint shift of coefficients and indices makes the recurrence hold.

    A recurrence written against an offset the entry no longer uses is a slip on the
    entry, not a false statement, and must not be reported as a disproof.
    """
    r = len(ps) - 1
    for c in range(-span, span + 1):
        for s in range(-span, span + 1):
            if c == 0 and s == 0:
                continue
            ok, cnt = True, 0
            for m in range(off + r, off + len(data)):
                idx = [m - i + s - off for i in range(r + 1)]
                if min(idx) < 0 or max(idx) >= len(data):
                    continue
                tot = sum(sp.Rational(sp.Poly(p, n).eval(m + c)) * data[m - i + s - off]
                          for i, p in enumerate(ps) if p != 0)
                if tot != 0:
                    ok = False
                    break
                cnt += 1
            if ok and cnt >= 8:
                return (c, s)
    return None


def decide_one(conj, data, off, egf, cands):
    """The whole decision for one conjecture. Run in a child process so a stuck
    computation can be killed by the operating system rather than waited on."""
    rec = {}
    src, A, co, fixes = strict_gf(cands, data, off, egf)
    if A is None:
        return {"status": "no g.f. reproduces every published term"}
    ps = parse_conj(conj)
    if egf:
        m_ = le.to_module(A)
        ok, B = le.is_polynomial(le.residual_egf(m_[0], m_[1], m_[2], ps, n))
    else:
        q = qf.to_quad(A)
        mm = None if q is not None else mq.to_multi(A)
        if q is not None:
            ok, B = qf.is_polynomial(qf.residual(q, ps, n))
        elif mm is not None:
            ok, B = mq.is_polynomial(mq.residual(mm[0], mm[1], ps, n))
        else:
            K, u = af.from_expr(A)
            ok, B = K.is_polynomial(K.residual(u, ps, n))
    corrected = [[int(i), sp.sstr(v)] for i, v in fixes]
    if ok:
        deg = int(sp.Poly(B, x).total_degree()) if B != 0 else -1
        return {"status": "PROVED", "gf_src": src, "degree": deg,
                "order": len(ps) - 1, "gf_corrected": corrected}
    r = len(ps) - 1
    first = None
    for m in range(off + r, off + len(data)):
        tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * co[m - i]
                  for i, p in enumerate(ps) if p != 0)
        if tot != 0:
            first = (m, sp.nsimplify(tot, rational=True))
            break
    rx = reindexable(ps, data, off)
    if rx is not None:
        return {"status": "INDEXING SLIP", "shift": list(rx), "gf_src": src}
    bad = malformed(conj)
    if bad:
        return {"status": "MALFORMED ON THE ENTRY", "reason": bad, "gf_src": src}
    if first is None:
        return {"status": "residual not polynomial, but no counterexample "
                          "among the published terms"}
    return {"status": "DISPROVED", "gf_src": src, "gf_corrected": corrected,
            "fails_at": int(first[0]), "value": sp.sstr(first[1]),
            "order": len(ps) - 1}


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    per = int(os.environ.get("PER", "150"))
    for a in todo:
        F, data, off, name = entry(a)
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        if not conjs or len(data) < 10:
            continue
        egf = not any(GFL.match(l) for l in F)
        lines = [l for l in F if (EGFL if egf else GFL).match(l)]
        if not lines:
            continue
        cands = [c for l in lines for c in gfclean.candidates(l)]
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off,
                   "mode": "egf" if egf else "ogf"}
            st, val = timeoutrun.call(decide_one, (conj, data, off, egf, cands),
                                      timeout=per)
            if st == "ok":
                rec.update(val)
            elif st == "timeout":
                rec["status"] = "timeout (worker killed)"
            else:
                rec["status"] = str(val)
            if rec["status"] in ("PROVED", "DISPROVED"):
                print(f"{key}  {rec['status']}"
                      + (f"  first failure at n={rec['fails_at']}"
                         if rec["status"] == "DISPROVED" else ""), flush=True)
            out[key] = rec
            json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    from collections import Counter
    print(Counter(v["status"].split(",")[0][:44] for v in out.values()))


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
