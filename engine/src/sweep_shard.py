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
import json

import atomicjson, re, os, sys, collections, gc, resource, signal, zlib, time

# Without an address-space limit the KERNEL decides what a runaway build costs, and it kills the
# whole shard rather than the one entry. STATE.md records that re-asking `deep-check/capped.txt`
# at the standing cap "was killed by the kernel for memory" -- and it still is: a run over the
# 688 off-roster capped entries died at 106 with empty logs. `uniform.build` allocates toward
# the cap before it can refuse, so the refusal has to be made enforceable from outside. With a
# limit the allocation raises MemoryError, which the build's own try/except records as a refusal
# and the sweep carries on to the next entry. `sweep_prec` has had this since the day it was
# written; this sweep never did.
MEMGB = float(os.environ.get('MEMGB', '6'))
resource.setrlimit(resource.RLIMIT_AS, (int(MEMGB * 2 ** 30), resource.RLIM_INFINITY))
# Emergency reserve, released by the MemoryError handlers so that RECORDING the failure does not
# fail in its turn. Dropping the automaton and calling gc.collect() was tried first and does not
# work: RLIMIT_AS caps ADDRESS SPACE, and CPython does not hand freed arenas back to the OS, so
# a collection lowers nothing the limit is measuring. A bytearray this size is mmap'd on its own
# and IS unmapped when deleted, which is the only thing that actually buys the handler room.
_RESERVE = bytearray(48 * 1024 * 1024)
import conjlines
import localentry as LE, ratrec, openness, uniform


class Timeout(BaseException):
    """BaseException, not Exception, and that is the whole point.

    The alarm fires INSIDE `uniform.build', whose last clause is `except Exception: return
    None' -- so a Timeout derived from Exception was swallowed there and the build returned
    None, which every caller reads as "the state space exceeded the cap". Measured: a W=9 entry
    asked with a 2-second budget and a cap of 10^12 was recorded as `state space > cap'. Every
    build timeout in this project has been filed as a cap refusal, which is why
    `uniall_caps.json' over-reports and why the 33 entries of `residue.txt' were finished with
    no record of what finished them.

    `uniform.build' already re-raises MemoryError for exactly this reason, with the comment
    that an out-of-memory "is a different fact". A timeout is a different fact by the same
    argument. Deriving from BaseException makes it one no `except Exception' can absorb --
    the idiom Python itself uses for KeyboardInterrupt.
    """
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
# Entries the MACHINE has already refused, and the largest limit each was refused under.
# `merge_shards.py' folds a shard's own `done' into `uniall_done.json' and then DELETES it, and
# `sweep_shard' deliberately ignores the global done set whenever ANUMS is given -- so an
# ANUMS_FILE runner starts its list again after every merge and spends its budget re-asking the
# entries that already failed. Re-asking at the SAME memory limit cannot succeed: the state
# space did not shrink because a file was deleted. Skipped only while this shard's MEMGB is no
# larger than the limit it failed under, so raising MEMGB re-opens it automatically -- which is
# the defect-34 rule (a refusal about the machine carries an expiry) with the expiry being a
# bigger machine rather than a changed engine.
try:
    GOOM = {k: float(v) for k, v in json.load(open('uniall_oom.json')).items()}
except Exception:
    GOOM = {}
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
WHY = f'shard{TAG}_why_{SHARD}.json'
# ... and an out-of-memory is not an actual refusal for size either, which is the same mistake
# one layer down. `uniform.build' wrapped everything including MemoryError in `except
# Exception: return None', and None is read here as the cap refusing, so every entry whose
# build outgrew the shard's MEMGB went into CAPS as though the model were too big. A186012
# builds at S=900096 under a cap of 2,000,000 and is in `uniall_caps.json' because the shard
# that asked it had 4 GB. Recorded here in its own file, with the limit it failed under, so it
# can be re-asked with the memory it needs instead of being read back as settled.
OOM = f'shard{TAG}_oom_{SHARD}.json'
# Entries the CLOCK refused, named. A timeout was `res['build timed out'] += 1' and nothing
# else: a count in the why file, with no way to say WHICH entries ran out of budget, so a
# shortened budget bought progress at the price of an unidentifiable population (defect 40).
# Separate from `oom' on purpose -- what a timeout exceeded is the budget, and folding the two
# together is exactly how a cap came to wear an out-of-memory's name.
TMO = f'shard{TAG}_tmo_{SHARD}.json'
INFLIGHT = f'shard{TAG}_inflight_{SHARD}.json'
caps = json.load(open(CAPS)) if os.path.exists(CAPS) else {}
oom = json.load(open(OOM)) if os.path.exists(OOM) else {}
tmo = json.load(open(TMO)) if os.path.exists(TMO) else {}
res = collections.Counter()
# A marker left behind means the previous shard died inside that entry without reaching any
# handler -- MemoryError the handler could not survive, the OOM killer, a container restart.
# Read it here so the entry is named instead of vanishing, and so the next run does not simply
# walk into the same wall with the same limit.


def _boot():
    """The wall-clock time this machine booted, as a stamp for WHICH boot wrote the marker.

    A container restart kills a shard exactly as the OOM killer does, and the recovery below
    cannot tell them apart from the marker alone -- so every restart retired one entry as a
    refusal that never happened. This container restarted twice in eleven minutes on the night
    this was written, and t17big.sh asks entries that take tens of minutes each: left alone,
    the restarts would have retired its whole list without ever refusing anything.

    The first version of this stamped UPTIME and compared `marker > current', reasoning that
    uptime only increases within a boot. That is true and still gets it wrong: a marker written
    10 seconds into the previous boot, read 20 seconds into the new one, has the SMALLER number
    and reads as a genuine death. It misfired the first time it ran in production, on A252303
    and A252147, both of which were killed by the 05:47 restart and recorded as refusals.

    Boot time -- now minus uptime -- is constant within a boot and differs across boots, so
    comparing it needs no reasoning about which number is larger. A few seconds of tolerance
    absorbs clock jitter and the rounding.
    """
    # NOT `except Exception: return -1'. That sentinel is what hid a missing `import time':
    # _boot() returned -1 on every call, `abs(-1 - anything) > 5' held always, and every marker
    # read as a container restart -- genuine deaths included. An OSError reading /proc is the
    # only failure worth tolerating; a NameError is a bug and must not be dressed up as data.
    try:
        return int(time.time() - float(open('/proc/uptime').read().split()[0]))
    except OSError:
        return -1


def inflight(a=None, phase=''):
    """Name the entry being worked on, before the work starts.

    Every other record here is written after an outcome is known, which is exactly the case a
    process that dies cannot reach. A186012 died twice in `uniform.threshold' and left no row
    anywhere saying it had ever been asked -- not a hit, not a cap, not an oom. This file says
    `we are inside phase P of entry A' and is removed when the entry finishes, so whatever kills
    the shard, the next run can read who it was killed on. It survives SIGKILL and the OOM
    killer, which no exception handler does.
    """
    try:
        if a is None:
            if os.path.exists(INFLIGHT):
                os.remove(INFLIGHT)
        else:
            atomicjson.dump({'anum': a, 'phase': phase, 'memgb': MEMGB, 'boot': _boot()},
                            INFLIGHT, indent=0)
    except Exception:
        pass


def save():
    inflight()
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)
    atomicjson.dump(caps, CAPS, indent=0, sort_keys=True)
    if oom:
        atomicjson.dump(oom, OOM, indent=0, sort_keys=True)
    if tmo:
        atomicjson.dump(tmo, TMO, indent=0, sort_keys=True)
    # The counters were printed ONCE, after the loop, so a shard that is still running or that
    # dies mid-way reports nothing at all about why it refused anything -- and these shards do
    # die: four launched over the capped list, three gone, four empty logs and no idea what the
    # 74 finished entries had said. That is defect 31 again (a measurement that reports only at
    # the end can be lost whole), here in the sweep that has produced more results than any
    # other. Written every entry, beside the hits.
    atomicjson.dump(dict(res), WHY, indent=1, sort_keys=True)


_prev = None
if os.path.exists(INFLIGHT):
    try:
        _prev = json.load(open(INFLIGHT))
    except Exception:
        _prev = None
_rebooted = (_prev is not None and _prev.get('boot') is not None
             and abs(_prev.get('boot', 0) - _boot()) > 5)
if _prev and _prev.get('anum') and _rebooted:
    # The machine rebooted while this entry was in flight: the marker records more uptime than
    # the machine now has. The shard was killed by the restart, not by the entry, so the entry
    # is owed another ask. Clearing the marker without recording anything is the whole fix --
    # it will be selected again on this pass.
    print('previous shard on %s was killed by a container restart, not by the entry; '
          're-asking' % _prev['anum'], flush=True)
    inflight()
elif _prev and _prev.get('anum'):
    print('previous shard died on %s in phase %s at MEMGB=%s'
          % (_prev['anum'], _prev.get('phase'), _prev.get('memgb')), flush=True)
    oom[_prev['anum']] = max(oom.get(_prev['anum'], 0), float(_prev.get('memgb') or 0))
    # ... and mark it done, or the next shard walks into the same wall and dies in the same
    # place, forever. The entry was killed outright -- by the OOM killer, which no handler
    # survives -- so `done.add' never ran for it, and the runner re-selected it on every
    # iteration: rcap2 sat on A205024 for an hour, dying and restarting, while 595 entries
    # behind it went unasked. Naming the entry was only half of it; getting PAST the entry is
    # the other half. It is in `oom', so it is re-askable deliberately, at a memory limit
    # chosen for it rather than by walking into it again.
    done.add(_prev['anum'])
    try:
        atomicjson.dump(sorted(done), DONE)
        atomicjson.dump(oom, OOM, indent=0, sort_keys=True)
    except Exception:
        print('  could not record the death of %s' % _prev['anum'], flush=True)
    inflight()


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
# ANUMS names entries to ask about, so it must be able to name one the cached candidate list
# has never heard of. Iterating CANDS alone meant a newly written engine's entries -- which
# are not in a cache built before it existed -- were filtered out to nothing, and the sweep
# reported that it had processed zero of them. That is the fifth cache in this codebase found
# holding back work rather than saving it.
for a in sorted(set(CANDS) | ANUMS):
    if ANUMS and a not in ANUMS:
        continue
    if ONLY and CANDS[a] != ONLY:
        continue
    # ONLY names a newly written engine, and its candidates were marked done by earlier
    # sweeps that had no engine to offer them. Honouring `done` there would refuse to ask
    # the new question, which is the whole reason for the run.
    if a in roster or a in GHITS:
        continue
    if MEMGB <= GOOM.get(a, 0):
        res['out of memory on an earlier pass, at this limit or more'] += 1
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
    nm = names.get(a)
    if nm is None:
        try:
            nm = LE.get(a)['name']
        except Exception:
            res['name unknown'] += 1; done.add(a); save(); continue
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
    # conjlines understands a "Conjectures from X: (Start) ... (End)" block, whose formula
    # lines carry no conjectural word of their own; MARK alone could not see them
    recs = [r for r in (ratrec.parse_rec(L) for L in conjlines.claims(e)) if r]
    if not recs:
        res['no parsable recurrence'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    inflight(a, 'build')
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['build timed out'] += 1
        tmo[a] = max(tmo.get(a, 0), BUDGET)
        done.add(a); save(); continue
    except MemoryError:
        # marked done so the run makes progress, but NOT written to caps: what this entry
        # exceeded is MEMGB, and the file says which so a later run can ask it again with more
        signal.alarm(0); res['out of memory'] += 1; oom[a] = MEMGB
        done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['build failed'] += 1; done.add(a); save(); continue
    if b is None:
        res['state space > cap'] += 1; caps[a] = max(caps.get(a, 0), CAP)
        done.add(a); save(); continue
    S = uniform.size(en, p, b)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    inflight(a, 'terms')
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, len(d) + off + 5)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['terms timed out'] += 1
        tmo[a] = max(tmo.get(a, 0), BUDGET)
        done.add(a); save(); continue
    except MemoryError:
        signal.alarm(0); res['out of memory'] += 1; oom[a] = MEMGB
        # Release the reserve and drop the automaton BEFORE saving. Saving allocates, and on this path the address
        # space is already exhausted, so the save raised MemoryError too and the shard died
        # having written nothing: A186012's run left no file at all to say what happened to it.
        # It has to be `b' that goes -- handing the automaton to save() and deleting the
        # parameter there frees nothing, because this name still holds the only reference that
        # matters. Catching MemoryError is not enough if the recovery path allocates.
        _RESERVE = None; b = None; gc.collect()
        done.add(a); save(); continue
    except Exception:
        signal.alarm(0); res['terms failed'] += 1; done.add(a); save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        res['model does not match DATA'] += 1; done.add(a); save(); continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    inflight(a, 'threshold')
    try:
        signal.alarm(BUDGET)
        thr = uniform.threshold(en, p, b, coeffs, order)
        signal.alarm(0)
    except Timeout:
        signal.alarm(0); res['annihilation timed out'] += 1
        tmo[a] = max(tmo.get(a, 0), BUDGET)
        done.add(a); save(); continue
    except MemoryError:
        # A186012's BUILD fits: S=900096 under a cap of 2,000,000. What did not fit was
        # `lumpauto.lump' inside `uniform.threshold', at 7 GB. The build is not the only phase
        # that can exhaust the limit, and recording an out-of-memory here as a timeout is the
        # same conflation one phase later.
        signal.alarm(0); res['out of memory'] += 1; oom[a] = MEMGB
        # Release the reserve and drop the automaton BEFORE saving. Saving allocates, and on this path the address
        # space is already exhausted, so the save raised MemoryError too and the shard died
        # having written nothing: A186012's run left no file at all to say what happened to it.
        # It has to be `b' that goes -- handing the automaton to save() and deleting the
        # parameter there frees nothing, because this name still holds the only reference that
        # matters. Catching MemoryError is not enough if the recovery path allocates.
        _RESERVE = None; b = None; gc.collect()
        done.add(a); save(); continue
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
        # A proof retires the out-of-memory row: the entry was refused by the container on an
        # earlier pass and is not refused now, and a list that is written but never retracted
        # over-reports exactly as uniall_caps.json did. Six of the first thirty rows were entries
        # that had since been proved and installed.
        oom.pop(a, None)
        res['PROVED'] += 1
        hits.append({'anum': a, 'name': nm, 'engine': en, 'S': S, 'order': order,
                     'offset': off, 'shift': sh, 'nthr': nthr, 'nterms': len(d),
                     'claimed': dd,
                     'coeffs': {int(k): str(v) for k, v in coeffs.items()}})
    done.add(a); save()
    print('done', a, res['PROVED'], flush=True)
save()
print(dict(res))
