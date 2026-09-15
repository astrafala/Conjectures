#!/usr/bin/env python3
"""Completeness pass: every conjecture that has a usable generating-function source but
was never put through an engine.

These fell through because an entry's first conjecture was attempted and the rest were
not, or because the entry was skipped wholesale for a settlement note that turned out to
concern a different statement. Each is run through the whole stack in order --
quadratic, multiquadratic, general algebraic field, transcendental module -- rather than
whichever engine happened to own the class it was found in.
"""
import json, os, re, signal
import sympy as sp
from prove_rec import parse_gf, parse_conj, residual_poly
from holonomic import taylor
import quadfield as qf, multiquad as mq, algfield as af, logexp as le

x, n = sp.symbols('x n')
RES = os.environ.get("RES", "final-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def load_sources():
    src = {}
    for f in ("scan-cache.json", "nogf-cache.json", "midline-cache.json"):
        if not os.path.exists(f):
            continue
        for a, v in json.load(open(f)).items():
            e = src.setdefault(a, {"gfs": [], "egfs": [], "data": v["data"],
                                   "offset": v["offset"], "name": v.get("name", ""),
                                   "conjs": []})
            for g in v.get("gfs", []):
                if g not in e["gfs"]:
                    e["gfs"].append(g)
            for g in v.get("egfs", []):
                if g not in e["egfs"]:
                    e["egfs"].append(g)
            if "src" in v and v["src"] not in e["gfs"]:
                e["gfs"].append(v["src"])
            for c in v.get("conjs", []):
                if c not in e["conjs"]:
                    e["conjs"].append(c)
    return src


def attempted():
    out = set()
    import glob
    for f in glob.glob("*results*.json") + glob.glob("scan-results-*.json") + \
             glob.glob("zeil-[0-9].json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for r in d.values():
            if isinstance(r, dict) and r.get("conj") and r.get("anum"):
                out.add((r["anum"], norm(r["conj"])))
    return out


def settle(A, ps, egf):
    """Run the whole stack. Returns (degree, B, engine) or (None, None, why)."""
    if egf:
        m = le.to_module(A)
        if m is None:
            return None, None, "e.g.f. not in Q(x)[log,exp]"
        ok, B = le.is_polynomial(le.residual_egf(m[0], m[1], m[2], ps, n))
        if not ok:
            return None, None, "residual not polynomial"
        return (int(sp.Poly(B, x).total_degree()) if B != 0 else 0), B, "logexp"
    if qf.to_quad(A) is not None or mq.to_multi(A) is not None:
        deg, B = residual_poly(A, ps)
        if deg is None:
            return None, None, "residual not polynomial"
        return deg, B, ("quadratic" if qf.to_quad(A) is not None else "multiquad")
    F, u = af.from_expr(A)
    if F is None:
        return None, None, "not algebraic of low degree"
    ok, B = F.is_polynomial(F.residual(u, ps, n))
    if not ok:
        return None, None, "residual not polynomial"
    return (int(sp.Poly(B, x).total_degree()) if B != 0 else -1), B, "algfield"


def main():
    src = load_sources()
    done = attempted()
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    todo = [(a, c) for a, v in sorted(src.items()) for c in v["conjs"]
            if (a, norm(c)) not in done]
    print(f"{len(todo)} conjectures never attempted")
    for a, conj in todo:
        key = f"{a}|{norm(conj)[:40]}"
        if key in out:
            continue
        v = src[a]
        rec = {"anum": a, "conj": conj, "name": v["name"], "status": None}
        signal.alarm(int(os.environ.get("PER", "120")))
        try:
            ps = parse_conj(conj)
            off, N0 = v["offset"], min(len(v["data"]) - 1, 11)
            A = egf = None
            for g, kind in [(s, False) for s in v["gfs"]] + \
                           [(s, True) for s in v["egfs"]]:
                try:
                    G = parse_gf(g, 'x', raw=g)
                    base = taylor(G, off + N0 + 6)
                    if kind:
                        base = [c * sp.factorial(i) for i, c in enumerate(base)]
                except Exception:
                    continue
                for sh in ((0,) if kind else (0, 1, 2, -1, -2, 3, -3)):
                    idx = [off + i - sh for i in range(N0 + 1)]
                    if any(j < 0 or j >= len(base) for j in idx):
                        continue
                    if all(sp.simplify(base[j] - v["data"][i]) == 0
                           for i, j in enumerate(idx)):
                        A = sp.together(x ** sh * G) if not kind else G
                        egf = kind
                        rec["gf_src"], rec["shift"] = g, sh
                        break
                if A is not None:
                    break
            if A is None:
                rec["status"] = "no posted g.f. reproduces the terms"
            else:
                deg, B, why = settle(A, ps, egf)
                if deg is None:
                    rec["status"] = why
                else:
                    rec.update(status="PROVED", degree=int(deg), B=sp.sstr(B),
                               engine=why, mode="egf" if egf else "ogf",
                               order=len(ps) - 1, gf=sp.sstr(A))
                    print(f"{a}  PROVED via {why}  B={rec['B']}  n>{deg}")
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
