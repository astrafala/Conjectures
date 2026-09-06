#!/usr/bin/env python3
"""Re-check the papers that recovered a conjecture the entry does not write down.

These are the riskiest results in the roster: the entry says only "Empirical recurrence of
order 99", with the recurrence itself in a linked file, and the paper reconstructs it. The
argument is that the count is a walk count on S states, so Berlekamp-Massey on 2S exact terms
returns the MINIMAL recurrence; if its order equals the order the entry states, then any
recurrence of that order the sequence satisfies has the same characteristic polynomial, so the
entry's unreadable line is the recovered one.

What is checked here is the load-bearing step: rebuild the model, recompute the minimal
recurrence from scratch, and confirm its order is exactly the order the entry states. A
mismatch would break the uniqueness argument and the paper with it.
"""
import json, os, re, sys, signal, collections, time
import localentry as LE, uniform, bmrec

OUT = 'audit_recover%s.json' % os.environ.get('SHARD', '')
ORD = re.compile(r'\[?order\s+(\d+)\]?', re.I)


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


def stated_orders(e):
    # a table entry writes the order on a continuation line -- "k=2: [order 46]" -- which
    # carries no Empirical marker of its own, so every comment and formula line is read
    out = []
    for L in e['comment'] + e['formula']:
        out += [int(m) for m in ORD.findall(L)]
    return sorted(set(out))


def main(budget, per_entry):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    rm = json.load(open('rank-map.json'))
    todo = sorted({r['anum'] for r in rm
                   if r['engine'] in ('order-recovery', 'table-order-recovery')})
    w, N = int(os.environ.get('W', 0)), int(os.environ.get('N', 1))
    todo = [a for i, a in enumerate(todo) if i % N == w]
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        orders = stated_orders(e)
        if not orders:
            out[a] = {'v': 'NO ORDER STATED'}; continue
        got = uniform.read(e['name'])
        if not got:
            out[a] = {'v': 'NOT AN ARRAY MODEL', 'orders': orders}; continue
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
                out[a] = {'v': 'TOO BIG', 'engine': en}; continue
            S = uniform.size(en, p, b)
            t = uniform.terms(en, p, b, min(2 * S + 10, 4200))
            signal.alarm(0)
        except Slow:
            signal.alarm(0)
            out[a] = {'v': 'SLOW', 'engine': en}; continue
        except Exception as ex:
            signal.alarm(0)
            out[a] = {'v': 'ERROR', 'engine': en, 'err': str(ex)[:80]}; continue
        vals = [x for x in t if x is not None]
        # the walk index and the entry's n differ by a constant: the model counts the empty
        # array and the one-row arrays, which the entry does not publish, and one unpublished
        # leading term raises the minimal order by one. Line the two up on the DATA, then take
        # the minimal recurrence of that tail -- which is what the paper's argument is about.
        signal.alarm(per_entry)
        try:
            mo, seen = settled_order(vals)
        except Slow:
            signal.alarm(0)
            out[a] = {'v': 'SLOW MINREC', 'S': S}; continue
        except Exception as ex:
            signal.alarm(0)
            out[a] = {'v': 'MINREC ERROR', 'err': str(ex)[:80]}; continue
        signal.alarm(0)
        out[a] = {'v': 'ok' if mo in orders else 'ORDER MISMATCH',
                  'settled_order': mo, 'by_tail': seen, 'stated_orders': orders, 'S': S,
                  'terms_used': len(vals), 'engine': en}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    if len(sys.argv) > 4:
        os.environ['W'], os.environ['N'], os.environ['SHARD'] = sys.argv[3], sys.argv[4], sys.argv[3]
        OUT = 'audit_recover%s.json' % sys.argv[3]
    main(int(sys.argv[1]), int(sys.argv[2]))
