"""The check that uses NO model at all: does each paper's claim hold on the entry's own
published terms, at every index the paper says it holds and the data can test?

If a paper says "holds for all n > T" and the OEIS data itself contradicts that at some
n > T, the paper is wrong. This uses only the published integers and the published
recurrence, so no part of my machinery can hide an error here.
"""
import json, re, glob, collections
import localentry as LE, ratrec
MARK = re.compile(r'onjectur|Empirical', re.I)
res = collections.Counter(); bad = []
seen = set()
for f in sorted(glob.glob('transfer*_hits.json')):
    for h in json.load(open(f)):
        if h.get('FAILS'):
            continue
        a = h['anum']
        if a in seen:
            continue
        seen.add(a)
        thr = h.get('nthr', h.get('threshold'))
        if thr is None:
            res['no threshold recorded'] += 1; continue
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                            if MARK.search(L)) if r]
        if not recs:
            res['no recurrence'] += 1; continue
        coeffs, dd = recs[0]; order = max(coeffs)
        tested = 0; fails = []
        for n in range(max(thr + 1, off + order), off + len(d)):
            i = n - off
            if i - max(coeffs) < 0:
                continue
            tested += 1
            if d[i] != sum(c * d[i - k] for k, c in coeffs.items()):
                fails.append(n)
        if not tested:
            res['no published index available to test'] += 1
        elif fails:
            res['CONTRADICTED BY PUBLISHED DATA'] += 1
            bad.append((a, thr, fails[:4], tested))
        else:
            res['confirmed on published data'] += 1
print(dict(res))
for b in bad[:20]:
    print('  WRONG:', b)
