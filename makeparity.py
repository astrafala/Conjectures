#!/usr/bin/env python3
"""Build one paper per conjecture settled by splitting the closed form on parity.

The argument is redone from the live entry, independently of the search run.
"""
import json, os, re, subprocess, sys, time
import sympy as sp
import cfparse, parity, hyperterm as ht
from parity import m
from paritytex import TEMPLATE
from makerecpapers import tex_escape, render_conj, rec_latex
from prove_rec import parse_conj
from parity_run import parse_with_rounding
from verify_open import fetch

n = sp.Symbol('n')


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
        cf = parse_with_rounding(v["formula"])
        if cf is None:
            print(f"{num:4d}  {a}  SKIP the formula did not reparse"); continue
        cf, shift = cfparse.align(cf, data, off)
        if cf is None:
            print(f"{num:4d}  {a}  SKIP the formula does not match the live terms")
            continue
        h = parity.halves(cf)
        if h is None:
            print(f"{num:4d}  {a}  SKIP the parity split left a rounding"); continue
        e0, e1 = h
        fv = cfparse.first_valid(cf, data, off)
        if fv is None:
            print(f"{num:4d}  {a}  SKIP the formula is not usable at any index"); continue
        ps = parse_conj(v["conj"])
        res = {}
        for odd in (False, True):
            res[odd] = ht.is_zero_sum(parity.combination(ps, e0, e1, odd), m)
        if not (res[False][0] and res[True][0]):
            print(f"{num:4d}  {a}  SKIP did not reproduce: {res[False][0]}/{res[True][0]}")
            continue
        order = len(ps) - 1
        bad, nver, firstn = [], 0, None
        for idx in range(order, len(data)):
            nn = idx + off
            tot = sum(sp.Rational(sp.Poly(p, n).eval(nn)) * data[idx - i]
                      for i, p in enumerate(ps) if p != 0)
            if tot != 0:
                bad.append(nn)
            else:
                nver += 1
                firstn = nn if firstn is None else firstn
        if bad or nver < 3:
            print(f"{num:4d}  {a}  SKIP integer re-check failed at {bad[:3]}"); continue
        ne, no = len(res[False][1]), len(res[True][1])
        word = lambda c: ("one" if c == 1 else "two" if c == 2 else
                          "three" if c == 3 else str(c))
        subs = {
            "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "FORMULA": render_conj(v["formula"]),
            "CFLATEX": sp.latex(cf),
            "SHIFTNOTE": ("the formula is stated in the entry's own indexing."
                          if not shift else
                          f"the formula as posted gives $a(n+{shift})$, and is used here "
                          f"shifted accordingly." if shift > 0 else
                          f"the formula as posted gives $a(n{shift})$, and is used here "
                          f"shifted accordingly."),
            "CONJ": render_conj(v["conj"]),
            "TIME": e["time"][:10], "REV": e["revision"],
            "ORDER": order, "RECLATEX": rec_latex(ps),
            "EVENLATEX": sp.latex(e0), "ODDLATEX": sp.latex(e1),
            "NEVEN": word(ne), "EES": "" if ne == 1 else "es",
            "NODD": word(no), "OES": "" if no == 1 else "es",
            "EXCLTEX": r"\ge %d" % max(order + off, fv + order),
            "NCHECK": min(len(data), 13), "NVER": nver, "FIRSTN": firstn,
        }
        tex = TEMPLATE % subs
        d = f"build/par{num}"
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
