#!/usr/bin/env python3
"""The entry NAME as the known side.

A052183 is named "a(n) = (n + 2) * binomial(3*n, n) / (2*n + 1)". That is not a formula
someone contributed later and might have guessed -- it is the DEFINITION of the sequence,
the strongest fact an entry can offer. Anything derived from it is unconditional.

Every sweep here read %F lines for the known side and never looked at %N. This one parses
the name, checks it against the entry's own data, and decides the conjectured recurrence
with hyperterm.py, which is a decision procedure for identities between hypergeometric
terms: the shift quotients are rational, terms group into similarity classes, dissimilar
classes are linearly independent over Q(n), and the identity holds exactly when every
class residual is the zero rational function.
"""
import json, os, re, sys
sys.path.insert(0, ".")
import sympy as sp
import cfparse, conjlines, hyperterm, blocks, fsplit
from prove_rec import parse_conj
import timeoutrun

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*(D-finite with recurrence\s*)?", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
n = sp.Symbol('n')


def candidates():
    out = []
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            a = "A" + fn[1:7]
            name, fl = None, []
            for l in open(os.path.join(dd, fn), errors="ignore"):
                if len(l) < 4 or l[0] != "%":
                    continue
                b = re.sub(r"^%.\s+A\d{6}\s*", "", l.rstrip())
                if l[1] == "N" and name is None:
                    name = b
                elif l[1] in "FC":
                    fl.append(b)
            if not name or not re.match(r"^\s*a\(n\)\s*=", name, re.I):
                continue
            if any(SETTLED.search(l) for l in fl):
                continue
            conj = [l for l in fl if conjlines.is_recurrence(l)]
            if conj:
                out.append((a, name, conj))
    return out


def attack(item):
    a, name, conj = item
    from regf import entry
    F, data, off, nm = entry(a)
    e = None
    for part in [name] + fsplit.split(name):
        e = cfparse.parse(part)
        if e is not None:
            break
    if e is None:
        return ("no", "the name did not parse")
    al, shift = cfparse.align(e, data, off)
    if al is None:
        return ("no", "the name does not reproduce the entry's terms")
    out = []
    for cl in conj:
        ps = parse_conj(MARK.sub("", cl))
        if ps is None:
            continue
        ok, ev = hyperterm.is_zero_sum(
            sp.expand(sum(p * al.subs(n, n - j) for j, p in enumerate(ps) if p != 0)), n)
        if not ok:
            out.append(("fails", cl, None))
            continue
        order = len(ps) - 1
        bad = [i + off for i in range(order, len(data))
               if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                      for j, p in enumerate(ps) if p != 0) != 0]
        if bad or len(data) - order < 4:
            out.append(("integer re-check failed", cl, bad[:3]))
            continue
        out.append(("PROVED", cl, {"name": name, "closed": sp.srepr(al),
                                   "order": order, "nver": len(data) - order,
                                   "firstn": order + off, "classes": len(ev)}))
    return ("ok", out)


if __name__ == "__main__":
    c = candidates()
    print(f"{len(c)} entries whose NAME is a formula and whose recurrence is conjectured",
          flush=True)
    hits = []
    for i, it in enumerate(c):
        st, r = timeoutrun.call(attack, (it,), timeout=120)
        if st != "ok" or r[0] != "ok":
            continue
        for verdict, cl, extra in r[1]:
            if verdict == "PROVED":
                hits.append({"anum": it[0], "conj": cl, **extra})
                print(f"  PROVED {it[0]}  {cl[:70]}", flush=True)
        if i % 100 == 0:
            print(f"  ...{i}", flush=True)
    json.dump(hits, open("name_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
