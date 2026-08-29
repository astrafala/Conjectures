#!/usr/bin/env python3
"""Entries whose NAME states a plain relation to another sequence.

"a(n) = A000522(n) - 2" gives this entry's generating function directly from the other
entry's, so the residual test applies even though the entry itself posts nothing.
"""
import json, os, re
import sympy as sp
from prove_rec import parse_gf, parse_conj
from holonomic import taylor
import logexp as le

x, n = sp.symbols('x n')
ROOT = "/home/user/oeis/oeisdata/seq"
LABEL = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
TERM = re.compile(r"A(\d{6})\(\s*n\s*([+-]\s*\d+)?\s*\)")


def fields(a):
    p = f"{ROOT}/{a[:4]}/{a}.seq"
    f = {}
    for line in open(p, errors="ignore"):
        if line.startswith("%"):
            f.setdefault(line[1], []).append(
                re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def egf_of(a):
    """The other entry's e.g.f., taken as posted and checked against its own terms."""
    f = fields(a)
    data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
    terms = [int(t) for t in data.split(",") if t.strip()]
    off = int((f.get("O") or ["0"])[0].split(",")[0])
    for l in f.get("F", []):
        m = re.match(r"E\.g\.f\.\s*:?\s*(.+)", l.strip(), re.I)
        if not m or re.search(r"empirical|conjectur", l, re.I):
            continue
        src = m.group(1).strip()
        try:
            G = parse_gf(src, 'x', raw=src)
            base = [c * sp.factorial(k) for k, c in enumerate(taylor(G, off + 10))]
        except Exception:
            continue
        if all(sp.simplify(base[off + k] - terms[k]) == 0 for k in range(8)):
            return G, src
    return None, None


def main():
    out = {}
    for a in json.load(open("namerel-todo.json")):
        f = fields(a)
        nm = (f.get("N") or [""])[0].rstrip(".")
        conjs = [l for tag in ("C", "F", "e") for l in f.get(tag, [])
                 if LABEL.match(l) and "a(n-" in l.replace(" ", "")
                 and "=0" in l.replace(" ", "")]
        data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
        terms = [int(t) for t in data.split(",") if t.strip()]
        off = int((f.get("O") or ["0"])[0].split(",")[0])
        refs = []

        def grab(m):
            refs.append(("A" + m.group(1), int((m.group(2) or "0").replace(" ", ""))))
            return f"R{len(refs)-1}"

        body = TERM.sub(grab, nm[nm.index("=") + 1:])
        syms = {f"R{i}": sp.Symbol(f"R{i}") for i in range(len(refs))}
        expr = sp.sympify(body.replace("^", "**"), locals={**syms, "n": n})
        A = expr
        ok = True
        for i, (b, k) in enumerate(refs):
            if k != 0:
                ok = False
                break
            G, src = egf_of(b)
            if G is None:
                ok = False
                break
            A = A.subs(syms[f"R{i}"], G)
        if not ok or A.has(n):
            # a constant term c means c * e^x in the exponential generating function
            pass
        if not ok:
            out[a] = {"anum": a, "status": "no usable e.g.f. for the referenced entry"}
            continue
        const = sp.simplify(A - sum(
            (G for G in [A]), sp.Integer(0)))  # placeholder, handled below
        # rebuild properly: constants become c*exp(x) in an e.g.f.
        A = expr
        for i, (b, k) in enumerate(refs):
            G, _ = egf_of(b)
            A = A.subs(syms[f"R{i}"], G)
        A = A.subs(sp.Integer(1), sp.Integer(1))
        c = sp.simplify(expr.subs({s: 0 for s in syms.values()}))
        A = sp.simplify(A - c + c * sp.exp(x))
        base = [t * sp.factorial(k) for k, t in enumerate(taylor(A, off + 10))]
        if not all(sp.simplify(base[off + k] - terms[k]) == 0 for k in range(8)):
            out[a] = {"anum": a, "status": "derived e.g.f. does not reproduce the terms"}
            continue
        for j, conj in enumerate(conjs):
            ps = parse_conj(conj)
            m = le.to_module(A)
            if m is None:
                out[f"{a}#{j}"] = {"anum": a, "conj": conj,
                                   "status": "not in Q(x)[log,exp]"}
                continue
            okp, B = le.is_polynomial(le.residual_egf(m[0], m[1], m[2], ps, n))
            rec = {"anum": a, "conj": conj, "mode": "egf", "gf": sp.sstr(A),
                   "name_relation": nm}
            if okp:
                rec.update(status="PROVED", B=sp.sstr(B),
                           degree=int(sp.Poly(B, x).total_degree()) if B != 0 else 0,
                           order=len(ps) - 1)
                print(f"{a}#{j}  PROVED  B={rec['B']}")
            else:
                rec["status"] = "residual not polynomial"
                print(f"{a}#{j}  {rec['status']}")
            out[f"{a}#{j}"] = rec
    json.dump(out, open("namerel-results.json", "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
