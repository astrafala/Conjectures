#!/usr/bin/env python3
"""Build one paper per conjecture settled by boundary-corrected creative telescoping.

The argument is redone here from the live entry, independently of the search run: the
summand is re-parsed and re-checked, the certificate re-found and re-verified, the
inhomogeneity recomputed and re-tested on the published terms, and the division redone
and multiplied back.
"""
import json, os, subprocess, sys, time
import sympy as sp
import zeil, zeilb, ore, sumparse
from zeil import n, k
from zeilbtex import TEMPLATE
from makerecpapers import tex_escape, render_conj, rec_latex
from prove_rec import parse_conj
from verify_open import fetch
from zeil_run import numeric_ok
from maketel import oplatex


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
        time.sleep(0.4)
        data = [int(t) for t in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        parsed = sumparse.parse(v["formula"])
        if parsed is None:
            print(f"{num:4d}  {a}  SKIP the formula did not reparse"); continue
        F, lo, hi = parsed
        for i in range(min(6, len(data))):
            val = sumparse.evaluate(F, lo, hi, off + i)
            if val is None or sp.simplify(val - data[i]) != 0:
                print(f"{num:4d}  {a}  SKIP the summand does not match the live terms")
                break
        else:
            pc = parse_conj(v["conj"])
            C = ore.to_operator(pc)
            tel = None
            for r in range(1, v["order_derived"] + 2):
                tel = zeil.telescoper(F, r)
                if tel is not None:
                    break
            if tel is None:
                print(f"{num:4d}  {a}  SKIP telescoper did not reproduce"); continue
            sig, R = tel
            if not zeil.verify(F, sig, R):
                print(f"{num:4d}  {a}  SKIP certificate failed to verify"); continue
            h = zeilb.inhomogeneity(F, sig, R, lo, hi)
            if h is None:
                print(f"{num:4d}  {a}  SKIP inhomogeneity not computable"); continue
            if zeilb.check_numeric(F, lo, hi, sig, h, data, off) is not True:
                print(f"{num:4d}  {a}  SKIP the inhomogeneous recurrence fails on terms")
                continue
            L, how = zeilb.annihilator(sig, h)
            if L is None:
                print(f"{num:4d}  {a}  SKIP {how}"); continue
            Q, Rem = ore.right_divide(C, L)
            if not ore.is_zero(Rem):
                print(f"{num:4d}  {a}  SKIP division left a remainder"); continue
            back = [sp.Integer(0)] * (len(Q) + len(L))
            for d_, qc in enumerate(Q):
                for i, t in enumerate(ore.shift_mul(L, d_)):
                    back[i] += qc * t
            if any(sp.cancel(back[i] - (C[i] if i < len(C) else 0)) != 0
                   for i in range(len(back))):
                print(f"{num:4d}  {a}  SKIP Q*L does not expand back to C"); continue
            bad, nver, firstn = numeric_ok(pc, data, off)
            if bad or nver < 3:
                print(f"{num:4d}  {a}  SKIP numeric check failed"); continue
            exc = ore.exceptional_set(Q)
            ints = [int(t) for t in exc if t.is_integer]
            if [i for i in ints if i >= firstn]:
                print(f"{num:4d}  {a}  SKIP a denominator vanishes in range"); continue
            homog = sp.simplify(h) == 0
            if homog:
                cleartext = ("Here those terms cancel and $h$ is identically zero, so the "
                             "recurrence is homogeneous after all --- but that is a "
                             "conclusion of the computation, not an assumption of it.")
                clearsection = (
                    r"For %s the inhomogeneity \eqref{eq:h} vanishes identically, so "
                    r"$L=\sum_{i}\sigma_{i}(n)N^{i}$ already annihilates $a$. The "
                    r"conjectured operator is not $L$, and the two are connected by "
                    r"division." % a)
            else:
                rho = sp.cancel(sp.together(sp.simplify(h.subs(n, n + 1) / h)))
                cleartext = ("Since $h$ is a hypergeometric term, the first-order operator "
                             "$M=N-h(n+1)/h(n)$ annihilates it, and $ML$ annihilates $a$.")
                clearsection = (
                    r"The inhomogeneity \eqref{eq:h} is a hypergeometric term: its shift "
                    r"quotient is" "\n"
                    r"\[" "\n"
                    r"\frac{h(n+1)}{h(n)}\;=\;" + sp.latex(rho) + r"," "\n"
                    r"\]" "\n"
                    r"a rational function of $n$. Hence $M=N-h(n+1)/h(n)$ satisfies "
                    r"$M(h)=0$, and writing $L_{0}=\sum_{i}\sigma_{i}(n)N^{i}$ for the "
                    r"telescoped operator, Proposition~\ref{prop:inhom} reads "
                    r"$L_{0}(a)=h$, so" "\n"
                    r"\[" "\n"
                    r"L\;=\;ML_{0}\quad\text{satisfies}\quad L(a)=M\bigl(L_{0}(a)\bigr)"
                    r"=M(h)=0 ." "\n"
                    r"\]" "\n"
                    r"One extra order buys the homogeneity. Explicitly, "
                    r"$L=" + oplatex(L) + r"$.")
            if ints:
                exctext = (r"The coefficients of $Q$ are rational functions of $n$; their "
                           r"only integer poles are $n\in\{"
                           + ", ".join(str(i) for i in ints) +
                           r"\}$, below the range claimed here.")
                excproof = r"The integer poles of $Q$ all lie below $n=%d$." % firstn
            else:
                exctext = (r"No coefficient of $Q$ has an integer pole, so "
                           r"Lemma~\ref{lem:factor} applies at every index.")
                excproof = r"No coefficient of $Q$ has an integer pole."
            subs = {
                "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
                "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                               + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
                "FORMULA": render_conj(v["formula"]),
                "FLATEX": sp.latex(F), "LO": sp.latex(lo), "HI": sp.latex(hi),
                "CONJ": render_conj(v["conj"]),
                "TIME": e["time"][:10], "REV": e["revision"],
                "ORDERC": len(pc) - 1, "ORDERT": len(sig) - 1,
                "SIGMALATEX": ",\\qquad ".join(
                    f"\\sigma_{{{i}}}(n)={sp.latex(sp.cancel(t))}"
                    for i, t in enumerate(sig)),
                "CERTLATEX": sp.latex(sp.cancel(R)),
                "HLATEX": sp.latex(sp.simplify(h)),
                "CLEARTEXT": cleartext, "CLEARSECTION": clearsection,
                "QLATEX": oplatex(Q), "EXCTEXT": exctext, "EXCPROOF": excproof,
                "RECLATEX": rec_latex(pc), "NVER": nver, "FIRSTN": firstn,
            }
            tex = TEMPLATE % subs
            d = f"build/zb{num}"
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
    print(f"\n{sum(1 for m_ in made if m_[2])}/{len(made)} built")


if __name__ == "__main__":
    os.makedirs("papers-new", exist_ok=True)
    build(json.load(open(sys.argv[1])))
