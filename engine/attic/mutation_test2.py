"""Were the surviving mutants genuinely DIFFERENT models, or vacuous edits?

A mutation that changes nothing about the counted set is not evidence that the DATA gate is
weak. So each survivor is compared against the true model over forty terms BEYOND the
published data: if the two sequences agree everywhere, the mutation was vacuous (an offset
that falls outside the array, a relabelling symmetry, a complement that maps the condition to
itself). If they diverge past the data, the gate genuinely failed to tell them apart.
"""
import json, random, collections
import localentry as LE, transfer9 as T9

random.seed(20260901)
hits = [h for h in json.load(open('transfer9_hits.json')) if not h.get('FAILS')]
random.shuffle(hits)


def series(p, N):
    try:
        b = T9.build(p, cap=20000)
        if b is None:
            return None
        adj, start, end, st = b
        v = T9.avals(adj, start, end, p, N)
    except Exception:
        return None
    return [None if x is None else x // p['frac'] for x in v]


def mutants(p):
    out = []
    if len(p['offs']) > 1:
        q = dict(p); q['offs'] = p['offs'][:-1]; out.append(('drop a neighbour', q))
    q = dict(p); q['offs'] = p['offs'] + [(0, 2)]
    out.append(('add a neighbour', q))
    if p['mode'] in ('count', 'value') and p.get('set'):
        q = dict(p); q['set'] = [x + 1 for x in p['set']]
        out.append(('shift the count set by 1', q))
    if p['mode'] == 'value':
        q = dict(p); q['val'] = (p['val'] + 1) % (p['alpha'] + 1)
        out.append(('change which value is constrained', q))
    if p['mode'] == 'table':
        q = dict(p); t = list(p['tbl']); t[0] = (t[0] + 1) % (p['alpha'] + 1)
        q['tbl'] = t; out.append(('change one entry of the table', q))
    if p['mode'] == 'count':
        q = dict(p); q['uneq'] = not p.get('uneq')
        out.append(('flip equal/unequal', q))
    if p['mode'] != 'table':
        q = dict(p); q['alpha'] = p['alpha'] + 1
        out.append(('widen the alphabet by one', q))
    return out


res = collections.Counter(); real = []
n = 0
for h in hits:
    if n >= 60:
        break
    a = h['anum']; e = LE.get(a)
    p = T9.parse_name(e['name'])
    if not p:
        continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    N = off + len(d) + 40
    base = series(p, N)
    if base is None or base[off:off + len(d)] != d:
        continue
    n += 1
    for label, q in mutants(p):
        m = series(q, N)
        if m is None:
            res['mutant unbuildable -> rejected'] += 1; continue
        if m[off:off + len(d)] != d:
            res['mutant REJECTED by the DATA gate'] += 1; continue
        # it passed the gate: is it the same sequence, or did the gate genuinely miss it?
        if m[:N] == base[:N]:
            res['passed, but VACUOUS (identical model)'] += 1
        else:
            res['passed and GENUINELY DIFFERENT (gate failed)'] += 1
            j = next(i for i in range(len(base)) if base[i] != m[i])
            real.append((a, label, j, e['name'][:75]))
print(dict(res))
for r in real[:20]:
    print('  REAL GATE FAILURE:', r)
