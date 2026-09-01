"""Independent re-check of the FIVE older array families (transfer2,3,4,5 and transfer6).

Each is rebuilt from its own stored parameters, the sequence recomputed, compared against
every published DATA term, and the conjectured recurrence evaluated NUMERICALLY beyond the
proved threshold -- which is independent of the annihilation argument that produced the paper.
"""
import json, re, collections
import localentry as LE, ratrec, openness
import transfer2 as T2, transfer3 as T3, transfer4 as T4, transfer5 as T5, transfer6 as T6

# the sweep stored only the SIZE of the neighbourhood, so map it back
NB = {8: T5.KING, 6: T5.HDA, 4: T5.HV}

MARK = re.compile(r'onjectur|Empirical', re.I)
EXTRA = 45
res = collections.Counter()
bad = []


def check(a, terms_fn, thr, off_expected=None):
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        return 'NO RECURRENCE', None
    coeffs, dd = recs[0]
    order = max(coeffs)
    t = terms_fn(len(d) + EXTRA + 6)
    shift = next((s for s in range(0, 5) if t[s:s + len(d)] == d), None)
    if shift is None:
        return 'DATA MISMATCH', None
    lo = max(order, (thr or 0) + 1 - off + shift)
    if dd is not None:
        lo = max(lo, int(dd) + 1 - off + shift)
    bad_at = [j for j in range(lo, len(t))
              if all(j - i >= 0 for i in coeffs)
              and t[j] != sum(c * t[j - i] for i, c in coeffs.items())]
    op, _ = openness.status(a)
    return ('ok' if not bad_at else 'RECURRENCE FAILS'), {'bad': bad_at[:5], 'open': op,
                                                          'nterms': len(d)}


for h in json.load(open('transfer_hits.json')):
    if h.get('FAILS'):
        continue
    st, adj = T2.build(h['cols'], h['alpha'], h['sums'], h['extra'])
    v, info = check(h['anum'], lambda N: T2.terms(adj, len(st), N), h.get('threshold'))
    res['t2 ' + v] += 1
    if v != 'ok':
        bad.append(('t2', h['anum'], v, info))
        print('PROBLEM t2', h['anum'], v, info, flush=True)

print('t2 done', dict(res), flush=True)
for h in json.load(open('transfer3_hits.json')):
    if h.get('FAILS'):
        continue
    st, adj = T3.build(h['cols'], h['alpha'], h['c'], h['noadj'])
    v, info = check(h['anum'], lambda N: T2.terms(adj, len(st), N), h.get('threshold'))
    res['t3 ' + v] += 1
    if v != 'ok':
        bad.append(('t3', h['anum'], v, info))
        print('PROBLEM t3', h['anum'], v, info, flush=True)

print('t3 done', dict(res), flush=True)
for h in json.load(open('transfer4_hits.json')):
    if h.get('FAILS'):
        continue
    st, adj = T4.build(h['K'], h['alpha'], [tuple(x) for x in h['H']],
                       [tuple(x) for x in h['V']], h['L'])
    # the single-row count is prepended: the walk states already hold one row, so the walk
    # itself starts at TWO rows. Rebuilding without it puts the model one index ahead.
    v, info = check(h['anum'],
                    lambda N: [h['nrows']] + T2.terms(adj, len(st), N), h.get('threshold'))
    res['t4 ' + v] += 1
    if v != 'ok':
        bad.append(('t4', h['anum'], v, info))
        print('PROBLEM t4', h['anum'], v, info, flush=True)

print('t4 done', dict(res), flush=True)
for h in json.load(open('transfer5_hits.json')):
    if h.get('FAILS'):
        continue
    st, adj, start, end = T5.build(h['K'], h['alpha'], h['same'],
                                   h['counts'], NB[h['nb']], h['ul0'])
    one = T5.one_row(h['K'], h['alpha'], h['same'], h['counts'], NB[h['nb']], h['ul0'])
    v, info = check(h['anum'],
                    lambda N: [one] + T5.terms(adj, start, end, N), h.get('threshold'))
    res['t5 ' + v] += 1
    if v != 'ok':
        bad.append(('t5', h['anum'], v, info))
        print('PROBLEM t5', h['anum'], v, info, flush=True)

print(dict(res))
for b in bad[:25]:
    print('PROBLEM', b)
json.dump(bad, open('audit_old_bad.json', 'w'), indent=1)
