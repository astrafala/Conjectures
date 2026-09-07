"""Independent re-check of every array paper in the roster.

Deliberately does NOT trust the sweep's own verdict. For each paper it rebuilds the model
from the entry's NAME, recomputes the sequence, and then:

  1. compares against every published DATA term (this is the only thing that ties the model
     to the sequence -- a misread name gives different counts);
  2. evaluates the conjectured recurrence NUMERICALLY well beyond both the data and the
     proved threshold, which is independent of the annihilation argument that produced the
     paper: if that argument were buggy, this would catch it;
  3. records how many DATA terms the check actually had, and how large they are, so that a
     paper resting on a weak check can be found;
  4. re-checks that the entry is still recorded as open.


SUPERSEDED. This carries its own list of engines, which was the whole set when it
was written and is eleven of eighty-three now, so it can only re-check papers from
those eleven. `audit_deep.py` does the same job through `uniform`, which knows all of
them, and covers 8,667 entries. Kept for the record; do not run it and do not read its
output as coverage.
"""
import json, re, os, sys, collections, importlib, time, signal


class Slow(Exception):
    pass


def _alarm(sig, frm):
    raise Slow()


signal.signal(signal.SIGALRM, _alarm)
BUDGET = int(os.environ.get('AUDIT_BUDGET', '150'))
from math import factorial
import localentry as LE, ratrec, openness

MARK = re.compile(r'onjectur|Empirical', re.I)
ENG = ['transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10', 'transfer8',
       'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7']
M = {e: importlib.import_module(e) for e in ENG}
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
rm = json.load(open('rank-map.json'))
TM = {'transfer-matrix', 'relabelling', 'global-count', 'budget', 'order-flag',
      'order-cond', 'common-sum', 'defective'}
targets = [m for m in rm if m['engine'] in TM]
if sys.argv[1] == 'list':
    want = set(json.load(open('audit_left.json')))
    targets = [t for t in targets if t['anum'] in want]
    lo = 'LEFTOVERS'          # a separate output file: writing back over the input list
                              # made every target look already-done and audited nothing
else:
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    targets = targets[lo:hi]
EXTRA = 45
out = json.load(open(f'audit_{lo}.json')) if os.path.exists(f'audit_{lo}.json') else {}
res = collections.Counter()

for t in targets:
    a = t['anum']
    if a in out:
        continue
    nm = names.get(a)
    if nm is None:
        res['name missing'] += 1
        out[a] = {'v': 'NAME MISSING'}
        continue
    p = eng = None
    for e in ENG:
        try:
            q = M[e].parse_name(nm)
        except Exception:
            q = None
        if q:
            p, eng = q, e
            break
    if p is None:
        try:
            p = M['transfer7'].parse_nb(nm)
            eng = 'transfer7nb'
        except Exception:
            p = None
    if p is None:
        res['UNPARSED NOW'] += 1
        out[a] = {'v': 'UNPARSED'}
        continue
    e = LE.get(a)
    recs = [r for r in (ratrec.parse_rec(L) for L in e['comment'] + e['formula']
                        if MARK.search(L)) if r]
    if not recs:
        res['NO RECURRENCE NOW'] += 1
        out[a] = {'v': 'NO RECURRENCE'}
        continue
    coeffs, dd = recs[0]
    order = max(coeffs)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    op, flag = openness.status(a)
    signal.alarm(BUDGET)
    try:
        mod0 = M[eng.replace('nb', '')]
        try:
            built = mod0.build(p, cap=400000)
        except TypeError:
            built = mod0.build(p)          # transfer6's build takes no cap
    except Slow:
        signal.alarm(0)
        res['slow'] += 1
        out[a] = {'v': 'SLOW BUILD'}
        continue
    except Exception as ex:
        signal.alarm(0)
        res['build failed'] += 1
        out[a] = {'v': 'BUILD FAILED', 'err': str(ex)[:80]}
        continue
    signal.alarm(0)
    if built is None:
        res['too big to recheck'] += 1
        out[a] = {'v': 'TOO BIG'}
        continue
    mod = M[eng.replace('nb', '')]
    signal.alarm(BUDGET)
    try:
        if eng == 'transfer10':
            adj, start, _ = built
            vals = mod.avals(adj, start, p, off + len(d) + EXTRA)
        else:
            adj, start, end, _ = built
            vals = mod.avals(adj, start, end, p, off + len(d) + EXTRA)
    except Slow:
        signal.alarm(0)
        res['slow'] += 1
        out[a] = {'v': 'SLOW EVAL'}
        continue
    except Exception as ex:
        signal.alarm(0)
        res['eval failed'] += 1
        out[a] = {'v': 'EVAL FAILED', 'err': str(ex)[:80]}
        continue
    signal.alarm(0)
    f = p.get('frac', 1) * (factorial(p['K']) if eng in SCALED else 1)
    got = [None if v is None or v % f else v // f for v in vals]
    datok = got[off:off + len(d)] == d
    lo2 = off + order
    if dd is not None:
        lo2 = max(lo2, int(dd) + 1)
    lo2 = max(lo2, t.get('nthr', 0) + 1)
    bad = []
    for n in range(lo2, len(got)):
        if got[n] is None or any(got[n - i] is None for i in coeffs):
            continue
        if got[n] != sum(c * got[n - i] for i, c in coeffs.items()):
            bad.append(n)
    rec = {'v': 'ok' if (datok and not bad) else 'PROBLEM',
           'data_ok': datok, 'rec_bad_at': bad[:5], 'nterms': len(d),
           'maxterm_digits': len(str(max(d))) if d else 0, 'order': order,
           'open': op, 'engine': eng, 'checked_to': len(got) - 1}
    if not datok:
        res['DATA MISMATCH'] += 1
    elif bad:
        res['RECURRENCE FAILS'] += 1
    elif not op:
        res['not open'] += 1
    else:
        res['ok'] += 1
    out[a] = rec
    json.dump(out, open(f'audit_{lo}.json', 'w'))
print(dict(res))
