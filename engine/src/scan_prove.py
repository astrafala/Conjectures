#!/usr/bin/env python3
"""Attempt every conjecture in the full sweep that has not been attempted before."""
import json, os, re, signal, sys
import sympy as sp
from prove_rec import parse_gf, parse_conj, residual_poly
from holonomic import taylor
import logexp as le

x, n = sp.symbols('x n')
RES = os.environ.get("RES", "scan-results.json")


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def already():
    seen = set()
    for f, key in (("rec-cache.json", "seen"), ("egf-cache.json", None),
                   ("local-cache.json", None)):
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        if key:
            d = d[key]
        for a, v in d.items():
            if v and v.get("conj"):
                seen.add((a, norm(v["conj"])))
    for f in ("extra-conj.json",):
        if os.path.exists(f):
            for a, v in json.load(open(f)).items():
                for c in v["others"]:
                    seen.add((a, norm(c)))
    return seen


def main():
    cache = json.load(open("scan-cache.json"))
    seen = already()
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    todo = []
    for a, v in sorted(cache.items()):
        if v["settled"]:
            continue
        for j, c in enumerate(v["conjs"]):
            key = f"{a}#{j}"
            if key in out:
                continue
            if (a, norm(c)) in seen and os.environ.get("REDO") != "1":
                continue
            todo.append((key, a, j, c, v))
    shard = int(os.environ.get("SHARD", "0"))
    nshard = int(os.environ.get("NSHARD", "1"))
    if nshard > 1:
        todo = [t for i, t in enumerate(todo) if i % nshard == shard]
    print(f"{len(todo)} conjectures to attempt")
    for key, a, j, conj, v in todo:
        rec = {"anum": a, "conj": conj, "status": None}
        signal.alarm(int(os.environ.get("PER", "60")))
        try:
            ps = parse_conj(conj)
            off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
            A, mode = None, None
            for src, kind in [(s, "ogf") for s in v["gfs"]] + \
                             [(s, "egf") for s in v["egfs"]]:
                try:
                    G = parse_gf(src, 'x', raw=src)
                    base = taylor(G, off + N0 + 6)
                except Exception:
                    continue
                if kind == "egf":
                    base = [c * sp.factorial(k) for k, c in enumerate(base)]
                    shifts = (0,)
                else:
                    shifts = (0, 1, 2, -1, -2, 3, -3)
                for sh in shifts:
                    idx = [off + k - sh for k in range(N0 + 1)]
                    if any(i < 0 or i >= len(base) for i in idx):
                        continue
                    if all(sp.simplify(base[i] - v["data"][k]) == 0
                           for k, i in enumerate(idx)):
                        A = sp.together(x ** sh * G) if kind == "ogf" else G
                        rec["shift"], rec["gf_src"], mode = sh, src, kind
                        break
                if A is not None:
                    break
            if A is None:
                rec["status"] = "no posted g.f. parses and matches the terms"
            elif mode == "ogf":
                deg, B = residual_poly(A, ps)
                rec["status"] = "residual not polynomial" if deg is None else "PROVED"
                if deg is not None:
                    rec.update(degree=int(deg), B=sp.sstr(B), order=len(ps) - 1,
                               gf=sp.sstr(A), mode=mode)
            else:
                m = le.to_module(A)
                if m is None:
                    rec["status"] = "e.g.f. not in Q(x)[log,exp]"
                else:
                    coeffs, u, g = m
                    ok, P = le.is_polynomial(le.residual_egf(coeffs, u, g, ps, n))
                    if ok:
                        rec.update(status="PROVED", B=sp.sstr(P), mode=mode,
                                   degree=int(sp.Poly(P, x).total_degree()) if P != 0 else 0,
                                   order=len(ps) - 1, gf=sp.sstr(A))
                    else:
                        rec["status"] = "residual not polynomial"
            if rec["status"] == "PROVED":
                print(f"{key}  PROVED  B={rec['B']}  valid for n>{rec['degree']}")
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
