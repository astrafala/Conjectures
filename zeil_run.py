#!/usr/bin/env python3
"""Settle conjectured recurrences by deriving one from the summand, then dividing.

Two steps, and the second is what the earlier Gosper-only attempt was missing:

  1. Creative telescoping (zeil.py) produces an operator L, of whatever order the
     summand actually needs, that annihilates a(n) = sum_k F(n,k). L is derived from the
     entry's own formula for a(n), so nothing about a generating function is assumed.
  2. Right division in the Ore algebra (ore.py) asks whether the conjectured operator is
     a left multiple of L. A conjectured recurrence is usually NOT minimal, so this is
     the step that lets it through -- asking Gosper to hit the conjecture exactly, as
     wz.py did, was asking the wrong question.
"""
import json, os, re, signal
import sympy as sp
import zeil, ore
from zeil import n, k
from prove_rec import parse_conj
from eqform_prove import parse_eq

ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|it seems|guess|probably", re.I)
SUMF = re.compile(r"^a\(n\)\s*=\s*Sum_\{", re.I)
LOCALS = {'binomial': sp.binomial, 'C': sp.binomial, 'factorial': sp.factorial,
          'gamma': sp.gamma, 'n': n, 'k': k}
RES = os.environ.get("RES", "zeil-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def parse_sum(src):
    m = re.match(r"a\(n\)\s*=\s*Sum_\{\s*k\s*=\s*([^.]+?)\.\.\s*([^}]+?)\s*\}\s*(.+)$",
                 src.strip(), re.I)
    if not m:
        return None
    lo, hi, body = m.group(1), m.group(2), m.group(3)
    body = body.split(" - _")[0].strip().rstrip('.')
    body = re.sub(r"\.?\s*\(\s*End[^()]*\)\s*$", "", body, flags=re.I)
    if re.search(r"Sum_|Product_|Stirling|A\d{6}|floor|ceiling|\bmod\b|!!|hypergeom",
                 body, re.I):
        return None
    body = body.replace("^", "**")
    body = re.sub(r"(\d)\s*\(", r"\1*(", body)
    body = re.sub(r"\)\s*\(", r")*(", body)
    body = re.sub(r"(\d)\s*([nk])\b", r"\1*\2", body)
    try:
        expr = sp.sympify(body, locals=LOCALS)
        LO, HI = sp.sympify(lo, locals=LOCALS), sp.sympify(hi, locals=LOCALS)
    except Exception:
        return None
    if expr.free_symbols - {n, k} or (LO.free_symbols | HI.free_symbols) - {n}:
        return None
    return expr, LO, HI


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
            if "Conjectur" not in txt or "a(n-" not in txt or "Sum_{" not in txt:
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
            sums = [l for l in F if SUMF.match(l) and not CONJ.match(l)
                    and not GUESS.search(l)]
            if not conjs or not sums:
                continue
            data = "".join(S.get("S", []) + S.get("T", []) + S.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            out.append(("A" + fn[1:7], conjs, sums, terms,
                        int((S.get("O") or ["0"])[0].split(",")[0]),
                        (S.get("N") or [""])[0]))
    return out


def numeric_ok(ps, data, off):
    order = len(ps) - 1
    bad, checked, first = [], 0, None
    for idx in range(order, len(data)):
        nn = idx + off
        tot = sum(int(sp.Poly(p, n).eval(nn)) * data[idx - i]
                  for i, p in enumerate(ps) if p != 0)
        if tot != 0:
            bad.append(nn)
        else:
            checked += 1
            if first is None:
                first = nn
    return bad, checked, first


def main():
    out = json.load(open(RES)) if os.path.exists(RES) else {}
    cand = candidates()
    shard = int(os.environ.get("SHARD", "0"))
    nshard = int(os.environ.get("NSHARD", "1"))
    if nshard > 1:
        cand = [c for i, c in enumerate(cand) if i % nshard == shard]
    print(f"{len(cand)} entries with a non-conjectural hypergeometric sum")
    maxorder = int(os.environ.get("MAXORDER", "3"))
    for a, conjs, sums, data, off, name in cand:
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off, "status": None}
            signal.alarm(int(os.environ.get("PER", "300")))
            try:
                pc = parse_conj(conj)
                C = ore.to_operator(pc)
                done = False
                for src in sums:
                    parsed = parse_sum(src)
                    if not parsed:
                        continue
                    F, lo, hi = parsed
                    ok = True
                    for i in range(min(6, len(data))):
                        nn = off + i
                        try:
                            v = sum(sp.Integer(0) + F.subs({n: nn, k: kk})
                                    for kk in range(int(lo.subs(n, nn)),
                                                    int(hi.subs(n, nn)) + 1))
                        except Exception:
                            ok = False
                            break
                        if sp.simplify(v - data[i]) != 0:
                            ok = False
                            break
                    if not ok:
                        continue
                    if not zeil.natural_boundary(F, lo, hi, len(pc) - 1):
                        rec["status"] = "summand does not vanish outside the stated range"
                        done = True
                        break
                    tel = None
                    for r in range(1, maxorder + 1):
                        tel = zeil.telescoper(F, r)
                        if tel is not None:
                            break
                    if tel is None:
                        rec["status"] = "no telescoper found up to the order tried"
                        done = True
                        break
                    sig, R = tel
                    L = [sp.cancel(t) for t in sig]
                    Q, Rem = ore.right_divide(C, L)
                    if not ore.is_zero(Rem):
                        rec["status"] = ("derived a recurrence, but the conjecture is not "
                                         "a left multiple of it")
                        done = True
                        break
                    bad, checked, firstn = numeric_ok(pc, data, off)
                    if bad or checked < 3:
                        rec["status"] = f"conjecture fails on published terms at n={bad[:3]}"
                        done = True
                        break
                    rec.update(status="PROVED", summand=sp.sstr(F), lo=sp.sstr(lo),
                               hi=sp.sstr(hi), formula=src,
                               sigma=[sp.sstr(t) for t in L],
                               certificate=sp.sstr(R),
                               Q=[sp.sstr(t) for t in Q],
                               exceptional=[sp.sstr(t) for t in ore.exceptional_set(Q)],
                               order_conj=len(pc) - 1, order_derived=len(L) - 1,
                               terms_verified=checked, first_n=firstn)
                    print(f"{key}  PROVED  derived order {len(L)-1}, "
                          f"conjecture order {len(pc)-1}")
                    done = True
                    break
                if not done:
                    rec["status"] = "no usable hypergeometric sum formula"
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
