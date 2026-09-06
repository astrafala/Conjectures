#!/usr/bin/env python3
"""The table papers, verified column by column.

A table entry is written T(n,k) and lists an empirical recurrence per column -- "k=1: a(n) =
154*a(n-2) - ...". Column k is an ordinary fixed-width array count, so the engines read it once
k is substituted, which is what the paper does. audit_deep could not touch these: it feeds the
entry's own NAME to the parser, and no parser reads "T(n,k) is the number of ...".

For every column whose recurrence the entry writes out, this rebuilds that column's model,
lines it up on the column read out of the table's antidiagonal-ordered data, and evaluates the
recurrence past both the data and the threshold. Columns given only as "[order N]" belong to
the recovery audit and are skipped here.
"""
import json, os, re, sys, signal, collections, time
import localentry as LE, uniform, tablecol
from makeslots import coeffs_of
import sympy as sp

OUT = 'audit_table%s.json' % os.environ.get('SHARD', '')
n = sp.Symbol('n')
COLLINE = re.compile(r'^\s*k\s*=\s*(\d+)\s*:\s*(.+)$')


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


def col_recurrences(e):
    """{k: (coefficient polynomials, 'for n >= lo')} for the columns written out."""
    out = {}
    for L in e['comment'] + e['formula']:
        m = COLLINE.match(L)
        if not m:
            continue
        k, body = int(m.group(1)), m.group(2).strip()
        if 'order' in body.lower() and 'a(n' not in body:
            continue                       # "[order 35]" -- the recovery audit's business
        lo = None
        mm = re.search(r'\bfor\s+n\s*(>=|>)\s*(-?\d+)', body)
        if mm:
            lo = int(mm.group(2)) + (1 if mm.group(1) == '>' else 0)
        try:
            cs = coeffs_of('Empirical: ' + body)
        except Exception:
            continue
        if not cs or len(cs) < 2:
            continue
        ps = [ipoly(c) for c in cs]
        if any(p is None for p in ps):
            continue
        out[k] = (ps, lo, body[:90])
    return out


def coldata(e, k, want):
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    grid, i, diag = {}, 0, 1
    while i < len(d):
        for r in range(1, diag + 1):
            if i >= len(d):
                break
            grid[(r, diag + 1 - r)] = d[i]
            i += 1
        diag += 1
    out, r = [], 1
    while (r, k) in grid and len(out) < want:
        out.append(grid[(r, k)])
        r += 1
    return out


def main(budget, per_entry):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    # a table paper settles the columns it names -- usually the first few -- and the entry
    # lists more than that. Checking columns the paper never claimed made ten papers look
    # unverified because a column they say nothing about is too large to rebuild.
    SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
    claimed = json.load(open(SC + '/table_claimed.json'))
    rm = json.load(open('rank-map.json'))
    todo = sorted({r['anum'] for r in rm if r['engine'] == 'table-column'})
    w, N = int(os.environ.get('W', 0)), int(os.environ.get('N', 1))
    todo = [a for i, a in enumerate(todo) if i % N == w]
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        cols = col_recurrences(e)
        if not cols:
            out[a] = {'v': 'NO WRITTEN COLUMN RECURRENCE'}; continue
        off = int(e['offset'].split(',')[0])
        want = claimed.get(a)
        if want:
            cols = {k: v for k, v in cols.items() if k in want}
            if not cols:
                out[a] = {'v': 'CLAIMED COLUMNS NOT WRITTEN OUT', 'claimed': want}; continue
        rows, bad = {}, 0
        for k, (ps, lo, txt) in sorted(cols.items()):
            nm = tablecol.rewrite(e['name'], k)
            got = uniform.read(nm) if nm else None
            if not got:
                rows[k] = ['COLUMN NOT READ']; bad += 1; continue
            en, p = got
            d = coldata(e, k, 40)
            signal.alarm(per_entry)
            try:
                b = None
                for cap in (40000, int(os.environ.get('CAPMAX', '400000'))):
                    b = uniform.build(en, p, cap)
                    if b is not None:
                        break
                if b is None:
                    signal.alarm(0); rows[k] = ['TOO BIG']; bad += 1; continue
                vals = uniform.terms(en, p, b, len(d) + 45)
                signal.alarm(0)
            except Slow:
                signal.alarm(0); rows[k] = ['SLOW']; bad += 1; continue
            except Exception as ex:
                signal.alarm(0); rows[k] = ['ERROR ' + str(ex)[:50]]; bad += 1; continue
            g = [None if (v is None or v.denominator != 1) else v.numerator for v in vals]
            sh = next((s for s in range(6) if d and g[s:s + len(d)] == d), None)
            if sh is None:
                rows[k] = ['MODEL DOES NOT REPRODUCE THE COLUMN', len(d)]; bad += 1; continue
            seq, r = g[sh:], len(ps) - 1
            fails = []
            for i in range(r, len(seq)):
                N_ = off + i
                if lo is not None and N_ < lo:
                    continue
                if seq[i] is None or any(seq[i - j] is None for j in range(1, r + 1)):
                    continue
                if sum(ev(ps[j], N_) * seq[i - j] for j in range(r + 1)) != 0:
                    fails.append(N_)
            prefix = fails and fails == list(range(fails[0], fails[0] + len(fails)))
            ok = not fails or prefix
            rows[k] = ['ok' if ok else 'RECURRENCE FAILS', {'order': r, 'fails': fails[:5],
                       'prefix_only': bool(prefix), 'terms': len(d), 'checked': len(seq) - r}]
            if not ok:
                bad += 1
        out[a] = {'v': 'ok' if bad == 0 else 'PROBLEM', 'columns': rows,
                  'claimed': want}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    if len(sys.argv) > 4:
        os.environ['W'], os.environ['N'], os.environ['SHARD'] = sys.argv[3], sys.argv[4], sys.argv[3]
        OUT = 'audit_table%s.json' % sys.argv[3]
    main(int(sys.argv[1]), int(sys.argv[2]))
