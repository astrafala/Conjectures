"""Sweep the 3 X 3 subblock families."""
import json, re, os, sys, collections, signal
import localentry as LE, transfer17 as T, ratrec, openness


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)
# a single entry near the state cap can make the annihilation loop run for hours; the loop
# needs S+1 consecutive zeros to certify anything, so there is no partial credit -- better
# to abandon that entry and keep sweeping than to stall the whole run on it
BUDGET = int(os.environ.get('BUDGET', '600'))

MARK = re.compile(r'onjectur|Empirical', re.I)
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
HITS, DONE = 'transfer17_hits.json', 'transfer17_done.json'
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
    if (p['alpha'] + 1) ** (2 * p['fixed']) > CAP:
        res['state space > cap'] += 1; done.add(a); continue
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
    if b is None or not b[0]:
        res['state space > cap'] += 1; done.add(a); continue
    st, adj = b
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    t = [v // p['frac'] for v in T.terms(adj, len(st), len(d) + 3)]
    sh = next((s for s in range(0, 4) if t[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); continue
    off = int(e['offset'].split(',')[0])
    coeffs, dd = recs[0]
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        thr = T.threshold(adj, len(st), coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0)
        res['annihilation test timed out'] += 1; done.add(a); continue
    if thr is None:
        res['UNRESOLVED'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm})
    else:
        # the walk index j carries a(j + off - sh); the recurrence holds for j > thr, so in
        # the entry's own index it holds for n > thr + off - sh
        nthr = thr + off - sh
        bad = [off + k for k in range(len(d))
               if off + k > nthr and off + k - order >= off and
               d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
        if bad:
            res['claim contradicted by DATA'] += 1
            hits.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
        else:
            res['PROVED'] += 1
            hits.append({'anum': a, 'name': nm, 'walk': p['walk'], 'fixed': p['fixed'],
                         'base': p['base'], 'alpha': p['alpha'], 'frac': p['frac'],
                         'quant': p['quant'], 'tex': p['tex'], 'body': p['body'],
                         'S': len(st), 'order': order, 'offset': off, 'shift': sh,
                         'nterms': len(d), 'claimed': dd, 'nthr': nthr,
                         'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)
json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
