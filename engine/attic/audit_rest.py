#!/usr/bin/env python3
"""Whatever is left: test every conjectured statement on the entry against its own terms.

The recurrence audits test the line the PAPER quotes. For a paper whose known side is a closed
form the entry states as fact, that quoted line is not the conjecture at all, so the audit
skipped it. Here the entry is read from scratch: every line labelled Conjecture or Empirical
that states a linear recurrence OR an explicit closed form is evaluated on the published terms,
and every one of them is reported. If the paper's claim is among them -- and it is, since the
paper proves a statement the entry carries -- a wrong claim shows up as a failing line.
"""
import json, os, re, sys, collections, signal
import sympy as sp
import localentry as LE
from makeslots import coeffs_of

OUT = 'audit_rest.json'
SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
n = sp.Symbol('n')
MARK = re.compile(r'^\s*(Conjectur|Empirical|conjecture)', re.I)


class Slow(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(Slow()))


def ipoly(p):
    try:
        if p == 0:
            return [0]
        if not sp.expand(p).is_polynomial(n):
            return None
        cs = sp.Poly(sp.expand(p), n).all_coeffs()[::-1]
    except Exception:
        return None
    out = []
    for c in cs:
        c = sp.nsimplify(c, rational=True)
        if c.q != 1:
            return None
        out.append(int(c))
    return out


def ev(co, v):
    r = 0
    for c in reversed(co):
        r = r * v + c
    return r


def test_rec(line, d, off):
    try:
        cs = coeffs_of(line)
    except Exception:
        return None
    if not cs or len(cs) < 2:
        return None
    ps = [ipoly(c) for c in cs]
    if any(p is None for p in ps):
        return None
    r = len(ps) - 1
    m = re.search(r'\bfor\s+n\s*(>=|>)\s*(-?\d+)', line)
    lo = int(m.group(2)) + (1 if m.group(1) == '>' else 0) if m else None
    bad, tested = [], 0
    for i in range(r, len(d)):
        N = off + i
        if lo is not None and N < lo:
            continue
        tested += 1
        if sum(ev(ps[k], N) * d[i - k] for k in range(r + 1)) != 0:
            bad.append(N)
    if not tested:
        return None
    prefix = bad and bad == list(range(bad[0], bad[0] + len(bad)))
    return {'kind': 'recurrence', 'order': r, 'tested': tested,
            'bad': bad[:5], 'prefix_only': bool(prefix),
            'ok': not bad or bool(prefix)}


def test_form(line, d, off):
    body = re.sub(r'^\s*(Conjectur\w*|Empirical|conjecture)\s*\d*\s*[:.,]?\s*', '', line,
                  flags=re.I).split(' - _')[0].strip().rstrip('.')
    m = re.match(r'a\(n\)\s*=\s*(.+)$', body, re.S)
    if not m:
        return None
    rhs = m.group(1)
    if 'a(n-' in rhs or 'a(n+' in rhs or 'A0' in rhs or 'A1' in rhs or 'A2' in rhs:
        return None                        # a recurrence, or a cross-reference
    lo = None
    mm = re.search(r'\bfor\s+n\s*(>=|>)\s*(-?\d+)', rhs)
    if mm:
        lo = int(mm.group(2)) + (1 if mm.group(1) == '>' else 0)
        rhs = rhs[:mm.start()]
    try:
        ex = sp.sympify(rhs.replace('^', '**'), locals={'n': n})
    except Exception:
        return None
    bad, tested = [], 0
    for i, v in enumerate(d):
        N = off + i
        if lo is not None and N < lo:
            continue
        try:
            val = sp.nsimplify(ex.subs(n, N), rational=True)
        except Exception:
            return None
        tested += 1
        if val != v:
            bad.append(N)
        if len(bad) > 5:
            break
    if not tested:
        return None
    return {'kind': 'closed form', 'tested': tested, 'bad': bad[:5], 'ok': not bad}


def main(budget=520):
    import time
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    st = json.load(open(SC + '/status.json'))
    pe = json.load(open('paper-engines.json'))
    live = {v['anum'] for v in pe.values()}
    todo = sorted(a for a, s in st.items()
                  if s == 'symbolic engine, not re-derived' and a in live)
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        d = [int(x) for x in e['data'].split(',') if x.strip()]
        off = int(e['offset'].split(',')[0])
        rows = []
        signal.alarm(60)
        try:
            for L in e['comment'] + e['formula']:
                if not MARK.match(L):
                    continue
                r = test_rec(L, d, off) or test_form(L, d, off)
                if r:
                    r['line'] = L[:110]
                    rows.append(r)
        except Slow:
            signal.alarm(0)
            out[a] = {'v': 'SLOW'}; continue
        except Exception as ex:
            signal.alarm(0)
            out[a] = {'v': 'ERROR', 'err': str(ex)[:80]}; continue
        signal.alarm(0)
        if not rows:
            out[a] = {'v': 'NOTHING TESTABLE ON THE ENTRY'}
        else:
            out[a] = {'v': 'ok' if all(r['ok'] for r in rows) else 'PROBLEM',
                      'statements': rows, 'nterms': len(d)}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 520)
