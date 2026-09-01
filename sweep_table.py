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
import localentry as LE, ratrec, openness, tablecol

ENG = ['transfer9', 'transfer6', 'transfer16', 'transfer12', 'transfer10', 'transfer8',
       'transfer14', 'transfer11', 'transfer15', 'transfer13', 'transfer7']
M = {e: importlib.import_module(e) for e in ENG}
SCALED = ('transfer7', 'transfer8', 'transfer10', 'transfer12', 'transfer16')
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
COL = re.compile(r'^k=(\d+):\s*(a\(n\)\s*=.*)$')
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = 'table_hits.json', 'table_done.json'
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
    if a in done or a in roster:
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
                p, eng = q, en; break
        if p is None:
            skipped.append((c, 'no engine reads it')); continue
        try:
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
            try:
                if eng == 'transfer6':
                    st, adj = b
                    t = [x // p['frac'] for x in M[eng].terms(adj, len(st), len(colv) + 2)]
                    sh = next((s for s in range(0, 3) if t[s:s + len(colv)] == colv), None)
                    if sh is None:
                        continue
                    got = t; base = sh - 1
                elif eng == 'transfer10':
                    adj, start, _ = b
                    v = M[eng].avals(adj, start, p, len(colv) + 3)
                    f = factorial(p['K']) * p['frac']
                    got = [None if x is None or x % f else x // f for x in v]
                    base = 0
                    if got[1:1 + len(colv)] != colv:
                        continue
                else:
                    adj, start, end, _ = b
                    v = M[eng].avals(adj, start, end, p, len(colv) + 3)
                    f = p['frac'] * (factorial(p['K']) if eng in SCALED else 1)
                    got = [None if x is None or x % f else x // f for x in v]
                    base = 0
                    if got[1:1 + len(colv)] != colv:
                        continue
            except Exception:
                continue
            match = (True, got, base, colv); break
        if match is None:
            failed.append((c, 'model does not match the column')); continue
        up, got, base, colv = match
        try:
            if eng == 'transfer6':
                thr = M[eng].threshold(adj, len(st), coeffs, order)
                nthr = None if thr is None else thr - base
            elif eng == 'transfer10':
                thr = M[eng].threshold(adj, start, coeffs, order, p); nthr = thr
            else:
                thr = M[eng].threshold(adj, start, end, coeffs, order, p); nthr = thr
        except Exception:
            skipped.append((c, 'threshold failed')); continue
        if nthr is None:
            failed.append((c, 'UNRESOLVED')); continue
        # verify the claim on the column's own published terms
        bad = [n for n in range(max(nthr + 1, 1 + order), 1 + len(colv))
               if colv[n - 1] != sum(cc * colv[n - 1 - i] for i, cc in coeffs.items())]
        if bad:
            failed.append((c, 'claim contradicted at %s' % bad[:3])); continue
        proved.append({'k': c, 'engine': eng, 'order': order, 'nthr': nthr,
                       'coeffs': {int(x): str(y) for x, y in coeffs.items()},
                       'claimed': dd, 'nterms': len(colv), 'S': len(b[0]),
                       'upward': up, 'name_k': rn})
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
