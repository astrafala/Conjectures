#!/usr/bin/env python3
"""Run the Gosper-certificate engine over every entry whose sequence is given as a
hypergeometric sum and whose recurrence is still only conjectured."""
import json, os, re, signal
import sympy as sp
from wz import parse_sum, prove, certify, n, k
from prove_rec import parse_conj

ROOT = "/home/user/oeis/oeisdata/seq"
LABEL = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
SUMF = re.compile(r"^a\(n\)\s*=\s*Sum_\{", re.I)
PROOF = re.compile(r"\bproof\b|\bproved\b|\bproven\b|is true|Kauers|Koutschan|"
                   r"has been shown|follows from|confirm\w*|verified|checked using|"
                   r"establish\w*|settled|no longer a conjecture|"
                   r"immediate consequence|can be deduced|is a corollary|"
                   r"is now a theorem|now a theorem|this is a theorem|"
                   r"has been established|resolved by|closed by", re.I)


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def fields(path):
    f = {}
    for line in open(path, errors="ignore"):
        if line.startswith("%"):
            f.setdefault(line[1], []).append(
                re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def boundary_zero(G, lo, hi, order):
    """G must vanish at both ends of the summation range, for several concrete n."""
    for nn in range(max(order + 2, 4), max(order + 2, 4) + 5):
        for kk in (lo.subs(n, nn), hi.subs(n, nn) + 1):
            try:
                v = sp.simplify(G.subs({n: nn, k: kk}))
            except Exception:
                return False
            if v != 0:
                return False
    return True


def main():
    out = json.load(open("wz-results.json")) if os.path.exists("wz-results.json") else {}
    todo = []
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            p = os.path.join(dd, fn)
            txt = open(p, errors="ignore").read()
            if "Conjectur" not in txt or "a(n-" not in txt or "Sum_{" not in txt:
                continue
            f = fields(p)
            a = "A" + fn[1:7]
            conjs = [l for tag in ("C", "F", "e") for l in f.get(tag, [])
                     if LABEL.match(l) and "a(n-" in l.replace(" ", "")
                     and "=0" in l.replace(" ", "")]
            sums = [l for l in f.get("F", []) if SUMF.match(l) and not LABEL.match(l)]
            if not conjs or not sums:
                continue
            if any(PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I)
                   for tag in ("C", "F", "H", "e") for l in f.get(tag, [])):
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            todo.append((a, conjs, sums, terms,
                         int((f.get("O") or ["0"])[0].split(",")[0]),
                         (f.get("N") or [""])[0]))
    print(f"{len(todo)} entries to attempt")
    for a, conjs, sums, terms, off, name in todo:
        for ci, conj in enumerate(conjs):
            key = f"{a}#{ci}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off,
                   "status": None}
            signal.alarm(int(os.environ.get("PER", "90")))
            try:
                ps = parse_conj(conj)
                done = False
                for src in sums:
                    parsed = parse_sum(src)
                    if not parsed:
                        continue
                    F, lo, hi = parsed
                    # the formula must reproduce the entry's own terms
                    ok = True
                    for j in range(min(6, len(terms))):
                        nn = off + j
                        try:
                            k0 = int(lo.subs(n, nn))
                            k1 = int(hi.subs(n, nn))
                            v = sum(sp.Integer(0) + F.subs({n: nn, k: kk})
                                    for kk in range(k0, k1 + 1))
                            v = sp.simplify(v)
                        except Exception:
                            ok = False
                            break
                        if sp.simplify(v - terms[j]) != 0:
                            ok = False
                            break
                    if not ok:
                        continue
                    G, why = prove(ps, F, lo, hi)
                    if G is None:
                        rec["status"] = why
                        done = True
                        break
                    if not boundary_zero(G, lo, hi, len(ps) - 1):
                        rec["status"] = "certificate does not vanish at the boundary"
                        done = True
                        break
                    rec.update(status="PROVED", certificate=sp.sstr(G),
                               summand=sp.sstr(F), lo=sp.sstr(lo), hi=sp.sstr(hi),
                               order=len(ps) - 1, formula=src)
                    done = True
                    break
                if not done:
                    rec["status"] = "no usable hypergeometric-sum formula"
                if rec["status"] == "PROVED":
                    print(f"{key}  PROVED  certificate {rec['certificate'][:60]}")
            except _TO:
                rec["status"] = "skip: timeout"
            except Exception as e:
                rec["status"] = f"skip: {type(e).__name__}: {str(e)[:60]}"
            finally:
                signal.alarm(0)
                out[key] = rec
                json.dump(out, open("wz-results.json", "w"), indent=1, sort_keys=True)
    print("PROVED", sum(1 for r in out.values() if r["status"] == "PROVED"), "of", len(out))


if __name__ == "__main__":
    main()
