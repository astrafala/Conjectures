import json, re, os, collections, sys
import localentry as LE, transfer77 as T, ratrec, openness

MARK = re.compile(r'onjectur|Empirical', re.I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
HITS, DONE = 'transfer77_hits.json', 'transfer77_done.json'
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()

for a in sorted(names):
    if a in done:
        continue
    nm = names[a]
    if nm.strip().startswith('T(n,k)'):
        res['triangle'] += 1; done.add(a); continue
    p = T.parse_name(nm)
    if not p:
        res['name unparsed'] += 1; done.add(a); continue
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
    built = T.build(p, cap=CAP)
    if built is None:
        res['state space > cap'] += 1; continue
    adj, start, end, S = built
    tv = T.terms(adj, start, end, len(d) + off + 4)
    # the walk index j carries an array of j+1 lines; the entry's own offset says which index
    # its first published term has, and the shift is fixed by the data, not fitted per entry
    sh = 1 - off
    got = tv[sh:sh + len(d)] if sh >= 0 else None
    if got != d:
        res['does not match DATA'] += 1; done.add(a); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    thr = T.threshold(adj, start, end, coeffs, order, S)
    if thr is None:
        res['UNRESOLVED within the iteration budget'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    else:
        nthr = thr + off - sh
        bad = [off + k for k in range(len(d))
               if off + k > nthr and off + k - order >= off and
               d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
        if bad:
            res['claim contradicted by DATA'] += 1
            hits.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
        else:
            res['PROVED'] += 1
            hits.append({'anum': a, 'name': nm, 'R': p['R'], 'alpha': p['alpha'],
                         'dirs': p['dirs'],
                         'prec': p['prec'], 'S': S, 'order': order, 'offset': off,
                         'shift': sh, 'nterms': len(d), 'claimed': dd, 'nthr': nthr,
                         'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
