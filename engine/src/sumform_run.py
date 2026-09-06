#!/usr/bin/env python3
"""Settle a conjecture whose known side is a(n) = g(n) + c(n) * Sum_k F(n,k).

Creative telescoping gives an operator on the SUM, not on a(n). Since a = g + c*S we have
S = (a - g)/c, and substituting sigma_j(n) S(n+j) = h(n) gives

    sum_j sigma_j(n) * (a(n+j) - g(n+j)) / c(n+j) = h(n).

Multiplying through by prod_i c(n+i) clears the denominators and leaves an inhomogeneous
recurrence for a with coefficients tau_j(n) = sigma_j(n) * prod_{i != j} c(n+i) and
right-hand side H(n) = h(n)*prod_i c(n+i) + sum_j tau_j(n) g(n+j). zeilb.annihilator then
clears H, exactly as it does for the boundary term, and the result is a homogeneous
operator annihilating a -- the known side the conjecture is divided by.

The summand is checked against the entry's published terms before any of this is derived
from it.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import zeil, zeilb, ore, sumform, blocks, fsplit
from zeil import n as zn
from makeslots import coeffs_of
from regf import entry

n = sp.Symbol('n')
GUESS = re.compile(r"\b(guess|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)
ATTRIB = re.compile(r"\s+-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d.*$")


def value(g, c, F, idx, lo, hi, nn):
    a = g.subs(n, nn) + c.subs(n, nn) * sp.Sum(F.subs(n, nn), (idx, lo.subs(n, nn),
                                                              hi.subs(n, nn))).doit()
    return sp.nsimplify(sp.simplify(a), rational=True)


def attack(item):
    a = item["anum"]
    F_, data, off, nm = entry(a)
    cj = blocks.conjectured_lines(F_)
    known = [ATTRIB.sub("", l) for l in F_ if l.strip() not in cj and not GUESS.search(l)]
    parts = [q for l in known for q in [l] + fsplit.split(l)]
    for q in parts:
        r = sumform.split(q)
        if r is None:
            continue
        g, c, F, idx, lo, hi = r
        try:
            if not all(value(g, c, F, idx, lo, hi, off + i) == data[i]
                       for i in range(min(6, len(data)))):
                continue
        except Exception:
            continue
        Fk = F.subs(idx, sp.Symbol('k'))
        tel = None
        for order in range(1, 4):
            tel = zeil.telescoper(Fk, order)
            if tel is not None:
                break
        if tel is None:
            return ("no", "no telescoper for the summand")
        sig, R = tel
        h = zeilb.inhomogeneity(Fk, sig, R, lo.subs(idx, sp.Symbol('k')),
                                hi.subs(idx, sp.Symbol('k')))
        if h is None:
            return ("no", "boundary correction not computable")
        # move the operator from S to a
        m = len(sig) - 1
        prod = [sp.cancel(c.subs(n, n + i)) for i in range(m + 1)]
        allp = sp.cancel(sp.prod(prod))
        tau, H = [], sp.cancel(h * allp)
        for j in range(m + 1):
            t = sp.cancel(sig[j] * allp / prod[j])
            tau.append(sp.expand(sp.cancel(t)))
            H = sp.cancel(H + t * g.subs(n, n + j))
        H = sp.cancel(sp.expand(H))
        L, how = zeilb.annihilator(tau, H)
        if L is None:
            return ("no", how)
        out = []
        for cl in item["conj"]:
            try:
                ps = coeffs_of(cl)
            except Exception:
                continue
            if not ps or len(ps) < 2:
                continue
            Q, Rem = ore.right_divide(ore.to_operator(ps), L)
            if not ore.is_zero(Rem):
                out.append(("not a left multiple", cl, None)); continue
            order = len(ps) - 1
            bad = [i + off for i in range(order, len(data))
                   if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                          for j, p in enumerate(ps) if p != 0) != 0]
            if bad:
                out.append(("integer re-check failed", cl, bad[:3])); continue
            out.append(("PROVED", cl, {"formula": q, "how": how,
                                       "order_conj": order, "order_derived": len(L) - 1,
                                       "nver": len(data) - order, "firstn": order + off}))
        return ("ok", out)
    return ("no", "no g + c*Sum form matched the terms")


if __name__ == "__main__":
    import runpool
    items = json.load(open("sumform_todo.json"))
    def report(it, res):
        st, val = res
        if st != "ok" or not val or val[0] != "ok":
            return
        for v, cl, extra in val[1]:
            if v == "PROVED":
                print(f"  PROVED {it['anum']}  {cl[:58]}", flush=True)
    runpool.run(attack, items, lambda it: it["anum"], "sumform_progress.json",
                per_item=200, budget=int(sys.argv[1]) if len(sys.argv) > 1 else 460,
                workers=4, report=report)
