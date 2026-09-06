import json, re, os, collections, sys
import localentry as LE, transfer6 as T, ratrec, openness

MARK = re.compile(r'onjectur|Empirical', re.I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 4200
HITS = 'transfer6_hits.json'
DONE = 'transfer6_done.json'

names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()

cand = sorted(a for a in names if a not in done)
for a in cand:
    nm = names[a]
    if nm.strip().startswith('T(n,k)'):
        res['triangle'] += 1; done.add(a); continue
    p = T.parse_name(nm)
    if not p:
        res['name unparsed'] += 1; done.add(a); continue
    S = (p['alpha'] + 1) ** p['fixed']
    if S > CAP:
        res['state space > cap'] += 1; continue          # retry later with a bigger cap
    if a in roster:
        res['already papered'] += 1; done.add(a); continue
    op, _ = openness.status(a)
    if not op:
        res['not open'] += 1; done.add(a); continue
    e = LE.get(a)
    F = e['comment'] + e['formula']
    recs = [r for r in (ratrec.parse_rec(L) for L in F if MARK.search(L)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    st, adj = T.build(p)
    t = [x // p['frac'] for x in T.terms(adj, len(st), len(d) + 3)]
    shift = next((s for s in range(0, 4) if t[s:s + len(d)] == d), None)
    if shift is None:
        res['does not match DATA'] += 1; done.add(a); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    thr = T.threshold(adj, len(st), coeffs, order)
    off = int(e['offset'].split(',')[0])
    if thr is None:
        res['recurrence FAILS'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    else:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': nm, 'walk': p['walk'], 'fixed': p['fixed'],
                     'base': p['base'], 'alpha': p['alpha'], 'frac': p['frac'],
                     'quant': p['quant'], 'tex': p['tex'], 'body': p['body'],
                     'noadj': p['noadj'], 'S': len(st), 'order': order, 'shift': shift,
                     'offset': off, 'nterms': len(d), 'claimed': dd,
                     'coeffs': {int(k): str(v) for k, v in coeffs.items()},
                     'threshold': thr, 'nthr': thr - shift + off})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
