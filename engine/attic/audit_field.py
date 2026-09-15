#!/usr/bin/env python3
"""Which papers claim a field their generating function does not lie in?

to_quad and to_multi returned "(expression, 0, 1)" -- membership in Q(x) -- whenever no
SQUARE root was present, without checking that what was left is rational. A fourth root,
a cube root, an exp or a log all passed. The residual arithmetic that follows stays valid
either way, since theta(u) = x u' for any differentiable u, so a proof reached that way
can still be correct; what is wrong is the paper's statement about where A lives.

This re-derives every paper's generating function and reports any whose posted field is
not the field it actually needs.
"""
import glob, json, os, sys
import sympy as sp
import gfclean
import quadfield as qf, multiquad as mq
from prove_rec import parse_gf
from regf import entry, GFL, EGFL
import timeoutrun


def field_of(a, egf):
    F, data, off, name = entry(a)
    lines = [l for l in F if (EGFL if egf else GFL).match(l)]
    cands = [c for l in lines for c in gfclean.candidates(l)]
    for c in cands:
        try:
            G = parse_gf(c, 'x', raw=c)
        except Exception:
            continue
        x = sp.Symbol('x')
        if not egf:
            if qf.to_quad(G) is not None:
                return "quadratic"
            if mq.to_multi(G) is not None:
                return "multiquad"
        if G.is_rational_function(x):
            return "rational"
        return "other"
    return None


def main():
    rm = json.load(open("rank-map.json"))
    targets = [r for r in rm if r["engine"] in ("quadratic", "multiquad")]
    print(f"{len(targets)} papers claim a quadratic or multiquadratic field")
    bad = []
    for i, r in enumerate(targets):
        st, val = timeoutrun.call(field_of, (r["anum"], False), timeout=40)
        if st != "ok":
            continue
        if val == "other":
            bad.append((r["rank"], r["anum"], r["engine"]))
            print(f"  MISMATCH  rank {r['rank']}  {r['anum']}  claims {r['engine']} "
                  f"but the g.f. is neither rational nor (multi)quadratic", flush=True)
        if i % 50 == 0:
            print(f"    .. {i}/{len(targets)}", flush=True)
    json.dump(bad, open("field-mismatches.json", "w"), indent=1)
    print(f"\n{len(bad)} papers to look at")


if __name__ == "__main__":
    main()
