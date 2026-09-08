"""Column conjectures on the T(n,k) tables, which every earlier sweep skipped.

A table entry states a recurrence for each of its first few columns:

    Empirical for column k:
    k=1: a(n) = 8*a(n-1) + 7*a(n-2)
    k=2: a(n) = 24*a(n-1) + 49*a(n-2) - 34*a(n-3)

Column c of the table is the ordinary fixed-width array count the engines already model, so
the only new work is (a) rewriting the name with k := c and (b) reading column c out of the
DATA, which a table stores by antidiagonals. The antidiagonal orientation is not asserted:
both are tried and the one matching the model exactly is accepted, so a wrong reading is
rejected rather than fitted.
"""
import json, re, os, sys, collections, importlib, zlib, signal, time
from math import factorial
import uniform
import localentry as LE, ratrec, openness, tablecol, tablerow

# transfer3 is the constant-stress family; its name regex is the most specific of the set,
# so trying it first cannot steal a name from another engine. Its interface differs from the
# rest -- parse_name returns a tuple, build takes four positional arguments, and terms and
# threshold live in transfer2 -- so it is dispatched separately below.
# No engine list here: see the note at the dispatch below. `uniform` is the one
# place that knows all eighty-three.
import transfer2 as T2
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
COL = re.compile(r'^k=(\d+):\s*(a\(n\)\s*=.*)$')
ROW = re.compile(r'^n=([\d,\.\s]+):\s*(a\((?:n|k)\)\s*=.*)$')
MODE = os.environ.get('TMODE', 'col')
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = ('table_hits.json', 'table_done.json') if MODE == 'col' else \
             ('tablerow_hits.json', 'tablerow_done.json')
SKIP_ROSTER = os.environ.get('SKIP_ROSTER', '1') == '1'
if os.environ.get('HITS'):
    HITS, DONE = os.environ['HITS'], os.environ['DONE']
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()


def printed_rows(e):
    """the 'Table starts' block, which lists more terms per column than the antidiagonal
    DATA does: DATA stops at a fixed count of antidiagonals, the printed rows do not."""
    rows, on = [], False
    for L in e['comment']:
        t = L.strip()
        if t.lower().startswith('table starts'):
            on = True; continue
        if on:
            if not re.fullmatch(r'[.\d\s]+', t) or not re.search(r'\d', t):
                break
            rows.append([int(x) for x in re.findall(r'\d+', t)])
    return rows


def printed_column(rows, c):
    out = []
    for r in rows:
        if len(r) < c:
            break
        out.append(r[c - 1])
    return out


def printed_row(rows, r):
    return list(rows[r - 1]) if len(rows) >= r else []


def row_of(d, r, upward):
    grid, i, dd = {}, 0, 0
    while i < len(d):
        for j in range(dd + 1):
            if i >= len(d):
                break
            n, k = (dd - j + 1, j + 1) if upward else (j + 1, dd - j + 1)
            grid[(n, k)] = d[i]; i += 1
        dd += 1
    out, k = [], 1
    while (r, k) in grid:
        out.append(grid[(r, k)]); k += 1
    return out


def column(d, c, upward):
    out, i, dd = [], 0, 0
    grid = {}
    while i < len(d):
        for j in range(dd + 1):
            if i >= len(d):
                break
            n, k = (dd - j + 1, j + 1) if upward else (j + 1, dd - j + 1)
            grid[(n, k)] = d[i]; i += 1
        dd += 1
    n = 1
    while (n, c) in grid:
        out.append(grid[(n, c)]); n += 1
    return out


# Everything sweep_table needed, this sweep needed too and never got: it walked all 399,027
# names in A-number order, skipped non-tables WITHOUT recording the skip so every run re-read
# the same early index, and had no clock of any kind while a table states a recurrence for
# every row it has. Same pool, same shards, same three guards, each a setting named in the
# refusal it causes.
class _T(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_T()))
BUDGET = int(os.environ.get('BUDGET', '30'))
ROWCAP = int(os.environ.get('ROWCAP', '1024'))
ENTRY_BUDGET = int(os.environ.get('ENTRY_BUDGET', '90'))
POOL = os.environ.get('TABPOOL', 'deep-check/tabpool.txt')
if os.path.exists(POOL):
    targets = [a for a in open(POOL).read().split() if a.startswith('A')]
else:
    targets = sorted(names)
SHARD = int(os.environ.get('TABSHARD', '0'))
NSHARD = int(os.environ.get('TABNSHARD', '1'))

for a in targets:
    if a in done or (SKIP_ROSTER and a in roster):
        continue
    if zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    nm = names.get(a, '')
    if not nm.strip().startswith(('T(n,k)', 'T(n,m)')):
        done.add(a)
        continue
    e = LE.get(a)
    cols = {}
    if MODE == 'col':
        for L in e['comment'] + e['formula']:
            m = COL.match(L.strip())
            if m:
                r = ratrec.parse_rec(m.group(2))
                if r:
                    cols[int(m.group(1))] = r
    else:
        on = False
        for L in e['comment'] + e['formula']:
            t = L.strip()
            if re.match(r'^Empirical for row n', t, re.I):
                on = True; continue
            if on:
                m = ROW.match(t)
                if not m:
                    on = False; continue
                r = ratrec.parse_rec(m.group(2))
                if r:
                    for v in re.findall(r'\d+', m.group(1)):
                        cols[int(v)] = r
    if not cols:
        res['no explicit column recurrence'] += 1; done.add(a); continue
    op, _ = openness.status(a)
    if not op:
        res['not open'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    proved, failed, skipped = [], [], []
    t_entry = time.time()
    for c, (coeffs, dd) in sorted(cols.items()):
        if time.time() - t_entry > ENTRY_BUDGET:
            skipped.append((c, f'the table used its {ENTRY_BUDGET}s budget before this row'))
            continue
        rn = (tablecol if MODE == 'col' else tablerow).rewrite(nm, c)
        if rn is None:
            skipped.append((c, 'name not rewritable')); continue
        # The list of twelve engines that used to be tried here was all of them when this
        # was written and is twelve of eighty-three now, so every row or column whose model
        # needs a later engine was recorded as "no engine reads it". `uniform` knows all of
        # them and handles the ones whose interface differs.
        try:
            got_eng = uniform.read(rn)
        except Exception:
            got_eng = None
        if not got_eng:
            skipped.append((c, 'no engine reads it')); continue
        eng, p = got_eng
        # the size is estimated from the parse before anything is built: an alarm cannot
        # interrupt a build that spends its whole time inside one C-level call
        W = p.get('W') or p.get('fixed') or p.get('cols')
        A = p.get('alpha')
        if isinstance(W, int) and isinstance(A, int) and W > 0:
            try:
                nrows = (A + 1) ** W
            except Exception:
                nrows = None
            if nrows is not None and nrows > ROWCAP:
                skipped.append((c, f'{nrows} rows: above the row cap {ROWCAP}')); continue
        try:
            signal.alarm(BUDGET)
            b = uniform.build(eng, p, CAP)
            signal.alarm(0)
        except _T:
            signal.alarm(0)
            skipped.append((c, f'build over the {BUDGET}s budget')); continue
        except Exception:
            signal.alarm(0)
            skipped.append((c, 'build failed')); continue
        if b is None:
            skipped.append((c, 'state space > cap')); continue
        order = max(coeffs)
        match = None
        prows = printed_rows(e)
        if MODE == 'col':
            cands = [column(d, c, True), column(d, c, False), printed_column(prows, c)]
        else:
            cands = [row_of(d, c, True), row_of(d, c, False), printed_row(prows, c)]
        for colv in cands:
            if len(colv) < order + 2:
                continue
            # One interface, not a dispatch per engine. The old code called `avals`, which
            # most of the eighty-three do not have; the AttributeError landed in the `except`
            # just below and was reported as "model does not match the column", so a model
            # that matched perfectly was thrown away.
            try:
                signal.alarm(BUDGET)
                t = uniform.terms(eng, p, b, len(colv) + 5)
                signal.alarm(0)
                tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
            except Exception:
                signal.alarm(0)
                continue
            sh = next((s for s in range(0, 4) if tv[s:s + len(colv)] == colv), None)
            if sh is None:
                continue
            got, base = tv, sh - 1
            match = (True, got, base, colv); break
        if match is None:
            failed.append((c, 'model does not match the column')); continue
        up, got, base, colv = match
        try:
            signal.alarm(BUDGET * 3)
            thr = uniform.threshold(eng, p, b, coeffs, order)
            signal.alarm(0)
        except _T:
            signal.alarm(0)
            skipped.append((c, f'threshold over the {BUDGET * 3}s budget')); continue
        except Exception:
            signal.alarm(0)
            skipped.append((c, 'threshold failed')); continue
        nthr = None if thr is None else thr - base
        if nthr is None:
            failed.append((c, 'UNRESOLVED')); continue
        # verify the claim on the column's own published terms
        bad = [n for n in range(max(nthr + 1, 1 + order), 1 + len(colv))
               if colv[n - 1] != sum(cc * colv[n - 1 - i] for i, cc in coeffs.items())]
        if bad:
            failed.append((c, 'claim contradicted at %s' % bad[:3])); continue
        proved.append({'k': c, 'mode': MODE, 'engine': eng, 'order': order, 'nthr': nthr,
                       'coeffs': {int(x): str(y) for x, y in coeffs.items()},
                       'claimed': dd, 'nterms': len(colv), 'S': uniform.size(eng, p, b),
                       'upward': up, 'name_k': rn,
                       # the largest published column value the model reproduces: the
                       # Verification section quotes it, so it must be the real figure
                       'maxdig': len(str(max(colv))),
                       # total decimal digits of exact agreement between model and entry:
                       # the honest measure of how much a wrong reading would have to fake
                       'totdig': sum(len(str(v)) for v in colv)})
    if proved:
        # see sweep_table.py: re-asking a widened question must replace an entry's record,
        # not append a second one
        hits[:] = [x for x in hits if x.get('anum') != a]
        res['TABLE PROVED'] += 1
        res['columns proved'] += len(proved)
        hits.append({'anum': a, 'name': nm, 'cols': proved,
                     'failed': failed, 'skipped': skipped})
    else:
        res['nothing proved on this table'] += 1
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['TABLE PROVED'], res['columns proved'], flush=True)
json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
