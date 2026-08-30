#!/usr/bin/env python3
"""Build one paper per conjecture settled from a posted closed form.

The whole argument is redone here, independently of the search run: the formula is
re-parsed, re-checked against the entry's live DATA, and the class residuals recomputed
from scratch. A paper is written only if that reproduction succeeds.
"""
import json, os, re, subprocess, sys, time
import sympy as sp
import cfparse, hyperterm as ht
from hyperterm import n
from hypertex import TEMPLATE
from makerecpapers import tex_escape, render_conj, rec_latex
from prove_rec import parse_conj
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
            print(f"{num:4d}  {a}  SKIP could not fetch the entry"); continue
        time.sleep(0.4)
        data = [int(t) for t in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        cf = cfparse.parse(v["formula"])
        if cf is None:
            print(f"{num:4d}  {a}  SKIP the formula did not reparse"); continue
        if not cfparse.matches(cf, data, off):
            print(f"{num:4d}  {a}  SKIP the formula does not match the live terms")
            continue
        fv = cfparse.first_valid(cf, data, off)
        if fv is None:
            print(f"{num:4d}  {a}  SKIP the formula is not usable at any index"); continue
        ps = parse_conj(v["conj"])
        ok, info = ht.verdict(ps, cf)
        if ok is not True:
            print(f"{num:4d}  {a}  SKIP did not reproduce: {ok}"); continue
        excl = ht.excluded(info, ps)
        skip = {int(t) for t in excl if t.is_Integer}
        order = len(ps) - 1
        lo = order
        bad, nver = [], 0
        firstn = None
        for idx in range(lo, len(data)):
            nn = idx + off
            if nn in skip:
                continue
            tot = sum(sp.Rational(sp.Poly(p, n).eval(nn)) * data[idx - i]
                      for i, p in enumerate(ps) if p != 0)
            if tot != 0:
                bad.append(nn)
            else:
                nver += 1
                firstn = nn if firstn is None else firstn
        if bad or nver < 3:
            print(f"{num:4d}  {a}  SKIP integer re-check failed at {bad[:3]}"); continue
        ncl = len(info)
        exclint = sorted(skip)
        start = max(order + off, fv + order)
        if exclint:
            start = max(start, max(exclint) + 1)
        excltex = r"\ge %d" % start
        subs = {
            "ANUM": a, "NAME": tex_escape(e["name"].rstrip('.')), "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in data[:8]) + ",\\ \\dots"),
            "FORMULA": render_conj(v["formula"]),
            "CFLATEX": sp.latex(cf),
            "CONJ": render_conj(v["conj"]),
            "TIME": e["time"][:10], "REV": e["revision"],
            "ORDER": order, "RECLATEX": rec_latex(ps),
            "NCLASS": ("one" if ncl == 1 else "two" if ncl == 2 else str(ncl)),
            "ES": "" if ncl == 1 else "es",
            "IES": "y" if ncl == 1 else "ies",
            "CLASSLATEX": ",\\qquad ".join(sp.latex(c[0]) for c in info),
            "SLATEX": ",\\qquad ".join(
                f"S_{{{i+1}}}(n)\;=\;{sp.latex(sp.cancel(c[1]))}"
                for i, c in enumerate(info)),
            "EXCLTEX": excltex,
            "NCHECK": min(len(data), 13), "NVER": nver, "FIRSTN": firstn,
        }
        tex = TEMPLATE % subs
        d = f"build/hyp{num}"
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
