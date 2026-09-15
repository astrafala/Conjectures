"""Column and row conjectures on the T(n,k) tables, through the uniform engine interface.

A column of a table is a fixed-width array count and a row is a fixed-height one; both are
ordinary one-parameter counts once the fixed index is substituted into the entry's own
wording. Every engine is tried, and the model must reproduce the published values of that
line exactly -- from the antidiagonal DATA read both ways and from the printed "Table starts"
block -- before anything is claimed.
"""
import json, re, os, sys, collections, signal
import localentry as LE, ratrec, openness, tablecol, tablerow, uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '60'))
MODE = os.environ.get('TMODE', 'col')
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = ('tabcol2_hits.json', 'tabcol2_done.json') if MODE == 'col' else \
             ('tabrow_hits.json', 'tabrow_done.json')
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
COL = re.compile(r'^k=(\d+):\s*(a\((?:n|k)\)\s*=.*)$')
ROWH = re.compile(r'^Empirical for row n', re.I)
ROW = re.compile(r'^n=([\d,\.\s]+):\s*(a\((?:n|k)\)\s*=.*)$')


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
            rows.append([int(x) for x in re.findall(r'\d+', t)])
    return rows


def grid_of(d, upward):
    g, i, dd = {}, 0, 0
    while i < len(d):
        for j in range(dd + 1):
            if i >= len(d):
                break
            n, k = (dd - j + 1, j + 1) if upward else (j + 1, dd - j + 1)
            g[(n, k)] = d[i]; i += 1
        dd += 1
    return g


def line_of(d, idx, upward, mode):
    g = grid_of(d, upward)
    out, t = [], 1
    while (idx, t) in g if mode == 'row' else (t, idx) in g:
        out.append(g[(idx, t)] if mode == 'row' else g[(t, idx)]); t += 1
    return out


def printed_line(rows, idx, mode):
    if mode == 'row':
        return list(rows[idx - 1]) if len(rows) >= idx else []
    out = []
    for r in rows:
        if len(r) < idx:
            break
        out.append(r[idx - 1])
    return out


for a in sorted(names):
    if a in done or a in roster:
        continue
    nm = names[a]
    if not nm.strip().startswith('T(n,k)'):
        continue
    e = LE.get(a)
    lines = {}
    if MODE == 'col':
        for L in e['comment'] + e['formula']:
            m = COL.match(L.strip())
            if m:
                r = ratrec.parse_rec(m.group(2))
                if r:
                    lines[int(m.group(1))] = r
    else:
        on = False
        for L in e['comment'] + e['formula']:
            t = L.strip()
            if ROWH.match(t):
                on = True; continue
            if on:
                m = ROW.match(t)
                if not m:
                    on = False; continue
                r = ratrec.parse_rec(m.group(2))
                if r:
                    for v in re.findall(r'\d+', m.group(1)):
                        lines[int(v)] = r
    if not lines:
        res['no explicit line recurrence'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    prows = printed_rows(e)
    proved, failed = [], []
    for c, (coeffs, dd) in sorted(lines.items()):
        rn = (tablecol if MODE == 'col' else tablerow).rewrite(nm, c)
        if rn is None:
            failed.append((c, 'name not rewritable')); continue
        got = uniform.read(rn)
        if not got:
            failed.append((c, 'no engine reads it')); continue
        en, p = got
        try:
            signal.alarm(BUDGET)
            b = uniform.build(en, p, CAP)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); failed.append((c, 'build timed out')); continue
        if b is None:
            failed.append((c, 'state space > cap')); continue
        S = uniform.size(en, p, b)
        order = max(coeffs)
        match = None
        for cand in (line_of(d, c, True, MODE), line_of(d, c, False, MODE),
                     printed_line(prows, c, MODE)):
            if len(cand) < order + 2:
                continue
            try:
                signal.alarm(BUDGET)
                t = uniform.terms(en, p, b, len(cand) + 4)
                signal.alarm(0)
            except Timeout:
                signal.alarm(0); break
            except Exception:
                signal.alarm(0); continue
            tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
            sh = next((s for s in range(0, 4) if tv[s:s + len(cand)] == cand), None)
            if sh is not None:
                match = (sh, cand); break
        if match is None:
            failed.append((c, 'model does not match the line')); continue
        sh, cand = match
        try:
            signal.alarm(BUDGET)
            thr = uniform.threshold(en, p, b, coeffs, order)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); failed.append((c, 'annihilation timed out')); continue
        except Exception:
            signal.alarm(0); failed.append((c, 'threshold failed')); continue
        if thr is None:
            failed.append((c, 'UNRESOLVED')); continue
        nthr = thr - sh + 1                     # value i sits at walk index sh + i - 1
        bad = [i for i in range(max(nthr + 1, order + 1), len(cand) + 1)
               if cand[i - 1] != sum(cc * cand[i - 1 - j] for j, cc in coeffs.items())]
        if bad:
            failed.append((c, 'claim contradicted at %s' % bad[:3])); continue
        proved.append({'k': c, 'mode': MODE, 'engine': en, 'order': order, 'nthr': nthr,
                       'coeffs': {int(x): str(y) for x, y in coeffs.items()},
                       'claimed': dd, 'nterms': len(cand), 'S': S, 'shift': sh,
                       'name_k': rn, 'maxdig': len(str(max(cand))),
                       'totdig': sum(len(str(v)) for v in cand)})
    if proved:
        res['TABLE PROVED'] += 1
        res['lines proved'] += len(proved)
        hits.append({'anum': a, 'name': nm, 'cols': proved, 'failed': failed, 'mode': MODE})
    else:
        res['nothing proved on this table'] += 1
    done.add(a); save()
    print('done', a, res['TABLE PROVED'], res['lines proved'], flush=True)
save()
print(dict(res))
