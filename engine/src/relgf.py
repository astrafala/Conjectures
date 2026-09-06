#!/usr/bin/env python3
"""Derive an entry's generating function from a formula relating it to other entries.

Fifty-five entries carry a recurrence conjecture, no generating function of their own,
and a FORMULA line of the shape

    a(n) = A173184(n) - 1        a(n) = 2*A000045(n+1) + n

When every entry on the right posts a generating function, that relation supplies one
here, and the residual test applies as usual. The relation must not itself be
conjectural -- an "apparently" or "conjecture" on that line makes the whole derivation a
guess, so those are refused.
"""
import json, os, re
import sympy as sp
from prove_rec import parse_gf, parse_conj
from holonomic import taylor
import cross as C

x, n = sp.symbols('x n')
ROOT = "/home/user/oeis/oeisdata/seq"
LABEL = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
GUESS = re.compile(r"apparent|conjectur|empirical|it seems|probably|guess", re.I)
TERM = re.compile(r"A(\d{6})\(\s*n\s*([+-]\s*\d+)?\s*\)")


def fields(a):
    p = f"{ROOT}/{a[:4]}/{a}.seq"
    if not os.path.exists(p):
        return None
    f = {}
    for line in open(p, errors="ignore"):
        if line.startswith("%"):
            f.setdefault(line[1], []).append(
                re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def main():
    have = set()
    for f in ("scan-cache.json", "nogf-cache.json", "midline-cache.json",
              "eqform-cache.json", "cf-cache.json"):
        if os.path.exists(f):
            have |= set(json.load(open(f)))
    out = {}
    cache = {}
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            a = "A" + fn[1:7]
            if a in have:
                continue
            txt = open(os.path.join(dd, fn), errors="ignore").read()
            if "Conjectur" not in txt or "a(n-" not in txt:
                continue
            f = fields(a)
            conjs = [l for tag in ("C", "F", "e") for l in f.get(tag, [])
                     if LABEL.match(l) and "a(n-" in l.replace(" ", "")
                     and "=0" in l.replace(" ", "")]
            if not conjs:
                continue
            rels = [l for l in f.get("F", [])
                    if re.match(r"a\(n\)\s*=", l) and TERM.search(l)
                    and not LABEL.match(l) and not GUESS.search(l)]
            if not rels:
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            off = int((f.get("O") or ["0"])[0].split(",")[0])
            out[a] = {"name": (f.get("N") or [""])[0], "offset": off, "data": terms,
                      "conjs": conjs, "rels": rels}
    json.dump(out, open("relgf-cache.json", "w"), indent=1, sort_keys=True)
    print(f"{len(out)} entries with a non-conjectural relation to other entries")


if __name__ == "__main__":
    main()


def series_of(a, cache):
    """The other entry's g.f. and e.g.f., each checked against its own published terms."""
    if a in cache:
        return cache[a]
    f = fields(a)
    res = (None, None, None)
    if f:
        data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
        try:
            terms = [int(t) for t in data.split(",") if t.strip()]
        except ValueError:
            terms = []
        off = int((f.get("O") or ["0"])[0].split(",")[0])
        for l in f.get("F", []):
            for pat, kind in ((r"G\.f\.", "ogf"), (r"E\.g\.f\.", "egf")):
                m = re.match(pat + r"\s*:?\s*(.+)", l.strip(), re.I)
                if not m or GUESS.search(l):
                    continue
                src = m.group(1).strip()
                try:
                    G = parse_gf(src, 'x', raw=src)
                    base = taylor(G, off + 10)
                    if kind == "egf":
                        base = [c * sp.factorial(k) for k, c in enumerate(base)]
                except Exception:
                    continue
                if len(terms) >= 8 and all(
                        sp.simplify(base[off + k] - terms[k]) == 0 for k in range(8)):
                    res = (G, kind, off)
                    break
            if res[0] is not None:
                break
    cache[a] = res
    return res


def derive(rel, target_off, cache):
    """Build the target's generating function from the relation, or None."""
    refs = []

    def grab(m):
        refs.append(("A" + m.group(1), int((m.group(2) or "0").replace(" ", ""))))
        return f"R{len(refs)-1}"

    body = rel.split(" - _")[0]
    body = re.sub(r"\bfor\s+n\s*[><=].*$", "", body)
    body = re.sub(r",?\s*(with|where)\s.*$", "", body, flags=re.I).strip().rstrip(".")
    body = TERM.sub(grab, body[body.index("=") + 1:])
    if re.search(r"A\d{6}", body) or not refs:
        return None, None
    body = body.replace("^", "**")
    body = re.sub(r"(\d)\s*\(", r"\1*(", body)
    body = re.sub(r"\)\s*\(", r")*(", body)
    body = re.sub(r"(\d)\s*([nR])", r"\1*\2", body)
    syms = {f"R{i}": sp.Symbol(f"R{i}") for i in range(len(refs))}
    try:
        e = sp.expand(sp.sympify(body, locals={**syms, "n": n}))
    except Exception:
        return None, None
    if e.free_symbols - {n} - set(syms.values()):
        return None, None
    kinds = set()
    total = sp.Integer(0)
    for i, (b, k) in enumerate(refs):
        G, kind, boff = series_of(b, cache)
        if G is None:
            return None, None
        kinds.add(kind)
        c = sp.expand(e.coeff(syms[f"R{i}"]))
        if c.has(*syms.values()):
            return None, None                    # a product of two entries is not linear
        S = G if k == 0 else None
        if k != 0:
            if kind == "egf":
                return None, None                # shifts of an e.g.f. are derivatives
            S = C.shifted(G, [], boff, k, 12)
        total += C.theta_apply(c, S)
    rest = sp.expand(e - sum(sp.expand(e.coeff(s)) * s for s in syms.values()))
    if rest.has(*syms.values()) or not sp.expand(rest).is_polynomial(n):
        return None, None
    if len(kinds) != 1:
        return None, None
    kind = kinds.pop()
    if rest != 0:
        if kind == "egf":
            # a polynomial p(n) contributes p(theta)[e^x] to an exponential g.f.
            total += C.theta_apply(rest, sp.exp(x))
        else:
            total += C.poly_gf(rest, 12)
    return sp.together(sp.simplify(total)), kind
