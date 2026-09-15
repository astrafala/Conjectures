import json, re, os, collections
import localentry as LE, transfer79 as T, openness

HITS, DONE = 'transfer79_hits.json', 'transfer79_done.json'
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
    P, Q = p['P'], p['Q']
    e = LE.get(a)
    src = e['comment'] + e['formula']
    emp = next((L for L in src if re.search(r'\(empirical\)', L, re.I)), None)
    gf = next((L for L in src if re.search(r'\(conjecture\)\s*G\.f\.', L, re.I)), None)
    if not emp and not gf:
        res['nothing conjectural to settle'] += 1; done.add(a); continue
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    off = int(e['offset'].split(',')[0])
    if T.terms(P, Q, len(d) + 1, off)[:len(d)] != d:
        res['does not match DATA'] += 1; done.add(a); continue
    okid, pts = T.identity_holds(P, Q)
    if emp and not okid:
        res['the entry product is NOT the box count'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': names[a], 'bad': pts})
        done.add(a); continue
    dn, dd = T.degrees(P, Q)
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': names[a], 'P': P, 'Q': Q, 'offset': off,
                 'nterms': len(d), 'emp': emp, 'gf': gf, 'degnum': dn, 'degden': dd,
                 'points': pts, 'gfnum': [str(x) for x in T.gf_numerator(P, Q)]})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
