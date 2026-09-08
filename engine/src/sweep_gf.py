"""Conjectured recurrences that follow from a generating function the entry records as fact."""
import json

import atomicjson, re, os, collections, signal, zlib
import sympy
import conjlines
import factlines
import localentry as LE, ratrec, openness, gfrec


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '30'))
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
# settable, so the four shards cannot overwrite one another: they had fixed names and every
# shard would have written the same file
HITS = os.environ.get('HITS', 'gf_hits.json')
DONE = os.environ.get('DONE', 'gf_done.json')
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
CONJ = re.compile(r'\b(conjecture|conjectured|conjecturally|empirical)\b', re.I)
REC = re.compile(r'a\(n\)\s*=.*a\(n\s*-\s*\d+\)')


def save():
    atomicjson.dump(hits, HITS, indent=1)
    atomicjson.dump(sorted(done), DONE)


# Three failures this sweep shared with every other one here, and a fourth of its own.
# It walked all 399,027 names in A-number order; it skipped an entry WITHOUT recording the
# skip, so every run re-read the same early part of the index and a timeout meant it never
# reached the rest; it did not shard; and it required the conjectural word to be ON the line,
# so a conjecture written as a "Conjectures from X: (Start)" block was invisible.
#
# The pool is the 3,520 entries that carry a conjectured recurrence AND a generating function
# the entry states as fact -- the premise this sweep is built on, and by far the largest
# settleable pool in the database.
POOL = os.environ.get('GFPOOL', 'deep-check/gfdef.txt')
targets = ([a for a in open(POOL).read().split() if a.startswith('A')]
           if os.path.exists(POOL) else sorted(names))
SHARD = int(os.environ.get('GFSHARD', '0'))
NSHARD = int(os.environ.get('GFNSHARD', '1'))

RECHECK = os.environ.get('RECHECK') == '1'   # ask again about entries already in the roster
for a in targets:
    if a in done or (a in roster and not RECHECK) or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    e = LE.get(a)
    lines = e['comment'] + e['formula']
    conj = [L for L in conjlines.lines(e) if REC.search(L)]
    if not conj:
        res['no conjectured recurrence line'] += 1; done.add(a); save(); continue
    recs = [r for r in (ratrec.parse_rec(L) for L in conj) if r]
    if not recs:
        res['conjectured recurrence unparsable'] += 1; done.add(a); save(); continue
    # The premise may only be a line the entry states as FACT. Absence of a conjectural word
    # is not that test: a `Conjectures from X: (Start)' block holds bare formula lines, and
    # the generating function there is the same conjecture as the recurrence, not a premise
    # for it. factlines removes every line conjlines names.
    gfl = [(L, g) for L, g in ((L, gfrec.parse_gf(L)) for L in factlines.facts(e))
           if g is not None]
    if not gfl:
        res['no usable generating function'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    coeffs, dd = recs[0]
    order = max(coeffs)
    hit = None
    for L, g in gfl:
        try:
            signal.alarm(BUDGET)
            s = gfrec.series(g, len(d) + off + 2)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); continue
        except Exception:
            signal.alarm(0); continue
        if s is None:
            continue
        # the g.f. usually starts at the entry's offset, but not always: pin it on the data
        sh = None
        for cand in (off, 0):
            if cand + len(d) <= len(s) and all(
                    s[cand + k] == d[k] for k in range(len(d))):
                sh = cand; break
        if sh is None:
            continue
        try:
            signal.alarm(BUDGET)
            deg = gfrec.residual_degree(g, coeffs)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); continue
        except Exception:
            signal.alarm(0); continue
        if deg is None:
            continue
        # a(n) - sum c_i a(n-i) = [x^(n - off + sh)] D(x)G(x), zero past the degree
        nthr = deg + off - sh
        bad = [off + k for k in range(len(d))
               if off + k > nthr and k - order >= 0 and
               d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
        if bad:
            res['claim contradicted by DATA'] += 1
            hits.append({'anum': a, 'FAILS': True, 'name': names[a], 'bad': bad[:3]})
            hit = 'bad'
            break
        hit = {'anum': a, 'name': names[a], 'gfline': L.strip(), 'gf': sympy.srepr(g),
               'gftex': sympy.latex(g), 'order': order, 'offset': off, 'shift': sh,
               'nthr': nthr, 'deg': deg, 'nterms': len(d), 'claimed': dd,
               'conj': conj[0].strip(),
               'coeffs': {int(k): str(v) for k, v in coeffs.items()}}
        break
    if hit is None:
        res['g.f. does not imply the recurrence'] += 1
    elif hit != 'bad':
        res['PROVED'] += 1
        hits.append(hit)
        print('done', a, res['PROVED'], flush=True)
    done.add(a); save()
save()
print(dict(res))
