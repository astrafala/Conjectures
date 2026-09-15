#!/usr/bin/env python3
"""Sweep the open conjectures with the D-finite engine.

Covers every entry that posts a generating function or an exponential generating
function, whatever it is made of, so it subsumes the earlier field-by-field engines and
reaches the Bessel and hypergeometric ones they could not.
"""
import json, os, re, signal, sys
import sympy as sp
import gfclean, holo, ore, oremod
from holo import x, n
from regf import entry, CONJ, GFL, EGFL, match
from prove_rec import parse_conj
from holonomic import taylor

RES = os.environ.get("RES", "holo-results.json")


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def egf_shift(ps):
    """Turn a recurrence for u(n)=a(n)/n! into one for a(n).

    If sum_j q_j(n) u(n+j) = 0 then multiplying by (n+r)! gives
    sum_j q_j(n) * (n+j+1)(n+j+2)...(n+r) * a(n+j) = 0, and each of those products is a
    polynomial, so the result is still a recurrence with polynomial coefficients.
    """
    r = len(ps) - 1
    return [sp.expand(ps[j] * sp.rf(n + j + 1, r - j)) for j in range(r + 1)]


def numeric_ok(pc, data, off):
    order = len(pc) - 1
    bad, checked, first = [], 0, None
    for idx in range(order, len(data)):
        nn = idx + off
        tot = sum(sp.Rational(sp.Poly(p, n).eval(nn)) * data[idx - i]
                  for i, p in enumerate(pc) if p != 0)
        if tot != 0:
            bad.append(nn)
        else:
            checked += 1
            first = nn if first is None else first
    return bad, checked, first


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    for a in todo:
        F, data, off, name = entry(a)
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        if not conjs:
            continue
        for egf in (False, True):
            lines = [l for l in F if (EGFL if egf else GFL).match(l)]
            if not lines:
                continue
            cands = [c for l in lines for c in gfclean.candidates(l)]
            for j, conj in enumerate(conjs):
                key = f"{a}#{j}" + ("e" if egf else "")
                if key in out:
                    continue
                rec = {"anum": a, "conj": conj, "name": name, "offset": off,
                       "mode": "egf" if egf else "ogf", "status": None}
                signal.alarm(int(os.environ.get("PER", "300")))
                try:
                    A, src = match(cands, data, off, egf)
                    if A is None:
                        rec["status"] = "no g.f. candidate reproduces the terms"
                    else:
                        got = holo.annihilator(A)
                        if got is None:
                            rec["status"] = "no D-finite annihilator"
                        else:
                            ps, start = got
                            co = taylor(A, max(off + len(data), 22))
                            sh = holo.align_shift(ps, co, start)
                            if sh is None:
                                rec["status"] = ("the derived recurrence does not hold "
                                                 "on the coefficients at any shift")
                            else:
                                # sum_j ps_j(m) co[m+j+sh] = 0 is the same relation as
                                # sum_j ps_j(m-sh) co[m+j] = 0, which is the indexing the
                                # rest of the pipeline uses
                                if sh:
                                    ps = [sp.expand(p.subs(n, n - sh)) for p in ps]
                                    start = start + sh
                                L = egf_shift(ps) if egf else ps
                                pc = parse_conj(conj)
                                C = ore.to_operator(pc)
                                Q, Rem = oremod.reduce_right(C, L)
                                # C(a) = R(a) after right division, and R(a) is decided
                                # in the module a satisfies -- asking instead whether C
                                # is a left multiple of L refuses true conjectures,
                                # because C only has to lie in the ideal of the MINIMAL
                                # annihilator and L is generally a proper multiple of it
                                seqterms = [sp.nsimplify(t, rational=True) for t in co]
                                okv, T, firstok, badn = oremod.vanishes(
                                    Rem, L, seqterms, 0, start)
                                if not okv:
                                    rec["status"] = ("the residual after division does "
                                                     "not vanish on the sequence")
                                else:
                                    bad, checked, firstn = numeric_ok(pc, data, off)
                                    if bad or checked < 3:
                                        rec["status"] = f"fails on terms at {bad[:3]}"
                                    else:
                                        rec.update(
                                            status="PROVED", gf_src=src, gf=sp.sstr(A),
                                            index_shift=int(sh),
                                            derived=[sp.sstr(t) for t in L],
                                            Q=[sp.sstr(t) for t in Q],
                                            exceptional=[sp.sstr(t)
                                                         for t in ore.exceptional_set(Q)],
                                            start=start, order_conj=len(pc) - 1,
                                            residual=[sp.sstr(t) for t in Rem],
                                            residual_annihilator=[sp.sstr(t) for t in
                                                                  (T or [])],
                                            residual_zero_from=int(firstok)
                                            if firstok is not None else None,
                                            residual_excluded=[int(b) for b in badn],
                                            order_derived=len(L) - 1,
                                            terms_verified=checked, first_n=firstn)
                                        print(f"{key}  PROVED  order {len(L)-1} "
                                              f"derived, {len(pc)-1} conjectured",
                                              flush=True)
                except TO:
                    rec["status"] = "timeout"
                except Exception as ex:
                    rec["status"] = f"{type(ex).__name__}: {str(ex)[:60]}"
                finally:
                    signal.alarm(0)
                    out[key] = rec
                    json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"),
          "of", len(out))


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
