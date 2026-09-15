#!/usr/bin/env python3
"""Settle open recurrence conjectures from a posted closed form for a(n).

Applies to every still-open entry, whether or not it posts a generating function: the
test needs only the formula. See hyperterm.py for what makes it a decision procedure.
"""
import json, os, re, signal, sys
import sympy as sp
import cfparse, hyperterm as ht
from hyperterm import n
from regf import entry, CONJ
from prove_rec import parse_conj

RES = os.environ.get("RES", "hyper-results.json")


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def numeric_ok(ps, data, off, skip):
    """The conjecture on the entry's own terms, ignoring the excluded n."""
    order = len(ps) - 1
    bad, checked, first = [], 0, None
    for idx in range(order, len(data)):
        nn = idx + off
        if nn in skip:
            continue
        tot = sum(sp.Rational(sp.Poly(p, n).eval(nn)) * data[idx - i]
                  for i, p in enumerate(ps) if p != 0)
        if tot != 0:
            bad.append(nn)
        else:
            checked += 1
            if first is None:
                first = nn
    return bad, checked, first


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    for a in todo:
        F, data, off, name = entry(a)
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        forms = [l for l in F if not CONJ.match(l)]
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off, "status": None}
            signal.alarm(int(os.environ.get("PER", "180")))
            try:
                ps = parse_conj(conj)
                got = None
                for line in forms:
                    e = cfparse.parse(line)
                    if e is None:
                        continue
                    e, shift = cfparse.align(e, data, off)
                    if e is None:
                        continue
                    ok, info = ht.verdict(ps, e)
                    if ok is None:
                        continue
                    got = (line, e, ok, info)
                    if ok:
                        break
                if got is None:
                    rec["status"] = "no usable closed form"
                else:
                    line, e, ok, info = got
                    if not ok:
                        rec["status"] = "closed form refutes the conjecture as an identity"
                        rec["formula"] = line
                    else:
                        skip = set(int(v) for v in ht.excluded(info, ps)
                                   if v.is_Integer)
                        bad, checked, firstn = numeric_ok(ps, data, off, skip)
                        if bad or checked < 3:
                            rec["status"] = f"fails on published terms at {bad[:3]}"
                        else:
                            rec.update(status="PROVED", formula=line, shift=shift,
                                       closed_form=sp.sstr(e),
                                       classes=[sp.sstr(c[0]) for c in info],
                                       excluded=[sp.sstr(v) for v in ht.excluded(info, ps)],
                                       order=len(ps) - 1, terms_verified=checked,
                                       first_n=firstn)
                            print(f"{key}  PROVED  {len(info)} class(es), "
                                  f"order {len(ps)-1}", flush=True)
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
