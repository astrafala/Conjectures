#!/usr/bin/env python3
"""Build one paper per conjecture settled by creative telescoping."""
import json, os, re, subprocess, sys, time
import sympy as sp
import zeil, ore
from zeil import n, k
from teltex import TEMPLATE
from makerecpapers import tex_escape, render_conj, rec_latex
from prove_rec import parse_conj
from verify_open import fetch
from zeil_run import parse_sum, numeric_ok

x = sp.Symbol('x')


def oplatex(c, sym="N"):
    parts = []
    for j, t in enumerate(c):
        t = sp.cancel(t)
        if t == 0:
            continue
        tl = sp.latex(sp.factor(t))
        if t.is_Add or sp.denom(t) != 1:
            tl = f"\\left({sp.latex(sp.cancel(t))}\\right)"
        parts.append(tl + ("" if j == 0 else f"\\,{sym}^{{{j}}}" if j > 1 else f"\\,{sym}"))
    return " + ".join(parts).replace("+ -", "- ") or "0"


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
            print(f"{num:4d}  {a}  SKIP could not fetch the entry"); continue
        time.sleep(0.5)
        data = [int(t) for t in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        F, lo, hi = parse_sum(v["formula"])
        pc = parse_conj(v["conj"])
        C = ore.to_operator(pc)
        # redo the whole argument here, independently of the search run
        tel = None
        for r in range(1, v["order_derived"] + 1):
            tel = zeil.telescoper(F, r)
            if tel is not None:
                break
        if tel is None:
            print(f"{num:4d}  {a}  SKIP telescoper did not reproduce"); continue
        sig, R = tel
        if not zeil.verify(F, sig, R):
            print(f"{num:4d}  {a}  SKIP certificate failed to verify"); continue
        if not zeil.natural_boundary(F, lo, hi, len(pc) - 1):
            print(f"{num:4d}  {a}  SKIP summand does not vanish off the range"); continue
        L = [sp.cancel(t) for t in sig]
        Q, Rem = ore.right_divide(C, L)
        if not ore.is_zero(Rem):
            print(f"{num:4d}  {a}  SKIP division left a remainder"); continue
        back = [sp.Integer(0)] * (len(Q) + len(L))
        for d, qc in enumerate(Q):
            for i, t in enumerate(ore.shift_mul(L, d)):
                back[i] += qc * t
        if any(sp.cancel(back[i] - (C[i] if i < len(C) else 0)) != 0
               for i in range(len(back))):
            print(f"{num:4d}  {a}  SKIP Q*L does not expand back to C"); continue
        bad, nver, firstn = numeric_ok(pc, data, off)
        if bad or nver < 3:
            print(f"{num:4d}  {a}  SKIP numeric check failed"); continue
        exc = ore.exceptional_set(Q)
        ints = [int(t) for t in exc if t.is_integer]
        inrange = [i for i in ints if i >= firstn]
        if inrange:
            print(f"{num:4d}  {a}  SKIP a denominator vanishes in range at n={inrange}")
            continue
        oc, od = len(pc) - 1, len(L) - 1
        if oc > od:
            why = (f"the conjectured recurrence has order ${oc}$ while the summand only "
                   f"needs order ${od}$, so it is not itself a telescoper and cannot be "
                   f"produced directly.")
            why2 = (f"It has order ${od}$, below the conjectured order ${oc}$: the "
                    f"conjecture is a consequence of a shorter relation, not the shortest "
                    f"relation itself.")
        else:
            why = ("the two operators have the same order but are not proportional, so "
                   "the conjecture still has to be derived from what telescoping gives.")
            why2 = ("It has the same order as the conjectured one but is not a multiple "
                    "of it by a constant.")
        if ints:
            exctext = (r"The coefficients of $Q$ are rational functions of $n$; their only "
                       r"integer poles are $n\in\{" + ", ".join(str(i) for i in ints) +
                       r"\}$, below the range claimed here.")
            excproof = (r"The integer poles of $Q$ all lie below $n=%d$." % firstn)
        else:
            exctext = (r"No coefficient of $Q$ has an integer pole, so "
                       r"Lemma~\ref{lem:factor} applies at every index.")
            excproof = r"No coefficient of $Q$ has an integer pole."
        subs = {
            "ANUM": a,
            "NAME": tex_escape(e["name"].rstrip('.')),
            "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "FORMULA": render_conj(v["formula"]),
            "FLATEX": sp.latex(F),
            "LO": sp.latex(lo), "HI": sp.latex(hi),
            "CONJ": render_conj(v["conj"]),
            "TIME": e["time"][:10], "REV": e["revision"],
            "ORDERC": oc, "ORDERD": od,
            "WHYDIV": why, "WHYDIV2": why2,
            "SIGMALATEX": ",\\qquad ".join(
                f"\\sigma_{{{i}}}(n)={sp.latex(sp.cancel(t))}" for i, t in enumerate(L)),
            "CERTLATEX": sp.latex(sp.cancel(R)),
            "QLATEX": oplatex(Q),
            "EXCTEXT": exctext, "EXCPROOF": excproof,
            "RECLATEX": rec_latex(pc),
            "NVER": nver, "FIRSTN": firstn,
        }
        tex = TEMPLATE % subs
        d = f"build/tel{num}"
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
