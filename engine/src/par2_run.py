#!/usr/bin/env python3
"""Settle a conjectured recurrence from a known side that is only valid one parity at a time.

116 entries state their fact side either as two branches, a(2n) = ... and a(2n+1) = ..., or
as a single formula whose arguments round, C(n+3, ceiling(n/2))*C(n+2, floor(n/2)) - ... .
Neither is a hypergeometric term: a shift quotient cannot be taken through a floor. Both
become one after the substitutions n = 2m and n = 2m+1, which resolve the rounding exactly,
and then each branch is decided by hyperterm.py.

The conjecture must hold on BOTH branches; parity.combination writes it out in m at each,
and a recurrence of order r becomes two identities in m. Openness is taken from
open_index.json, so nothing already settled is attacked.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import cfparse, parity, hyperterm as ht, blocks, fsplit
from parity import m
from makeslots import coeffs_of
from regf import entry

n = sp.Symbol('n')
GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)
ATTRIB = re.compile(r"\s+-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d.*$")


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    cj = blocks.conjectured_lines(F)
    known = [ATTRIB.sub("", l) for l in F if l.strip() not in cj and not GUESS.search(l)]
    parts = [q for l in known for q in [l] + fsplit.split(l)]
    forms = []
    for q in parts:
        e = cfparse.parse(q, rounding=True)
        if e is None:
            continue
        h = parity.halves(e)
        if h is None:
            continue
        al, sh = cfparse.align(e, data, off)
        if al is None:
            continue
        hh = parity.halves(al)
        if hh is not None:
            forms.append((q, hh))
    if not forms:
        return ("no", "no parity-split closed form that matches the terms")
    out = []
    for cl in item["conj"]:
        try:
            ps = coeffs_of(cl)
        except Exception:
            continue
        if not ps or len(ps) < 2:
            continue
        for q, (e0, e1) in forms:
            res = {}
            for odd in (False, True):
                res[odd] = ht.is_zero_sum(parity.combination(ps, e0, e1, odd), m)
            if not (res[False][0] and res[True][0]):
                continue
            order = len(ps) - 1
            bad = [i + off for i in range(order, len(data))
                   if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                          for j, p in enumerate(ps) if p != 0) != 0]
            if bad:
                out.append(("integer re-check failed", cl, bad[:3])); break
            out.append(("PROVED", cl, {"formula": q, "order": order,
                                       "neven": len(res[False][1]),
                                       "nodd": len(res[True][1]),
                                       "nver": len(data) - order, "firstn": order + off}))
            break
        else:
            out.append(("not settled", cl, None))
    return ("ok", out)
