#!/usr/bin/env python3
"""One-dimensional words under a window condition, with values introduced in order.

    Number of length n+3 0..2 arrays with no four elements in a row with pattern abba
    (possibly a=b) and new values 0..2 introduced in 0..2 order.

Nothing here is two-dimensional, which is why none of the eighty-odd array engines read a
single one of these: they all parse a shape like "n X 4" and there is no second dimension to
find. The object is a word, the condition is on a bounded window of consecutive letters, and
the count is therefore a walk count on the windows -- the same argument as everywhere else in
this repository, one dimension down.

Two clauses appear throughout and both are local:

* **a forbidden pattern.** "pattern abba" names a shape, not letters: a window matches when
  positions carrying the same letter of the pattern carry the same value. "(with a!=b)" also
  requires positions carrying different letters to differ; "(possibly a=b)" does not, so
  "possibly a=b" forbids strictly more words -- aaaa matches abba there and not in the strict
  reading.
* **"new values 0..m introduced in 0..m order".** The first occurrences must be 0, then 1,
  then 2, and so on, so a word may use value v only once v-1 has appeared. That is one extra
  number in the state: how many distinct values have been used.

The reading was pinned by direct enumeration before the engine was written. For A243027 the
length-4 words are the 14 restricted-growth words over three values, two of them (0000 and
0110) match abba with a=b, and the entry's first term is 12.
"""
import re
from itertools import product

import namecanon

NUM = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
       'one': 1, 'no': 0}
DIM = r'(?:n\s*\+\s*(\d+)|n)'
HEAD = re.compile(
    r'^\s*Number of length\s+' + DIM + r'\s+(\d+)\.\.(\d+)\s+arrays?\s+with\s+(.+?)\s*\.?\s*$',
    re.I)
PAT = re.compile(
    r'^no\s+(\w+)\s+(?:consecutive\s+)?elements?(?:\s+in a row)?(?:\s+consecutive)?'
    r'\s+with pattern\s+([a-z]+(?:\s+or\s+[a-z]+)*)\s*'
    r'\((?:with\s+)?(a\s*!=\s*b|possibly\s+a\s*=\s*b)\)$', re.I)
RGS = re.compile(r'^new values\s+\d+\.\.\d+\s+introduced in\s+\d+\.\.\d+\s+order$', re.I)
# "at most one downstep in every 3 consecutive neighbor pairs": a sliding window over the
# NEIGHBOUR PAIRS, not over the elements, so the window spans W+1 elements. Reading it as a
# global bound, or as a window of n pairs, both disagree with the entry's own terms -- which
# is how the right one was picked.
DOWN = re.compile(r'^at most\s+(\w+)\s+downsteps?\s+in every\s+(\w+)\s+consecutive '
                  r'neighbou?r pairs$', re.I)
SUM3 = re.compile(r'^no consecutive\s+(\w+)\s+elements? summing to more than\s+(\d+)$', re.I)
UNEQ = re.compile(r'^no\s+(\w+)\s+(unequal|equal)\s+elements? in a row$', re.I)


def _split(body):
    """the clauses, which are joined by ' and ' except inside a parenthesis"""
    out, depth, cur = [], 0, ''
    for tok in re.split(r'(\(|\)|\s+and\s+)', body):
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
        if re.fullmatch(r'\s+and\s+', tok or '') and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += tok or ''
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_name(nm):
    m = HEAD.match(namecanon.canon(re.sub(r'\s+', ' ', nm).strip()))
    if not m:
        return None
    base = int(m.group(1)) if m.group(1) else 0
    lo, hi = int(m.group(2)), int(m.group(3))
    if lo != 0 or hi < 1 or hi > 9:
        return None
    pats, rgs, down, sums = [], False, None, None
    for cl in _split(m.group(4)):
        cl = cl.strip().rstrip('.')
        q = PAT.match(cl)
        if q:
            k = NUM.get(q.group(1).lower())
            strict = '!=' in q.group(3)
            for p in re.split(r'\s+or\s+', q.group(2).strip()):
                if k is None or len(p) != k:
                    return None
                pats.append((p, strict))
            continue
        if RGS.match(cl):
            rgs = True
            continue
        q = DOWN.match(cl)
        if q:
            D = NUM.get(q.group(1).lower())
            Wd = NUM.get(q.group(2).lower())
            if Wd is None and q.group(2).isdigit():
                Wd = int(q.group(2))
            if D is None or Wd is None or Wd < 1 or Wd > 8:
                return None
            down = (D, Wd)
            continue
        q = SUM3.match(cl)
        if q:
            k = NUM.get(q.group(1).lower())
            if k is None or k > 6:
                return None
            sums = (k, int(q.group(2)))
            continue
        q = UNEQ.match(cl)
        if q:
            k = NUM.get(q.group(1).lower())
            if k is None:
                return None
            if q.group(2).lower() == 'equal':
                pats.append(('a' * k, False))
            else:
                # "no k unequal elements in a row": every window of k with all values
                # distinct is forbidden, which is the strict all-different pattern
                pats.append((''.join(chr(97 + i) for i in range(k)), True))
            continue
        return None
    if not pats and down is None and sums is None:
        return None
    W = max([len(p) for p, _ in pats] + ([down[1] + 1] if down else [])
            + ([sums[0]] if sums else []))
    if W > 7 or (hi + 1) ** (W - 1) > 200000:
        return None
    return {'base': base, 'alpha': hi + 1, 'pats': tuple(pats), 'rgs': rgs, 'W': W,
            'down': down, 'sums': sums, 'frac': 1}


def _matches(win, pat, strict):
    k = len(pat)
    for x in range(k):
        for y in range(x + 1, k):
            if pat[x] == pat[y] and win[x] != win[y]:
                return False
            if strict and pat[x] != pat[y] and win[x] == win[y]:
                return False
    return True


def _win_ok(win, p):
    """is this window of consecutive letters allowed by every clause?"""
    for pt, st in p['pats']:
        if len(pt) <= len(win) and _matches(win[-len(pt):], pt, st):
            return False
    d = p.get('down')
    if d is not None:
        D, Wd = d
        if len(win) >= Wd + 1:
            tail = win[-(Wd + 1):]
            if sum(1 for i in range(Wd) if tail[i] > tail[i + 1]) > D:
                return False
    sm = p.get('sums')
    if sm is not None:
        k, cap_ = sm
        if len(win) >= k and sum(win[-k:]) > cap_:
            return False
    return True


def build(p, cap=200000):
    A, W, rgs = p['alpha'], p['W'], p['rgs']
    if A ** (W - 1) > cap:
        return None
    # a state is the last W-1 letters, plus how many distinct values have been used when the
    # values must be introduced in order
    states, index = [], {}

    def sid(s):
        i = index.get(s)
        if i is None:
            i = index[s] = len(states)
            states.append(s)
        return i

    # start states: the words of length W-1 that are themselves admissible
    starts = {}
    for w in product(range(A), repeat=W - 1):
        used = 0
        ok = True
        if rgs:
            for v in w:
                if v > used:
                    ok = False
                    break
                if v == used:
                    used += 1
        else:
            used = A
        if not ok:
            continue
        if any(not _win_ok(w[:i + 1], p) for i in range(len(w))):
            continue
        starts[sid((w, used))] = starts.get(sid((w, used)), 0) + 1

    adj = {}
    queue = list(starts)
    seen = set(queue)
    while queue:
        if len(states) > cap:
            return None
        i = queue.pop()
        w, used = states[i]
        row = []
        top = min(used, A - 1) if rgs else A - 1
        for v in range(top + 1):
            nw = w + (v,)
            if not _win_ok(nw, p):
                continue
            nu = used + 1 if (rgs and v == used) else used
            j = sid((nw[1:], nu))
            row.append(j)
            if j not in seen:
                seen.add(j)
                queue.append(j)
        adj[i] = row
    S = len(states)
    ivec = [0] * S
    for i, c in starts.items():
        ivec[i] = c
    return {'adj': [adj.get(i, []) for i in range(S)], 'ivec': ivec, 'S': S, 'W': W}


def terms(b, N):
    """a(L) for L = 0, 1, 2, ... : the number of admissible words of length L"""
    S, W = b['S'], b['W']
    out = [0] * (W - 1)
    out.append(sum(b['ivec']))                    # length W-1
    v = list(b['ivec'])
    for _ in range(N):
        nv = [0] * S
        for i, row in enumerate(b['adj']):
            if v[i]:
                for j in row:
                    nv[j] += v[i]
        v = nv
        out.append(sum(v))
    return out


def threshold(b, coeffs, order):
    S = b['S']
    t = terms(b, 2 * S + order + 8)
    last, run = None, 0
    for j in range(order + 1, len(t)):
        u = t[j] - sum(c * t[j - i] for i, c in coeffs.items())
        if u:
            last, run = j, 0
        else:
            run += 1
    if run < S:
        return None
    return last if last is not None else 0
