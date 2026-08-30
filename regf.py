#!/usr/bin/env python3
"""Retry every still-open conjecture whose entry posts a generating function.

Two things changed since the last sweep. The expression is now recovered from the
formula line by offering several candidate cuts and keeping the one whose expansion is
the entry's own terms (gfclean.py), which gets past prose tails that defeated the parser.
And the residual test is tried in every field the toolkit has, not just the first that
applies.

A candidate that parses but is the wrong cut cannot survive the term check, so the
permissive extraction adds candidates without adding risk.
"""
import json, os, re, signal, sys
import sympy as sp
import gfclean
import quadfield as qf, multiquad as mq, algfield as af, logexp as le
from prove_rec import parse_gf, parse_conj, residual_poly
from holonomic import taylor

x, n = sp.symbols('x n')
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
GFL = re.compile(r"^(G\.f\.|O\.g\.f\.|g\.f\.|Generating function)\s*[:.]", re.I)
EGFL = re.compile(r"^E\.g\.f\.\s*[:.]", re.I)
RES = os.environ.get("RES", "regf-results.json")


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def entry(a):
    F, S, O, N = [], [], "0", ""
    for l in open(f"{ROOT}/{a[:4]}/{a}.seq", errors="ignore"):
        tag, body = l[:2], re.sub(r"^A\d{6}\s*", "", l[3:].strip())
        if tag in ("%F", "%C"):
            F.append(body)
        elif tag in ("%S", "%T", "%U"):
            S.append(body)
        elif tag == "%O":
            O = body
        elif tag == "%N":
            N = body
    return F, [int(v) for v in "".join(S).split(",") if v.strip()], \
        int(O.split(",")[0]), N


def match(cands, data, off, egf):
    """The first candidate expression whose expansion is the entry's terms."""
    N0 = min(len(data) - 1, 9)
    for c in cands:
        try:
            signal.alarm(25)
            G = parse_gf(c, 'x', raw=c)
            base = taylor(G, off + N0 + 5)
            if egf:
                base = [t * sp.factorial(i) for i, t in enumerate(base)]
            signal.alarm(0)
        except Exception:
            signal.alarm(0)
            continue
        for sh in ((0,) if egf else (0, 1, 2, 3, -1, -2, -3)):
            idx = [off + k - sh for k in range(N0 + 1)]
            if any(i < 0 or i >= len(base) for i in idx):
                continue
            try:
                if all(sp.simplify(base[i] - data[k]) == 0 for k, i in enumerate(idx)):
                    return (G if egf else sp.together(x ** sh * G)), c
            except Exception:
                pass
    return None, None


def settle(A, ps, egf):
    """(degree, B, engine) if the residual is a polynomial, else (None, None, why)."""
    if egf:
        m = le.to_module(A)
        ok, B = le.is_polynomial(le.residual_egf(m[0], m[1], m[2], ps, n))
        return ((int(sp.Poly(B, x).total_degree()) if B != 0 else 0), B, "logexp") \
            if ok else (None, None, "logexp: residual not polynomial")
    if qf.to_quad(A) is not None or mq.to_multi(A) is not None:
        deg, B = residual_poly(A, ps)
        eng = "quadratic" if qf.to_quad(A) is not None else "multiquad"
        return (deg, B, eng) if deg is not None else (None, None, f"{eng}: not polynomial")
    alg, u = af.from_expr(A)
    ok, B = alg.is_polynomial(alg.residual(u, ps, n))
    return ((int(sp.Poly(B, x).total_degree()) if B != 0 else -1), B, "algfield") \
        if ok else (None, None, "algfield: residual not polynomial")


def integer_check(ps, data, off, deg):
    lo = max(len(ps) - 1, deg + 1)
    for idx in range(lo, len(data)):
        nn = idx + off
        if sum(sp.Rational(sp.Poly(p, n).eval(nn)) * data[idx - i]
               for i, p in enumerate(ps) if p != 0) != 0:
            return None, None
    return len(data) - lo, lo + off


def main(todo):
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    for a in todo:
        F, data, off, name = entry(a)
        conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        egf = not any(GFL.match(l) for l in F)
        lines = [l for l in F if (EGFL if egf else GFL).match(l)]
        cands = [c for l in lines for c in gfclean.candidates(l)]
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off,
                   "mode": "egf" if egf else "ogf", "status": None}
            signal.alarm(int(os.environ.get("PER", "240")))
            try:
                A, src = match(cands, data, off, egf)
                if A is None:
                    rec["status"] = "no g.f. candidate reproduces the terms"
                else:
                    ps = parse_conj(conj)
                    deg, B, eng = settle(A, ps, egf)
                    if deg is None:
                        rec["status"] = eng
                    else:
                        nver, firstn = integer_check(ps, data, off, deg)
                        if nver is None or nver < 3:
                            rec["status"] = "integer re-check failed"
                        else:
                            rec.update(status="PROVED", gf_src=src, gf=sp.sstr(A),
                                       engine=eng, degree=deg, order=len(ps) - 1,
                                       terms_verified=nver, first_n=firstn)
                            print(f"{key}  PROVED  {eng}  order {len(ps)-1} deg {deg}",
                                  flush=True)
            except TO:
                rec["status"] = "timeout"
            except Exception as e:
                rec["status"] = f"{type(e).__name__}: {str(e)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"),
          "of", len(out))


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))
    sh, ns = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARD", 1))
    main([a for i, a in enumerate(todo) if i % ns == sh])
