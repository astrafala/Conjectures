#!/usr/bin/env python3
"""Build a paper for a conjecture settled by the complete annihilation test.

Used where the conjectured operator is NOT a left multiple of the one the entry states.
The argument is redone here from the live entry.
"""
import json, os, subprocess, sys, time
import sympy as sp
import ore, oremod
from ore import n
from ore2tex import TEMPLATE
from ore_prove import coeffs as rec_coeffs
from makerecpapers import tex_escape, render_conj, rec_latex
from maketel import oplatex
from regf import entry
from verify_open import fetch


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
        pc, pp = rec_coeffs(v["conj"]), rec_coeffs(v["proven"])
        C, P = ore.to_operator(pc), ore.to_operator(pp)
        Q, R = oremod.reduce_right(C, P)
        if ore.is_zero(R):
            print(f"{num:4d}  {a}  SKIP the remainder is zero: use the plain builder")
            continue
        seq = [sp.Integer(t) for t in data]
        ok, T, sfrom, bad = oremod.vanishes(R, P, seq, off, off)
        if not ok:
            print(f"{num:4d}  {a}  SKIP the residual does not vanish"); continue
        order = len(pc) - 1
        nver, firstn = 0, None
        for idx in range(order, len(data)):
            m = idx + off
            tot = sum(sp.Rational(sp.Poly(p, n).eval(m)) * data[idx - i]
                      for i, p in enumerate(pc) if p != 0)
            if tot != 0:
                nver = -1
                break
            nver += 1
            firstn = m if firstn is None else firstn
        if nver < 3:
            print(f"{num:4d}  {a}  SKIP the conjecture fails on the published terms")
            continue
        d = len(T) - 1
        subs = {
            "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "CONJ": render_conj(v["conj"]), "PROVEN": render_conj(v["proven"]),
            "TIME": e["time"][:10], "REV": e["revision"],
            "ORDERC": order, "ORDERP": len(pp) - 1,
            "QLATEX": oplatex(Q), "RLATEX": oplatex(R),
            "TLATEX": oplatex(T), "TORDER": d,
            "TPOLETEXT": (("The leading coefficient of $T$ has integer zeros at $n\\in\\{"
                           + ", ".join(str(b) for b in bad) + "\\}$, all below the range "
                           "used here.") if bad else
                          "The leading coefficient of $T$ has no integer zero, so the "
                          "propagation in Lemma~3 is valid at every index."),
            "SFROM": int(sfrom), "RECLATEX": rec_latex(pc),
            "NVER": nver, "FIRSTN": firstn,
        }
        tex = TEMPLATE % subs
        dd = f"build/or{num}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(tex)
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "p.tex"],
                           cwd=dd, capture_output=True)
        log = open(f"{dd}/p.log", errors="ignore").read()
        errs = [l for l in log.split("\n") if l.startswith("! ")]
        good = os.path.exists(f"{dd}/p.pdf") and not errs
        if good:
            subprocess.run(["cp", f"{dd}/p.pdf", f"papers-new/{num}-PROOF.pdf"])
        made.append((num, a, good))
        print(f"{num:4d}  {a}  {'OK' if good else 'FAILED ' + str(errs[:1])}")
    print(f"\n{sum(1 for m in made if m[2])}/{len(made)} built")


if __name__ == "__main__":
    os.makedirs("papers-new", exist_ok=True)
    build(json.load(open(sys.argv[1])))
