"""One shard of the sweep: the same work as sweep_uni.py, on a slice of the candidates.

The sweep is one process and the container has four cores, and with five thousand candidates
still unprocessed --- entries an engine already parses and that carry a conjecture, simply
never reached --- the queue is the bottleneck and not the mathematics. This runs a slice of
it and writes its own files, so shards never share a list and cannot overwrite each other:
that is the failure the lock in sweep_uni.py exists to prevent, and the fix here is to give
each shard its own file rather than to serialise them. `merge_shards.py` folds the results
back under that lock.

    python3 src/sweep_shard.py 2000000 0 4        cap 2000000, shard 0 of 4

Nothing is proved here that sweep_uni.py would not prove: same engines, same DATA match, same
annihilation test.
"""
_ORIGINAL_DOC = """One sweep over every array entry, through every engine.

The per-engine sweeps each carried their own candidate list and their own bookkeeping, so an
entry became reachable the moment a parser changed and then sat there because that engine's
sweep had already been run. This asks every engine about every name, every time.

The walk index and the entry's own n differ by a constant that depends on the engine, and the
constant is not assumed: the model's terms are matched against the entry's published DATA and
the offset read off from where they line up. The engine's threshold is in the same index its
terms are, so one conversion serves them all.
"""
import json, re, os, sys, collections, signal, zlib
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
SHARD, NSHARD = int(sys.argv[2]), int(sys.argv[3])
# Two sweeps running at once on different pools must not share files: each holds its whole
# hit list in memory and writes it back whole, so sharing one would have each silently
# discard the other's results. TAG gives a run its own namespace; without it the names are
# the ones every earlier run used, so nothing already on disk moves.
TAG = os.environ.get('TAG', '')
HITS, DONE = f'shard{TAG}_hits_{SHARD}.json', f'shard{TAG}_done_{SHARD}.json'
# the shard skips what the global sweep has already settled, but never writes those files
GDONE = set(json.load(open('uniall_done.json'))) if os.path.exists('uniall_done.json') else set()
GHITS = ({h['anum'] for h in json.load(open('uniall_hits.json'))}
         if os.path.exists('uniall_hits.json') else set())
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
# The standing rule is that a cap is a setting and not a wall, so a refusal is only
# meaningful next to the cap it was made at. Without this the refused pool cannot be told
# apart from the pool already re-tried at a higher cap, and the same work gets redone.
# This used to record the cap for every entry the sweep ATTEMPTED, which is not the same
# thing at all: reading it back as a list of refusals turned "563 attempted, none settled"
# into "563 refused at the cap", a claim nothing had measured. Only an actual refusal for
# size is recorded here now.
CAPS = f'shard{TAG}_caps_{SHARD}.json'
caps = json.load(open(CAPS)) if os.path.exists(CAPS) else {}
res = collections.Counter()


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    json.dump(caps, open(CAPS, 'w'), indent=0, sort_keys=True)


# asking eighteen parsers about 29k names costs ten seconds, which is most of a chunk when
# the sweep has to run in short foreground pieces; the candidate list is cached instead
CANDS = json.load(open('uni_cands.json'))
# a chunk of the sweep can be aimed at one engine's candidates: a newly written engine has
# its answers in minutes instead of behind every other engine's leftovers
ONLY = os.environ.get('ONLY', '')
# a widened parser makes a handful of named entries reachable without making a new engine;
# asking about that handful should not mean re-asking about every candidate the engine has
ANUMS = {x for x in os.environ.get('ANUMS', '').replace(',', ' ').split() if x}
if os.environ.get('ANUMS_FILE'):
    ANUMS |= {x for x in open(os.environ['ANUMS_FILE']).read().replace(',', ' ').split() if x}
for a in sorted(CANDS):
    if ANUMS and a not in ANUMS:
        continue
    if ONLY and CANDS[a] != ONLY:
        continue
    # ONLY names a newly written engine, and its candidates were marked done by earlier
    # sweeps that had no engine to offer them. Honouring `done` there would refuse to ask
    # the new question, which is the whole reason for the run.
    if a in roster or a in GHITS:
        continue
    # `done` is this shard's own record and is always honoured --- ignoring it made every
    # interrupted rerun reprocess from the front and append the same hits again. Only the
    # global set is bypassed under ONLY, since that is where a new engine's candidates were
    # parked by sweeps that had no engine to offer them.
    if a in done or (not (ONLY or ANUMS) and a in GDONE):
        continue
    # crc32, not hash(): Python randomises string hashing per process, so hash() would
    # partition differently in every shard and entries would be both duplicated and dropped
    if zlib.crc32(a.encode()) % NSHARD != SHARD:
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
                res['state space > cap'] += 1; caps[a] = max(caps.get(a, 0), CAP)
                done.add(a); save(); continue
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
        res['state space > cap'] += 1; caps[a] = max(caps.get(a, 0), CAP)
        done.add(a); save(); continue
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
