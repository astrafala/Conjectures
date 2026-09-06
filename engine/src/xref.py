#!/usr/bin/env python3
"""Resolve a definition that names another sequence into a closed form in n.

Entries like

    A082143:  a(n) = A000079(n-1) * A001700(n), for n > 0
    A150500:  a(n) = (A201805(n+1) + 3*A201805(n))/4

give no formula of their own, but the sequences they name do. Substituting those closed
forms turns the definition into an ordinary expression in n, which hyperterm.py then
decides.

The formulas taken from the referenced entries are the ones those entries state as fact,
never as conjectures, and each is checked against its own DATA (with the index alignment
searched for) before being used. That is the same standard the rest of this work uses for
the entry under study: the posted non-conjectural formula is the input, and the paper says
so.
"""
import functools, re
import sympy as sp
import cfparse
import fsplit
from regf import entry, CONJ

n = sp.Symbol('n')
REF1 = re.compile(r"\bA(\d{6})\s*\(([^(),]*)\)")
REF2 = re.compile(r"\bA\d{6}\s*\([^()]*,[^()]*\)")


@functools.lru_cache(maxsize=None)
def closed_form_of(anum):
    """A non-conjectural closed form for that entry, aligned to its own terms."""
    try:
        F, data, off, name = entry(anum)
    except Exception:
        return None
    if len(data) < 8:
        return None
    for line in F:
        if CONJ.match(line) or re.search(r"conjectur|empirical|apparent", line, re.I):
            continue
        # a %F line often carries several formulas separated by full stops, and the
        # closed form is one of them: A000027 states "G.f.: x/(1-x)^2. E.g.f.: x*exp(x).
        # a(n)=n." on a single line, which cfparse reads whole and rejects.
        for part in [line] + fsplit.split(line):
            e = cfparse.parse(part)
            if e is None:
                continue
            al, sh = cfparse.align(e, data, off)
            if al is not None:
                return al
    return None


def resolve(line, depth=0):
    """The right-hand side of a(n) = ... with every A-reference substituted, or None."""
    m = re.match(r"\s*a\(n\)\s*=\s*(.+)$", line.strip(), re.I)
    if not m:
        return None
    b = m.group(1).split(" - _")[0]
    b = re.sub(r"\.?\s*\(\s*End[^()]*\)\s*$", "", b, flags=re.I)
    b = re.sub(r",?\s*\bfor\b\s+n\s*[<>=].*$", "", b, flags=re.I)
    b = re.sub(r"\s*\[.*?\]\s*$", "", b)
    b = b.split("=")[0] if b.count("=") and not re.search(r"[<>!]=", b) else b
    b = b.strip().rstrip(".").strip()
    if REF2.search(b):
        return None                     # a triangle reference needs the triangle's formula
    refs = REF1.findall(b)
    if not refs:
        return None
    if re.search(r"Sum_|Product_|\bmod\b|floor|ceiling", b, re.I):
        return None
    subs = {}
    for i, (num, arg) in enumerate(refs):
        cf = closed_form_of("A" + num)
        if cf is None:
            return None
        try:
            a = sp.sympify(cfparse._ready(arg), locals=dict(cfparse.LOCALS))
        except Exception:
            return None
        if a.free_symbols - {n}:
            return None
        subs[f"__R{i}__"] = cf.subs(n, a)
    out = b
    for i, (num, arg) in enumerate(refs):
        out = out.replace(f"A{num}({arg})", f"__R{i}__", 1)
    if re.search(r"A\d{6}", out):
        return None
    try:
        e = sp.sympify(cfparse._ready(out),
                       locals=dict(cfparse.LOCALS, **{k: v for k, v in subs.items()}))
    except Exception:
        return None
    if not isinstance(e, sp.Expr) or e.free_symbols - {n}:
        return None
    return e
