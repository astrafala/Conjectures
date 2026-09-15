#!/usr/bin/env python3
"""Build one paper per proved cross-entry identity."""
import json, os, re, subprocess, sys
import sympy as sp
import cross as C
from cross import x, n
from crosstex import TEMPLATE
from makerecpapers import tex_escape, render_conj
from verify_open import fetch
import time


def integer_check(refs, poly, target, cache, deg):
    """Evaluate both sides on the published terms, in exact integer arithmetic."""
    dataA, offA = cache[target][1], cache[target][2]
    lo = deg + 1
    checked, first = 0, None
    for idx in range(len(dataA)):
        nn = idx + offA
        if nn <= deg:
            continue
        rhs = sp.Rational(sp.Poly(poly, n).eval(nn)) if poly != 0 else sp.Integer(0)
        ok = True
        for c, nm, k in refs:
            dB, oB = cache[nm][1], cache[nm][2]
            j = nn + k - oB
            if j < 0 or j >= len(dB):
                ok = False
                break
            cv = sp.Poly(c, n).eval(nn) if c.free_symbols else sp.nsimplify(c, rational=True)
            rhs += sp.Rational(cv) * dB[j]
        if not ok:
            continue
        if sp.Rational(dataA[idx]) != sp.nsimplify(rhs, rational=True):
            return None, None
        checked += 1
        if first is None:
            first = nn
    return checked, first


def build(spec):
    made = []
    cache = {}
    for v in spec:
        num, a = v["num"], v["anum"]
        parsed = C.parse_identity(re.sub(r"^Conjecture[s]?[:.]?\s*", "", v["conj"],
                                         flags=re.I))
        if not parsed:
            print(f"{num:4d}  {a}  SKIP reparse failed")
            continue
        refs, poly = parsed
        for nm in [a] + [r[1] for r in refs]:
            if nm not in cache:
                cache[nm] = C.series_of(nm)
        if cache[a] is None or any(cache[r[1]] is None for r in refs):
            print(f"{num:4d}  {a}  SKIP a g.f. went missing")
            continue
        FA, dataA, offA = cache[a]
        rhs = C.poly_gf(poly, 12)
        reflines = []
        for c, nm, k in refs:
            FB, dB, oB = cache[nm]
            S = C.shifted(FB, dB, oB, k, 12)
            rhs = sp.together(rhs + C.theta_apply(c, S))
            reflines.append(rf"F_{{{nm}}}(x) \;=\; {sp.latex(sp.simplify(FB))}")
        ok, B = C.is_polynomial(FA - rhs)
        if not ok:
            print(f"{num:4d}  {a}  SKIP difference is not a polynomial")
            continue
        deg = int(sp.Poly(B, x).total_degree()) if B != 0 else -1
        nver, firstn = integer_check(refs, poly, a, cache, deg)
        if not nver or nver < 3:
            print(f"{num:4d}  {a}  SKIP integer re-check failed")
            continue
        e = fetch(a)
        time.sleep(0.3)
        subs = {
            "ANUM": a,
            "NAME": tex_escape(e["name"].rstrip('.')),
            "OFFSET": offA,
            "FIRSTTERMS": (f"a({offA}),\\dots,a({offA+7})\;=\;"
                           + ", ".join(str(t) for t in dataA[:8]) + ",\\ \\dots"),
            "GFLATEX": sp.latex(sp.simplify(FA)),
            "REFLIST": ", ".join(sorted({r[1] for r in refs})),
            "REFGFS": " \\qquad ".join(dict.fromkeys(reflines)),
            "RHSLATEX": sp.latex(sp.simplify(rhs)),
            "BLATEX": sp.latex(B),
            "DEG": deg,
            "CONJ": render_conj(v["conj"]),
            "TIME": e["time"][:10],
            "REV": e["revision"],
            "NVER": nver,
            "FIRSTN": firstn,
        }
        tex = TEMPLATE % subs
        d = f"build/{num}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(tex)
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "p.tex"],
                           cwd=d, capture_output=True)
        log = open(f"{d}/p.log", errors="ignore").read()
        errs = [l for l in log.split("\n") if l.startswith("! ")]
        good = os.path.exists(f"{d}/p.pdf") and not errs
        if good:
            subprocess.run(["cp", f"{d}/p.pdf", f"papers/{num}-PROOF.pdf"])
        made.append((num, a, good))
        print(f"{num:4d}  {a}  {'OK' if good else 'FAILED ' + str(errs[:1])}")
    print(f"\n{sum(1 for m in made if m[2])}/{len(made)} built")


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])))
