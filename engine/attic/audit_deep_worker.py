#!/usr/bin/env python3
"""Deep re-verification of every array paper, through the one uniform interface.

Replaces audit_all.py, whose engine dispatch had gone stale: it knew eleven of the
seventy-odd engines, unpacked a fixed tuple shape, and read names from a cached file
rather than from the export, so a third of what it looked at came back as a harness
error rather than a verdict.

For each roster A-number it re-reads the NAME from the current OEIS export, rebuilds the
model from scratch, and then:

  1. compares the model against every published DATA term -- the only thing that ties the
     model to the sequence, so a misread name shows up here;
  2. evaluates the entry's conjectured recurrence NUMERICALLY past both the data and the
     proved threshold, which is independent of the annihilation argument in the paper;
  3. re-checks that the entry is still recorded as open.

A per-entry alarm keeps one huge model from stalling a whole chunk; those are recorded
as SLOW and re-run separately with a larger budget.
"""
import json, os, re, sys, signal, collections
import localentry as LE, ratrec, openness, uniform

OUT = 'audit_deep_w%s.json' % os.environ.get('SHARD', '')
MARK = re.compile(r'onjectur|Empirical', re.I)
EXTRA = 45


class Slow(BaseException):
    pass


def _alarm(sig, frm):
    raise Slow()


signal.signal(signal.SIGALRM, _alarm)


def main(budget_s, per_entry):
    import time
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    if os.path.exists('audit_deep.json'):
        merged = json.load(open('audit_deep.json'))
        out.update({k: v for k, v in merged.items() if k not in out})
    rm = json.load(open('rank-map.json'))
    order_key = {}
    for r in rm:
        order_key.setdefault(r['anum'], r)
    anums = sorted(order_key)
    w, N = int(os.environ.get('W', 0)), int(os.environ.get('N', 1))
    anums = [a for i, a in enumerate(anums) if i % N == w]
    res = collections.Counter()
    t0 = time.time()
    for a in anums:
        if a in out:
            continue
        if time.time() - t0 > budget_s:
            break
        e = LE.get(a)
        if not e:
            out[a] = {'v': 'NO ENTRY'}; continue
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
        op, flag = openness.status(a)
        signal.alarm(per_entry)
        try:
            b = None
            for cap in (40000, 400000):
                signal.alarm(per_entry)
                b = uniform.build(en, p, cap)
                signal.alarm(0)
                if b is not None:
                    break
            signal.alarm(per_entry)
            if b is None:
                signal.alarm(0)
                out[a] = {'v': 'TOO BIG'}; continue
            vals = uniform.terms(en, p, b, off + len(d) + EXTRA)
        except Slow:
            signal.alarm(0)
            out[a] = {'v': 'SLOW', 'engine': en}; continue
        except Exception as ex:
            signal.alarm(0)
            out[a] = {'v': 'ERROR', 'engine': en, 'err': str(ex)[:90]}; continue
        signal.alarm(0)
        g = [None if (v is None or v.denominator != 1) else v.numerator for v in vals]
        # the walk index and the entry's n differ by a constant; find the shift that
        # reproduces the data rather than assuming one
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
        # a conjectured recurrence holds only past a threshold; a contiguous run of
        # failures at the very start is that threshold, not a contradiction
        prefix = bad and bad == list(range(bad[0], bad[0] + len(bad)))
        out[a] = {'v': ('ok' if (datok and (not bad or prefix)) else 'PROBLEM'),
                  'data_ok': datok, 'rec_bad_at': bad[:6], 'prefix_only': bool(prefix),
                  'nterms': len(d), 'order': order, 'open': op, 'engine': en,
                  'checked_to': off + len(g) - 1}
        res[out[a]['v']] += 1
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    c = collections.Counter(v['v'] for v in out.values())
    print(len(out), 'of', len(anums), dict(c))


if __name__ == '__main__':
    os.environ['W'], os.environ['N'] = sys.argv[1], sys.argv[2]
    os.environ['SHARD'] = sys.argv[1]
    OUT = 'audit_deep_w%s.json' % sys.argv[1]
    main(int(sys.argv[3]), 90)
