#!/usr/bin/env python3
"""Prove conjectures of the form "Conjecture: a(n) = f(n)" against the entry's g.f.

If the entry posts a generating function A(x) and the conjecture claims a closed form
f(n), then the conjecture says exactly

    sum_{n >= off} f(n) x^n  =  A(x)

as formal power series. When f is a linear combination of terms n^k * r^n (and more
generally whenever sympy can sum it in closed form), the left side is computable
exactly, and the identity is decided by symbolic cancellation -- not by comparing
finitely many terms.

As with the recurrence work, the entry's posted g.f. is taken as given; that is stated
in every write-up.
"""
import json, os, re, signal, sys
import sympy as sp
from prove_rec import parse_gf, normalise

x, n = sp.symbols('x n')
ROOT = "/home/user/oeis/oeisdata/seq"
CF = re.compile(r'^%[CF] A\d{6} Conjecture[:.]?\s*(?:that\s+)?a\(n\)\s*=\s*(.+)$')


def parse_formula(s):
    s = re.sub(r'^\s*Conjecture[:.]?\s*(?:that\s+)?a\(n\)\s*=\s*', '', s.strip(), flags=re.I)
    s = s.split(' - _')[0].strip().rstrip('.')
    s = re.sub(r'\.?\s*\(\s*End[^()]*\)\s*$', '', s, flags=re.I)
    for cut in (' for ', ' with ', ', where', ' where ', ' checked', ';',
                ' [', ' Cf.', ' See ', ' This ', ' It '):
        s = s.split(cut)[0]
    s = s.strip().rstrip('.').strip().rstrip(',').strip()
    if re.search(r'a\(n\s*[-+]\s*\d+\)', s):
        raise ValueError('this is a recurrence, not a closed form')
    if re.search(r'A\d{6}', s):
        raise ValueError('refers to another entry')
    if re.search(r'\[\s*x\s*\^', s) or 'Sum_' in s or 'Product_' in s:
        raise ValueError('coefficient extraction or an unevaluated sum, not a closed form')
    # a chained "f(n) = g(n)" asserts both halves; take the first
    parts = re.split(r'(?<![<>=!])=(?!=)', s)
    if len(parts) > 1:
        s = parts[0]
    s = s.strip().rstrip('.').strip().rstrip(',').strip()
    s = s.replace('^', '**')
    s = s.replace(' ', '')
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    s = re.sub(r'\)([a-zA-Z0-9(])', r')*\1', s)
    s = re.sub(r'\*{3,}', '**', s)
    e = sp.sympify(s, locals={'n': n, 'binomial': sp.binomial,
                              'sqrt': sp.sqrt, 'floor': sp.floor}, rational=True)
    if e.free_symbols - {n}:
        raise ValueError(f'formula has stray symbols {e.free_symbols}')
    if e.has(sp.floor) or e.has(sp.ceiling) or e.has(sp.Mod):
        raise ValueError('floor/mod formula: not summable in closed form')
    return e


def _theta(e, k):
    for _ in range(k):
        e = sp.expand(x * sp.diff(e, x))
    return e


def gf_of(f, off):
    """sum_{n>=off} f(n) x^n as an exact rational function.

    Decompose f into terms (polynomial in n) * r^n. Since sum_{n>=0} r^n x^n =
    1/(1-r x) and multiplying the coefficient by n is theta = x d/dx, each term's
    generating function is p(theta) applied to 1/(1-r x). Finally drop the terms
    below the offset. Everything here is exact rational-function arithmetic.
    """
    f = sp.expand(sp.powsimp(sp.expand(f), force=True))
    terms = sp.Add.make_args(f)
    total = sp.Integer(0)
    for t in terms:
        r = sp.Integer(1)
        poly = sp.Integer(1)
        for fac in sp.Mul.make_args(t):
            b, e = fac.as_base_exp()
            if e.has(n):
                q = sp.simplify(e / n)
                if q.has(n):
                    raise ValueError('exponent is not linear in n')
                r *= b ** q
                extra = sp.simplify(e - q * n)
                if extra != 0:
                    poly *= b ** extra
            else:
                poly *= fac
        if poly.has(n) and not poly.is_polynomial(n):
            raise ValueError('non-polynomial coefficient')
        p = sp.Poly(sp.expand(poly), n) if poly.has(n) else None
        base = 1 / (1 - r * x)
        if p is None:
            total += poly * base
        else:
            for (k,), c in zip(p.monoms(), p.coeffs()):
                total += c * _theta(base, k)
    total = sp.cancel(sp.together(total))
    # strip the terms with n < off
    head = sum(sp.nsimplify(f.subs(n, m)) * x ** m for m in range(off))
    return sp.cancel(sp.together(total - head))


def entries():
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith('.seq'):
                continue
            txt = open(os.path.join(dd, fn), errors='ignore').read()
            conj = None
            for line in txt.split('\n'):
                m = CF.match(line)
                if m:
                    conj = m.group(1)
                    break
            if not conj:
                continue
            gfs = re.findall(r'^%F A\d{6} G\.f\.\s*:?\s*(.+)$', txt, re.M)
            if not gfs:
                continue
            name = (re.findall(r'^%N A\d{6} (.+)$', txt, re.M) or [''])[0]
            offs = (re.findall(r'^%O A\d{6} (.+)$', txt, re.M) or ['0'])[0]
            data = ''.join(re.findall(r'^%[STU] A\d{6} (.+)$', txt, re.M))
            proof = None
            for l in txt.split('\n'):
                if re.search(r'\bprove[dn]?\b|\bproof\b', l, re.I) and 'onjectur' in l:
                    proof = l[:120]
            try:
                terms = [int(t) for t in data.split(',') if t.strip()]
                off = int(offs.split(',')[0])
            except ValueError:
                continue
            if len(terms) < 6:
                continue
            yield "A" + fn[1:7], {"name": name, "offset": off, "data": terms,
                                  "conj": conj, "gfs": gfs, "proof": proof}
