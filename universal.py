#!/usr/bin/env python3
"""Every route, every open conjecture. The sweep that is meant to leave nothing readable.

The lesson of today is that the mathematics was never the bottleneck -- the parsers were.
376 candidates were hidden by one regex, 18 by never reading the entry's name, 69 by a
mistyped "G.f f:" prefix. So this stops hunting shapes one at a time and instead offers
every fact line on every open entry to every reader in the project, in order of how much
the resulting proof is worth:

    a recurrence stated as fact   -> Ore right division, oremod for the residual
    a generating function          -> the residual-polynomial criterion in its field
    an algebraic relation for the g.f. -> the same, after solving for the branch
    a coefficient extraction       -> Lagrange inversion, then the same
    a closed form                  -> hyperterm, a decision procedure
    a closed form that rounds      -> the parity split, then hyperterm on each branch
    a sum                          -> creative telescoping with boundary correction
    a reference to another entry   -> resolved, then hyperterm

Openness comes from open_index.json, so nothing already settled is attacked, and entries
that already have a paper for that conjecture are skipped by the caller.
"""
import json, os, re, sys
sys.path.insert(0, ".")
import sympy as sp
import blocks, fsplit, cfparse, gfclean, sumparse, fzparse, diagonal, xref
import decide, hyperterm, parity, ore, oremod, algfield as af
from parity import m as pm
from makeslots import coeffs_of
from regf import entry

x, n = sp.symbols('x n')
GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)
FINITE = re.compile(r"for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b|\bverified for\b|\bup to\b\s+n", re.I)
ATTRIB = re.compile(r"\s+-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d.*$")
# the colon is optional: gfclean now colonises "G.f. <expr>" and "G.f. (for offset 1): ..."
# itself, so a matcher that still demands one refuses exactly the lines the fix was for.
GF = re.compile(r"^\s*(o\.)?g\.f\.\s*(\(for offset[^)]*\))?\s*[:=]?\s*[-(\dx]", re.I)
EGF = re.compile(r"^\s*e\.g\.f\.\s*(\(for offset[^)]*\))?\s*[:=]?\s*[-(\dx]", re.I)
STATED = re.compile(r"^\s*(Recurrence\s*[:.]?\s*|D-finite with recurrence\s*[:.]?\s*)?"
                    r"[-+0-9(na ].*\ba\(n\s*[-+]\s*\d+\)", re.I)
SAT = re.compile(r"g\.f\.[^.]{0,40}?\b([A-Za-z])\s*\(?\s*x?\s*\)?\s*satisfies\b[: ]*(.*)$", re.I)


def _implicit(line, data, off):
    """The MINIMAL POLYNOMIAL of a g.f. given by an algebraic relation.

    Returning the polynomial rather than a solved branch is both more robust and closer to
    what is wanted: algfield.Field takes a minimal polynomial directly, so solving a cubic
    for radicals -- which then defeats the series check used to pick the branch -- is work
    that need not be done at all. The relation is verified against the entry's own terms by
    substituting the data series and asking for the result to vanish.
    """
    mm = SAT.search(line)
    if not mm:
        return None
    sym, body = mm.group(1), mm.group(2).strip().rstrip(".")
    if "=" not in body:
        return None
    lhs, rhs = body.split("=", 1)
    y = sp.Symbol('__y__')
    def prep(s):
        s = s.replace("^", "**")
        s = re.sub(rf"\b{re.escape(sym)}\s*\(\s*x\s*\)", "__y__", s)
        s = re.sub(rf"\b{re.escape(sym)}\b(?!\s*\()", "__y__", s)
        s = re.sub(r"(\d)\s*([a-zA-Z(_])", r"\1*\2", s)
        s = re.sub(r"\)\s*\(", r")*(", s)
        # "(x-2) x f(x)^2" and "(2 x^2 - 2 x + 1) f(x)": a closing bracket followed by a
        # variable, and a variable followed by a variable, are both implicit products
        s = re.sub(r"\)\s*(?=[A-Za-z_\d])", ")*", s)
        s = re.sub(r"\b([a-zA-Z_]\w*)\s+(?=[A-Za-z_])", r"\1*", s)
        return s
    try:
        P = sp.expand(sp.sympify(prep(lhs), locals={'x': x, '__y__': y})
                      - sp.sympify(prep(rhs), locals={'x': x, '__y__': y}))
    except Exception:
        return None
    if not isinstance(P, sp.Expr) or (P.free_symbols - {x, y}) or not P.has(y):
        return None
    P = sp.expand(sp.numer(sp.together(P)))
    if sp.Poly(P, y).degree() < 1:
        return None
    # verify the relation against the entry's own terms before it is used
    N = min(len(data), 12)
    A = sum(sp.Integer(data[i]) * x ** (i + off) for i in range(N))
    chk = sp.expand(P.subs(y, A))
    try:
        pc = sp.Poly(chk, x)
    except Exception:
        return None
    if any(pc.coeff_monomial(x ** k) != 0 for k in range(0, N + off)):
        return None
    return sp.expand(P)


def known_sides(F, data, off):
    """Every readable fact side, tagged with the route it opens."""
    cj = blocks.conjectured_lines(F)
    known = [ATTRIB.sub("", l) for l in F
             if l.strip() not in cj and not GUESS.search(l) and not FINITE.search(l)]
    parts = [q for l in known for q in [l] + fsplit.split(l)]
    out = []
    for q in parts:
        try:
            if STATED.match(q):
                v = coeffs_of(q)
                if v and len(v) > 1:
                    out.append(("stated recurrence", q, v))
            if GF.match(q):
                for c in gfclean.candidates(q):
                    out.append(("gf", q, c[0] if isinstance(c, (tuple, list)) else c))
            if EGF.match(q):
                for c in gfclean.candidates(q):
                    out.append(("egf", q, c[0] if isinstance(c, (tuple, list)) else c))
            A = fzparse.parse(q, data, off)
            if A is not None:
                out.append(("gf", q, sp.sstr(A)))
            P = _implicit(q, data, off)
            if P is not None:
                out.append(("algpoly", q, sp.sstr(P)))
            fg = diagonal.parse_extraction(q)
            if fg is not None:
                out.append(("extraction", q, fg))
            e = cfparse.parse(q)
            if e is not None:
                out.append(("closedform", q, e))
            else:
                e = cfparse.parse(q, rounding=True)
                if e is not None:
                    out.append(("parity", q, e))
            e = xref.resolve(q)
            if e is not None:
                out.append(("closedform", q, e))
        except Exception:
            continue
    return out


def decide_all(item):
    """Every conjecture on the entry, against every readable known side."""
    a = item["anum"]
    F, data, off, nm = entry(a)
    sides = known_sides(F, data, off)
    if not sides:
        return ("no", "no readable known side")
    out = []
    for cl in item["conj"]:
        try:
            ps = coeffs_of(cl)
        except Exception:
            continue
        if not ps or len(ps) < 2:
            continue
        got = None
        for kind, src, val in sides:
            try:
                if kind in ("gf", "egf"):
                    r = decide.decide_one(_strip(cl), data, off, kind == "egf", [str(val)])
                    if r.get("status") in ("PROVED", "DISPROVED"):
                        got = dict(r, route=kind, src=src)
                elif kind == "algpoly":
                    P = sp.sympify(str(val)).subs(sp.Symbol('__y__'), sp.Symbol('y'))
                    K = af.Field(sp.expand(P))
                    ok, B = K.is_polynomial(K.residual(sp.Poly(sp.Symbol('y'), sp.Symbol('y')),
                                                       ps, n))
                    if ok:
                        deg = int(sp.Poly(B, x).total_degree()) if B != 0 else -1
                        got = {"status": "PROVED", "route": "algpoly", "src": src,
                               "degree": deg, "minpoly": str(val)}
                elif kind == "extraction":
                    got = _extraction(val, ps, data, off, src)
                elif kind == "closedform":
                    al, sh = cfparse.align(val, data, off)
                    if al is None:
                        continue
                    ok, ev = hyperterm.is_zero_sum(
                        sp.expand(sum(p * al.subs(n, n - j)
                                      for j, p in enumerate(ps) if p != 0)), n)
                    if ok:
                        got = {"status": "PROVED", "route": "closedform", "src": src,
                               "degree": -1, "closed": sp.srepr(al)}
                elif kind == "parity":
                    al, sh = cfparse.align(val, data, off)
                    if al is None:
                        continue
                    h = parity.halves(al)
                    if h is None:
                        continue
                    r0 = hyperterm.is_zero_sum(parity.combination(ps, h[0], h[1], False), pm)
                    r1 = hyperterm.is_zero_sum(parity.combination(ps, h[0], h[1], True), pm)
                    if r0[0] and r1[0]:
                        got = {"status": "PROVED", "route": "parity", "src": src,
                               "degree": -1}
                elif kind == "stated recurrence":
                    L = ore.to_operator(val)
                    Q, R = ore.right_divide(ore.to_operator(ps), L)
                    if ore.is_zero(R) or oremod.vanishes(R, L, data, off, len(val) - 1):
                        got = {"status": "PROVED", "route": "stated recurrence",
                               "src": src, "degree": -1}
            except Exception:
                continue
            if got:
                break
        if not got:
            continue
        if got["status"] == "PROVED":
            deg = got.get("degree", -1)
            order = len(ps) - 1
            lo = max(order, deg + 1 + (order if got.get("route") == "egf" else 0))
            bad = [i + off for i in range(lo, len(data))
                   if sum(int(sp.Poly(p, n).eval(i + off)) * data[i - j]
                          for j, p in enumerate(ps) if p != 0) != 0]
            if bad:
                out.append(("integer re-check failed", cl, bad[:3])); continue
            got["nver"] = len(data) - lo
            got["firstn"] = lo + off
        out.append((got["status"], cl, got))
    return ("ok", out)


def _strip(cl):
    return re.sub(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*"
                  r"(?:(?:to be\s+)?D-finite\s+with\s+recurrence\s*[:.,]?\s*)?", "", cl, flags=re.I)


def _extraction(fg, ps, data, off, src):
    f, g = fg
    N = min(len(data) - 1, 9)
    ser = diagonal.series(f, g, off + N + 3)
    if ser is None or not all(sp.simplify(ser[off + i] - data[i]) == 0 for i in range(N + 1)):
        return None
    P = diagonal.minimal_polynomial(f, g)
    if P is None:
        return None
    fac = diagonal.pick_factor(P, ser, off + N + 3)
    if fac is None:
        return None
    K = af.Field(sp.expand(fac.subs(diagonal.t, x)))
    ok, B = K.is_polynomial(K.residual(sp.Poly(diagonal.y, diagonal.y), ps, n))
    if not ok:
        return None
    return {"status": "PROVED", "route": "extraction", "src": src,
            "degree": int(sp.Poly(B, x).total_degree()) if B != 0 else -1}
