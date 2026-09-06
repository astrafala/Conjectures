#!/usr/bin/env python3
"""The array papers the fast pass could not rebuild: bigger cap, longer per-entry budget."""
import json, os, re, sys, signal, collections, time
import localentry as LE, ratrec, openness, uniform

OUT = 'audit_big%s.json' % os.environ.get('SHARD','')
MARK = re.compile(r'onjectur|Empirical', re.I)
EXTRA = 45


class Slow(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(Slow()))


def main(budget_s, per_entry, cap):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    deep = json.load(open('audit_deep.json'))
    todo = sorted(a for a, v in deep.items() if v['v'] in ('TOO BIG', 'SLOW'))
    w, N = int(os.environ.get('W', 0)), int(os.environ.get('N', 1))
    todo = [a for i, a in enumerate(todo) if i % N == w]
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget_s:
            continue
        e = LE.get(a)
        got = uniform.read(e['name'])
        if not got:
            out[a] = {'v': 'NOT AN ARRAY MODEL'}; continue
        en, p = got
        recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                            if MARK.search(L)) if r]
        if not recs:
            out[a] = {'v': 'NO RECURRENCE ON ENTRY'}; continue
        coeffs, dd = recs[0]
        order = max(coeffs)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        op, _ = openness.status(a)
        signal.alarm(per_entry)
        try:
            b = uniform.build(en, p, cap)
            signal.alarm(0)
            if b is None:
                out[a] = {'v': 'STILL TOO BIG', 'engine': en}; continue
            signal.alarm(per_entry)
            vals = uniform.terms(en, p, b, off + len(d) + EXTRA)
            signal.alarm(0)
        except Slow:
            signal.alarm(0)
            out[a] = {'v': 'STILL SLOW', 'engine': en}; continue
        except Exception as ex:
            signal.alarm(0)
            out[a] = {'v': 'ERROR', 'engine': en, 'err': str(ex)[:90]}; continue
        g = [None if (v is None or v.denominator != 1) else v.numerator for v in vals]
        shift = None
        for s in range(0, min(8, max(1, len(g) - len(d)))):
            if g[s:s + len(d)] == d:
                shift = s; break
        datok = shift is not None
        bad = []
        if datok:
            seq = g[shift:]
            lo = max(order, (int(dd) + 1 - off) if dd is not None else 0)
            for i in range(lo, len(seq)):
                if seq[i] is None or any(seq[i - k] is None for k in coeffs):
                    continue
                if seq[i] != sum(c * seq[i - k] for k, c in coeffs.items()):
                    bad.append(off + i)
        prefix = bad and bad == list(range(bad[0], bad[0] + len(bad)))
        out[a] = {'v': ('ok' if (datok and (not bad or prefix)) else 'PROBLEM'),
                  'data_ok': datok, 'rec_bad_at': bad[:6], 'prefix_only': bool(prefix),
                  'nterms': len(d), 'order': order, 'open': op, 'engine': en,
                  'S': uniform.size(en, p, b)}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    if len(sys.argv) > 4:
        os.environ['W'], os.environ['N'], os.environ['SHARD'] = sys.argv[4], sys.argv[5], sys.argv[4]
        OUT = 'audit_big%s.json' % sys.argv[4]
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
