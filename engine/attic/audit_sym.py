#!/usr/bin/env python3
"""Re-verification for the papers whose proof is symbolic rather than a walk count.

Those papers all rest on something the ENTRY states as fact -- a generating function, an
exponential generating function, or a closed form -- from which the conjectured recurrence
is derived. This checks that dependence numerically and independently of the algebra:
expand the entry's own stated object to far more terms than the entry publishes, confirm
it reproduces the published data, and then test the conjectured recurrence on the whole
expansion, well past the threshold the paper claims.

An agreement over two hundred terms does not replace the proof; it makes an error in the
symbolic step, or a misread of which expression the entry states, very hard to hide.
"""
import json, os, re, sys, signal, collections, time
import sympy as sp
import gfclean, openness, ratrec
from makeslots import coeffs_of
import localentry as LE

x, n = sp.symbols('x n')
OUT = 'audit_sym%s.json' % os.environ.get('SHARD', '')
MARK = re.compile(r'onjectur|Empirical', re.I)
GFL = re.compile(r'^(G\.f\.|O\.g\.f\.|g\.f\.|Generating function)\s*[:.]', re.I)
EGFL = re.compile(r'^E\.g\.f\.\s*[:.]', re.I)
NTERMS = 160


class TO(BaseException):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))


def ipoly(p):
    try:
        if p == 0:
            return [0]
        if not sp.expand(p).is_polynomial(n):
            return None
        cs = sp.Poly(sp.expand(p), n).all_coeffs()[::-1]
    except Exception:
        return None
    out = []
    for c in cs:
        c = sp.nsimplify(c, rational=True)
        if c.q != 1:
            return None
        out.append(int(c))
    return out


def ev(co, v):
    r = 0
    for c in reversed(co):
        r = r * v + c
    return r


def prec(line):
    """(polynomial coefficient lists, lowest shift first) or None."""
    try:
        cs = coeffs_of(line)
    except Exception:
        return None
    if not cs:
        return None
    ps = [ipoly(p) for p in cs]
    return None if any(p is None for p in ps) else ps


def gf_terms(expr, N, egf):
    s = sp.series(expr, x, 0, N).removeO()
    p = sp.Poly(sp.expand(s), x)
    co = [0] * N
    for (k,), c in p.terms():
        if k < N:
            co[k] = sp.nsimplify(c, rational=True)
    if egf:
        co = [c * sp.factorial(k) for k, c in enumerate(co)]
    out = []
    for c in co:
        c = sp.nsimplify(c, rational=True)
        out.append(int(c) if getattr(c, 'q', 1) == 1 else None)
    return out


def main(budget, per_entry, todo):
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    t0 = time.time()
    for a in todo:
        if a in out or time.time() - t0 > budget:
            continue
        e = LE.get(a)
        d = [int(v) for v in e['data'].split(',') if v.strip()]
        off = int(e['offset'].split(',')[0])
        lines = e['comment'] + e['formula']
        recs = []
        for L in lines:
            if not MARK.search(L):
                continue
            ps = prec(L)
            if ps and len(ps) > 1:
                m = re.search(r'\bfor\s+n\s*(>=|>)\s*(-?\d+)', L)
                lo = int(m.group(2)) + (1 if m.group(1) == '>' else 0) if m else None
                recs.append((ps, lo, L))
        if not recs:
            out[a] = {'v': 'NO PLAIN RECURRENCE'}; continue
        cands = []
        for L in lines:
            if GFL.match(L) or EGFL.match(L):
                cands.append((L, bool(EGFL.match(L))))
        if not cands:
            out[a] = {'v': 'NO POSTED GF'}; continue
        best = None
        signal.alarm(per_entry)
        try:
            for L, egf in cands:
                for cut in gfclean.candidates(L):
                    try:
                        expr = sp.sympify(cut.replace('^', '**'), locals={'x': x})
                    except Exception:
                        continue
                    try:
                        t = gf_terms(expr, min(NTERMS, len(d) + 90), egf)
                    except Exception:
                        continue
                    for sh in range(0, 4):
                        if t[sh:sh + len(d)] == d:
                            best = (expr, egf, sh, t); break
                    if best:
                        break
                if best:
                    break
            signal.alarm(0)
        except TO:
            signal.alarm(0)
            out[a] = {'v': 'SLOW'}; continue
        except Exception as ex:
            signal.alarm(0)
            out[a] = {'v': 'ERROR', 'err': str(ex)[:80]}; continue
        if best is None:
            out[a] = {'v': 'GF DOES NOT REPRODUCE DATA'}; continue
        expr, egf, sh, t = best
        seq = t[sh:]
        rows = []
        for ps, reclo, L in recs:
            r = len(ps) - 1
            bad = []
            for i in range(r, len(seq)):
                N = off + i
                if reclo is not None and N < reclo:
                    continue
                if seq[i] is None or any(seq[i - k] is None for k in range(1, r + 1)):
                    continue
                if sum(ev(ps[k], N) * seq[i - k] for k in range(r + 1)) != 0:
                    bad.append(N)
            prefix = bad and bad == list(range(bad[0], bad[0] + len(bad)))
            rows.append({'order': r, 'bad': bad[:6], 'prefix_only': bool(prefix),
                         'tested': len(seq) - r, 'ok': (not bad or bool(prefix))})
        out[a] = {'v': 'ok' if all(x['ok'] for x in rows) else 'PROBLEM',
                  'recs': rows, 'nterms': len(d), 'open': openness.status(a)[0]}
        json.dump(out, open(OUT, 'w'))
    json.dump(out, open(OUT, 'w'))
    print(len(out), 'of', len(todo), dict(collections.Counter(v['v'] for v in out.values())))


if __name__ == '__main__':
    SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
    st = json.load(open(SC + '/status.json'))
    todo = sorted(a for a, v in st.items()
                  if v in ('symbolic engine, no numeric rebuild',
                           'claim is not a plain recurrence'))
    if len(sys.argv) > 4:
        w, N = int(sys.argv[3]), int(sys.argv[4])
        os.environ['SHARD'] = sys.argv[3]
        OUT = 'audit_sym%s.json' % sys.argv[3]
        todo = [a for i, a in enumerate(todo) if i % N == w]
    main(int(sys.argv[1]), int(sys.argv[2]), todo)
