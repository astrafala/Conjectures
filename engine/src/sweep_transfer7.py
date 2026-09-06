import json, re, os, collections, sys
from math import factorial
import localentry as LE, transfer7 as T7, ratrec, openness

MARK = re.compile(r'onjectur|Empirical', re.I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
HITS, DONE = 'transfer7_hits.json', 'transfer7_done.json'
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
    kind, p = 'sub', T7.parse_name(nm)
    if not p:
        kind, p = 'nb', T7.parse_nb(nm)
    if not p:
        res['name unparsed'] += 1; done.add(a); continue
    raw = sum(i ** p['fixed'] for i in range(1, p['K'] + 1))
    S = sum(T7.npatterns(p['fixed'], i) for i in range(1, p['K'] + 1))
    if S > CAP or raw > 400000:
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
    adj, start, plist = T7.build_lumped(p, kind)
    t = T7.lterms(adj, start, len(d) + 3, p, kind)
    f = factorial(p['K']) * p['frac']
    t = [x // f if x % f == 0 else None for x in t]
    shift = next((s for s in range(0, 4) if t[s:s + len(d)] == d), None)
    if shift is None:
        res['does not match DATA'] += 1; done.add(a); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    thr = T7.lthreshold(adj, start, coeffs, order, p, kind)
    off = int(e['offset'].split(',')[0])
    if thr is None:
        res['recurrence FAILS'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    else:
        res['PROVED'] += 1
        rec = {'anum': a, 'name': nm, 'kind': kind, 'walk': p['walk'], 'fixed': p['fixed'],
               'base': p['base'], 'alpha': p['alpha'], 'K': p['K'], 'frac': p['frac'],
               'S': len(adj), 'raw': raw, 'order': order, 'shift': shift, 'offset': off,
               'nterms': len(d), 'claimed': dd, 'threshold': thr, 'nthr': thr - shift + off,
               'coeffs': {int(k): str(v) for k, v in coeffs.items()},
               'tex': p.get('tex', ''), 'body': p.get('body', ''),
               'noadj': p.get('noadj', False), 'quant': p.get('quant', 'every')}
        if kind == 'nb':
            rec['offs'] = p['offs']; rec['lim'] = p['lim']; rec['nbtex'] = p['nbtex']
        hits.append(rec)
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
