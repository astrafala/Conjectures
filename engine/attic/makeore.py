#!/usr/bin/env python3
"""Build one paper per conjecture that factors through the entry's stated recurrence."""
import json, os, re, subprocess, sys, time
import sympy as sp
import ore
from ore import n
from ore_prove import coeffs, numeric_ok
from oretex import TEMPLATE
from makerecpapers import tex_escape, render_conj, rec_latex
from verify_open import fetch

x = sp.Symbol('x')


def qlatex(Q):
    parts = []
    for j, c in enumerate(Q):
        c = sp.cancel(c)
        if c == 0:
            continue
        cl = sp.latex(sp.factor(c))
        if c.is_Add or (sp.denom(c) != 1):
            cl = f"\\left({sp.latex(sp.cancel(c))}\\right)"
        parts.append(cl + ("" if j == 0 else f"\\,N^{{{j}}}" if j > 1 else "\\,N"))
    return " + ".join(parts).replace("+ -", "- ") or "0"


def build(spec):
    made = []
    for v in spec:
        num, a = v["num"], v["anum"]
        e = None
        for attempt in range(4):
            try:
                e = fetch(a)
                break
            except Exception:
                time.sleep(2 * (attempt + 1))
        if e is None:
            print(f"{num:4d}  {a}  SKIP could not fetch the live entry")
            continue
        time.sleep(0.4)
        data = [int(t) for t in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        pc, pp = coeffs(v["conj"]), coeffs(v["proven"])
        C, P = ore.to_operator(pc), ore.to_operator(pp)
        Q, R = ore.right_divide(C, P)
        if not ore.is_zero(R) or ore.trivial(Q):
            print(f"{num:4d}  {a}  SKIP factorisation did not reproduce")
            continue
        # multiply back, as the paper claims was done
        back = [sp.Integer(0)] * (len(Q) + len(P))
        for d, qc in enumerate(Q):
            for i, t in enumerate(ore.shift_mul(P, d)):
                back[i] += qc * t
        if any(sp.cancel(back[i] - (C[i] if i < len(C) else 0)) != 0
               for i in range(len(back))):
            print(f"{num:4d}  {a}  SKIP Q*P does not expand back to C")
            continue
        bad, nver, firstn = numeric_ok(pc, data, off)
        badp, nverp, _ = numeric_ok(pp, data, off)
        if bad or badp or nver < 3:
            print(f"{num:4d}  {a}  SKIP numeric check failed")
            continue
        exc = ore.exceptional_set(Q)
        ints = [int(t) for t in exc if t.is_integer]
        inrange = [i for i in ints if i >= firstn]
        if inrange:
            print(f"{num:4d}  {a}  SKIP a denominator vanishes inside the claimed range "
                  f"at n={inrange}")
            continue
        if ints:
            exctext = (r"The coefficients of $Q$ are rational functions of $n$. Their only "
                       r"integer poles are $n\in\{" + ", ".join(str(i) for i in ints) +
                       r"\}$, all of them below the range claimed here, so no $n$ in "
                       r"question is excluded.")
            excproof = (r"The integer poles of the coefficients of $Q$ all lie below "
                        r"$n=%d$, so the lemma applies throughout the stated range." % firstn)
        else:
            exctext = (r"The coefficients of $Q$ are rational functions of $n$, and none of "
                       r"their poles is an integer, so Lemma~\ref{lem:factor} applies at "
                       r"every index.")
            excproof = (r"No coefficient of $Q$ has an integer pole, so the lemma applies "
                        r"at every $n$.")
        subs = {
            "ANUM": a,
            "NAME": tex_escape(e["name"].rstrip('.')),
            "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "CONJ": render_conj(v["conj"]),
            "PROVEN": render_conj(v["proven"]),
            "TIME": e["time"][:10],
            "REV": e["revision"],
            "ORDERC": len(pc) - 1,
            "ORDERP": len(pp) - 1,
            "QLATEX": qlatex(Q),
            "EXCTEXT": exctext,
            "EXCPROOF": excproof,
            "RECLATEX": rec_latex(pc),
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
