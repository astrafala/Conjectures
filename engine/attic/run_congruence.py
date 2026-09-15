#!/usr/bin/env python3
"""Apply the congruence decision procedure to every candidate in the local clone."""
import json, os, re, signal
import sympy as sp
import congruence as C
from local_extract import parse, PROOF
from prove_rec import parse_gf
from holonomic import taylor

ROOT = "/home/user/oeis/oeisdata/seq"
x = sp.Symbol('x')

SHAPES = [
    re.compile(r'Conjecture[:.]\s*(?:for\s*n\s*>=?\s*(?P<n0b>\d+)\s*,?\s*)?'
               r'a\(n\)\s*(?:is\s*)?(?:==?|is congruent to)\s*(?P<c>-?\d+)\s*'
               r'\(?\s*mod(?:ulo)?\s*(?P<m>\d+)\s*\)?', re.I),
    re.compile(r'Conjecture[:.]\s*(?:every|all|each)?\s*(?:terms?|a\(n\))\s*'
               r'(?:are|is)?\s*(?:a\s*)?multiple of\s*(?P<m>\d+)'
               r'(?:\s*(?:for|when)\s*n\s*>=?\s*(?P<n0>\d+))?', re.I),
    # "a(n) == c (mod m) for n >= n0"  /  "a(n) == c mod m"
    re.compile(r'Conjecture[:.]\s*a\(n\)\s*==?\s*(?P<c>-?\d+)\s*\(?\s*mod\s*(?P<m>\d+)\s*\)?'
               r'(?:\s*(?:for|when)\s*n\s*>=?\s*(?P<n0>\d+))?', re.I),
    # "all terms are divisible by m"  /  "a(n) is divisible by m"
    re.compile(r'Conjecture[:.]\s*(?:all\s+)?(?:terms?|a\(n\))\s*(?:are|is)?\s*'
               r'divisible by\s*(?P<m>\d+)'
               r'(?:\s*(?:for|when)\s*n\s*>=?\s*(?P<n0>\d+))?', re.I),
]


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def candidates():
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            f = parse(os.path.join(dd, fn))
            hit = None
            for tag in ("C", "F"):
                for l in f.get(tag, []):
                    for rx in SHAPES:
                        mm = rx.search(l)
                        if mm:
                            hit = (l, mm)
                            break
                    if hit:
                        break
                if hit:
                    break
            if not hit:
                continue
            gfs = [re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I).group(1).strip()
                   for l in f.get("F", []) if re.match(r"G\.f\.", l.strip(), re.I)]
            name = (f.get("N") or [""])[0]
            nm = re.match(r"\s*Expansion of\s+(.+)", name, re.I)
            if nm:
                gfs.append(nm.group(1).strip().rstrip('.'))
            if not gfs:
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
                off = int((f.get("O") or ["0"])[0].split(",")[0])
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            proof = None
            for tag in ("C", "F", "H"):
                for l in f.get(tag, []):
                    if PROOF.search(l) and re.search(r"conjectur", l, re.I):
                        proof = l[:120]
            yield "A" + fn[1:7], {"name": name, "offset": off, "data": terms,
                                  "conj": hit[0], "m": hit[1], "gfs": gfs, "proof": proof}


def main():
    res = {}
    for a, v in candidates():
        if v["proof"]:
            continue
        rec = {"anum": a, "status": None, "conj": v["conj"][:150]}
        signal.alarm(30)
        try:
            g = v["m"].groupdict()
            m = int(g["m"])
            c = int(g.get("c") or 0)
            n0 = int(g.get('n0') or g.get('n0b') or v['offset'])
            A = None
            N = min(len(v["data"]) - 1, 10)
            for src in v["gfs"]:
                try:
                    cand = parse_gf(src, 'x', raw=src)
                    t = taylor(cand, v["offset"] + N + 3)
                    if all(sp.simplify(t[v["offset"] + k] - v["data"][k]) == 0
                           for k in range(N + 1)):
                        A = cand
                        rec["gf_src"] = src
                        break
                except Exception:
                    continue
            if A is None:
                rec["status"] = "no g.f. reproduces the terms"
            else:
                verdict, detail = C.decide(A, m, c, n0)
                rec["detail"] = detail
                rec["m"], rec["c"], rec["n0"] = m, c, n0
                rec["status"] = ("PROVED" if verdict is True else
                                 "DISPROVED" if verdict is False else f"undecided: {detail}")
            print(f"{a}  {rec['status']}  {rec.get('detail','')}"[:150])
        except _TO:
            rec["status"] = "skip: timeout"
            print(f"{a}  timeout")
        except Exception as e:
            rec["status"] = f"skip: {type(e).__name__}: {str(e)[:45]}"
            print(f"{a}  {rec['status']}")
        finally:
            signal.alarm(0)
            res[a] = rec
            json.dump(res, open("cong-results.json", "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in res.values() if r["status"] == "PROVED"),
          "| DISPROVED", sum(1 for r in res.values() if r["status"] == "DISPROVED"),
          "| of", len(res))


if __name__ == "__main__":
    main()
