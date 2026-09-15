"""Adversarial test of the ONE gate everything rests on: the DATA comparison.

For each sampled paper the model is deliberately corrupted -- a neighbour dropped, a count
set shifted, a comparison flipped, the alphabet changed -- and the corrupted model is then
asked to reproduce the entry's published terms. If corrupted readings still match, the gate
is worthless and every paper resting on it is unsupported.
"""
import json, random, copy, collections
from math import factorial
import localentry as LE, transfer9 as T9

names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
hits = [h for h in json.load(open('transfer9_hits.json')) if not h.get('FAILS')]
random.seed(20260901)
random.shuffle(hits)


def evaluate(p, d, off):
    try:
        b = T9.build(p, cap=20000)
    except Exception:
        return None                       # a corrupted model that cannot even be built
                                          # counts as rejected, not as a survivor
    if b is None:
        return None
    adj, start, end, st = b
    try:
        v = T9.avals(adj, start, end, p, off + len(d) + 1)
    except Exception:
        return None
    got = [None if x is None else x // p['frac'] for x in v]
    return got[off:off + len(d)] == d


def mutants(p):
    out = []
    if len(p['offs']) > 1:                      # drop one neighbour direction
        q = dict(p); q['offs'] = p['offs'][:-1]; out.append(('drop a neighbour', q))
    q = dict(p); q['offs'] = p['offs'] + [(0, 2)]      # add a spurious neighbour
    out.append(('add a neighbour', q))
    if p['mode'] == 'count' and p.get('set'):
        q = dict(p); q['set'] = [x + 1 for x in p['set']]
        out.append(('shift the count set by 1', q))
    if p['mode'] == 'value':
        q = dict(p); q['set'] = [x + 1 for x in p['set']]
        out.append(('shift the count set by 1', q))
        q2 = dict(p); q2['val'] = (p['val'] + 1) % (p['alpha'] + 1)
        out.append(('change which value is constrained', q2))
    if p['mode'] == 'table':
        q = dict(p); t = list(p['tbl']); t[0] = (t[0] + 1) % (p['alpha'] + 1)
        q['tbl'] = t; out.append(('change one entry of the table', q))
    if p['mode'] == 'count':
        q = dict(p); q['uneq'] = not p.get('uneq')
        out.append(('flip equal/unequal', q))
    if p['mode'] not in ('table',):        # the table is indexed by the alphabet
        q = dict(p); q['alpha'] = p['alpha'] + 1
        out.append(('widen the alphabet by one', q))
    return out


res = collections.Counter()
survivors = []
n = 0
for h in hits:
    if n >= 60:
        break
    a = h['anum']
    e = LE.get(a)
    p = T9.parse_name(e['name'])
    if not p or p.get('mode') is None:
        continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    base = evaluate(p, d, off)
    if base is not True:
        continue                                # only test where the true model passes
    n += 1
    res['true model accepted'] += 1
    for label, q in mutants(p):
        r = evaluate(q, d, off)
        if r is None:
            continue
        res['mutant ' + ('ACCEPTED (gate failed)' if r else 'rejected')] += 1
        if r:
            survivors.append((a, label, e['name'][:80]))
print(dict(res))
for s in survivors[:15]:
    print('  MUTANT SURVIVED:', s)
