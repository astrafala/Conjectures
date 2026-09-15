#!/usr/bin/env python3
"""The identity papers: check the identity against the two entries' published terms.

These conjectures say a(n) equals some expression in the terms of OTHER entries -- a bisection,
a difference of two sequences, a multiple. Nothing on the entry alone can test that, which is
why the other audits skipped them; reading the referenced entries makes it a direct check.
"""
import json, os, re, sys, collections
import sympy as sp
import localentry as LE

OUT = 'audit_ident.json'
SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
n = sp.Symbol('n')


def terms(a):
    e = LE.get(a)
    if not e:
        return None, None
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    return d, int(e['offset'].split(',')[0])


def unesc(s):
    s = re.sub(r'\\(?:small|textbf|texttt|emph|textit|normalsize)\b', '', s)
    s = s.replace('\\textasciicircum{}', '^').replace('\\textbackslash{}', '\\')
    s = re.sub(r'\\([&%$#_{}])', r'\1', s)
    return re.sub(r'[{}\\]', '', s).strip()


def main():
    tex = json.load(open(SC + '/texfacts.json'))
    left = json.load(open(SC + '/left.json'))
    out = {}
    for a in left:
        for r in tex.get(a, []):
            t = r['title']
            if not re.search(r'identity', t, re.I):
                continue
            line = unesc(r['quote'] or '')
            body = re.sub(r'^.*?Conjectur\w*:?\s*|^.*?Empirical:?\s*', '', line, flags=re.I)
            body = body.split(' - ')[0].split('---')[0].strip().rstrip('.')
            m = re.match(r'a\(n\)\s*=\s*(.+)$', body)
            if not m:
                out[a] = {'v': 'CLAIM NOT PARSED', 'line': line[:120]}; continue
            rhs = m.group(1)
            lo = None
            mm = re.search(r'\bfor\s+n\s*(>=|>)\s*(-?\d+)', rhs)
            if mm:
                lo = int(mm.group(2)) + (1 if mm.group(1) == '>' else 0)
                rhs = rhs[:mm.start()]
            # "a(n) = A089928(4*n-2), for n > 0" leaves a trailing comma once the range is
            # cut off, and "F(4*n-2)," evaluates to a one-element TUPLE, which never equals an
            # integer. One entry came back a disproof because of that comma.
            rhs = re.sub(r'\[[^\]]*\]', '', rhs).strip().rstrip('.').strip().rstrip(',').strip()
            refs = sorted(set(re.findall(r'A\d{6}', rhs)))
            data = {}
            for b in refs:
                d, o = terms(b)
                if d is None:
                    out[a] = {'v': 'REFERENCED ENTRY MISSING', 'ref': b}; break
                data[b] = (d, o)
            else:
                d, off = terms(a)
                def val(b, idx):
                    dd, oo = data[b]
                    j = idx - oo
                    return dd[j] if 0 <= j < len(dd) else None
                expr = rhs
                for b in refs:
                    expr = expr.replace(b, 'F_' + b)
                bad, tested, skipped = [], 0, 0
                for i, v in enumerate(d):
                    N = off + i
                    if lo is not None and N < lo:
                        continue
                    env = {'n': N}
                    ok = True
                    for b in refs:
                        env['F_' + b] = (lambda bb: (lambda k: val(bb, int(k))))(b)
                    try:
                        got = eval(expr.replace('^', '**'), {'__builtins__': {}}, env)
                    except TypeError:
                        skipped += 1; continue
                    except Exception as ex:
                        out[a] = {'v': 'EVAL FAILED', 'err': str(ex)[:70], 'expr': expr[:90]}
                        ok = False; break
                    if got is None:
                        skipped += 1; continue
                    tested += 1
                    if got != v:
                        bad.append(N)
                    if len(bad) > 5:
                        break
                if not ok:
                    continue
                out[a] = {'v': 'ok' if (tested and not bad) else
                          ('NOT ENOUGH OVERLAP' if not tested else 'PROBLEM'),
                          'tested': tested, 'skipped': skipped, 'bad': bad[:5],
                          'refs': refs, 'line': line[:110]}
    json.dump(out, open(OUT, 'w'), indent=1)
    print(len(out), dict(collections.Counter(v['v'] for v in out.values())))
    for a, v in out.items():
        if v['v'] != 'ok':
            print('  ', a, json.dumps(v)[:220])


if __name__ == '__main__':
    main()
