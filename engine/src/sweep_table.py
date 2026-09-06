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
import json, re, os, sys, collections, importlib
from math import factorial
import localentry as LE, ratrec, openness, tablecol, uniform

# transfer3 is the constant-stress family; its name regex is the most specific of the set,
# so trying it first cannot steal a name from another engine. Its interface differs from the
# rest -- parse_name returns a tuple, build takes four positional arguments, and terms and
# threshold live in transfer2 -- so it is dispatched separately below.
ENG = ['transfer3', 'transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10',
       'transfer8', 'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7']
M = {e: importlib.import_module(e) for e in ENG}
import transfer2 as T2
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
COL = re.compile(r'^k=(\d+):\s*(a\(n\)\s*=.*)$')
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = 'table_hits.json', 'table_done.json'
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


for a in sorted(names):
    if a in done or (SKIP_ROSTER and a in roster):
        continue
    nm = names[a]
    if not nm.strip().startswith('T(n,k)'):
        continue
    e = LE.get(a)
    cols = {}
    for L in e['comment'] + e['formula']:
        m = COL.match(L.strip())
        if m:
            r = ratrec.parse_rec(m.group(2))
            if r:
                cols[int(m.group(1))] = r
    if not cols:
        res['no explicit column recurrence'] += 1; done.add(a); continue
    op, _ = openness.status(a)
    if not op:
        res['not open'] += 1; done.add(a); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    proved, failed, skipped = [], [], []
    for c, (coeffs, dd) in sorted(cols.items()):
        rn = tablecol.rewrite(nm, c)
        if rn is None:
            skipped.append((c, 'name not rewritable')); continue
        p = eng = None
        for en in ENG:
            try:
                q = M[en].parse_name(rn)
            except Exception:
                q = None
            if q:
                p, eng = ({'t3': q} if en == 'transfer3' else q), en; break
        if p is None:
            skipped.append((c, 'no engine reads it')); continue
        try:
            if eng == 'transfer3':
                t3cols, t3alpha, _, _ = p['t3']
                if (t3alpha + 1) ** t3cols > CAP:
                    skipped.append((c, 'state space > cap')); continue
                b = M[eng].build(*p['t3'])
                if not b[0]:
                    skipped.append((c, 'empty state space')); continue
            else:
                try: b = M[eng].build(p, cap=CAP)
                except TypeError: b = M[eng].build(p)
        except Exception as ex:
            skipped.append((c, 'build failed')); continue
        if b is None:
            skipped.append((c, 'state space > cap')); continue
        order = max(coeffs)
        match = None
        prows = printed_rows(e)
        cands = [column(d, c, True), column(d, c, False), printed_column(prows, c)]
        for colv in cands:
            if len(colv) < order + 2:
                continue
            # Go through the shared interface rather than dispatching per engine by hand.
            # The old code called <engine>.avals directly, which 62 of the 71 engines do not
            # have; the AttributeError was swallowed by the except below and reported as
            # "model does not match the column", so every table whose column model came from
            # one of those engines was silently rejected. Same failure as the transfer7 one
            # already in the ledger, and the same fix.
            try:
                t = uniform.terms(eng, p, b, len(colv) + 5)
                tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
            except Exception:
                continue
            sh = next((x for x in range(0, 4) if tv[x:x + len(colv)] == colv), None)
            if sh is None:
                continue
            got, base = tv, sh - 1
            match = (True, got, base, colv)
            break
        if match is None:
            failed.append((c, 'model does not match the column')); continue
        up, got, base, colv = match
        try:
            thr = uniform.threshold(eng, p, b, coeffs, order)
        except Exception:
            skipped.append((c, 'threshold failed')); continue
        nthr = None if thr is None else thr - base
        if nthr is None:
            failed.append((c, 'UNRESOLVED')); continue
        # verify the claim on the column's own published terms
        bad = [n for n in range(max(nthr + 1, 1 + order), 1 + len(colv))
               if colv[n - 1] != sum(cc * colv[n - 1 - i] for i, cc in coeffs.items())]
        if bad:
            failed.append((c, 'claim contradicted at %s' % bad[:3])); continue
        proved.append({'k': c, 'engine': eng, 'order': order, 'nthr': nthr,
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
