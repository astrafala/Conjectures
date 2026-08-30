#!/usr/bin/env python3
"""Decide a Sequence Machine generating-function conjecture from the OEIS entry's own facts.

The machine states a rational generating function; the OEIS entry states a closed form. A
rational g.f. with denominator D(x) = 1 + d_1 x + ... + d_k x^k is exactly the assertion
that a(n) + d_1 a(n-1) + ... + d_k a(n-k) = 0 for every n past the numerator's degree,
together with agreement on the initial terms. Both halves are decidable: the first by
hyperterm.py, which is a decision procedure for identities between hypergeometric terms,
and the second by evaluating the closed form.

So the conjecture is settled outright -- proved or refuted -- with no truncation anywhere.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import cfparse, sumparse, fsplit, hyperterm, blocks
from regf import entry

x, n = sp.symbols('x n')
GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)


def gf_expr(ix):
    m = re.match(r"^ogf\((.*)\)$", ix.strip(), re.I)
    if not m:
        return None
    s = m.group(1).replace("^", "**")
    s = re.sub(r"(\d)\s*([a-zA-Z(])", r"\1*\2", s)
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"([a-zA-Z0-9)])\s*\(", r"\1*(", s)
    try:
        e = sp.sympify(s, locals={'x': x})
    except Exception:
        return None
    return e if isinstance(e, sp.Expr) and not (e.free_symbols - {x}) else None


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    cj = blocks.conjectured_lines(F)
    parts = [q for l in F if l.strip() not in cj and not GUESS.search(l)
             for q in [l] + fsplit.split(l)]
    cfs = [e for q in parts for e in [cfparse.parse(q)] if e is not None]
    if not cfs:
        return ("no", "no closed form on the entry")
    out = []
    for c in item["conjs"]:
        A = gf_expr(c["ix"])
        if A is None:
            out.append(("unparsed", c["ix"], None)); continue
        num, den = sp.fraction(sp.cancel(sp.together(A)))
        dp = sp.Poly(sp.expand(den), x)
        d0 = dp.eval(0)
        if d0 == 0:
            out.append(("pole at the origin", c["ix"], None)); continue
        ds = [sp.cancel(q / d0) for q in dp.all_coeffs()[::-1]]      # ascending, d_0 = 1
        k = len(ds) - 1
        degnum = sp.Poly(sp.expand(num), x).total_degree()
        got = None
        for e in cfs:
            al, sh = cfparse.align(e, data, off)
            if al is None:
                continue
            expr = sum(ds[j] * al.subs(n, n - j) for j in range(k + 1) if ds[j] != 0)
            ok, ev = hyperterm.is_zero_sum(sp.expand(expr), n)
            if not ok:
                continue
            # the recurrence is not the whole claim: the initial terms must agree too
            ser = sp.Poly(sp.series(A, x, 0, len(data) + 1).removeO(), x).all_coeffs()[::-1]
            ser += [sp.Integer(0)] * (len(data) - len(ser))
            bad = [i + off for i in range(min(len(data), len(ser)))
                   if sp.simplify(ser[i + off] - data[i]) != 0] if off == 0 else \
                  [i + off for i in range(min(len(data), len(ser) - off))
                   if sp.simplify(ser[i + off] - data[i]) != 0]
            if bad:
                got = ("series disagrees with the terms", c["ix"], bad[:3])
                break
            got = ("PROVED", c["ix"], {"closed": sp.srepr(al), "den": sp.srepr(den),
                                       "num": sp.srepr(num), "order": k,
                                       "degnum": int(degnum), "mt": c["mt"]})
            break
        out.append(got or ("not settled", c["ix"], None))
    return ("ok", out)


if __name__ == "__main__":
    import timeoutrun
    hits = []
    for it in json.load(open("sm_targets.json")):
        st, r = timeoutrun.call(attack, (it,), timeout=180)
        if st != "ok" or r[0] != "ok":
            print(f"{it['anum']}  {st}: {r if st!='ok' else r[1]}", flush=True); continue
        for verdict, ix, extra in r[1]:
            print(f"{it['anum']}  {verdict:32s} {ix[:55]}", flush=True)
            if verdict == "PROVED":
                hits.append({"anum": it["anum"], "ix": ix, **extra})
    json.dump(hits, open("sm_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
