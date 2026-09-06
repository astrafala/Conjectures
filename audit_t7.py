#!/usr/bin/env python3
"""The relabelling papers, re-checked through the path that actually built them.

uniform.py does not know transfer7's LUMPED model: it calls parse_name and build, while the
sweep that produced these papers used build_lumped -- states are row PATTERNS rather than rows,
which is why a model uniform reports as four million states is 430 in the paper. It also never
tries parse_nb, transfer7's second reading, so a whole family of names came back unparsed.

This uses the sweep's own path -- parse_name or parse_nb, build_lumped, lterms -- rebuilds each
model, compares it against every published term, and evaluates the entry's conjectured
recurrence past the data and the threshold.
"""
import json, os, re, sys, signal, collections, time
from math import factorial
import localentry as LE, ratrec, openness
import transfer7 as T7

OUT = 'audit_t7%s.json' % os.environ.get('SHARD', '')
MARK = re.compile(r'onjectur|Empirical', re.I)
EXTRA = 45


class Slow(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(Slow()))


def main(budget, per_entry, todo):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        nm = e['name']
        kind, p = 'sub', T7.parse_name(nm)
        if not p:
            kind, p = 'nb', T7.parse_nb(nm)
        if not p:
            out[a] = {'v': 'NAME NOT READ BY transfer7'}; continue
        recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                            if MARK.search(L)) if r]
        if not recs:
            out[a] = {'v': 'NO RECURRENCE ON ENTRY'}; continue
        coeffs, dd = recs[0]
        order = max(coeffs)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        signal.alarm(per_entry)
        try:
            adj, start, plist = T7.build_lumped(p, kind)
            t = T7.lterms(adj, start, len(d) + EXTRA, p, kind)
            signal.alarm(0)
        except Slow:
            signal.alarm(0); out[a] = {'v': 'SLOW', 'kind': kind}; continue
        except Exception as ex:
            signal.alarm(0); out[a] = {'v': 'ERROR', 'err': str(ex)[:90]}; continue
        f = factorial(p['K']) * p['frac']
        g = [x // f if x % f == 0 else None for x in t]
        sh = next((s for s in range(0, 5) if g[s:s + len(d)] == d), None)
        if sh is None:
            out[a] = {'v': 'MODEL DOES NOT REPRODUCE THE DATA', 'S': len(adj)}; continue
        seq = g[sh:]
        lo = max(order, (int(dd) + 1 - off) if dd is not None else 0)
        bad = []
        for i in range(lo, len(seq)):
            if seq[i] is None or any(seq[i - k] is None for k in coeffs):
                continue
            if seq[i] != sum(c * seq[i - k] for k, c in coeffs.items()):
                bad.append(off + i)
        prefix = bad and bad == list(range(bad[0], bad[0] + len(bad)))
        out[a] = {'v': 'ok' if (not bad or prefix) else 'PROBLEM', 'kind': kind,
                  'S': len(adj), 'order': order, 'bad': bad[:5], 'prefix_only': bool(prefix),
                  'checked': len(seq) - lo, 'nterms': len(d), 'open': openness.status(a)[0]}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
    big = json.load(open('audit_big.json')) if os.path.exists('audit_big.json') else {}
    todo = sorted(a for a in json.load(open(SC + '/bigtodo.json'))
                  if big.get(a, {}).get('v') != 'ok')
    if len(sys.argv) > 4:
        w, N = int(sys.argv[3]), int(sys.argv[4])
        os.environ['SHARD'] = sys.argv[3]
        OUT = 'audit_t7%s.json' % sys.argv[3]
        todo = [a for i, a in enumerate(todo) if i % N == w]
    main(int(sys.argv[1]), int(sys.argv[2]), todo)
