#!/usr/bin/env python3
"""For each paper whose field claim failed the audit, can it be redone correctly?"""
import json
import sympy as sp
import gfclean, timeoutrun
import algfield as af
import quadfield as qf, multiquad as mq
from prove_rec import parse_gf, parse_conj
from regf import entry, CONJ, GFL, EGFL
from holonomic import taylor

x, n = sp.symbols('x n')


def check(a):
    F, data, off, name = entry(a)
    conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
             and "=0" in l.replace(" ", "")]
    lines = [l for l in F if GFL.match(l)]
    for c in (cc for l in lines for cc in gfclean.candidates(l)):
        try:
            G = parse_gf(c, 'x', raw=c)
            base = taylor(G, off + min(len(data), 10) + 4)
        except Exception:
            continue
        for sh in (0, 1, 2, 3, -1, -2, -3):
            idx = [off + k - sh for k in range(min(len(data), 10))]
            if any(i < 0 or i >= len(base) for i in idx):
                continue
            try:
                if not all(sp.simplify(base[i] - data[k]) == 0
                           for k, i in enumerate(idx)):
                    continue
            except Exception:
                continue
            A = sp.together(x ** sh * G)
            if qf.to_quad(A) is not None:
                return {"field": "quadratic", "gf": c}
            if mq.to_multi(A) is not None:
                return {"field": "multiquad", "gf": c}
            try:
                K, u = af.from_expr(A)
            except Exception as e:
                return {"field": "NOT ALGEBRAIC", "gf": c, "why": str(e)[:60]}
            deg = K.P.degree()
            res = []
            for conj in conjs:
                try:
                    ps = parse_conj(conj)
                except Exception:
                    continue
                ok, B = K.is_polynomial(K.residual(u, ps, n))
                res.append(bool(ok))
            return {"field": f"algfield degree {deg}", "gf": c, "residual_ok": res}
    return {"field": "no matching g.f."}


if __name__ == "__main__":
    todo = ["A025754", "A025756", "A025757", "A025758", "A097180", "A097188",
            "A097189", "A097192", "A115967", "A174169"]
    out = {}
    for a in todo:
        st, val = timeoutrun.call(check, (a,), timeout=240)
        out[a] = val if st == "ok" else {"field": st}
        print(f"{a}: {out[a]}", flush=True)
    json.dump(out, open("recheck-field.json", "w"), indent=1)
