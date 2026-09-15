#!/usr/bin/env python3
"""Run the cross-entry identity test over every such conjecture in the clone."""
import json, os, re, signal
import sympy as sp
import cross as C
from cross import x, n

PROOF = re.compile(r"\bproof\b|\bproved\b|\bproven\b|is true|has been shown|"
                   r"follows from|confirm\w*|verified|checked using|establish\w*|"
                   r"settled|no longer a conjecture|immediate consequence|"
                   r"can be deduced|is a corollary", re.I)
RES = os.environ.get("RES", "cross-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def candidates():
    out = []
    for d in sorted(os.listdir(C.ROOT)):
        dd = os.path.join(C.ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            p = os.path.join(dd, fn)
            txt = open(p, errors="ignore").read()
            if "Conjecture" not in txt:
                continue
            a = "A" + fn[1:7]
            f = C.fields(a)
            if not f:
                continue
            settled = any(PROOF.search(l) and re.search(r"conjectur", l, re.I)
                          for tag in ("C", "F", "H", "e") for l in f.get(tag, []))
            if settled:
                continue
            for tag in ("C", "F", "e"):
                for l in f.get(tag, []):
                    if not re.match(r"Conjectur", l, re.I):
                        continue
                    body = re.sub(r"^Conjecture[s]?[:.]?\s*", "", l, flags=re.I)
                    if "a(n-" in body.replace(" ", "") or "A" not in body:
                        continue
                    if not re.search(r"A\d{6}\(", body):
                        continue
                    out.append((a, l, body))
    return out


def main():
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    cand = candidates()
    print(f"{len(cand)} cross-entry conjectures found")
    cache = {}
    for a, raw, body in cand:
        key = f"{a}|{body[:60]}"
        if key in out:
            continue
        rec = {"anum": a, "conj": raw, "status": None}
        signal.alarm(int(os.environ.get("PER", "120")))
        try:
            parsed = C.parse_identity(body)
            if not parsed:
                rec["status"] = "not a plain shifted combination of other entries"
            else:
                refs, poly = parsed
                for nm in [a] + [r[1] for r in refs]:
                    if nm not in cache:
                        cache[nm] = C.series_of(nm)
                if cache[a] is None or any(cache[r[1]] is None for r in refs):
                    rec["status"] = "an entry involved posts no usable g.f."
                else:
                    FA, dataA, offA = cache[a]
                    rhs = C.poly_gf(poly, 12)
                    for c, nm, k in refs:
                        FB, dataB, offB = cache[nm]
                        S = C.shifted(FB, dataB, offB, k, 12)
                        rhs = sp.together(rhs + C.theta_apply(c, S))
                    ok, B = C.is_polynomial(FA - rhs)
                    if ok:
                        deg = sp.Poly(B, x).total_degree() if B != 0 else -1
                        rec.update(status="PROVED", B=sp.sstr(B), degree=int(deg),
                                   refs=[[sp.sstr(c), nm, k] for c, nm, k in refs],
                                   poly=sp.sstr(poly), gf=sp.sstr(FA))
                        print(f"{a}  PROVED  B={rec['B']}  valid for n>{deg}")
                    else:
                        rec["status"] = "difference is not a polynomial"
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
