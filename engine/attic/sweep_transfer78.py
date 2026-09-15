import json, re, os, collections
import localentry as LE, transfer78 as T, ratrec, openness

MARK = re.compile(r'onjectur|Empirical', re.I)
HITS, DONE = 'transfer78_hits.json', 'transfer78_done.json'
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()

for a in sorted(names):
    if a in done:
        continue
    p = T.parse_name(names[a])
    if not p:
        res['name unparsed'] += 1; done.add(a); continue
    if a in roster:
        res['already papered'] += 1; done.add(a); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); continue
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); continue
    b = T.build(p)
    if b is None:
        res['too many edges for the subset sum'] += 1; continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    if T.terms(b, len(d) + 1, off)[:len(d)] != d:
        res['does not match DATA'] += 1; done.add(a); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    q, A, C = T.minimal_annihilator(b, off)
    r = [0] * (order + 1)
    r[order] = 1
    for i, c in coeffs.items():
        r[order - i] -= int(c)
    if not T.divides([int(x) for x in q], r):
        res['claim is NOT a multiple of the minimal annihilator'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': names[a]})
        done.add(a); continue
    # a direct check on the model's own values, independent of the divisibility argument
    tv = T.terms(b, order + 60, off)
    bad = [off + k for k in range(order, len(tv))
           if tv[k] != sum(int(c) * tv[k - i] for i, c in coeffs.items())]
    if bad:
        res['direct check fails'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': names[a], 'bad': bad[:3]})
        done.add(a); continue
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': names[a], 'K': p['K'], 'shift': p['shift'],
                 'T': b['T'], 'nedges': len(T.edges(p['K'])),
                 'order': order, 'offset': off, 'nterms': len(d), 'claimed': dd,
                 'nthr': off + order - 1,
                 'degA': len(A) - 1, 'degC': len(C) - 1,
                 'A': [str(x) for x in A], 'C': [str(x) for x in C],
                 'minimal': len(q) - 1,
                 'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
