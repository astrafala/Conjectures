#!/usr/bin/env python3
"""Build one paper per slot from an explicit list.

Unlike the earlier builders this is keyed on the conjecture, not on the entry: two
entries here carry two separate conjectured recurrences apiece, and each of them is
its own result and its own paper. Each paper stands alone and refers to no other.
"""
import json, os, re, subprocess, sys
import sympy as sp
from prove_rec import parse_gf, parse_conj, residual_poly
from eqform_prove import parse_eq
from holonomic import taylor
import quadfield as qf
import multiquad as mq
import logexp as le
import algfield as af
from makerecpapers import TEMPLATE as OGF_TEMPLATE, tex_escape, render_conj, rec_latex
from makelogexppapers import TEMPLATE as EGF_TEMPLATE
import multitex

x, n = sp.symbols('x n')


def coeffs_of(conj):
    body = conj.split(" - _")[0]
    if re.search(r"=\s*0\s*\.?\s*$", body.strip()):
        return parse_conj(conj)
    b = re.sub(r"^\s*Conjecture[s]?[:.]?\s*", "", body, flags=re.I)
    b = re.sub(r"\bfor\s+n\s*[><=].*$", "", b)
    b = re.sub(r",?\s*(with|where)\s.*$", "", b, flags=re.I)
    b = b.strip().rstrip(".").strip().rstrip(",").strip()
    # a chained "a(n) = <recurrence> = <closed form>" asserts both halves; the
    # recurrence being settled here is the first equality
    parts = re.split(r"(?<![<>=!])=(?!=)", b)
    if len(parts) > 2:
        b = "=".join(parts[:2])
    return parse_eq(b.strip())


def implicit_branch(v):
    """Some entries define the generating function by a relation rather than a formula:
    "A(x) satisfies A(x) = (1+x^2*A(x)^2)/(1-x+3*x^2)", or as a series reversion. Solve
    for the branch whose expansion is the entry's own data."""
    from alg_prove import implicit_poly
    import reversion as rv
    off, N0 = v["offset"], min(len(v["data"]) - 1, 9)
    for g in ([v["gf_src"]] if v.get("gf_src") else []) + v["gfs"]:
        if not g:
            continue
        cands = []
        P = implicit_poly(g)
        if P is not None:
            cands.append(P)
        Q = rv.parse(g)
        if Q is not None:
            cands.extend(rv.branch_factors(Q))
        for P in cands:
            try:
                roots = sp.solve(sp.Eq(P, 0), sp.Symbol('y'))
            except Exception:
                continue
            for r in roots:
                try:
                    base = taylor(r, off + N0 + 3)
                except Exception:
                    continue
                if all(sp.simplify(base[off + k] - v["data"][k]) == 0
                       for k in range(N0 + 1)):
                    return sp.together(r), g
    return None, None


def match_gf(v, egf):
    off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
    srcs = v["egfs"] if egf else v["gfs"]
    if v.get("gf_src") and not egf:
        srcs = [v["gf_src"]] + [g for g in srcs if g != v["gf_src"]]
    for g in srcs:
        try:
            G = parse_gf(g, 'x', raw=g)
            base = taylor(G, off + N0 + 6)
            if egf:
                base = [c * sp.factorial(k) for k, c in enumerate(base)]
        except Exception:
            continue
        for sh in ((0,) if egf else (0, 1, 2, -1, -2, 3, -3)):
            idx = [off + k - sh for k in range(N0 + 1)]
            if any(i < 0 or i >= len(base) for i in idx):
                continue
            if all(sp.simplify(base[i] - v["data"][k]) == 0 for k, i in enumerate(idx)):
                return (sp.together(x ** sh * G) if not egf else G), g
    return (None, None) if egf else implicit_branch(v)


def integer_check(ps, data, off, deg):
    order = len(ps) - 1
    lo = max(order, deg + 1)
    for idx in range(lo, len(data)):
        nn = idx + off
        if sum(int(sp.Poly(p, n).eval(nn)) * data[idx - i]
               for i, p in enumerate(ps) if p != 0) != 0:
            return None, None
    return len(data) - lo, lo + off


def build(slots):
    made = []
    for v in slots:
        num, a = v["num"], v["anum"]
        egf = v["mode"] == "egf"
        A, src = match_gf(v, egf)
        if A is None:
            print(f"{num:4d}  {a}  SKIP no g.f. reproduces the terms")
            continue
        ps = coeffs_of(v["conj"])
        alg = ualg = None
        if not egf and qf.to_quad(A) is None and mq.to_multi(A) is None:
            try:
                alg, ualg = af.from_expr(A)
            except Exception as e:
                print(f"{num:4d}  {a}  SKIP minimal polynomial: {e}")
                continue
        if egf:
            m = le.to_module(A)
            ok, B = le.is_polynomial(le.residual_egf(m[0], m[1], m[2], ps, n))
            deg = (int(sp.Poly(B, x).total_degree()) if B != 0 else 0) if ok else None
        elif alg is not None:
            ok, B = alg.is_polynomial(alg.residual(ualg, ps, n))
            deg = (int(sp.Poly(B, x).total_degree()) if B != 0 else -1) if ok else None
        else:
            try:
                deg, B = residual_poly(A, ps)
            except Exception as e:
                print(f"{num:4d}  {a}  SKIP {e}")
                continue
        if deg is None:
            print(f"{num:4d}  {a}  SKIP residual not polynomial")
            continue
        nver, firstn = integer_check(ps, v["data"], v["offset"], deg)
        if nver is None or nver < 3:
            print(f"{num:4d}  {a}  SKIP integer re-check failed")
            continue
        q = None if egf else qf.to_quad(A)
        Ds, multi = [], False
        if alg is not None:
            Dtex = sp.latex(sp.factor(alg.P.as_expr()))
            fieldtex = r"\mathbb{Q}(x)[y]/\bigl(P(x,y)\bigr)"
        elif q is not None:
            Dtex, fieldtex = sp.latex(sp.factor(q[2])), r"\mathbb{Q}(x)[\sqrt{D}]"
        else:
            mm = mq.to_multi(A)
            Ds = mm[1] if mm else []
            multi = len(Ds) > 1
            Dtex = ",\\quad ".join(sp.latex(sp.factor(D)) for D in Ds)
            fieldtex = (r"\mathbb{Q}(x)\bigl[\sqrt{D_{1}},\dots,\sqrt{D_{%d}}\bigr]" % len(Ds)) \
                if Ds else r"\mathbb{Q}(x)"
        off = v["offset"]
        subs = {
            "ANUM": a,
            "NAME": tex_escape(v["name"].rstrip('.')),
            "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\;=\;"
                           + ", ".join(str(t) for t in v["data"][:8]) + ",\\ \\dots"),
            "GFLATEX": sp.latex(sp.simplify(A)),
            "DLATEX": Dtex,
            "FIELD": fieldtex,
            "BLATEX": sp.latex(B),
            "DEG": deg,
            "ORDER": len(ps) - 1,
            "CONJ": render_conj(v["conj"]),
            "TIME": v["time"],
            "REV": v["revision"],
            "PSLIST": ",\\qquad ".join(
                f"p_{{{i}}}(n)={sp.latex(sp.factor(p))}" for i, p in enumerate(ps)),
            "RECLATEX": rec_latex(ps),
            "DLIST": (f"P(x,y) \\;=\\; {Dtex}" if alg is not None else
                      ",\\quad ".join(
                          f"D_{{{i+1}}} \\;=\\; {sp.latex(sp.factor(D))}"
                          for i, D in enumerate(Ds))),
            "NCHECK": min(len(v["data"]), 13),
            "NVER": nver,
            "FIRSTN": firstn,
        }
        base = EGF_TEMPLATE if egf else (
            multitex.algebraic(OGF_TEMPLATE) if alg is not None else
            multitex.adapt(OGF_TEMPLATE) if multi else OGF_TEMPLATE)
        if v.get("gf_from_name"):
            base = multitex.name_gf(base)
        tex = base % subs
        if v.get("second_half"):
            tex = tex.replace(r"\begin{thebibliography}",
                              v["second_half"] + "\n\n" + r"\begin{thebibliography}", 1)
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
