#!/usr/bin/env python3
"""Second pass on the field audit, without the flaw in the first.

The first pass took the first generating-function line that parsed, which need not be the
one the paper used -- an entry often posts several. The question is narrower: is there
ANY posted generating function that both reproduces the entry's terms and lies in the
field the paper claims? If there is, the paper is fine. If none does, the claim needs
looking at.

Papers 1-30 are the hand-written ones whose engine label is nominal, and are skipped.
"""
import json
import sympy as sp
import gfclean, timeoutrun
import quadfield as qf, multiquad as mq
from prove_rec import parse_gf
from regf import entry, GFL, EGFL
from holonomic import taylor

x = sp.Symbol('x')


def best_field(a):
    """The narrowest field any data-matching posted g.f. lies in, or None."""
    F, data, off, name = entry(a)
    best = None
    for egf in (False, True):
        lines = [l for l in F if (EGFL if egf else GFL).match(l)]
        for c in (cc for l in lines for cc in gfclean.candidates(l)):
            try:
                G = parse_gf(c, 'x', raw=c)
                base = taylor(G, off + min(len(data), 10) + 4)
                if egf:
                    base = [t * sp.factorial(i) for i, t in enumerate(base)]
            except Exception:
                continue
            ok = False
            for sh in ((0,) if egf else (0, 1, 2, 3, -1, -2, -3)):
                idx = [off + k - sh for k in range(min(len(data), 10))]
                if any(i < 0 or i >= len(base) for i in idx):
                    continue
                try:
                    if all(sp.simplify(base[i] - data[k]) == 0
                           for k, i in enumerate(idx)):
                        G = G if egf else sp.together(x ** sh * G)
                        ok = True
                        break
                except Exception:
                    pass
            if not ok:
                continue
            if not egf:
                if qf.to_quad(G) is not None:
                    return "quadratic"
                if mq.to_multi(G) is not None:
                    best = best or "multiquad"
            else:
                best = best or "egf-module"
    return best


def main():
    rm = {r["rank"]: r for r in json.load(open("rank-map.json"))}
    flagged = [int(l.split()[2]) for l in open("audit_field.log")
               if l.strip().startswith("MISMATCH")]
    out = []
    for rank in flagged:
        r = rm[rank]
        if rank <= 30:
            print(f"  rank {rank:4d}  {r['anum']}  hand-written paper, engine label is "
                  f"nominal -- skipped")
            continue
        st, val = timeoutrun.call(best_field, (r["anum"],), timeout=90)
        verdict = val if st == "ok" else f"({st})"
        agree = (verdict == r["engine"]) or (verdict == "multiquad"
                                             and r["engine"] == "multiquad")
        print(f"  rank {rank:4d}  {r['anum']}  claims {r['engine']:10s} "
              f"actual {str(verdict):12s} {'ok' if agree else 'LOOK'}", flush=True)
        if not agree:
            out.append({"rank": rank, "anum": r["anum"], "claims": r["engine"],
                        "actual": verdict})
    json.dump(out, open("field-mismatches.json", "w"), indent=1)
    print(f"\n{len(out)} papers whose field claim does not hold up")


if __name__ == "__main__":
    main()
