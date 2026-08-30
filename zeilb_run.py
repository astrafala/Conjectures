#!/usr/bin/env python3
"""Settle conjectured recurrences by boundary-corrected creative telescoping.

Strictly more general than zeil_run.py: where the summand vanishes outside the stated
range the correction term is zero and this reduces to the old argument, and where it does
not the inhomogeneity is written out and cleared by one extra order (zeilb.py).

Three independent checks stand between a search and a claim:
  * the summand must reproduce the entry's published terms;
  * the certificate identity is verified exactly, as a rational identity;
  * the inhomogeneous recurrence is evaluated on the published terms, which is what
    catches an error in the boundary bookkeeping rather than in the certificate.
Only then is the conjecture divided by the derived operator.
"""
import json, os, re, signal, sys
import sympy as sp
import zeil, zeilb, ore, sumparse
from zeil import n, k
from prove_rec import parse_conj
from zeil_run import candidates, numeric_ok

RES = os.environ.get("RES", "zeilb-results.json")


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def main():
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    cand = candidates()
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    cand = [c for i, c in enumerate(cand) if i % ns == sh]
    maxorder = int(os.environ.get("MAXORDER", "3"))
    print(f"{len(cand)} entries in this shard", flush=True)
    for a, conjs, sums, data, off, name in cand:
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off, "status": None}
            signal.alarm(int(os.environ.get("PER", "300")))
            try:
                pc = parse_conj(conj)
                C = ore.to_operator(pc)
                done = False
                for src in sums:
                    parsed = sumparse.parse(src)
                    if not parsed:
                        continue
                    F, lo, hi = parsed
                    ok = True
                    for i in range(min(6, len(data))):
                        v = sumparse.evaluate(F, lo, hi, off + i)
                        if v is None or sp.simplify(v - data[i]) != 0:
                            ok = False
                            break
                    if not ok:
                        continue
                    tel = None
                    for r in range(1, maxorder + 1):
                        tel = zeil.telescoper(F, r)
                        if tel is not None:
                            break
                    if tel is None:
                        rec["status"] = "no telescoper found up to the order tried"
                        done = True
                        break
                    sig, R = tel
                    h = zeilb.inhomogeneity(F, sig, R, lo, hi)
                    if h is None:
                        rec["status"] = "boundary correction not computable for this range"
                        done = True
                        break
                    chk = zeilb.check_numeric(F, lo, hi, sig, h, data, off)
                    if chk is not True:
                        rec["status"] = ("the inhomogeneous recurrence fails on the "
                                         "published terms" if chk is False else
                                         "could not evaluate the inhomogeneity")
                        done = True
                        break
                    L, how = zeilb.annihilator(sig, h)
                    if L is None:
                        rec["status"] = how
                        done = True
                        break
                    Q, Rem = ore.right_divide(C, L)
                    if not ore.is_zero(Rem):
                        rec["status"] = ("derived a recurrence, but the conjecture is "
                                         "not a left multiple of it")
                        done = True
                        break
                    bad, checked, firstn = numeric_ok(pc, data, off)
                    if bad or checked < 3:
                        rec["status"] = f"conjecture fails on published terms at {bad[:3]}"
                        done = True
                        break
                    rec.update(status="PROVED", summand=sp.sstr(F), lo=sp.sstr(lo),
                               hi=sp.sstr(hi), formula=src, how=how,
                               sigma=[sp.sstr(t) for t in sig],
                               certificate=sp.sstr(R), inhomogeneity=sp.sstr(h),
                               operator=[sp.sstr(t) for t in L],
                               Q=[sp.sstr(t) for t in Q],
                               exceptional=[sp.sstr(t) for t in ore.exceptional_set(Q)],
                               order_conj=len(pc) - 1, order_derived=len(L) - 1,
                               terms_verified=checked, first_n=firstn)
                    print(f"{key}  PROVED  {how}  derived order {len(L)-1}, "
                          f"conjecture order {len(pc)-1}", flush=True)
                    done = True
                    break
                if not done:
                    rec["status"] = "no usable hypergeometric sum formula"
            except TO:
                rec["status"] = "timeout"
            except Exception as e:
                rec["status"] = f"{type(e).__name__}: {str(e)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"),
          "of", len(out))


if __name__ == "__main__":
    main()
