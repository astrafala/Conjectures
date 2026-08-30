#!/usr/bin/env python3
"""Build one paper per conjecture settled from a coefficient-extraction definition.

The whole derivation is redone here, independently of the search run, and the series is
computed a second way -- straight from the definition -- so the paper's claim that two
independent computations agree is one this script actually establishes.
"""
import json, os, re, subprocess, sys, time
import sympy as sp
import diagonal as dg
import algfield as af
from diagonal import t, y
from prove_rec import parse_conj
from makerecpapers import tex_escape, render_conj, rec_latex
from verify_open import fetch

X, n = sp.symbols('x n')


def xcoeffs(e, N):
    """The first N coefficients of a rational function of x, as a power series at 0.

    Long division on coefficient lists. Taking .coeff(x, i) of a rational expression does
    not do this: it reads the numerator's coefficient and keeps the denominator, which is
    silently wrong for every f or g that is not a polynomial.
    """
    num, den = sp.fraction(sp.cancel(sp.together(e)))
    a = sp.Poly(sp.expand(num), dg.x).all_coeffs()[::-1]
    b = sp.Poly(sp.expand(den), dg.x).all_coeffs()[::-1]
    a += [sp.Integer(0)] * (N - len(a))
    b += [sp.Integer(0)] * (N - len(b))
    if b[0] == 0:
        return None                      # a pole at the origin: no power series
    out = [sp.Integer(0)] * N
    for i in range(N):
        out[i] = sp.cancel((a[i] - sum(b[j] * out[i - j] for j in range(1, i + 1))) / b[0])
    return out


def direct_series(f, g, N):
    """a(n) = [x^n] f g^n, straight from the definition, for the independent check.

    This shares nothing with diagonal.series, which goes through the residue formula: here
    the n-th power of g is formed and its n-th coefficient read off.
    """
    out, gp = [], sp.Integer(1)
    for i in range(N):
        c = xcoeffs(sp.cancel(f * gp), i + 1)
        out.append(None if c is None else c[i])
        gp = sp.cancel(gp * g)
    return out


def build(spec):
    made = []
    for v in spec:
        num, a = v["num"], v["anum"]
        e = None
        for i in range(5):
            try:
                e = fetch(a); break
            except Exception:
                time.sleep(3 * (i + 1))
        if e is None:
            print(f"{num:4d}  {a}  SKIP could not fetch"); continue
        time.sleep(0.4)
        data = [int(q) for q in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        fg = dg.parse_extraction(v["definition"])
        if fg is None:
            print(f"{num:4d}  {a}  SKIP definition did not reparse"); continue
        f, g = fg
        N = min(len(data) - 1, 10)
        ser = dg.series(f, g, off + N + 3)
        if ser is None or not all(sp.simplify(ser[off + i] - data[i]) == 0
                                  for i in range(N + 1)):
            print(f"{num:4d}  {a}  SKIP series does not reproduce the terms"); continue
        # the second, independent computation the paper claims was done
        try:
            direct = direct_series(f, g, off + N + 1)
            agree = all(direct[i] is not None and sp.simplify(direct[i] - ser[i]) == 0
                        for i in range(off + N + 1))
        except Exception:
            agree = False
        if not agree:
            print(f"{num:4d}  {a}  SKIP the two series computations disagree"); continue
        P = dg.minimal_polynomial(f, g)
        fac = dg.pick_factor(P, ser, off + N + 3)
        if fac is None:
            print(f"{num:4d}  {a}  SKIP no branch"); continue
        minp = sp.expand(fac.subs(t, X))
        F = af.Field(minp)
        ps = parse_conj(v["conj"])
        ok, B = F.is_polynomial(F.residual(sp.Poly(y, y), ps, n))
        if not ok:
            print(f"{num:4d}  {a}  SKIP residual not polynomial"); continue
        deg = int(sp.Poly(B, X).total_degree()) if B != 0 else -1
        order = len(ps) - 1
        lo = max(order, deg + 1)
        bad = [i + off for i in range(lo, len(data))
               if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                      for j, p in enumerate(ps) if p != 0) != 0]
        nver, firstn = len(data) - lo, lo + off
        if bad or nver < 3:
            print(f"{num:4d}  {a}  SKIP integer re-check failed at n={bad[:3]}"); continue
        subs = {
            "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(q) for q in data[:8]) + ",\\ \\dots"),
            "DEFN": render_conj(v["definition"]),
            "FLATEX": sp.latex(f), "GLATEX": sp.latex(g),
            "MINPOLY": sp.latex(sp.factor(minp.subs(X, t))),
            "CONJ": render_conj(v["conj"]),
            "TIME": e["time"][:10], "REV": e["revision"],
            "BLATEX": sp.latex(B), "DEG": deg, "ORDER": order,
            "RECLATEX": rec_latex(ps),
            "NCHECK": min(len(data), 13), "NVER": nver, "FIRSTN": firstn,
        }
        from diagtex import TEMPLATE
        tex = TEMPLATE % subs
        d = f"build/diag{num}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(tex)
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "p.tex"],
                           cwd=d, capture_output=True)
        log = open(f"{d}/p.log", errors="ignore").read()
        errs = [l for l in log.split("\n") if l.startswith("! ")]
        good = os.path.exists(f"{d}/p.pdf") and not errs
        if good:
            subprocess.run(["cp", f"{d}/p.pdf", f"papers-new/{num}-PROOF.pdf"])
        made.append((num, a, good))
        print(f"{num:4d}  {a}  {'OK' if good else 'FAILED ' + str(errs[:1])}")
    print(f"\n{sum(1 for m in made if m[2])}/{len(made)} built")


if __name__ == "__main__":
    os.makedirs("papers-new", exist_ok=True)
    build(json.load(open(sys.argv[1])))
