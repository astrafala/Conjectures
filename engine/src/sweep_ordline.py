"""Table columns and rows that state only the ORDER of their empirical recurrence.

`k=2: [order 17]` --- 1872 such lines across 626 tables. The recurrence is not printed, but
the same uniqueness argument as for the whole-sequence case settles it: the line is a
fixed-width (or fixed-height) array count, hence a walk count on S vertices, hence satisfies
some monic recurrence of order at most S; Berlekamp--Massey on 2S exact terms returns the
minimal one; and if that order equals the stated one, every recurrence of that order the line
satisfies is the same polynomial. The tail is checked too, since the entry's recurrence may
hold only from some index on.
"""
import json, re, os, sys, collections, signal
from fractions import Fraction
import localentry as LE, openness, uniform, bmrec, tablecol, tablerow


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '40'))
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
P62 = (1 << 61) - 1
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
SKIP_ROSTER = os.environ.get('SKIP_ROSTER', '1') == '1'
HITS, DONE = (('ordline_hits.json', 'ordline_done.json') if SKIP_ROSTER else
              ('ordline_ros_hits.json', 'ordline_ros_done.json'))
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
ORD = re.compile(r'^([nk])=([\d,\.\s]+):\s*\[\s*order\s+(\d+)\s*\]', re.I)


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


def printed_rows(e):
    rows, on = [], False
    for L in e['comment']:
        t = L.strip()
        if t.lower().startswith('table starts'):
            on = True; continue
        if on:
            if not re.fullmatch(r'[.\d\s]+', t) or not re.search(r'\d', t):
                break
            rows.append([int(v) for v in re.findall(r'\d+', t)])
    return rows


def grid_of(d, up):
    g, i, dd = {}, 0, 0
    while i < len(d):
        for j in range(dd + 1):
            if i >= len(d):
                break
            n, k = (dd - j + 1, j + 1) if up else (j + 1, dd - j + 1)
            g[(n, k)] = d[i]; i += 1
        dd += 1
    return g


def cands(d, prows, idx, mode):
    out = []
    for up in (True, False):
        g = grid_of(d, up)
        v, t = [], 1
        while ((idx, t) if mode == 'row' else (t, idx)) in g:
            v.append(g[(idx, t) if mode == 'row' else (t, idx)]); t += 1
        out.append(v)
    if mode == 'row':
        out.append(list(prows[idx - 1]) if len(prows) >= idx else [])
    else:
        v = []
        for r in prows:
            if len(r) < idx:
                break
            v.append(r[idx - 1])
        out.append(v)
    return out


for a in sorted(names):
    if a in done or (SKIP_ROSTER and a in roster):
        continue
    nm = names[a]
    if not nm.strip().startswith('T(n,k)'):
        continue
    e = LE.get(a)
    lines = {}
    for L in e['comment'] + e['formula']:
        m = ORD.match(L.strip())
        if m:
            for v in re.findall(r'\d+', m.group(2)):
                lines[(m.group(1), int(v))] = (int(m.group(3)), L.strip())
    if not lines:
        continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    prows = printed_rows(e)
    proved = []
    for (var, idx), (stated, line) in sorted(lines.items()):
        mode = 'col' if var == 'k' else 'row'
        rn = (tablecol if mode == 'col' else tablerow).rewrite(nm, idx)
        if rn is None:
            res['name not rewritable'] += 1; continue
        got = uniform.read(rn)
        if not got:
            res['no engine reads it'] += 1; continue
        en, p = got
        try:
            signal.alarm(BUDGET)
            b = uniform.build(en, p, CAP)
            signal.alarm(0)
        except Exception:
            signal.alarm(0); res['build failed'] += 1; continue
        if b is None:
            res['state space > cap'] += 1; continue
        S = uniform.size(en, p, b)
        try:
            signal.alarm(BUDGET)
            t = uniform.terms(en, p, b, 2 * S + 8)
            signal.alarm(0)
        except Exception:
            signal.alarm(0); res['terms timed out'] += 1; continue
        tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
        match = None
        for cand in cands(d, prows, idx, mode):
            if len(cand) < 3:
                continue
            sh = next((s for s in range(0, 4) if tv[s:s + len(cand)] == cand), None)
            if sh is not None:
                match = (sh, cand); break
        if match is None:
            res['model does not match the line'] += 1; continue
        sh, cand = match
        seq = [v for v in tv[sh:] if v is not None]
        if len(seq) < 2 * S + 2:
            res['not enough terms'] += 1; continue
        try:
            signal.alarm(BUDGET)
            L0 = bmrec.bm_mod([v % P62 for v in seq], P62)
            k = min(stated + 4, max(0, len(seq) - 2 * stated - 4))
            Lt = bmrec.bm_mod([v % P62 for v in seq[k:]], P62)
            signal.alarm(0)
        except Exception:
            signal.alarm(0); res['filter failed'] += 1; continue
        if L0 != stated or Lt != stated:
            res['minimal order differs from the stated one'] += 1; continue
        try:
            signal.alarm(4 * BUDGET)
            Lx, cs = bmrec.bm([Fraction(v) for v in seq])
            signal.alarm(0)
        except Exception:
            signal.alarm(0); res['exact BM timed out'] += 1; continue
        if Lx != stated or any(c.denominator != 1 for c in cs):
            res['exact run disagrees'] += 1; continue
        rec = {i + 1: int(c) for i, c in enumerate(cs)}
        bad = [i for i in range(Lx, len(cand))
               if cand[i] != sum(rec[j] * cand[i - j] for j in rec)]
        if bad:
            res['contradicted by the published line'] += 1; continue
        proved.append({'k': idx, 'mode': mode, 'engine': en, 'S': S, 'order': Lx,
                       'stated': stated, 'shift': sh, 'nterms': len(cand), 'line': line,
                       'coeffs': {i + 1: str(int(c)) for i, c in enumerate(cs)}})
    if proved:
        res['TABLE PROVED'] += 1
        res['lines recovered'] += len(proved)
        hits.append({'anum': a, 'name': nm, 'cols': proved})
        print('done', a, res['TABLE PROVED'], res['lines recovered'], flush=True)
    else:
        res['nothing recovered on this table'] += 1
    done.add(a); save()
save()
print(dict(res))
