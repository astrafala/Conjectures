"""Sweep the constant-stress family. Saves after every item so a restart resumes."""
import json, re, os, collections
import localentry as LE, transfer3 as T3, transfer2 as T, ratrec, openness

OUT = 'transfer3_hits.json'
DONE = 'transfer3_done.json'
MARK = re.compile(r'onjectur|Empirical', re.I)

hits = json.load(open(OUT)) if os.path.exists(OUT) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()

fam = json.load(open('hardin_families.json'))['subblock sum <= / >=']
sel = [a for a in fam if 'diagonal sum differing from its antidiago' in LE.get(a)['name']]
print('candidates:', len(sel), ' already done:', len(done), flush=True)

def save():
    json.dump(hits, open(OUT, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))

res = collections.Counter()
for a in sel:
    if a in done:
        continue
    e = LE.get(a); nm = e['name']
    p = T3.parse_name(nm)
    if not p:
        res['name unparsed/square'] += 1; done.add(a); save(); continue
    cols, alpha, c, noadj = p
    if (alpha + 1) ** cols > 20000:
        res['state space > 20000'] += 1; done.add(a); save(); continue
    op, _ = openness.status(a)
    if not op:
        res['not open'] += 1; done.add(a); save(); continue
    F = e['comment'] + e['formula']
    recs = [r for r in (ratrec.parse_rec(L) for L in F if MARK.search(L)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    st, adj = T3.build(cols, alpha, c, noadj)
    if not st:
        res['empty state space'] += 1; done.add(a); save(); continue
    t = T.terms(adj, len(st), len(d) + 3)
    shift = next((s for s in range(0, 3) if t[s:s + len(d)] == d), None)
    if shift is None:
        res['transfer does not match DATA'] += 1; done.add(a); save(); continue
    coeffs, dd = recs[0]; order = max(coeffs)
    thr = T.threshold(adj, len(st), coeffs, order)
    if thr is not None:
        res['PROVED'] += 1
        hits.append({'anum': a, 'cols': cols, 'alpha': alpha, 'c': c, 'noadj': noadj,
                     'S': len(st), 'coeffs': {int(k): str(v) for k, v in coeffs.items()},
                     'order': order, 'shift': shift, 'nterms': len(d), 'name': nm,
                     'threshold': thr, 'claimed': dd})
    else:
        res['recurrence FAILS'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    done.add(a); save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
print('PROVED entries:', sum(1 for h in hits if not h.get('FAILS')))
