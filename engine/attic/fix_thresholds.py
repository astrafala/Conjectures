"""Recompute the threshold of every transfer4 and transfer5 paper in the ENTRY'S index.

Those two engines store the threshold as a WALK index. Their model prepends the single-line
count, so the entry's index n and the walk index j are related by n = j + 2 (transfer4) and
n = j + 1 (transfer5), and the builders printed the walk index as if it were n. The printed
range was therefore too large: for 477 of the 1284 papers the OEIS data itself contradicts
the printed claim.

Rather than adding the constant, the true onset is recomputed from the model's own terms --
the largest index at which the recurrence actually fails, or one below the first index at
which it can be stated. That is both correct and tight.
"""
import json, re, collections
import localentry as LE, ratrec
import transfer2 as T2, transfer4 as T4, transfer5 as T5
MARK = re.compile(r'onjectur|Empirical', re.I)
NB = {8: T5.KING, 6: T5.HDA, 4: T5.HV}
res = collections.Counter()

for fname, kind in (('transfer4_hits.json', 4), ('transfer5_hits.json', 5)):
    hits = json.load(open(fname))
    for h in hits:
        if h.get('FAILS'):
            continue
        a = h['anum']; e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                            if MARK.search(L)) if r]
        if not recs:
            res['no rec'] += 1; continue
        coeffs, dd = recs[0]; order = max(coeffs)
        N = len(d) + 40
        if kind == 4:
            st, adj = T4.build(h['K'], h['alpha'], [tuple(x) for x in h['H']],
                               [tuple(x) for x in h['V']], h['L'])
            model = [h['nrows']] + T2.terms(adj, len(st), N)
        else:
            st, adj, start, end = T5.build(h['K'], h['alpha'], h['same'], h['counts'],
                                           NB[h['nb']], h['ul0'])
            one = T5.one_row(h['K'], h['alpha'], h['same'], h['counts'], NB[h['nb']], h['ul0'])
            model = [one] + T5.terms(adj, start, end, N)
        if model[:len(d)] != d:
            res['DATA MISMATCH'] += 1; continue      # model[i] = a(off+i)
        first = off + order
        worst = first - 1
        for n in range(first, off + len(model)):
            i = n - off
            if i >= len(model) or i - order < 0:
                continue
            if model[i] != sum(c * model[i - k] for k, c in coeffs.items()):
                worst = n
        old = h['threshold']
        h['threshold_walk_index'] = old
        h['threshold'] = worst
        if worst != old:
            res['corrected'] += 1
        else:
            res['already right'] += 1
        res['shift %+d' % (worst - old)] += 1
    json.dump(hits, open(fname, 'w'), indent=1)
print(dict(res))
