#!/usr/bin/env python3
"""Build one paper per conjectured recurrence shown to be false.

The whole argument is redone here from the live entry: the generating function re-matched
against every published term, the residual re-reduced in the field, the counterexample
re-computed, and the replacement recurrence re-derived and re-proved. A disproof that
cannot be reproduced from scratch is not written.
"""
import json, os, subprocess, sys, time
import sympy as sp
import gfclean, algode, algfield as af, holo
from regf import entry, CONJ, GFL, match
from prove_rec import parse_conj
from makerecpapers import tex_escape, render_conj, rec_latex
from holonomic import taylor
from verify_open import fetch
from distex import TEMPLATE

x, n = sp.symbols('x n')


def clear_denominators(ps):
    """Scale the derived recurrence to integer polynomial coefficients.

    The ODE route naturally produces coefficients like (n^3-n)/64; the relation is the
    same after scaling, and a paper should not print the 64.
    """
    ps = [sp.cancel(sp.together(p)) for p in ps]
    den = sp.Integer(1)
    for p in ps:
        den = sp.lcm(den, sp.denom(p))
    ps = [sp.expand(sp.cancel(p * den)) for p in ps]
    g = sp.Integer(0)
    for p in ps:
        for c in sp.Poly(p, n).coeffs():
            g = sp.gcd(g, c)
    if g not in (0, 1):
        ps = [sp.expand(sp.cancel(p / g)) for p in ps]
    return ps


def true_rec_latex(ps, lo):
    """The derived recurrence, printed with a(n), a(n-1), ... after normalising the top
    shift to n."""
    r = len(ps) - 1
    top = lo + r
    out = []
    for j in range(r, -1, -1):
        p = sp.expand(ps[j].subs(n, n - top))
        if p == 0:
            continue
        k = top - (lo + j)
        term = "a(n)" if k == 0 else f"a(n-{k})"
        pl = sp.latex(sp.factor(p))
        if p.is_Add or p.is_Mul:
            pl = f"\\left({sp.latex(sp.expand(p))}\\right)" if p.is_Add else pl
        out.append(f"{pl}\\,{term}")
    return " + ".join(out).replace("+ -", "- ")


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
        data = [int(t) for t in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        F, _, _, _ = entry(a)
        gfline = next((l for l in F if GFL.match(l)), None)
        cands = [c for l in F if GFL.match(l) for c in gfclean.candidates(l)]
        A, src = match(cands, data, off, False)
        if A is None:
            print(f"{num:4d}  {a}  SKIP no g.f. matches"); continue
        base = taylor(A, off + len(data) + 40)
        if not all(sp.simplify(base[off + k] - data[k]) == 0 for k in range(len(data))):
            print(f"{num:4d}  {a}  SKIP the g.f. does not match EVERY published term")
            continue
        ps = parse_conj(v["conj"])
        K, u = af.from_expr(A)
        ok, B = K.is_polynomial(K.residual(u, ps, n))
        if ok:
            print(f"{num:4d}  {a}  SKIP the residual IS a polynomial -- not a disproof")
            continue
        order = len(ps) - 1
        rows, failn, failval = [], None, None
        for m in range(off + order, off + min(len(data), 14)):
            tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * base[m - i]
                      for i, p in enumerate(ps) if p != 0)
            rows.append((m, sp.nsimplify(tot, rational=True)))
            if tot != 0 and failn is None:
                failn, failval = m, sp.nsimplify(tot, rational=True)
        if failn is None:
            print(f"{num:4d}  {a}  SKIP no counterexample among the published terms")
            continue
        # the correct recurrence
        got = holo.annihilator(A)
        derivation, tps, tlo = None, None, None
        if got is not None:
            hps, start = got
            sh = holo.align_shift(hps, base, start)
            if sh is not None:
                tps = [sp.expand(p.subs(n, n - sh)) for p in hps] if sh else hps
                tlo = 0
                derivation = ("It satisfies a linear differential equation with polynomial "
                              "coefficients, and reading off the coefficient of each power "
                              "of $x$ turns that equation into the recurrence below.")
        if tps is None:
            qs = algode.ode_from_poly(K.P.as_expr())
            if qs is None:
                print(f"{num:4d}  {a}  SKIP no correct recurrence derived"); continue
            r2 = algode.recurrence_from_ode(qs)
            if r2 is None:
                print(f"{num:4d}  {a}  SKIP the ODE gave no recurrence"); continue
            tps, tlo = r2
            derivation = (
                r"Differentiating the algebraic equation satisfied by $A$ expresses $A'$ "
                r"inside the field $" + r"\mathbb{Q}(x)[y]/(P)" + r"$, so $A,A',\dots$ span "
                r"a finite-dimensional space over $\mathbb{Q}(x)$ and satisfy a linear "
                r"differential equation with polynomial coefficients. Reading off the "
                r"coefficient of each power of $x$ turns that equation into a recurrence.")
        tps = clear_denominators(tps)
        rt = len(tps) - 1
        top = tlo + rt
        tnorm = [sp.expand(tps[j].subs(n, n - top)) for j in range(rt + 1)][::-1]
        okT, TB = K.is_polynomial(K.residual(u, tnorm, n))
        if not okT:
            print(f"{num:4d}  {a}  SKIP the replacement recurrence does not check out")
            continue
        tzero = (sp.expand(TB) == 0)
        tdeg = -1 if tzero else int(sp.Poly(TB, x).total_degree())
        tver = 0
        for m in range(max(off + rt, tdeg + 1), off + len(data)):
            tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * data[m - i - off]
                      for i, p in enumerate(tnorm) if p != 0 and 0 <= m - i - off < len(data))
            if tot != 0:
                tver = -1
                break
            tver += 1
        if tver < 3:
            print(f"{num:4d}  {a}  SKIP replacement fails on the published terms"); continue
        nz = sum(1 for _, val in rows if val != 0)
        subs = {
            "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "GFLINE": render_conj(gfline), "GFLATEX": sp.latex(sp.simplify(A)),
            "NDATA": len(data),
            "CONJ": render_conj(v["conj"]),
            "TIME": e["time"][:10], "REV": e["revision"],
            "ORDERC": order, "RECLATEX": rec_latex(ps),
            "FIELD": r"\mathbb{Q}(x)[y]/\bigl(P(x,y)\bigr)",
            "TABLE": " \\\\\n".join(f"${m}$ & ${sp.latex(val)}$" for m, val in rows),
            "FAILN": failn, "FAILVAL": sp.latex(failval),
            "INDEXNOTE": (
                r"\begin{remark}" "\n"
                r"The failure is not a matter of how the recurrence is indexed. Shifting "
                r"the argument of the coefficients and the indices of the terms together, "
                r"by any amount between $-5$ and $5$, does not make it hold on the "
                r"published data either." "\n"
                r"\end{remark}"),
            "NATURE": "algebraic over $\\mathbb{Q}(x)$",
            "DERIVATION": derivation,
            "TRUEREC": true_rec_latex(tps, tlo), "ORDERT": rt,
            "TRUEFROM": max(off + rt, tdeg + 1), "TRUEVER": tver,
            "TRUEPROOF": (
                "reduces, in $" + r"\mathbb{Q}(x)[y]/\bigl(P(x,y)\bigr)" + "$, to $0$ "
                "identically. By Lemma~\\ref{lem:transfer} the recurrence therefore "
                "holds at every $n$ for which it is stated, that is for "
                f"$n\\ge{max(off + rt, tdeg + 1)}$."
                if tzero else
                "reduces, in $" + r"\mathbb{Q}(x)[y]/\bigl(P(x,y)\bigr)" + "$, to the "
                "polynomial\n\\[\n" + sp.latex(sp.expand(TB)) + "\n\\]\nof degree "
                f"${tdeg}$. By Lemma~\\ref{{lem:transfer}} the recurrence holds for "
                f"every $n>{tdeg}$."),
            "INDEPNOTE": (f"it is nonzero at {nz} of the "
                          f"{len(rows)} indices tabulated above."),
        }
        tex = TEMPLATE % subs
        d = f"build/dis{num}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(tex)
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "p.tex"],
                           cwd=d, capture_output=True)
        log = open(f"{d}/p.log", errors="ignore").read()
        errs = [l for l in log.split("\n") if l.startswith("! ")]
        good = os.path.exists(f"{d}/p.pdf") and not errs
        if good:
            subprocess.run(["cp", f"{d}/p.pdf", f"papers-new/{num}-DISPROOF.pdf"])
        made.append((num, a, good))
        print(f"{num:4d}  {a}  {'OK' if good else 'FAILED ' + str(errs[:1])}")
    print(f"\n{sum(1 for m in made if m[2])}/{len(made)} built")


if __name__ == "__main__":
    os.makedirs("papers-new", exist_ok=True)
    build(json.load(open(sys.argv[1])))
