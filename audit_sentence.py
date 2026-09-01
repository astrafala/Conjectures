"""Model-free check for the 632 NON-array papers.

Same lesson as the array families: verify the claim against the entry's own published
integers, using none of the machinery that produced the paper. Here the claim is the entry's
conjectured formula itself, so the test is simply whether that formula holds on the published
terms. A paper claiming to prove something the data contradicts is wrong, whichever way the
error runs.

Handles both shapes the entries use: a recurrence with polynomial coefficients in n, and a
closed form in n.
"""
import json, re, collections, sys
import sympy as sp
import localentry as LE

n = sp.Symbol('n')
MARK = re.compile(r'onjectur|Empirical', re.I)
rm = json.load(open('rank-map.json'))
TM = {'transfer-matrix', 'relabelling', 'global-count', 'budget', 'order-flag',
      'order-cond', 'common-sum', 'defective'}
targets = [m for m in rm if m['engine'] not in TM]


def prep(s):
    s = s.split(' - _')[0]
    s = re.sub(r'^\s*(Conjecture[sd]?|Empirical)\s*[:.]?\s*', '', s, flags=re.I).strip()
    s = s.rstrip('. ')
    return s


def to_expr(s):
    """-> (sympy expr that should vanish, max shift) or None."""
    if 'a(' not in s:
        return None
    if s.count('=') != 1:
        return None
    lhs, rhs = s.split('=')
    body = f'({lhs})-({rhs})'
    shifts = set(int(m) for m in re.findall(r'a\(\s*n\s*-\s*(\d+)\s*\)', body))
    body = re.sub(r'a\(\s*n\s*-\s*(\d+)\s*\)', r'A\1', body)
    body = re.sub(r'a\(\s*n\s*\)', 'A0', body)
    if 'a(' in body:
        return None                     # a(2n), a(n+1), other sequences: not handled
    body = body.replace('^', '**')
    try:
        e = sp.sympify(body)
    except Exception:
        return None
    syms = {str(x) for x in e.free_symbols}
    if not syms <= ({'n'} | {f'A{k}' for k in shifts | {0}}):
        return None
    return e, (max(shifts) if shifts else 0)


res = collections.Counter(); bad = []
for m in targets:
    a = m['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    lines = [L for L in e['comment'] + e['formula'] if MARK.search(L)]
    checked = False
    for L in lines:
        # the entry's own range, if it states one
        mb = re.search(r'for\s+n\s*>=?\s*(\d+)', L)
        lo_extra = int(mb.group(1)) if mb else None
        got = to_expr(prep(L))
        if not got:
            continue
        expr, r = got
        fails = []; tested = 0
        for k in range(r, len(d)):
            idx = off + k
            if lo_extra is not None and idx < lo_extra:
                continue
            sub = {n: idx}
            for j in range(0, r + 1):
                sub[sp.Symbol(f'A{j}')] = d[k - j]
            try:
                v = sp.simplify(expr.subs(sub))
            except Exception:
                continue
            if not v.is_number:
                continue
            tested += 1
            if v != 0:
                fails.append(idx)
        if tested >= 3:
            checked = True
            if fails and len(fails) < tested:
                res['FAILS AT SOME INDICES'] += 1
                bad.append((m['rank'], a, m['engine'], fails[:4], tested, L[:90]))
            elif fails:
                res['fails everywhere (transcription, not a real claim)'] += 1
                bad.append((m['rank'], a, m['engine'], 'ALL', tested, L[:90]))
            else:
                res['confirmed on published data'] += 1
            break
    if not checked:
        res['no machine-checkable formula line'] += 1
print(dict(res))
for b in bad[:30]:
    print('  FLAG:', b)
