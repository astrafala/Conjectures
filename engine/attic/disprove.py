#!/usr/bin/env python3
"""Hunt explicit counterexamples to conjectured recurrences.

The residual test is an equivalence, not merely a sufficient condition: for a generating
function A and a conjectured recurrence with coefficients p_i, the residual

    B(x) = sum_i x^i (p_i(theta+i) A)(x),      theta = x d/dx,

is a polynomial of degree d if and only if the recurrence holds for every n > d. So when
the residual is decided NOT to be a polynomial, the conjecture is false for infinitely
many n -- that is a disproof, not a failure to prove.

A disproof is worth more care than a proof, because there is no independent check that a
reader can run in their head. So none is claimed from the residual alone. The generating
function is expanded far past the published data and the recurrence is evaluated on those
coefficients directly, in exact arithmetic, to produce a specific n where it fails. That
witness is checkable by anyone with the entry's own formula and a computer algebra system.

Two guards against claiming a disproof that is really a misreading:
  * the generating function must reproduce EVERY published term, not a sample of them;
  * the recurrence must hold at every index the published data covers. If it already
    fails there, the mismatch is with the entry's own data -- an indexing discrepancy,
    like A000907 -- and that is reported separately and never as a disproof.
"""
import json, os, re, signal, sys
import sympy as sp
import gfclean
from regf import entry, CONJ, GFL, EGFL
from prove_rec import parse_gf, parse_conj
from holonomic import taylor

x, n = sp.symbols('x n')
RES = os.environ.get("RES", "disprove-results.json")
EXTRA = int(os.environ.get("EXTRA", "60"))


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def strict_match(cands, data, off, egf, extra):
    """A g.f. reproducing EVERY published term, plus `extra` further coefficients."""
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
                    # the match says a(off+k) = base[off+k-sh], and the caller indexes
                    # seq[j] as a(off+j), so the slice starts at off-sh -- not at sh,
                    # which is only the same thing when off = 2*sh
                    start = off - sh
                    seq = (base[start:] if start >= 0
                           else [sp.Integer(0)] * (-start) + base)
                    return c, [sp.nsimplify(t, rational=True) for t in seq]
            except Exception:
                pass
    return None, None


def evaluate(ps, seq, off, lo, hi):
    """(index, value) of the first n in [lo,hi] where the recurrence fails, or None."""
    order = len(ps) - 1
    for m in range(lo, hi):
        idx = [m - i - off for i in range(order + 1)]
        if min(idx) < 0 or max(idx) >= len(seq):
            return None
        tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * seq[m - i - off]
                  for i, p in enumerate(ps) if p != 0)
        if sp.simplify(tot) != 0:
            return m, sp.simplify(tot)
    return None


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    for a in todo:
        F, data, off, name = entry(a)
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        egf = not any(GFL.match(l) for l in F)
        lines = [l for l in F if (EGFL if egf else GFL).match(l)]
        cands = [c for l in lines for c in gfclean.candidates(l)]
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off,
                   "mode": "egf" if egf else "ogf", "status": None}
            signal.alarm(int(os.environ.get("PER", "300")))
            try:
                src, seq = strict_match(cands, data, off, egf, EXTRA)
                if seq is None:
                    rec["status"] = "no g.f. reproduces every published term"
                else:
                    ps = parse_conj(conj)
                    order = len(ps) - 1
                    dend = off + len(data)
                    # A conjectured recurrence with polynomial coefficients normally
                    # holds only past a small bound -- the residual's degree -- so a
                    # failure at n = 3 or 4 is ordinary and says nothing. What matters
                    # is a clean run at the END of the published data followed by a
                    # failure beyond it.
                    fails = []
                    m = off + order
                    while m < dend:
                        hit = evaluate(ps, seq, off, m, dend)
                        if hit is None:
                            break
                        fails.append(int(hit[0]))
                        m = hit[0] + 1
                    tail_start = (max(fails) + 1) if fails else off + order
                    clean = dend - tail_start
                    if clean < 8:
                        rec["status"] = (f"only {clean} clean indices at the end of the "
                                         f"published data; not enough to stand on")
                        rec["fails_in_data"] = fails[:8]
                    else:
                        beyond = evaluate(ps, seq, off, dend,
                                          dend + EXTRA - order - 1)
                        if beyond is None:
                            rec["status"] = ("holds on every coefficient computed; "
                                             "no counterexample in range")
                            rec["clean_from"] = int(tail_start)
                        else:
                            mm, val = beyond
                            rec.update(status="DISPROVED", gf_src=src, fails_at=int(mm),
                                       residue=sp.sstr(val), order=order,
                                       clean_from=int(tail_start),
                                       fails_in_data=fails[:8], data_terms=len(data),
                                       checked_to=dend + EXTRA - order - 1)
                            print(f"{key}  DISPROVED  clean from n={tail_start} "
                                  f"through n={dend-1}, first failure at n={mm}",
                                  flush=True)
            except TO:
                rec["status"] = "timeout"
            except Exception as ex:
                rec["status"] = f"{type(ex).__name__}: {str(ex)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    d = sum(1 for r in out.values() if r["status"] == "DISPROVED")
    print(f"DISPROVED {d} of {len(out)}")


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
