#!/usr/bin/env python3
"""The papers that settled an empirical CLOSED FORM rather than a recurrence.

The entry states a polynomial in n and calls it empirical. The count is a walk count in a
finite graph, so it is C-finite; the paper's argument is that the conjectured polynomial
satisfies the same constant-coefficient recurrence and agrees at enough consecutive indices.
This re-checks the load-bearing fact directly and independently of that argument: rebuild the
model and evaluate the entry's own polynomial at every index the model reaches, far past the
terms the entry publishes.
"""
import json, os, re, sys, signal, collections, time
from fractions import Fraction
import sympy as sp
import localentry as LE, uniform

OUT = 'audit_closed%s.json' % os.environ.get('SHARD', '')
n = sp.Symbol('n')


class Slow(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(Slow()))


def forms(e):
    """The conjectured closed forms on the entry, as (expression, 'for n >= lo')."""
    out = []
    for L in e['comment'] + e['formula']:
        if not re.match(r'\s*(Conjectur|Empirical)', L, re.I):
            continue
        body = re.sub(r'^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*', '', L, flags=re.I)
        body = body.split(' - _')[0].strip().rstrip('.')
        m = re.match(r'a\(n\)\s*=\s*(.+)$', body, re.S)
        if not m:
            continue
        rhs = m.group(1)
        lo = None
        mm = re.search(r'\bfor\s+n\s*(>=|>)\s*(-?\d+)', rhs)
        if mm:
            lo = int(mm.group(2)) + (1 if mm.group(1) == '>' else 0)
            rhs = rhs[:mm.start()]
        if 'a(n-' in rhs or 'a(n+' in rhs:
            continue                     # a recurrence, not a closed form
        try:
            ex = sp.sympify(rhs.replace('^', '**'), locals={'n': n})
        except Exception:
            continue
        out.append((ex, lo, L[:110]))
    return out


def main(budget, per_entry):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    rm = json.load(open('rank-map.json'))
    todo = sorted({r['anum'] for r in rm if r['engine'] == 'walk-closed-form'})
    w, N = int(os.environ.get('W', 0)), int(os.environ.get('N', 1))
    todo = [a for i, a in enumerate(todo) if i % N == w]
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        fs = forms(e)
        if not fs:
            out[a] = {'v': 'NO CLOSED FORM PARSED'}; continue
        got = uniform.read(e['name'])
        if not got:
            out[a] = {'v': 'NOT AN ARRAY MODEL'}; continue
        en, p = got
        d = [int(x) for x in e['data'].split(',') if x.strip()]
        off = int(e['offset'].split(',')[0])
        signal.alarm(per_entry)
        try:
            b = None
            for cap in (40000, 400000):
                b = uniform.build(en, p, cap)
                if b is not None:
                    break
            if b is None:
                signal.alarm(0); out[a] = {'v': 'TOO BIG'}; continue
            vals = uniform.terms(en, p, b, len(d) + 60)
            signal.alarm(0)
        except Slow:
            signal.alarm(0); out[a] = {'v': 'SLOW'}; continue
        except Exception as ex:
            signal.alarm(0); out[a] = {'v': 'ERROR', 'err': str(ex)[:80]}; continue
        g = [None if (v is None or v.denominator != 1) else v.numerator for v in vals]
        sh = next((s for s in range(6) if g[s:s + len(d)] == d), None)
        if sh is None:
            out[a] = {'v': 'MODEL DOES NOT REPRODUCE DATA'}; continue
        seq = g[sh:]
        rows = []
        for ex, lo, txt in fs:
            bad, tested = [], 0
            for i, v in enumerate(seq):
                if v is None:
                    continue
                N_ = off + i
                if lo is not None and N_ < lo:
                    continue
                tested += 1
                val = sp.nsimplify(ex.subs(n, N_), rational=True)
                if val != v:
                    bad.append(N_)
                if len(bad) > 5:
                    break
            rows.append({'ok': not bad, 'tested': tested, 'bad': bad[:5], 'line': txt})
        out[a] = {'v': 'ok' if all(r['ok'] for r in rows) else 'PROBLEM',
                  'forms': rows, 'engine': en, 'terms_published': len(d)}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    if len(sys.argv) > 4:
        os.environ['W'], os.environ['N'], os.environ['SHARD'] = sys.argv[3], sys.argv[4], sys.argv[3]
        OUT = 'audit_closed%s.json' % sys.argv[3]
    main(int(sys.argv[1]), int(sys.argv[2]))
