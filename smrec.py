#!/usr/bin/env python3
"""Extract the Sequence Machine's recurrence conjectures, deduplicated by what they SAY.

The machine emits many algebraically identical variants of the same recurrence --
a(n-1)+a(n-2)+a(n-2)-a(n-3), a(n-1)-(a(n-3)-2*a(n-2)) and a(n-1)+2*a(n-2)-a(n-3) are one
conjecture written three ways -- so counting program strings overstates the pool badly.
Each is parsed and reduced to its coefficient vector, and the vector is what gets counted.

Kept: unproven, not sourced from the OEIS, at least 200 matching terms, and built only
from n, integers and arithmetic on earlier terms -- no floor, mod, gcd, digits or other
sequences, none of which the engines here can take as input.
"""
import json, os, re, sys
import sympy as sp

ROOT = "/home/user/jonmaiga/sequence-machine-data/oeis"
OUT = "sm_rec.json"
BAD = re.compile(r"floor|ceil|round|%|gcd|lcm|\bval\b|prime|xor|\bdr\b|A\d{6}|∑|∏|√|sqrt"
                 r"|log|exp|ϕ|π|φ|γ|!|\bC\(|binomial|filter|char|comp|record|ratio"
                 r"|\bde\b|contfrac|lim|\bor\(|\band\(|\bit\b")
REC = re.compile(r"a\(n-(\d+)\)")
n = sp.Symbol('n')


def vector(ix):
    """The coefficient vector of a(n) = <expr>, as [1, -c1, -c2, ...], or None."""
    s = ix.replace("^", "**")
    if BAD.search(s) or not REC.search(s):
        return None
    order = max(int(m) for m in REC.findall(s))
    if order > 12:
        return None
    syms = {f"__a{j}__": sp.Symbol(f"__a{j}__") for j in range(1, order + 1)}
    for j in range(order, 0, -1):
        s = s.replace(f"a(n-{j})", f"__a{j}__")
    if "a(" in s:
        return None
    try:
        e = sp.expand(sp.sympify(s, locals=dict(syms, n=n)))
    except Exception:
        return None
    if not isinstance(e, sp.Expr):
        return None
    out = [sp.Integer(1)]
    rest = e
    for j in range(1, order + 1):
        c = sp.expand(rest.coeff(syms[f"__a{j}__"], 1))
        if c.has(*syms.values()):
            return None                      # nonlinear in the earlier terms
        out.append(sp.expand(-c))
        rest = sp.expand(rest - c * syms[f"__a{j}__"])
    if rest.has(*syms.values()) or rest != 0:
        return None                          # an inhomogeneous term: not our shape
    if any(c.free_symbols - {n} for c in out):
        return None
    return [sp.sstr(c) for c in out]


def main():
    got = json.load(open(OUT)) if os.path.exists(OUT) else {"done": [], "hits": {}}
    done, hits = set(got["done"]), got["hits"]
    dirs = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    for d in dirs:
        if d in done:
            continue
        dd = os.path.join(ROOT, d)
        for fn in os.listdir(dd):
            if not fn.endswith(".programs.json"):
                continue
            try:
                j = json.load(open(os.path.join(dd, fn)))
            except Exception:
                continue
            a = "A%06d" % j.get("oi", 0)
            seen = {}
            for p in j.get("ps", []):
                if "proven" in (p.get("tags") or []) or p.get("s") == "oeis":
                    continue
                if p.get("mt", 0) < 200:
                    continue
                v = vector(p.get("ix", ""))
                if v is None:
                    continue
                seen.setdefault(tuple(v), (p["ix"], p["mt"]))
            if seen:
                hits[a] = [{"vec": list(k), "ix": v[0], "mt": v[1]} for k, v in seen.items()]
        done.add(d)
        json.dump({"done": sorted(done), "hits": hits}, open(OUT, "w"))
    tot = sum(len(v) for v in hits.values())
    print(f"{len(done)}/{len(dirs)} dirs; {tot} distinct recurrence conjectures "
          f"over {len(hits)} entries")


if __name__ == "__main__":
    main()
