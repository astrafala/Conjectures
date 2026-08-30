#!/usr/bin/env python3
"""Why did the engines fail on the 290 entries that DO post a generating function?

Every failure is bucketed by its cause, so the next engine is aimed at whatever the
biggest cause turns out to be, rather than at whatever is most interesting to write.
"""
import json, os, re, signal
from collections import Counter
import sympy as sp
from prove_rec import parse_gf, parse_conj, residual_poly, normalise
from holonomic import taylor

ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*Conjectur", re.I)
GFL = re.compile(r"^(G\.f\.|O\.g\.f\.|g\.f\.)\s*[:.]", re.I)


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def entry(a):
    p = f"{ROOT}/{a[:4]}/{a}.seq"
    F, S, O = [], [], "0"
    for l in open(p, errors="ignore"):
        if l[:2] in ("%F", "%C"):
            F.append(re.sub(r"^A\d{6}\s*", "", l[3:].strip()))
        elif l[:2] in ("%S", "%T", "%U"):
            S.append(re.sub(r"^A\d{6}\s*", "", l[3:].strip()))
        elif l[:2] == "%O":
            O = re.sub(r"^A\d{6}\s*", "", l[3:].strip())
    data = [int(v) for v in "".join(S).split(",") if v.strip()]
    return F, data, int(O.split(",")[0])


def why(a):
    F, data, off = entry(a)
    conjs = [l for l in F if CONJ.match(l) and "a(n-" in l.replace(" ", "")
             and "=0" in l.replace(" ", "")]
    gfs = [l for l in F if GFL.match(l)]
    if not gfs:
        return "no g.f. line after all", None
    src = None
    reasons = []
    for g in gfs:
        body = g.split(":", 1)[-1] if ":" in g else g
        raw = body.split(" - _")[0].strip()
        if re.search(r"continued fraction|G\(k\)|U\(k\)|Q\(k\)|W\(k\)|/\(1 \+ ", raw) \
                and re.search(r"\bk\b", raw):
            reasons.append("continued fraction"); continue
        if re.search(r"Sum_|Product_|Integral|hypergeom|Bessel|LambertW|Zeta|"
                     r"exp\(|log\(|sin\(|cos\(", raw):
            reasons.append("transcendental or infinite sum in the g.f."); continue
        try:
            signal.alarm(25)
            G = parse_gf(raw, 'x', raw=raw)
            base = taylor(G, off + min(len(data) - 1, 8) + 4)
            signal.alarm(0)
        except TO:
            signal.alarm(0); reasons.append("timeout parsing/expanding the g.f."); continue
        except Exception as e:
            signal.alarm(0); reasons.append(f"g.f. does not parse"); continue
        ok = False
        for sh in (0, 1, 2, -1, -2):
            idx = [off + k - sh for k in range(min(len(data), 9))]
            if any(i < 0 or i >= len(base) for i in idx):
                continue
            try:
                if all(sp.simplify(base[i] - data[k]) == 0 for k, i in enumerate(idx)):
                    ok = True; src = sp.together(sp.Symbol('x') ** sh * G); break
            except Exception:
                pass
        if not ok:
            reasons.append("g.f. parses but does not match the published terms"); continue
        # it parses and matches: so the failure is in the residual test
        try:
            signal.alarm(60)
            ps = parse_conj(conjs[0])
            deg, B = residual_poly(src, ps)
            signal.alarm(0)
            return ("residual not polynomial" if deg is None
                    else "SHOULD HAVE WORKED"), src
        except TO:
            signal.alarm(0); return "timeout in the residual test", src
        except Exception as e:
            signal.alarm(0); return f"residual test raised: {type(e).__name__}", src
    return (reasons[0] if reasons else "unknown"), None


if __name__ == "__main__":
    ex = json.load(open("census2.json"))
    mine = {r["anum"] for r in json.load(open("rank-map.json"))}
    todo = [a for a in ex["g.f. posted"] if a not in mine]
    cnt, rows = Counter(), {}
    for i, a in enumerate(todo):
        try:
            r, src = why(a)
        except Exception as e:
            r, src = f"harness error: {type(e).__name__}", None
        cnt[r] += 1
        rows[a] = r
        if i % 25 == 0:
            print(f"  .. {i}/{len(todo)}", flush=True)
    json.dump(rows, open("diagnose.json", "w"), indent=1, sort_keys=True)
    print()
    for r, c in cnt.most_common():
        print(f"{c:5d}  {r}")
        print(f"        e.g. {' '.join([a for a in todo if rows[a] == r][:6])}")
