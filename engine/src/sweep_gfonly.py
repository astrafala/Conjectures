import json

import atomicjson, os, collections, signal, sys, zlib
import sympy
import localentry as LE, uniform, openness, gfonly, conjgf, conjlines

# sharded, and each shard writes its own files: one entry can take minutes of sympy, so a
# single process asks about 1,328 entries far too slowly, and two processes on one hits file
# destroy each other's results.
SHARD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NSHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 1
SFX = '' if NSHARD == 1 else f'_{SHARD}'
HITS, DONE = f'gfonly_hits{SFX}.json', f'gfonly_done{SFX}.json'
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
# The pool used to be a 135-entry list built by hand from a snapshot, and only 2 of the
# 1,328 entries that actually carry a conjectured generating function were in it. That is the
# eighth stale filter found in this project, and they all hide the same way: the sweep runs,
# reports a small clean number, and never asks about the rest. The pool is now read from a
# file rebuilt from the clone, and the old list is only the fallback.
POOL = os.environ.get('GFPOOL', 'deep-check/gfpool.txt')
if os.path.exists(POOL):
    pool = [a for a in open(POOL).read().split() if a.startswith('A')]
else:
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

def save():
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)
    # the reasons were printed only after the whole pool, which a timeout never reaches, so a
    # run that refused everything looked the same as a run that had not started. They are
    # stored now, and a refusal that is only a setting says which setting.
    atomicjson.dump(dict(res), f'gfonly_why{SFX}.json', indent=1, sort_keys=True)


# The sweep used to write its files only after a PROVED hit, so a run that was killed -- and
# these runs are killed by a timeout every time -- threw away every refusal it had recorded
# and the next run asked all the same questions again. Saving on the way out of every entry
# costs nothing against a sympy check that can take minutes.
import atexit
atexit.register(save)

for a in sorted(pool):
    if a in done or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    save()
    e = LE.get(a)
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); continue
    gl = None
    # conjgf, not gfonly: the corpus writes the conjectural marker behind the expression as
    # often as in front of it, and gfonly.parse refuses `G.f.: ... (conjectured).' outright.
    # And the line must be one the entry means conjecturally -- inside a `Conjectures from
    # X: (Start)' block counts, a bare statement of fact does not.
    for L in conjlines.lines(e):
        g = conjgf.parse(L)
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
    # Enough coefficients for the g.f. argument is NOT necessarily enough to check the entry's
    # own DATA: an entry publishing more terms than the coefficient budget was being rejected
    # as "model does not match DATA" when the model in fact matched every published term. Ask
    # for whichever is longer.
    want_terms = max(need, len(d) + off) + off + 6
    try:
        signal.alarm(BUDGET * 4)
        t = uniform.terms(en, p, b, want_terms)
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
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)
    print('done', a, res['PROVED'], flush=True)

atomicjson.dump(hits, HITS, indent=1)
atomicjson.dump(sorted(done), DONE)
print(dict(res))
