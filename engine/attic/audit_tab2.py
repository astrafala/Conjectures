"""Independent re-check of the table row and column results.

Rebuilds each line's model from the entry's own wording, confirms it still reproduces every
published value of that line, checks the recurrence forty steps past the proved threshold and
confirms the threshold is tight.
"""
import json, os, re, collections
import localentry as LE, uniform

DONE = 'audit_tab2_done.json'
hits = json.load(open('tab2_hits.json'))
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
prob, n = [], 0


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


for h in hits:
    a = h['anum']
    if a in done:
        continue
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    prows = printed_rows(e)
    for c in h['cols']:
        got = uniform.read(c['name_k'])
        if not got:
            prob.append((a, c['k'], 'name no longer read')); continue
        en, p = got
        # the recorded S is the size AFTER trimming, while an engine's cap test looks at the
        # size before it, so re-building with S+1 as the cap can refuse a model that was
        # perfectly buildable. Escalate rather than report a phantom failure.
        b = None
        for cap in (c['S'] + 1, 4 * c['S'] + 8, 40000, 200000):
            b = uniform.build(en, p, cap)
            if b is not None:
                break
        if b is None:
            prob.append((a, c['k'], 'model no longer builds')); continue
        coeffs = {int(x): int(y) for x, y in c['coeffs'].items()}
        order, nthr, sh = c['order'], c['nthr'], c['shift']
        t = uniform.terms(en, p, b, nthr + 50 + sh)
        tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
        # two antidiagonal readings can have the SAME length and different values, so the
        # audit has to try them all rather than take the first of the right length
        line = next((v for v in cands(d, prows, c['k'], c['mode'])
                     if len(v) == c['nterms'] and tv[sh:sh + len(v)] == v), None)
        if line is None:
            prob.append((a, c['k'], 'model no longer reproduces the line')); continue
        V = lambda i: tv[sh + i - 1] if 0 <= sh + i - 1 < len(tv) else None
        bad = [i for i in range(nthr + 1, nthr + 41)
               if V(i) is not None and V(i - order) is not None and
               V(i) != sum(cc * V(i - j) for j, cc in coeffs.items())]
        if bad:
            prob.append((a, c['k'], 'CLAIM FAILS at', bad[:3])); continue
        if nthr - order >= 1 and V(nthr) is not None and V(nthr - order) is not None:
            if V(nthr) == sum(cc * V(nthr - j) for j, cc in coeffs.items()):
                prob.append((a, c['k'], 'range not tight at', nthr))
    done.add(a); n += 1
    json.dump(sorted(done), open(DONE, 'w'))
print('chunk', n, 'cumulative', len(done), 'of', len(hits), 'problems', len(prob))
for q in prob[:20]:
    print(q)
