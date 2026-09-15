#!/usr/bin/env python3
"""The Ore engine again, with the complete test instead of the divisibility test.

ore_prove.py asks whether the conjectured operator C is a left multiple of an operator P
the entry already states as established. When it is, C(a) = 0 follows. When it is not,
nothing follows -- and the old runner recorded that as a refusal, which was wrong: C(a)=0
requires only that C lie in the left ideal of the MINIMAL annihilator, and P is generally
a proper multiple of that.

oremod.py decides the real question. Divide, C = QP + R with order(R) < order(P); then
C(a) = R(a), and R(a) lies in the finite-dimensional module the sequence spans, so its
shifts satisfy an operator that can be computed, and vanishing is decided by evaluating
it at finitely many indices. R = 0 recovers the old test as a special case.
"""
import json, os, signal, sys
import sympy as sp
import ore, oremod
from ore import n
from ore_prove import candidates, coeffs, numeric_ok

RES = os.environ.get("RES", "ore2-results.json")


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def main():
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    cand = candidates()
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    cand = [c for i, c in enumerate(cand) if i % ns == sh]
    print(f"{len(cand)} entries in this shard carry both kinds of recurrence", flush=True)
    for a, conjs, proven, data, off, name in cand:
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off, "status": None}
            signal.alarm(int(os.environ.get("PER", "180")))
            try:
                pc = coeffs(conj)
                C = ore.to_operator(pc)
                seq = [sp.Integer(t) for t in data]
                done = False
                for pr in proven:
                    try:
                        pp = coeffs(pr)
                        P = ore.to_operator(pp)
                        Q, R = oremod.reduce_right(C, P)
                    except Exception:
                        continue
                    okv, T, firstok, badn = oremod.vanishes(R, P, seq, off, off)
                    if not okv:
                        continue
                    if ore.is_zero(R) and ore.trivial(Q):
                        rec["status"] = ("the two recurrences are the same one rescaled; "
                                         "nothing new to prove")
                        done = True
                        break
                    bad, checked, first = numeric_ok(pc, data, off)
                    if bad or checked < 3:
                        rec["status"] = f"conjecture fails on published terms at {bad[:3]}"
                        done = True
                        break
                    rec.update(status="PROVED", proven=pr,
                               Q=[sp.sstr(t) for t in Q],
                               residual=[sp.sstr(t) for t in R],
                               residual_is_zero=bool(ore.is_zero(R)),
                               residual_annihilator=[sp.sstr(t) for t in (T or [])],
                               residual_zero_from=(int(firstok)
                                                  if firstok is not None else None),
                               exceptional=[sp.sstr(t) for t in ore.exceptional_set(Q)],
                               order_conj=len(pc) - 1, order_proven=len(pp) - 1,
                               terms_verified=checked, first_n=first)
                    print(f"{key}  PROVED  "
                          f"{'divides' if ore.is_zero(R) else 'residual vanishes'}",
                          flush=True)
                    done = True
                    break
                if not done and rec["status"] is None:
                    rec["status"] = ("no stated recurrence makes the conjecture follow")
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
    main()
