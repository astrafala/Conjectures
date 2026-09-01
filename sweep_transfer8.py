import json, re, os, collections, sys
from math import factorial
import localentry as LE, transfer8 as T8, ratrec, openness

MARK = re.compile(r'onjectur|Empirical', re.I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
HITS, DONE = 'transfer8_hits.json', 'transfer8_done.json'
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()

for a in sorted(names):
    if a in done:
        continue
    nm = names[a]
    if nm.strip().startswith('T(n,k)'):
        res['triangle'] += 1; done.add(a); continue
    p = T8.parse_name(nm)
    if not p:
        res['name unparsed'] += 1; done.add(a); continue
    S = sum(T8.npatterns(2 * p['fixed'], i) for i in range(1, p['K'] + 1))
    if S > CAP or p['K'] ** p['fixed'] > 200000:
        res['state space > cap'] += 1; continue
    if a in roster:
        res['already papered'] += 1; done.add(a); continue
    op, _ = openness.status(a)
    if not op:
        res['not open'] += 1; done.add(a); continue
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    built = T8.build(p)
    if built is None:
        res['state space > cap'] += 1; continue
    adj, start, end, plist = built
    f = factorial(p['K']) * p['frac']
    v = T8.avals(adj, start, end, p, off + len(d) + 1)
    got = [None if v[off + k] is None or v[off + k] % f else v[off + k] // f
           for k in range(len(d))]
    if got != d:
        res['does not match DATA'] += 1; done.add(a); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    thr = T8.threshold(adj, start, end, coeffs, order, p)
    if thr is None:
        res['UNRESOLVED within the iteration budget'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    else:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': nm, 'walk': p['walk'], 'fixed': p['fixed'],
                     'base': p['base'], 'mult': p['mult'], 'alpha': p['alpha'],
                     'K': p['K'], 'frac': p['frac'], 'S': len(adj),
                     'raw': sum(i ** (2 * p['fixed']) for i in range(1, p['K'] + 1)),
                     'order': order, 'offset': off, 'nterms': len(d), 'claimed': dd,
                     'coeffs': {int(k): str(vv) for k, vv in coeffs.items()},
                     'nthr': thr, 'ckind': p['kind'], 'tex': p['tex'], 'rest': p['rest']})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
