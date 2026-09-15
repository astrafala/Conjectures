#!/usr/bin/env python3
"""Settle recurrence conjectures on entries defined by coefficient extraction.

The generating function is derived from the entry's own definition of a(n) (diagonal.py),
the branch is picked by matching the published terms, and the conjecture is then settled
by the residual test in the algebraic function field that branch generates.
"""
import json, os, re, signal
import sympy as sp
import diagonal as dg
import algfield as af
import quadfield as qf, multiquad as mq
from prove_rec import parse_conj, residual_poly
from holonomic import taylor

x_, t, y = dg.x, dg.t, dg.y
X, n = sp.symbols('x n')
ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|guess|probably", re.I)
EXTRACT = re.compile(r"^a\(n\)\s*=\s*(\[\s*x\^\(?n\)?\s*\]|[Cc]oefficient of x\^n in)")
RES = os.environ.get("RES", "diag-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def candidates():
    out = []
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            txt = open(os.path.join(dd, fn), errors="ignore").read()
            if "Conjectur" not in txt or "a(n-" not in txt or "x^n" not in txt:
                continue
            F, S = [], {}
            for line in txt.split("\n"):
                if line[:2] in ("%F", "%C", "%e"):
                    F.append(re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
                elif line[:2] in ("%S", "%T", "%U", "%O", "%N"):
                    S.setdefault(line[1], []).append(
                        re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
            conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
                     and "=0" in l.replace(" ", "")]
            defs = [l for l in F if EXTRACT.match(l) and not CONJ.match(l)
                    and not GUESS.search(l)]
            if not conjs or not defs:
                continue
            data = "".join(S.get("S", []) + S.get("T", []) + S.get("U", []))
            try:
                terms = [int(v) for v in data.split(",") if v.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            out.append(("A" + fn[1:7], conjs, defs, terms,
                        int((S.get("O") or ["0"])[0].split(",")[0]),
                        (S.get("N") or [""])[0]))
    return out


def branch_for(f, g, data, off, N):
    """The minimal polynomial of A(t), and the check that it is the right branch.

    No closed-form root is needed, and for good reason: the minimal polynomial can have
    degree five or more in y, where none exists. The series is computed directly from the
    residue formula and used to pick the irreducible factor it satisfies.
    """
    ser = dg.series(f, g, off + N + 4)
    if ser is None:
        return None, None
    if not all(sp.simplify(ser[off + i] - data[i]) == 0 for i in range(N + 1)):
        return None, None
    P = dg.minimal_polynomial(f, g)
    if P is None:
        return None, None
    fac = dg.pick_factor(P, ser, off + N + 4)
    if fac is None:
        return None, None
    return sp.expand(fac.subs(t, X)), ser


def main():
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    cand = candidates()
    shard, nshard = int(os.environ.get("SHARD", "0")), int(os.environ.get("NSHARD", "1"))
    if nshard > 1:
        cand = [c for i, c in enumerate(cand) if i % nshard == shard]
    print(f"{len(cand)} entries defined by coefficient extraction")
    for a, conjs, defs, data, off, name in cand:
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off, "status": None}
            signal.alarm(int(os.environ.get("PER", "240")))
            try:
                ps = parse_conj(conj)
                N = min(len(data) - 1, 9)
                A = used = None
                minpoly = None
                for src in defs:
                    fg = dg.parse_extraction(src)
                    if fg is None:
                        continue
                    f, g = fg
                    minpoly, ser = branch_for(f, g, data, off, N)
                    if minpoly is not None:
                        used = src
                        break
                if minpoly is None:
                    rec["status"] = "no branch reproduces the terms"
                else:
                    F = af.Field(minpoly)
                    ok, B = F.is_polynomial(F.residual(sp.Poly(sp.Symbol('y'), sp.Symbol('y')), ps, n))
                    deg = (int(sp.Poly(B, X).total_degree()) if B != 0 else -1) if ok else None
                    if deg is None:
                        rec["status"] = "residual not polynomial"
                    else:
                        rec.update(status="PROVED", B=sp.sstr(B), degree=int(deg),
                                   order=len(ps) - 1, minpoly=sp.sstr(minpoly),
                                   definition=used, engine="algfield")
                        print(f"{key}  PROVED  B={rec['B']}  valid for n>{deg}")
            except _TO:
                rec["status"] = "skip: timeout"
            except Exception as e:
                rec["status"] = f"skip: {type(e).__name__}: {str(e)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open(RES, "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"), "of", len(out))


if __name__ == "__main__":
    main()
