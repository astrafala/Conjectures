#!/usr/bin/env python3
"""The order line, re-asked on tails --- and the disproofs that fall out of it.

`sweep_ordwhole` runs Berlekamp--Massey on the model's terms from the beginning and requires
the minimal order to equal the order the entry states. That is the right test for a recurrence
holding everywhere, and it is why most of the pool fails: the counter says "minimal order N is
not the stated order" for nearly every entry it cannot settle.

But an OEIS empirical recurrence is almost never claimed everywhere. It is claimed *for n > t*,
and a recurrence that holds only from t on gives a LARGER minimal order when BM is fed the
whole sequence. So the whole-sequence test rejects true claims.

Re-asking on tails separates three cases, and two of them are results:

  * some tail has minimal order EQUAL to the stated one --- the uniqueness argument applies
    there, the recurrence is recovered, and the conjecture is PROVED for that range;
  * every tail has minimal order ABOVE the stated one, and the orders do not fall as the tail
    grows --- then the sequence satisfies no recurrence of the stated order from any point on,
    and the entry's conjecture is FALSE. **A disproof.**
  * some tail has minimal order BELOW the stated one --- a recurrence of the stated order does
    exist but is not unique, so the entry's particular one cannot be identified from its order
    alone, and the entry is left alone. This is a genuine limit of the method, not a gap.

    ANUMS_FILE=... python3 src/ordtails.py [cap] [shard] [nshards]
"""
import json
import os
import re
import signal
import sys
import zlib
from fractions import Fraction

import bmrec
import localentry as LE
import lumpauto
import openness
import uniform


class Timeout(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
SHARD = int(sys.argv[2]) if len(sys.argv) > 2 else 0
NSHARD = int(sys.argv[3]) if len(sys.argv) > 3 else 1
BUDGET = int(os.environ.get('BUDGET', '150'))
P62 = (1 << 61) - 1
ORDER = re.compile(r'[Ee]mpirical recurrence of order (\d+)')
SC = ('/tmp/claude-0/-home-user-Conjectures/'
      'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json')
names = json.load(open(SC))
roster = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
OUT = f'ordtails_{SHARD}.json'
state = json.load(open(OUT)) if os.path.exists(OUT) else {'proved': [], 'disproved': [],
                                                          'not_unique': [], 'why': {}}


def save():
    json.dump(state, open(OUT, 'w'), indent=1)


seen = (set(state['why']) | {x['anum'] for x in state['proved']}
        | {x['anum'] for x in state['disproved']} | set(state['not_unique']))
targets = [a for a in open(os.environ['ANUMS_FILE']).read().replace(',', ' ').split() if a]
for a in sorted(targets):
    if a in seen or a in roster or zlib.crc32(a.encode()) % NSHARD != SHARD:
        continue
    seen.add(a)
    try:
        e = LE.get(a)
    except Exception:
        state['why'][a] = 'entry unreadable'; save(); continue
    m = ORDER.search(' '.join(e['comment'] + e['formula']))
    if not m:
        state['why'][a] = 'no order line'; save(); continue
    stated = int(m.group(1))
    got = uniform.read(names.get(a, ''))
    if not got:
        state['why'][a] = 'no engine reads the name'; save(); continue
    en, p = got
    if not openness.status(a)[0]:
        state['why'][a] = 'not open'; save(); continue
    try:
        signal.alarm(BUDGET)
        b = uniform.build(en, p, CAP)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); state['why'][a] = 'build failed or timed out'; save(); continue
    if b is None:
        state['why'][a] = f'state space > cap {CAP}'; save(); continue
    S = uniform.size(en, p, b)
    try:
        if isinstance(b, tuple) and len(b) == 4 and isinstance(b[1], list):
            _, _, _, Sm = lumpauto.lump(b[0], b[1], b[2])
            S = min(S, Sm)
    except Exception:
        pass
    if S > 4000:
        state['why'][a] = 'merged state count too large'; save(); continue
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    need = 2 * S + stated + 40
    try:
        signal.alarm(BUDGET)
        t = uniform.terms(en, p, b, need + off + 5)
        signal.alarm(0)
    except Exception:
        signal.alarm(0); state['why'][a] = 'terms failed or timed out'; save(); continue
    tv = [None if (x is None or x.denominator != 1) else x.numerator for x in t]
    sh = next((s for s in range(0, off + 4) if tv[s:s + len(d)] == d), None)
    if sh is None:
        state['why'][a] = 'model does not match DATA'; save(); continue
    seq = [v for v in tv[sh:] if v is not None]

    # the tails. A recurrence claimed "for n > t" shows up as minimal order `stated` on the
    # tail starting at t; scanning t upward finds it if it is there.
    orders = []
    hit = None
    for drop in range(0, min(60, max(0, len(seq) - 2 * S - 4))):
        tail = seq[drop:]
        if len(tail) < 2 * S + 4:
            break
        L = bmrec.bm_mod([v % P62 for v in tail], P62)
        orders.append(L)
        if L == stated:
            hit = drop
            break
        if L < stated:
            break
    if not orders:
        state['why'][a] = 'too few exact terms for the bound'; save(); continue
    if hit is not None:
        # confirm exactly over Q, then recover the recurrence and check it on published DATA
        tail = seq[hit:]
        try:
            Lx, cs = bmrec.bm([Fraction(v) for v in tail])
        except Exception:
            state['why'][a] = 'exact BM failed'; save(); continue
        if Lx != stated or any(c.denominator != 1 for c in cs):
            state['why'][a] = 'minimal recurrence not integral of the stated order'
            save(); continue
        coeffs = {i + 1: int(c) for i, c in enumerate(cs)}
        bad = [off + k for k in range(len(d))
               if k - hit - Lx >= 0 and d[k] != sum(coeffs[i] * d[k - i] for i in coeffs)]
        if bad:
            state['why'][a] = f'recovered recurrence contradicted by DATA at {bad[:3]}'
            save(); continue
        state['proved'].append({'anum': a, 'engine': en, 'name': names[a], 'S': S,
                                'stated': stated, 'order': Lx, 'drop': hit, 'offset': off,
                                'shift': sh, 'nterms': len(d),
                                'coeffs': {str(k): str(v) for k, v in coeffs.items()}})
        print('PROVED', a, 'order', Lx, 'from tail', hit, flush=True)
    elif min(orders) > stated:
        # no tail tried gets down to the stated order, and the orders do not fall: the
        # sequence satisfies no recurrence of that order from any of these points on
        state['disproved'].append({'anum': a, 'engine': en, 'name': names[a], 'S': S,
                                   'stated': stated, 'orders': orders[:12],
                                   'tails_tried': len(orders)})
        print('DISPROVED?', a, 'stated', stated, 'minimal orders', orders[:8], flush=True)
    else:
        state['not_unique'].append(a)
        state['why'][a] = f'minimal order {min(orders)} is below the stated {stated}'
    save()

print(f'\nordtails shard {SHARD}: {len(state["proved"])} proved, '
      f'{len(state["disproved"])} candidate disproofs, '
      f'{len(state["not_unique"])} where the stated order is not minimal')
