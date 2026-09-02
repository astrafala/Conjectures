"""Entries that state only the ORDER of their empirical recurrence, the recurrence itself
being in a linked file the local copy does not carry."""
import json, re, os, sys, collections, signal
from fractions import Fraction
import localentry as LE, openness, uniform, bmrec


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '45'))
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 600
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = 'ord_hits.json', 'ord_done.json'
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
ORD = re.compile(r'Empirical recurrence of order (\d+)', re.I)
P62 = (1 << 61) - 1


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


for a in sorted(names):
    if a in done or a in roster:
        continue
    nm = names[a]
    e = LE.get(a)
    stated = None
    for L in e['comment'] + e['formula']:
        m = ORD.search(L)
        if m:
            stated = int(m.group(1)); line = L.strip(); break
    if stated is None:
        continue
    got = uniform.read(nm)
    if not got:
        res['no engine reads the name'] += 1; done.add(a); save(); continue
    en, p = got
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['build failed'] += 1; done.add(a); save(); continue
    if b is None:
        res['state space > cap'] += 1; done.add(a); save(); continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    N = 2 * S + 6
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, max(N, len(d) + off + 4))
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['terms timed out'] += 1; done.add(a); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); save(); continue
    seq = [v for v in tv[sh:sh + N] if v is not None]
    if len(seq) < 2 * S + 2:
        res['not enough terms'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(BUDGET)
        Lm = bmrec.bm_mod([v % P62 for v in seq], P62)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['filter failed'] += 1; done.add(a); save(); continue
    if Lm != stated:
        res['minimal order %s the stated one' % ('below' if Lm < stated else 'above')] += 1
        done.add(a); save(); continue
    try:
        signal.alarm(4 * BUDGET)
        Lx, cs = bmrec.bm([Fraction(v) for v in seq])
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['exact BM timed out'] += 1; done.add(a); save(); continue
    if Lx != stated or any(c.denominator != 1 for c in cs):
        res['exact run disagrees with the filter'] += 1; done.add(a); save(); continue
    # the recurrence must reproduce the entry's own published terms
    bad = [off + k for k in range(len(d))
           if k - Lx >= 0 and d[k] != sum(int(c) * d[k - i - 1] for i, c in enumerate(cs))]
    if bad:
        res['contradicted by DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
    else:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': nm, 'engine': en, 'S': S, 'order': Lx,
                     'stated': stated, 'offset': off, 'shift': sh, 'nterms': len(d),
                     'line': line, 'coeffs': {i + 1: str(int(c)) for i, c in enumerate(cs)}})
        print('done', a, 'order', Lx, res['PROVED'], flush=True)
    done.add(a); save()
save()
print(dict(res))
