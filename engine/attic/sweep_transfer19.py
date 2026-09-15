"""Sweep the named neighbour-set families."""
import json, re, os, sys, collections, signal
import localentry as LE, transfer19 as T, ratrec, openness


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)
BUDGET = int(os.environ.get('BUDGET', '600'))
MARK = re.compile(r'onjectur|Empirical', re.I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
HITS, DONE = 'transfer19_hits.json', 'transfer19_done.json'
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()

for a in sorted(names):
    if a in done or a in roster:
        continue
    nm = names[a]
    if nm.strip().startswith('T(n,k)'):
        continue
    p = T.parse_name(nm)
    if not p:
        continue
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); continue
    try:
        signal.alarm(BUDGET)
        b = T.build(p, cap=CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0)
        res['build timed out'] += 1; done.add(a); continue
    if b is None:
        res['state space > cap'] += 1; done.add(a); continue
    adj, start, end, S = b
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    try:
        signal.alarm(BUDGET)
        t = [v // p['frac'] for v in T.terms(adj, start, end, len(d) + 3)]
        signal.alarm(0)
    except Timeout:
        signal.alarm(0)
        res['term evaluation timed out'] += 1; done.add(a); continue
    sh = next((s for s in range(0, 3) if t[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); continue
    off = int(e['offset'].split(',')[0])
    coeffs, dd = recs[0]
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        thr = T.threshold(adj, start, end, coeffs, order, S)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0)
        res['annihilation test timed out'] += 1; done.add(a); continue
    if thr is None:
        res['UNRESOLVED'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    else:
        # the walk index j carries a(j + off - sh)
        nthr = thr + off - sh
        bad = [off + k for k in range(len(d))
               if off + k > nthr and k - order >= 0 and
               d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
        if bad:
            res['claim contradicted by DATA'] += 1
            hits.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
        else:
            res['PROVED'] += 1
            hits.append({'anum': a, 'name': nm, 'walk': p['walk'], 'fixed': p['fixed'],
                         'base': p['base'], 'alpha': p['alpha'], 'frac': p['frac'],
                         'exc': p['exc'], 'tex': p['tex'], 'body': p['body'],
                         'offs': p['offs'], 'offs2': p['offs2'],
                         'S': S, 'order': order, 'offset': off, 'shift': sh,
                         'nterms': len(d), 'claimed': dd, 'nthr': nthr,
                         'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)
json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
