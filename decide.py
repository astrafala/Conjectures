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
import json, os, re, signal, sys
import sympy as sp
import gfclean
import algfield as af
from regf import entry, CONJ, GFL, EGFL
from prove_rec import parse_gf, parse_conj
from holonomic import taylor

x, n = sp.symbols('x n')
RES = os.environ.get("RES", "decide-results.json")


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


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
            try:
                if all(sp.simplify(base[i] - data[k]) == 0 for k, i in enumerate(idx)):
                    A = G if egf else sp.together(x ** sh * G)
                    return c, A, taylor(A, N) if not egf else base
            except Exception:
                pass
    return None, None, None


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


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
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
                   "mode": "egf" if egf else "ogf", "status": None}
            signal.alarm(int(os.environ.get("PER", "240")))
            try:
                src, A, co = strict_gf(cands, data, off, egf)
                if A is None:
                    rec["status"] = "no g.f. reproduces every published term"
                else:
                    ps = parse_conj(conj)
                    K, u = af.from_expr(A)
                    ok, B = K.is_polynomial(K.residual(u, ps, n))
                    if ok:
                        deg = int(sp.Poly(B, x).total_degree()) if B != 0 else -1
                        rec.update(status="PROVED", gf_src=src, degree=deg,
                                   order=len(ps) - 1)
                        print(f"{key}  PROVED  deg {deg}", flush=True)
                    else:
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
                            rec.update(status="INDEXING SLIP", shift=list(rx),
                                       gf_src=src)
                        elif first is None:
                            rec["status"] = ("residual not polynomial, but no "
                                             "counterexample among the published terms")
                        else:
                            rec.update(status="DISPROVED", gf_src=src,
                                       fails_at=int(first[0]),
                                       value=sp.sstr(first[1]), order=len(ps) - 1)
                            print(f"{key}  DISPROVED  first failure at n={first[0]}",
                                  flush=True)
            except TO:
                rec["status"] = "timeout"
            except Exception as ex:
                rec["status"] = f"{type(ex).__name__}: {str(ex)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    from collections import Counter
    print(Counter(v["status"].split(",")[0][:40] for v in out.values()))


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
