#!/usr/bin/env python3
"""Settle conjectured recurrences from a closed form that depends on the parity of n.

Same decision procedure as hyper_run.py, applied to each residue class separately
(parity.py). Both halves must hold; one of two is not a result.
"""
import json, os, re, signal, sys
import sympy as sp
import cfparse, parity, hyperterm as ht
from parity import m
from regf import entry, CONJ
from prove_rec import parse_conj

n = sp.Symbol('n')
RES = os.environ.get("RES", "parity-results.json")
# the parity engine needs the rounding that the plain closed-form parser refuses
PARITY_OK = re.compile(r"floor|ceiling|\(-1\)\^", re.I)


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def parse_with_rounding(line):
    saved = cfparse.REFUSE
    cfparse.REFUSE = re.compile(
        r"Sum_|Product_|\bA\d{6}\b|\bmod\b|hypergeom|Integral|sqrt|"
        r"\ba\(n\s*-|\ba\(n\s*\+|~|\.\.\.|Stirling|\bround\b|\bif\b|\botherwise\b|"
        r"\blog\b|\bexp\b|Bessel|\bPi\b|\bO\(", re.I)
    cfparse.LOCALS = dict(cfparse.LOCALS, floor=sp.floor, ceiling=sp.ceiling)
    try:
        return cfparse.parse(line)
    finally:
        cfparse.REFUSE = saved


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    for a in todo:
        F, data, off, name = entry(a)
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        forms = [l for l in F if not CONJ.match(l) and PARITY_OK.search(l)]
        if not forms:
            continue
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off, "status": None}
            signal.alarm(int(os.environ.get("PER", "240")))
            try:
                ps = parse_conj(conj)
                got = None
                for line in forms:
                    e = parse_with_rounding(line)
                    if e is None or not e.has(sp.floor, sp.ceiling, sp.Pow):
                        continue
                    e, shift = cfparse.align(e, data, off)
                    if e is None:
                        continue
                    h = parity.halves(e)
                    if h is None:
                        continue
                    e0, e1 = h
                    res = {}
                    for odd in (False, True):
                        T = parity.combination(ps, e0, e1, odd)
                        res[odd] = ht.is_zero_sum(T, m)
                    if res[False][0] is None or res[True][0] is None:
                        continue
                    got = (line, shift, e0, e1, res)
                    if res[False][0] and res[True][0]:
                        break
                if got is None:
                    rec["status"] = "no usable parity-split closed form"
                else:
                    line, shift, e0, e1, res = got
                    if not (res[False][0] and res[True][0]):
                        which = "even" if not res[False][0] else "odd"
                        rec["status"] = f"identity fails on the {which} indices"
                        rec["formula"] = line
                    else:
                        order = len(ps) - 1
                        bad, nver, firstn = [], 0, None
                        for idx in range(order, len(data)):
                            nn = idx + off
                            tot = sum(sp.Rational(sp.Poly(p, n).eval(nn)) * data[idx - i]
                                      for i, p in enumerate(ps) if p != 0)
                            if tot != 0:
                                bad.append(nn)
                            else:
                                nver += 1
                                firstn = nn if firstn is None else firstn
                        if bad or nver < 3:
                            rec["status"] = f"fails on published terms at {bad[:3]}"
                        else:
                            rec.update(status="PROVED", formula=line, shift=shift,
                                       even=sp.sstr(e0), odd=sp.sstr(e1),
                                       order=order, terms_verified=nver, first_n=firstn)
                            print(f"{key}  PROVED  parity split, order {order}",
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
