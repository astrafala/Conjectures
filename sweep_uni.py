"""One sweep over every array entry, through every engine.

The per-engine sweeps each carried their own candidate list and their own bookkeeping, so an
entry became reachable the moment a parser changed and then sat there because that engine's
sweep had already been run. This asks every engine about every name, every time.

The walk index and the entry's own n differ by a constant that depends on the engine, and the
constant is not assumed: the model's terms are matched against the entry's published DATA and
the offset read off from where they line up. The engine's threshold is in the same index its
terms are, so one conversion serves them all.
"""
import json, re, os, sys, collections, signal
import localentry as LE, ratrec, openness, uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '45'))
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
MARK = re.compile(r'onjectur|Empirical', re.I)
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
# NOT 'uni_hits.json': that name was already taken by an older sweep, and this one
# silently appended its records to it. Nothing was mis-proved -- the schemas differ
# and the integrator reads only its own fields -- but the two runs were mixed in one
# file and only a KeyError on a missing field made it visible.
HITS, DONE = 'uniall_hits.json', 'uniall_done.json'
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


# asking eighteen parsers about 29k names costs ten seconds, which is most of a chunk when
# the sweep has to run in short foreground pieces; the candidate list is cached instead
CANDS = json.load(open('uni_cands.json'))
for a in sorted(CANDS):
    if a in done or a in roster:
        continue
    nm = names[a]
    got = uniform.read(nm)
    if not got:
        continue
    en, p = got
    # a cheap size estimate first: an alphabet of 16 over a width of 7 is 2.7e8 rows, and
    # letting build discover that costs the whole time budget for each such entry
    if isinstance(p, dict) and 'alpha' in p and 'fixed' in p:
        try:
            if (p['alpha'] + 1) ** p['fixed'] > 4 * CAP:
                res['state space > cap'] += 1; done.add(a); save(); continue
        except Exception:
            pass
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['build timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['build failed'] += 1; done.add(a); save(); continue
    if b is None:
        res['state space > cap'] += 1; done.add(a); save(); continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['terms timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['terms failed'] += 1; done.add(a); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); save(); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    try:
        signal.alarm(BUDGET)
        thr = uniform.threshold(en, p, b, coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['annihilation timed out'] += 1; done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['threshold failed'] += 1; done.add(a); save(); continue
    if thr is None:
        res['UNRESOLVED'] += 1; done.add(a); save(); continue
    nthr = thr + off - sh
    bad = [off + k for k in range(len(d))
           if off + k > nthr and k - order >= 0 and
           d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
    if bad:
        res['claim contradicted by DATA'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': nm, 'bad': bad[:3]})
    else:
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': nm, 'engine': en, 'S': S, 'order': order,
                     'offset': off, 'shift': sh, 'nthr': nthr, 'nterms': len(d),
                     'claimed': dd,
                     'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a); save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
