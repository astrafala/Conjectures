import json, re, os, collections
import sympy
import localentry as LE, transfer80 as T, ratrec, openness, gfrec

HITS, DONE = 'transfer80_hits.json', 'transfer80_done.json'
names = json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                       'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
hits = json.load(open(HITS)) if os.path.exists(HITS) else []
done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
res = collections.Counter()
n_ = sympy.Symbol('n')
CLOSED = re.compile(r'a\(n\)\s*=\s*(.+?)(?:\s+for\s+n\s*[>=].*)?\s*\.?\s*$')


def closed_lines(src):
    out = []
    for L in src:
        if 'a(n-' in L or 'G.f' in L:
            continue
        if not re.search(r'onjectur|Empirical', L, re.I) and 'Barker' not in L:
            pass
        m = CLOSED.search(L)
        if m and 'n' in m.group(1) and 'a(' not in m.group(1):
            body = re.sub(r'\s*-\s*_[^_]+_,.*$', '', m.group(1)).strip().rstrip('.')
            if re.fullmatch(r'[-+*/()0-9n^. ]+', body):
                out.append((L, body))
    return out


for a in sorted(names):
    if a in done:
        continue
    p = T.parse_name(names[a])
    if not p:
        res['name unparsed'] += 1; done.add(a); continue
    if a in roster:
        res['already papered'] += 1; done.add(a); continue
    if not openness.status(a)[0]:
        res['not open'] += 1; done.add(a); continue
    b = T.build(p)
    if b is None:
        res['neighbour graph disconnected'] += 1; done.add(a); continue
    e = LE.get(a)
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    off = int(e['offset'].split(',')[0])
    model = T.terms(b, max(len(d) - 1, b['bound'] + 2 - off), off)
    if model[:len(d)] != d:
        res['does not match DATA'] += 1; done.add(a); continue
    N, C = T.line(b)
    val = lambda m: N * m + C
    thr = 0
    for m in range(b['bound'], off - 1, -1):
        if model[m - off] != val(m):
            thr = m + 1
            break
    src = e['comment'] + e['formula']

    settled, failed = [], []
    for L, body in closed_lines(src):
        try:
            ex = sympy.sympify(body.replace('^', '**'), locals={'n': n_}, rational=True)
        except Exception:
            continue
        if sympy.simplify(ex - (N * n_ + C)) == 0:
            settled.append(('closed form', L.strip()))
        else:
            failed.append(('closed form', L.strip()))
    for L in src:
        # the family writes "Empirical g.f.: ..." and "Conjectured g.f.: ...", which the
        # shared parser refuses because it looks for a bare "G.f.:" and then rejects any body
        # carrying the word. Strip the marker and the line is an ordinary g.f. line.
        LL = re.sub(r'^\s*(?:Empirical|Conjectur\w*)\s*[:,]?\s*(?=G\.f\.)', '', L,
                    flags=re.I)
        g = gfrec.parse_gf(LL)
        if g is None:
            continue
        ser = gfrec.series(g, len(d) + 6)
        if ser is None:
            continue
        want = [0] * off + [val(m) if m >= thr else model[m - off]
                            for m in range(off, len(ser))]
        if all(sympy.Integer(want[i]) == ser[i] for i in range(len(ser))):
            settled.append(('generating function', L.strip()))
        else:
            failed.append(('generating function', L.strip()))
    for L in src:
        if 'a(n-' not in L:
            continue
        r = ratrec.parse_rec(L)
        if not r:
            continue
        coeffs, dd = r
        order = max(coeffs)
        bad = [m for m in range(max(thr + order, off + order), b['bound'] + 40)
               if val(m) != sum(int(c) * val(m - i) for i, c in coeffs.items())]
        (settled if not bad else failed).append(('recurrence', L.strip()))

    if failed:
        res['a conjectured statement is FALSE'] += 1
        hits.append({'anum': a, 'FAILS': True, 'name': names[a], 'failed': failed})
        done.add(a); continue
    if not settled:
        res['nothing conjectural to settle'] += 1; done.add(a); continue
    res['PROVED'] += 1
    hits.append({'anum': a, 'name': names[a], 'K': p['K'], 'd': p['d'], 'kind': p['kind'],
                 'dirs': p['dirs'], 'D': b['D'], 'bound': b['bound'], 'slope': N,
                 'intercept': C, 'thr': thr, 'offset': off, 'nterms': len(d),
                 'settled': settled})
    done.add(a)
    json.dump(hits, open(HITS, 'w'), indent=1)
    json.dump(sorted(done), open(DONE, 'w'))
    print('done', a, res['PROVED'], len(settled), 'statements', flush=True)

json.dump(hits, open(HITS, 'w'), indent=1)
json.dump(sorted(done), open(DONE, 'w'))
print(dict(res))
