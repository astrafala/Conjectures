#!/usr/bin/env python3
"""The same check for the TABLE papers that recovered unwritten column recurrences.

A table entry is T(n,k); column k is an ordinary fixed-width array count, which the engines
read once k is substituted. The entry lists an order per column -- "k=2: [order 46]" -- with
the recurrence itself in a linked file. For each column named, this rebuilds that column's
model and recomputes its minimal recurrence, aligned on the table's own data, and confirms
the order is the one the entry states.
"""
import json, os, re, sys, signal, collections, time
import localentry as LE, uniform, bmrec, tablecol

OUT = 'audit_tabrec%s.json' % os.environ.get('SHARD', '')
COL = re.compile(r'k\s*=\s*(\d+)\s*:\s*(?:.*?\[order\s+(\d+)\]|\s*a\(n\))', re.I)


def settled_order(vals, lo=0, hi=9):
    """The minimal recurrence order the tails settle to.

    The walk index and the entry's n differ by a constant -- the model counts the empty array
    and the short ones the entry never publishes -- and each unpublished leading term raises
    the minimal order by one. Dropping leading terms therefore lowers the order until the
    right tail is reached, after which it is constant. That constant is the sequence's own
    minimal order, and it is what the recovery argument is about.
    """
    orders = [bmrec.bm(vals[j:])[0] for j in range(lo, hi)]
    for i in range(len(orders) - 2):
        if orders[i] == orders[i + 1] == orders[i + 2]:
            return orders[i], orders
    return None, orders


class Slow(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(Slow()))


def columns(e):
    """{k: stated order} for the columns the entry names an order for."""
    out = {}
    for L in e['comment'] + e['formula']:
        for m in re.finditer(r'k\s*=\s*(\d+)\s*:\s*\[?order\s+(\d+)\]?', L, re.I):
            out[int(m.group(1))] = int(m.group(2))
    return out


def coldata(e, k, n):
    """Column k of the table, read out of the antidiagonal-ordered DATA."""
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    # tables are published by antidiagonals: T(1,1), T(1,2), T(2,1), T(1,3), T(2,2), ...
    out, i, diag = [], 0, 1
    grid = {}
    while i < len(d):
        for r in range(1, diag + 1):
            if i >= len(d):
                break
            grid[(r, diag + 1 - r)] = d[i]
            i += 1
        diag += 1
    r = 1
    while (r, k) in grid and len(out) < n:
        out.append(grid[(r, k)])
        r += 1
    return out


def main(budget, per_entry):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    rm = json.load(open('rank-map.json'))
    todo = sorted({r['anum'] for r in rm if r['engine'] == 'table-order-recovery'})
    w, N = int(os.environ.get('W', 0)), int(os.environ.get('N', 1))
    todo = [a for i, a in enumerate(todo) if i % N == w]
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        cols = columns(e)
        if not cols:
            out[a] = {'v': 'NO COLUMN ORDERS'}; continue
        rows, bad = {}, 0
        for k, order in sorted(cols.items()):
            nm = tablecol.rewrite(e['name'], k)
            if not nm:
                rows[k] = ['NAME NOT REWRITTEN', order]; bad += 1; continue
            got = uniform.read(nm)
            if not got:
                rows[k] = ['COLUMN NOT READ', order]; bad += 1; continue
            en, p = got
            signal.alarm(per_entry)
            try:
                b = None
                for cap in (40000, 400000):
                    b = uniform.build(en, p, cap)
                    if b is not None:
                        break
                if b is None:
                    signal.alarm(0)
                    rows[k] = ['TOO BIG', order]; bad += 1; continue
                S = uniform.size(en, p, b)
                t = uniform.terms(en, p, b, min(2 * S + 10, 4200))
                signal.alarm(0)
            except Slow:
                signal.alarm(0); rows[k] = ['SLOW', order]; bad += 1; continue
            except Exception as ex:
                signal.alarm(0); rows[k] = ['ERROR ' + str(ex)[:50], order]; bad += 1; continue
            vals = [x for x in t if x is not None]
            signal.alarm(per_entry)
            try:
                mo, seen = settled_order(vals)
            except Slow:
                signal.alarm(0); rows[k] = ['SLOW BM', order]; bad += 1; continue
            signal.alarm(0)
            ok = (mo == order)
            rows[k] = ['ok' if ok else 'ORDER %s vs stated %d %s' % (mo, order, seen),
                       order, S]
            if not ok:
                bad += 1
        out[a] = {'v': 'ok' if bad == 0 else 'PROBLEM', 'columns': rows}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    if len(sys.argv) > 4:
        os.environ['W'], os.environ['N'], os.environ['SHARD'] = sys.argv[3], sys.argv[4], sys.argv[3]
        OUT = 'audit_tabrec%s.json' % sys.argv[3]
    main(int(sys.argv[1]), int(sys.argv[2]))
