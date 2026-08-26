#!/usr/bin/env python3
"""Re-attempt, in a general algebraic function field, every conjecture the quadratic and
multiquadratic engines refused.

Those engines only handle sums of independent square roots, and refuse anything else --
correctly, since their reduction assumes independent radicands. A nested radical, a cube
root, or a generating function given only implicitly still lies in a simple algebraic
extension of Q(x), so algfield.py settles it with the same residual test.
"""
import glob, json, os, re, signal, sys
import sympy as sp
from prove_rec import parse_gf, parse_conj
from holonomic import taylor
import algfield as af

x, y = sp.symbols('x y')
n = sp.Symbol('n')
RES = os.environ.get("RES", "alg-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def implicit_poly(raw):
    """Turn 'A(x) = 1 + x*A(x)^2' into the polynomial x*y^2 - y + 1."""
    s = raw.split(" - _")[0].strip().rstrip('.')
    m = re.match(r"\s*A\(x\)\s*satisfies\s*:?\s*(.+)$", s, re.I)
    if m:
        s = m.group(1)
    if "=" not in s:
        return None
    lhs, rhs = s.split("=", 1)
    body = f"({lhs})-({rhs})"
    body = body.replace("^", "**").replace("A(x)", "y")
    body = re.sub(r"(\d)\s*\(", r"\1*(", body)
    body = re.sub(r"\)\s*\(", r")*(", body)
    body = re.sub(r"(\d)\s*([xy])\b", r"\1*\2", body)
    try:
        e = sp.sympify(body, locals={'x': x, 'y': y})
    except Exception:
        return None
    if e.free_symbols - {x, y}:
        return None
    num, den = sp.fraction(sp.together(e))
    num = sp.expand(num)
    if not num.is_polynomial(x, y) or sp.Poly(num, y).degree() < 1:
        return None
    return num


def main(cache_file="scan-cache.json"):
    cache = json.load(open(cache_file))
    fresh = {}
    for f in glob.glob("scan-results-*.json"):
        fresh.update(json.load(open(f)))
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    todo = [k for k, r in sorted(fresh.items())
            if r["status"] != "PROVED" and k not in out]
    shard, nshard = int(os.environ.get("SHARD", "0")), int(os.environ.get("NSHARD", "1"))
    if nshard > 1:
        todo = [t for i, t in enumerate(todo) if i % nshard == shard]
    print(f"{len(todo)} conjectures to re-attempt")
    for key in todo:
        r = fresh[key]
        a = r["anum"]
        v = cache.get(a)
        rec = {"anum": a, "conj": r["conj"], "status": None}
        signal.alarm(int(os.environ.get("PER", "120")))
        try:
            if v is None:
                raise ValueError("entry not in the sweep cache")
            ps = parse_conj(r["conj"])
            off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
            F = u = None
            for src in v["gfs"]:
                cand = None
                try:
                    G = parse_gf(src, 'x', raw=src)
                    base = taylor(G, off + N0 + 6)
                    for sh in (0, 1, 2, -1, -2):
                        idx = [off + kk - sh for kk in range(N0 + 1)]
                        if any(i < 0 or i >= len(base) for i in idx):
                            continue
                        if all(sp.simplify(base[i] - v["data"][kk]) == 0
                               for kk, i in enumerate(idx)):
                            cand = sp.together(x ** sh * G)
                            rec["shift"], rec["gf_src"] = sh, src
                            break
                except Exception:
                    cand = None
                if cand is None:
                    continue
                F, u = af.from_expr(cand)
                if F is not None:
                    rec["gf"] = sp.sstr(cand)
                    break
            if F is None:
                # implicit definition posted instead of a closed form
                for src in v["gfs"]:
                    P = implicit_poly(src)
                    if P is None:
                        continue
                    try:
                        FF = af.Field(P)
                    except Exception:
                        continue
                    # pick the branch reproducing the terms
                    roots = sp.solve(sp.Eq(P, 0), y)
                    for rt in roots:
                        try:
                            base = taylor(rt, off + N0 + 6)
                        except Exception:
                            continue
                        if all(sp.simplify(base[off + kk] - v["data"][kk]) == 0
                               for kk in range(N0 + 1)):
                            F, u = FF, sp.Poly(y, y)
                            rec["gf_src"], rec["gf"] = src, sp.sstr(rt)
                            break
                    if F is not None:
                        break
            if F is None:
                rec["status"] = "no algebraic g.f. reproduces the terms"
            else:
                res = F.residual(u, ps, n)
                ok, B = F.is_polynomial(res)
                if ok:
                    deg = sp.Poly(B, x).total_degree() if B != 0 else -1
                    rec.update(status="PROVED", B=sp.sstr(B), degree=int(deg),
                               order=len(ps) - 1, mode="ogf",
                               minpoly=sp.sstr(F.P.as_expr()))
                    print(f"{key}  PROVED  B={rec['B']}  valid for n>{deg}")
                else:
                    rec["status"] = "residual not polynomial"
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
    main(*sys.argv[1:])
