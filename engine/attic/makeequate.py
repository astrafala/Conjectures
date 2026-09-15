#!/usr/bin/env python3
"""Build one paper per conjectured closed form or generating function settled by equate.py.

The whole argument is redone here from the live entry, independently of the search run.
"""
import json, os, re, subprocess, sys, time
import sympy as sp
import cfparse, equate, gfclean, equate_run, ore
from equate import x, n
from equatetex import TEMPLATE
from makerecpapers import tex_escape, render_conj, rec_latex
from prove_rec import parse_gf
from regf import entry
from holonomic import taylor
from verify_open import fetch


def oplatex(L):
    parts = []
    for j, t in enumerate(L):
        t = sp.cancel(t)
        if t == 0:
            continue
        tl = sp.latex(sp.factor(t))
        if t.is_Add:
            tl = f"\\left({sp.latex(sp.expand(t))}\\right)"
        parts.append(f"{tl}\\,a(n+{j})" if j > 1 else
                     (f"{tl}\\,a(n+1)" if j == 1 else f"{tl}\\,a(n)"))
    return (" + ".join(parts) + " \;=\; 0").replace("+ -", "- ")


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
        got = equate_run.work(a)
        if got.get("status") != "PROVED":
            print(f"{num:4d}  {a}  SKIP did not reproduce: {got.get('status')}")
            continue
        L = [sp.sympify(t) for t in got["operator"]]
        r = len(L) - 1
        n0 = got["from_n"]
        kind = got["kind"]
        conj = got["conj"]
        knownw = {"stated recurrence": "a recurrence",
                  "generating function": "a generating function",
                  "closed form": "a closed form"}[got["known"]]
        if got["known"] == "stated recurrence":
            deriv = ("The entry states the recurrence below as fact, so nothing has to be "
                     "derived; it is quoted here in the shift form used throughout, "
                     "$\\sum_{j}q_{j}(n)a(n+j)=0$.")
        elif got["known"] == "generating function":
            deriv = (
                "The generating function the entry posts is algebraic over "
                "$\\mathbb{Q}(x)$, hence $D$-finite: it satisfies a linear differential "
                "equation with polynomial coefficients, obtained by differentiating its "
                "defining equation inside the field it generates and taking a linear "
                "dependence among the derivatives. Reading off the coefficient of each "
                "power of $x$ turns that differential equation into a recurrence for the "
                "coefficients, which is")
        else:
            deriv = (
                "The closed form the entry posts is a sum of finitely many hypergeometric "
                "terms. For terms $t_{1},\\dots,t_{m}$ one may seek $c_{0},\\dots,c_{m}$ "
                "in $\\mathbb{Q}(n)$ with $\\sum_{k}c_{k}(n)t_{j}(n+k)=0$ for every $j$; "
                "dividing the $j$-th equation by $t_{j}(n)$ makes every coefficient a "
                "rational function, so this is $m$ equations in $m+1$ unknowns over "
                "$\\mathbb{Q}(n)$ and a nonzero solution exists. It gives")
        bad = got.get("leading_poles") or []
        poletext = (("Its only integer zeros are $n\\in\\{" + ", ".join(map(str, bad)) +
                     "\\}$, all below the range claimed here.") if bad else
                    "It has no integer zero at all, so the recurrence steps at every index.")
        if kind == "closed form":
            cf = cfparse.parse(equate_run.strip_conj(conj))
            cf, _ = cfparse.align(cf, data, off)
            claim = f"a(n) \;=\; {sp.latex(cf)}"
            check = (
                "The conjectured closed form is a sum of hypergeometric terms. Substituting "
                "it into \\eqref{eq:rec} and grouping the summands into similarity classes "
                "-- two terms being similar when their quotient is a rational function of "
                "$n$ -- every class contributes a rational function of $n$, and each of "
                "those cancels to zero identically. Since pairwise dissimilar "
                "hypergeometric terms are linearly independent over $\\mathbb{Q}(n)$, that "
                "is exactly the statement that the closed form satisfies \\eqref{eq:rec}.")
        else:
            src = None
            for c in gfclean.candidates(equate_run.strip_conj(conj)):
                try:
                    G = parse_gf(c, 'x', raw=c)
                    src = G
                    break
                except Exception:
                    continue
            claim = (r"\sum_{n\ge %d} a(n)x^{n} \;=\; %s" % (off, sp.latex(sp.simplify(src))))
            check = (
                "Write $\\theta=x\\,\\frac{d}{dx}$ and, for the coefficients $p_{i}$ of "
                "\\eqref{eq:rec} written in the backward form $\\sum_{i}p_{i}(n)a(n-i)=0$, "
                "set $B(x)=\\sum_{i}x^{i}\\,(p_{i}(\\theta+i)A)(x)$ for the conjectured "
                "generating function $A$. Then $[x^{n}]B=\\sum_{i}p_{i}(n)a(n-i)$, so the "
                "conjectured generating function has coefficients satisfying "
                "\\eqref{eq:rec} exactly when $B$ is a polynomial. Reducing $B$ inside the "
                "field $A$ generates, which is closed under $\\theta$, gives a polynomial, "
                "and the verification is an exact cancellation of rational functions.")
        subs = {
            "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "KINDWORD": kind, "KNOWNWORD": knownw, "KNOWNWORD2": knownw,
            "KNOWNLINE": render_conj(got["known_src"]),
            "CONJ": render_conj(conj),
            "TIME": e["time"][:10], "REV": e["revision"],
            "ORDER": r, "DERIVSECTION": deriv, "OPLATEX": oplatex(L),
            "LEADLATEX": sp.latex(sp.factor(sp.cancel(L[-1]))),
            "POLETEXT": poletext, "CHECKSECTION": check,
            "CLAIMLATEX": claim, "FROMN": n0,
            "NCHECK": min(len(data), 13),
        }
        tex = TEMPLATE % subs
        d = f"build/eq{num}"
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
