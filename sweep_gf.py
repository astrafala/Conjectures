"""Conjectured recurrences that follow from a generating function the entry records as fact."""
import json, re, os, collections, signal
import sympy
import localentry as LE, ratrec, openness, gfrec


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
BUDGET = int(os.environ.get('BUDGET', '30'))
P = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/'
names = json.load(open(P + 'all_names.json'))
roster = {r['anum'] for r in json.load(open('rank-map.json'))}
HITS, DONE = 'gf_hits.json', 'gf_done.json'
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
CONJ = re.compile(r'\b(conjecture|conjectured|conjecturally|empirical)\b', re.I)
REC = re.compile(r'a\(n\)\s*=.*a\(n\s*-\s*\d+\)')


def save():
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))


for a in sorted(names):
    if a in done or a in roster:
        continue
    e = LE.get(a)
    lines = e['comment'] + e['formula']
    conj = [L for L in lines if CONJ.search(L) and REC.search(L)]
    if not conj:
        continue
    recs = [r for r in (ratrec.parse_rec(L) for L in conj) if r]
    if not recs:
        continue
    gfl = [(L, g) for L, g in ((L, gfrec.parse_gf(L)) for L in lines if not CONJ.search(L))
           if g is not None]
    if not gfl:
        res['no usable generating function'] += 1; done.add(a); save(); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    coeffs, dd = recs[0]
    order = max(coeffs)
    hit = None
    for L, g in gfl:
        try:
            signal.alarm(BUDGET)
            s = gfrec.series(g, len(d) + off + 2)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); continue
        except Exception:
            signal.alarm(0); continue
        if s is None:
            continue
        # the g.f. usually starts at the entry's offset, but not always: pin it on the data
        sh = None
        for cand in (off, 0):
            if cand + len(d) <= len(s) and all(
                    s[cand + k] == d[k] for k in range(len(d))):
                sh = cand; break
        if sh is None:
            continue
        try:
            signal.alarm(BUDGET)
            deg = gfrec.residual_degree(g, coeffs)
            signal.alarm(0)
        except Timeout:
            signal.alarm(0); continue
        except Exception:
            signal.alarm(0); continue
        if deg is None:
            continue
        # a(n) - sum c_i a(n-i) = [x^(n - off + sh)] D(x)G(x), zero past the degree
        nthr = deg + off - sh
        bad = [off + k for k in range(len(d))
               if off + k > nthr and k - order >= 0 and
               d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items())]
        if bad:
            res['claim contradicted by DATA'] += 1
            hits.append({'anum': a, 'FAILS': True, 'name': names[a], 'bad': bad[:3]})
            hit = 'bad'
            break
        hit = {'anum': a, 'name': names[a], 'gfline': L.strip(), 'gf': sympy.srepr(g),
               'gftex': sympy.latex(g), 'order': order, 'offset': off, 'shift': sh,
               'nthr': nthr, 'deg': deg, 'nterms': len(d), 'claimed': dd,
               'conj': conj[0].strip(),
               'coeffs': {int(k): str(v) for k, v in coeffs.items()}}
        break
    if hit is None:
        res['g.f. does not imply the recurrence'] += 1
    elif hit != 'bad':
        res['PROVED'] += 1
        hits.append(hit)
        print('done', a, res['PROVED'], flush=True)
    done.add(a); save()
save()
print(dict(res))
