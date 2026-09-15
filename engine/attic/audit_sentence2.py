"""For every non-array paper whose entry conjecture fails at some index, does the PAPER
exclude that index? A paper that repeats an unconditional claim the data refutes is wrong;
one that states the correct range is right, and the flag is on the entry, not the paper."""
import json, re, collections
import sympy as sp
from pypdf import PdfReader
import localentry as LE
import audit_sentence as A          # reuse prep/to_expr

n = sp.Symbol('n')
MARK = re.compile(r'onjectur|Empirical', re.I)
rm = json.load(open('rank-map.json'))
TM = {'transfer-matrix', 'relabelling', 'global-count', 'budget', 'order-flag',
      'order-cond', 'common-sum', 'defective'}
res = collections.Counter(); bad = []
for m in [x for x in rm if x['engine'] not in TM]:
    a = m['anum']; e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    for L in [x for x in e['comment'] + e['formula'] if MARK.search(x)]:
        got = A.to_expr(A.prep(L))
        if not got:
            continue
        expr, r = got
        fails = []; tested = 0
        for k in range(r, len(d)):
            idx = off + k
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
        if tested < 3:
            break
        if not fails or len(fails) == tested:
            res['conjecture holds on the data (or fails everywhere)'] += 1
            break
        # the entry's conjecture fails at some indices: what does the PAPER say?
        try:
            t = re.sub(r'\s+', ' ', ''.join(p.extract_text() for p in
                       PdfReader(f"papers/{m['rank']}-{m['verdict']}.pdf").pages[:4]))
        except Exception:
            res['pdf unreadable'] += 1; break
        claims = [int(x) for x in re.findall(r'(?:for (?:all |every )?)n\s*>\s*(\d+)', t)]
        claims += [int(x) - 1 for x in re.findall(r'n\s*(?:>=|\\ge|≥)\s*(\d+)', t)]
        worst = max(fails)
        if claims and max(claims) >= worst:
            res['PAPER STATES A RANGE THAT EXCLUDES THE FAILURES'] += 1
        else:
            res['PAPER MAY OVERCLAIM'] += 1
            bad.append((m['rank'], a, m['engine'], fails[:4], sorted(set(claims))[-3:]))
        break
print(dict(res))
for b in bad[:30]:
    print('  CHECK BY HAND:', b)
