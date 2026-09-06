import json, os, collections, signal
import sympy
import localentry as LE, uniform, openness, gfonly

HITS, DONE = 'gfonly_hits.json', 'gfonly_done.json'
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
pool = json.load(open(P + 'gfonly.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
BUDGET = int(os.environ.get('BUDGET', '120'))
CAP = int(os.environ.get('CAP', '20000'))


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))

for a in sorted(pool):
    if a in done or a in roster:
        continue
    e = LE.get(a)
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); continue
    gl = None
    for L in e['comment'] + e['formula']:
        g = gfonly.parse(L)
        if g is not None:
            gl = (L.strip(), g)
            break
    if gl is None:
        res['no g.f. recovered'] += 1; done.add(a); continue
    got = uniform.read(names[a])
    if not got:
        res['name no longer read'] += 1; done.add(a); continue
    en, p = got
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['build failed or timed out'] += 1; done.add(a); continue
    if b is None:
        res['state space > cap'] += 1; continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    need = gfonly.coefficients_needed(S, gl[1])
    try:
        signal.alarm(BUDGET * 4)
        t = uniform.terms(en, p, b, need + off + 5)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['terms failed or timed out'] += 1; done.add(a); continue
    tv = [None if (v is None or v.denominator != 1) else v.numerator for v in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); continue
    try:
        signal.alarm(BUDGET * 4)
        ser = gfrec_series = None
        import gfrec
        ser = gfrec.series(gl[1], need)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); res['series failed'] += 1; done.add(a); continue
    if ser is None:
        res['series failed'] += 1; done.add(a); continue
    want = []
    okall = True
    for k in range(len(ser)):
        v = 0 if k < off else (tv[sh + k - off] if sh + k - off < len(tv) else None)
        if v is None:
            okall = False
            break
        want.append(v)
        if sympy.Integer(v) != ser[k]:
            okall = False
            break
    if not okall and len(want) < len(ser):
        if len(want) < need:
            res['not enough model terms'] += 1; done.add(a); continue
    if not okall:
        res['the conjectured g.f. is FALSE'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': names[a], 'line': gl[0],
                     'first_bad': len(want)})
        done.add(a); continue
    dn, dd = gfonly.degrees(gl[1])
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': names[a], 'engine': en, 'S': S, 'offset': off,
                 'shift': sh, 'nterms': len(d), 'line': gl[0],
                 'degnum': int(dn), 'degden': int(dd), 'checked': int(need)})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
