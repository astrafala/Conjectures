#!/usr/bin/env python3
"""Settle conjectured recurrences that factor through a recurrence the entry already
states as established."""
import json, os, re, signal
import sympy as sp
import ore
from ore import n
from prove_rec import parse_conj
from eqform_prove import parse_eq

ROOT = "/home/user/oeis/oeisdata/seq"
CONJ = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
GUESS = re.compile(r"conjectur|empirical|apparent|it seems|guess|probably", re.I)
PROVEN = re.compile(r"^\s*(Recurrence|D-finite with recurrence|Holonomic recurrence|"
                    r"P-recursive)\b[^:]*:\s*", re.I)
RES = os.environ.get("RES", "ore-results.json")


class _TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_TO()))


def coeffs(text):
    """Coefficient list p_0..p_r for either the '... = 0' or the 'a(n) = ...' form."""
    body = text.split(" - _")[0]
    body = PROVEN.sub("", body)
    body = re.sub(r"^\s*Conjecture[s]?\s*(D-finite with recurrence)?[:.]?\s*", "",
                  body, flags=re.I)
    body = re.sub(r"\bfor\s+n\s*[><=].*$", "", body)
    body = re.sub(r",?\s*(with|where)\s.*$", "", body, flags=re.I)
    body = body.strip().rstrip(".").strip().rstrip(",").strip()
    parts = re.split(r"(?<![<>=!])=(?!=)", body)
    if len(parts) > 2:
        body = "=".join(parts[:2])
    if re.search(r"=\s*0\s*$", body):
        return parse_conj("Conjecture: " + body)
    return parse_eq(body)


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
            if "Conjectur" not in txt or "a(n-" not in txt:
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
            proven = [l for l in F if PROVEN.match(l) and not GUESS.search(l)
                      and "a(n-" in l.replace(" ", "")]
            if not conjs or not proven:
                continue
            data = "".join(S.get("S", []) + S.get("T", []) + S.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            out.append(("A" + fn[1:7], conjs, proven, terms,
                        int((S.get("O") or ["0"])[0].split(",")[0]),
                        (S.get("N") or [""])[0]))
    return out


def numeric_ok(ps, data, off):
    """The conjectured recurrence must hold on the published terms it can reach."""
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
    print(f"{len(cand)} entries carry both kinds of recurrence")
    for a, conjs, proven, data, off, name in cand:
        for j, conj in enumerate(conjs):
            key = f"{a}#{j}"
            if key in out:
                continue
            rec = {"anum": a, "conj": conj, "name": name, "offset": off,
                   "status": None}
            signal.alarm(int(os.environ.get("PER", "120")))
            try:
                pc = coeffs(conj)
                C = ore.to_operator(pc)
                done = False
                for pr in proven:
                    try:
                        pp = coeffs(pr)
                        P = ore.to_operator(pp)
                        Q, R = ore.right_divide(C, P)
                    except Exception:
                        continue
                    if not ore.is_zero(R):
                        continue
                    if ore.trivial(Q):
                        rec["status"] = ("the two recurrences are the same one rescaled; "
                                         "nothing new to prove")
                        done = True
                        break
                    bad, checked, first = numeric_ok(pc, data, off)
                    if bad or checked < 3:
                        rec["status"] = f"conjecture fails on published terms at n={bad[:3]}"
                        done = True
                        break
                    rec.update(status="PROVED", proven=pr,
                               Q=[sp.sstr(t) for t in Q],
                               exceptional=[sp.sstr(t) for t in ore.exceptional_set(Q)],
                               order_conj=len(pc) - 1, order_proven=len(pp) - 1,
                               terms_verified=checked, first_n=first)
                    print(f"{key}  PROVED  Q of degree {len(Q)-1}, "
                          f"exceptions {rec['exceptional']}")
                    done = True
                    break
                if not done:
                    rec["status"] = "conjectured operator is not a left multiple"
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
