#!/usr/bin/env python3
"""Cell conditions over an explicit alphabet, two-line window, no relabelling.

Three name shapes, all saying the same kind of thing about every cell of the array:

  * "each element equal to the number of its horizontal and vertical neighbors unequal to
    itself"                                        -- the cell's VALUE is the neighbour count
  * "every element equal to 0, 1 or 4 horizontally, vertically or antidiagonally adjacent
    elements, with upper left element zero"        -- the count lies in a stated set
  * "each 1 adjacent to 0 or 2 king-move neighboring 1s"
    "every 1 horizontally, diagonally or antidiagonally adjacent to 1 neighboring 1"
                                                   -- the same, imposed only on the cells
                                                      carrying a stated value

Every neighbour set here reaches one line up and one line down, so the vertices are ordered
pairs of consecutive lines, (p,c) -> (c,x) is an edge when every cell of c passes with p
above and x below, and the first and last lines are tested with one neighbour line missing.
"""
import re
import namecanon
from itertools import product
import transfer6 as T6

H = [(0, -1), (0, 1)]
V = [(-1, 0), (1, 0)]
D = [(-1, -1), (1, 1)]
A = [(-1, 1), (1, -1)]
NUM = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
       'seven': 7, 'eight': 8, 'no': 0}


def _nums(s):
    out = []
    for t in re.findall(r'[a-z]+|\d+', s.lower()):
        if t in ('or', 'and', ','):
            continue
        if t in NUM:
            out.append(NUM[t])
        elif t.isdigit():
            out.append(int(t))
        else:
            return None
    return sorted(set(out)) or None


DIRS = {'horizontal': H, 'vertical': V, 'diagonal': D, 'antidiagonal': A,
        'horizontally': H, 'vertically': V, 'diagonally': D, 'antidiagonally': A,
        'nw-se': D, 'ne-sw': A, 'nwse': D, 'nesw': A}


def _nbset(txt):
    """'horizontally, vertically or antidiagonally' / 'king-move' -> offsets."""
    t = txt.strip().lower()
    if t in ('king-move', 'king move'):
        return H + V + D + A
    words = [w for w in re.split(r'[,\s]+|\bor\b|\band\b', t) if w]
    offs = []
    for w in words:
        if w not in DIRS:
            return None
        for o in DIRS[w]:
            if o not in offs:
                offs.append(o)
    return offs or None


DIRWORDS = r'(?:king-move|(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?' \
           r'(?:[,\s]+(?:or\s+|and\s+)?(?:horizontal|vertical|diagonal|antidiagonal)(?:ly)?)*)'

SELF = re.compile(r'(?:each|every) element equal to the number (?:of )?its (' + DIRWORDS +
                  r') neighbou?rs (equal|unequal) to itself', re.I)
COUNT = re.compile(r'(?:each|every) element (equal|unequal) to ([\w,\s]+?) (' + DIRWORDS +
                   r') adjacent elements(, with upper left element zero)?', re.I)
VALUE = re.compile(r'(?:each|every) (\d+) (?:(' + DIRWORDS + r') )?adjacent to ([\w,\s]+?) '
                   r'(?:(' + DIRWORDS + r') )?(?:neighbou?ring )?(\d+)s?', re.I)
TABLE = re.compile(r'(?:each|every) element x equal to the number (?:of )?its (' + DIRWORDS +
                   r') neighbou?rs equal to ([\d,\s]+) for x=([\d,\s]+)', re.I)
MAJOR = re.compile(r'no element (less than|greater than|equal to) a strict majority of its ('
                   + DIRWORDS + r') neighbou?rs', re.I)
SOMECMP = re.compile(r'every (nonzero )?element (less than or equal to|greater than or equal '
                     r'to|less than|greater than) some (' + DIRWORDS + r') neighbou?r', re.I)
SHIFT = re.compile(r'no entry increasing mod (\d+) by (\d+) rightwards or downwards, '
                   r'starting with upper left zero', re.I)
OFFLIST = r'((?:\(-?\d+,-?\d+\)[\s,]*(?:or\s*)?)+)'
NOADJ = re.compile(r'(?:top left (?:element equal to|value) (\d+) and )?no two '
                   r'(\d+s|ones|zeros|twos|threes) adjacent ([a-z, \-]+)', re.I)
GRAPH = re.compile(r'\d+\.\.\d+ label nodes of (?:a graph with edges ([\d,\s]+)|'
                   r'(the square grid graph)) and every array movement to a (' + DIRWORDS +
                   r') neighbou?r moves along an edge of this graph', re.I)
PATT = re.compile(r'without the pattern ((?:\d+\s+)+\d+) (' + DIRWORDS + r')', re.I)
MODNEXT = re.compile(r'(?:each|every) element (' + DIRWORDS + r') next to at least one '
                     r'element with value (?:\(x\(i,j\)\+(\d+)\) mod (\d+)|'
                     r'(\d+)-x\(i,j\))((?:,? (?:with|and) upper left element zero)?)', re.I)
CMPSELF = re.compile(r'(?:each|every) element equal to the number (?:of )?its (' + DIRWORDS +
                     r') neighbou?rs (less than or equal to|greater than or equal to|'
                     r'less than|greater than) itself', re.I)
BOTH = re.compile(r'every element both equal and not equal to some elements at offset '
                  + OFFLIST + r', with upper left element zero', re.I)
PLUSMOD = re.compile(r'every element plus (\d+) mod (\d+) equal to some element at offset '
                     + OFFLIST + r', with upper left element zero', re.I)


def _offlist(txt):
    return [(int(x), int(y)) for x, y in re.findall(r'\((-?\d+),(-?\d+)\)', txt)]


def _cond(rest):
    low = rest.strip().rstrip('.').lower()
    m = NOADJ.fullmatch(low)
    if m:
        ulv, valw, dirs = m.groups()
        val = {'ones': 1, 'zeros': 0, 'twos': 2, 'threes': 3}.get(valw)
        if val is None:
            val = int(valw.rstrip('s'))
        offs = _nbset(dirs)
        if offs is None:
            return None
        offs = [(dt, du) for dt, du in offs if dt > 0 or (dt == 0 and du > 0)]
        return {'mode': 'noadjval', 'offs': offs, 'val': val, 'ul0': False,
                'ulval': None if ulv is None else int(ulv),
                'tex': (r'\text{no two cells both equal to }' + str(val) +
                        r'\text{ are adjacent along an offset of }\mathcal N')}
    m = GRAPH.fullmatch(low)
    if m:
        edges, grid, dirs = m.groups()
        offs = _nbset(dirs)
        if offs is None:
            return None
        offs = [(dt, du) for dt, du in offs if dt > 0 or (dt == 0 and du > 0)]
        if edges:
            nums = [int(t) for t in re.findall(r'\d+', edges)]
            if len(nums) % 2:
                return None
            E = {frozenset((nums[i], nums[i + 1])) for i in range(0, len(nums), 2)}
            tx = r'\{' + ','.join('\\{%d,%d\\}' % tuple(sorted(e)) for e in
                                 sorted(map(sorted, E))) + r'\}'
        else:
            E, tx = 'grid', r'\text{the square grid graph}'
        return {'mode': 'graph', 'offs': offs, 'edges': E, 'ul0': False,
                'tex': (r'\{x_{t,u},x_{t+d_1,u+d_2}\}\in E\ \text{ for every offset in }'
                        r'\mathcal N,\quad E=' + tx)}
    m = PATT.fullmatch(low)
    if m:
        pat = [int(t) for t in m.group(1).split()]
        offs = _nbset(m.group(2))
        if offs is None or len(pat) not in (2, 3):
            return None
        dirs = []
        for dt, du in offs:
            if dt > 0 or (dt == 0 and du > 0):
                dirs.append((dt, du))
        return {'mode': 'patt', 'offs': dirs, 'pat': pat, 'ul0': False,
                'tex': (r'\text{no }' + ','.join(map(str, pat)) +
                        r'\text{ occurs consecutively along any direction in }\mathcal N')}
    m = MODNEXT.fullmatch(low)
    if m:
        dirs, dd, mod, cst, ul0 = m.groups()
        offs = _nbset(dirs)
        if offs is None:
            return None
        if dd is not None:
            f = lambda v, d=int(dd), md=int(mod): (v + d) % md
            tx = r'(x_{t,u}+' + dd + r')\bmod ' + mod
        else:
            f = lambda v, c=int(cst): c - v
            tx = cst + r'-x_{t,u}'
        return {'mode': 'modnext', 'offs': offs, 'f': f, 'ul0': bool(ul0),
                'tex': r'\exists\ \text{a neighbour with value }' + tx}
    m = CMPSELF.fullmatch(low)
    if m:
        dirs, rel = m.groups()
        offs = _nbset(dirs)
        if offs is None:
            return None
        f = {'less than or equal to': lambda y, v: y <= v,
             'greater than or equal to': lambda y, v: y >= v,
             'less than': lambda y, v: y < v, 'greater than': lambda y, v: y > v}[rel]
        sy = {'less than or equal to': r'\le', 'greater than or equal to': r'\ge',
              'less than': '<', 'greater than': '>'}[rel]
        return {'mode': 'cmpself', 'offs': offs, 'cmpf': f, 'ul0': False,
                'tex': r'x_{t,u}=\#\{\text{neighbours }y:\ y' + sy + r'x_{t,u}\}'}
    m = BOTH.fullmatch(low)
    if m:
        offs = _offlist(m.group(1))
        if not offs or any(abs(dt) > 1 for dt, _ in offs):
            return None
        return {'mode': 'both', 'offs': offs, 'ul0': True,
                'tex': (r'\exists\ \text{a neighbour }y=x_{t,u}\ \text{ and }\ '
                        r'\exists\ \text{a neighbour }y\ne x_{t,u}')}
    m = PLUSMOD.fullmatch(low)
    if m:
        dd, mod = int(m.group(1)), int(m.group(2))
        offs = _offlist(m.group(3))
        if not offs or any(abs(dt) > 1 for dt, _ in offs):
            return None
        return {'mode': 'plusmod', 'offs': offs, 'd': dd, 'mod': mod, 'ul0': True,
                'tex': (r'\exists\ \text{a neighbour }y\ \text{with}\ '
                        r'y\equiv x_{t,u}+' + str(dd) + r'\ (\mathrm{mod}\ ' + str(mod)
                        + r')')}
    m = TABLE.fullmatch(low)
    if m:
        offs = _nbset(m.group(1))
        tgt = [int(t) for t in re.findall(r'\d+', m.group(2))]
        xs = [int(t) for t in re.findall(r'\d+', m.group(3))]
        if not offs or xs != list(range(len(xs))) or len(tgt) != len(xs):
            return None
        return {'mode': 'table', 'offs': offs, 'tbl': tgt, 'ul0': False,
                'tex': (r'\#\{\text{neighbours with value }f(x_{t,u})\}=x_{t,u},\quad '
                        r'f=(' + ','.join(map(str, tgt)) + r')')}
    m = MAJOR.fullmatch(low)
    if m:
        rel, dirs = m.groups()
        offs = _nbset(dirs)
        if not offs:
            return None
        f = {'less than': lambda w, v: w > v, 'greater than': lambda w, v: w < v,
             'equal to': lambda w, v: w == v}[rel]
        sy = {'less than': '>', 'greater than': '<', 'equal to': '='}[rel]
        return {'mode': 'major', 'offs': offs, 'cmpf': f, 'ul0': False,
                'tex': (r'2\,\#\{\text{neighbours }y\text{ with }y' + sy +
                        r'x_{t,u}\}\le\#\{\text{neighbours}\}')}
    m = SOMECMP.fullmatch(low)
    if m:
        nz, rel, dirs = m.groups()
        offs = _nbset(dirs)
        if not offs:
            return None
        f = {'less than or equal to': lambda v, w: v <= w,
             'greater than or equal to': lambda v, w: v >= w,
             'less than': lambda v, w: v < w, 'greater than': lambda v, w: v > w}[rel]
        sy = {'less than or equal to': r'\le', 'greater than or equal to': r'\ge',
              'less than': '<', 'greater than': '>'}[rel]
        return {'mode': 'some', 'offs': offs, 'cmpf': f, 'nz': bool(nz), 'ul0': False,
                'tex': ((r'x_{t,u}\ne0\ \Rightarrow\ ' if nz else '') +
                        r'\exists\ \text{a neighbour }y:\ x_{t,u}' + sy + r'y')}
    m = SHIFT.fullmatch(low)
    if m:
        mod, dd = int(m.group(1)), int(m.group(2))
        return {'mode': 'shift', 'offs': [(0, 1), (1, 0)], 'mod': mod, 'd': dd, 'ul0': True,
                'tex': (r'x_{t,u+1}\ne x_{t,u}+' + str(dd) + r'\ (\mathrm{mod}\ ' +
                        str(mod) + r')\ \text{ and }\ x_{t+1,u}\ne x_{t,u}+' + str(dd) +
                        r'\ (\mathrm{mod}\ ' + str(mod) + r')')}
    m = SELF.fullmatch(low)
    if m:
        offs = _nbset(m.group(1))
        if not offs:
            return None
        uneq = m.group(2) == 'unequal'
        return {'mode': 'self', 'offs': offs, 'uneq': uneq, 'ul0': False,
                'tex': (r'x_{t,u}=\#\{\text{neighbours with a value }'
                        + ('different from' if uneq else 'equal to') + r'\ x_{t,u}\}')}
    m = COUNT.fullmatch(low)
    if m:
        sense, nums, dirs, ul0 = m.groups()
        offs = _nbset(dirs)
        v = _nums(nums)
        if not offs or not v:
            return None
        return {'mode': 'count', 'offs': offs, 'uneq': sense == 'unequal',
                'set': v, 'ul0': bool(ul0),
                'tex': (r'\#\{\text{neighbours with a value }'
                        + ('different from' if sense == 'unequal' else 'equal to')
                        + r'\ x_{t,u}\}\in\{' + ','.join(map(str, v)) + r'\}')}
    m = VALUE.fullmatch(low)
    if m:
        val, d1, nums, d2, val2 = m.groups()
        if val != val2:
            return None
        offs = _nbset(d1 or d2 or 'king-move')
        v = _nums(nums)
        if not offs or not v or (d1 and d2):
            return None
        return {'mode': 'value', 'offs': offs, 'val': int(val), 'set': v, 'ul0': False,
                'tex': (r'x_{t,u}=' + val + r'\ \Rightarrow\ \#\{\text{neighbours equal to }'
                        + val + r'\}\in\{' + ','.join(map(str, v)) + r'\}')}
    return None


def parse_name(nm):
    nm = namecanon.canon(nm)   # 'a(n) is the number of ...' and friends
    norm = re.sub(r'(\bn|\d|\))\s*[xX]\s*(?=[\d(n])', r'\1 X ', nm)
    norm = re.sub(r'\s+', ' ', norm).strip().rstrip('.')
    # several families carry a descriptive title before a colon
    title = ''
    mt = re.match(r'^([^:]{1,90}):\s*', norm)
    if mt:
        title = mt.group(1)
        norm = norm[mt.end():]
    frac = 1
    m = T6.FRAC.match(norm)
    if m:
        frac = 2 if m.group(1) else (4 if m.group(0).lower().startswith('one quarter')
                                     else int(m.group(2)))
        norm = norm[m.end():]
    else:
        m = T6.HEAD.match(norm)
        if not m:
            return None
        norm = norm[m.end():]
    from transfer8 import SHAPE2, _dim
    m = SHAPE2.match(norm)
    if not m:
        return None
    d1, d2 = _dim(m.group(1)), _dim(m.group(2))
    alpha = 1 if m.group(5) else int(m.group(4))
    rest = norm[m.end():].strip().rstrip('.')
    if d1[0] == 'n' and d2[0] == 'c':
        walk, fixed, base, mult = 'rows', d2[1], d1[1], d1[2]
    elif d2[0] == 'n' and d1[0] == 'c':
        walk, fixed, base, mult = 'cols', d1[1], d2[1], d2[2]
    else:
        return None
    c = _cond(rest)
    if not c:
        return None
    if c.get('edges') == 'grid':
        mg = re.search(r'(\d+)\s*X\s*(\d+)\s+square grid graph', title, re.I)
        if not mg:
            return None
        R, C = int(mg.group(1)), int(mg.group(2))
        if R * C != alpha + 1:
            return None
        E = set()
        for i in range(R):
            for j in range(C):
                k = i * C + j
                if j + 1 < C:
                    E.add(frozenset((k, k + 1)))
                if i + 1 < R:
                    E.add(frozenset((k, k + C)))
        c['edges'] = E
        c['tex'] = c['tex'].replace(r'\text{the square grid graph}',
                                    rf'\text{{the {R}\times{C} grid graph}}')
    if walk == 'cols':
        c = dict(c, offs=[(du, dt) for dt, du in c['offs']])
    c.update({'walk': walk, 'fixed': fixed, 'base': base, 'mult': mult, 'alpha': alpha,
              'frac': frac, 'rest': rest})
    return c


def _nbvals(above, cur, below, u, W, offs):
    out = []
    for dt, du in offs:
        uu = u + du
        if not (0 <= uu < W):
            continue
        L = cur if dt == 0 else (above if dt < 0 else below)
        if L is None:
            continue
        out.append(L[uu])
    return out


def cell_ok(above, cur, below, u, W, p):
    v = cur[u]
    mode = p['mode']
    if mode == 'table':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return sum(1 for y in vals if y == p['tbl'][v]) == v
    if mode == 'major':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return 2 * sum(1 for y in vals if p['cmpf'](y, v)) <= len(vals)
    if mode == 'some':
        if p['nz'] and v == 0:
            return True
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return any(p['cmpf'](v, y) for y in vals)
    if mode == 'noadjval':
        if v != p['val']:
            return True
        for dt, du in p['offs']:
            uu = u + du
            if not (0 <= uu < W):
                continue
            L = cur if dt == 0 else (below if dt > 0 else above)
            if L is None:
                continue
            if L[uu] == v:
                return False
        return True
    if mode == 'graph':
        for dt, du in p['offs']:
            uu = u + du
            if not (0 <= uu < W):
                continue
            L = cur if dt == 0 else (above if dt < 0 else below)
            if L is None:
                continue
            y = L[uu]
            if p['edges'] == 'grid':
                if abs(y - v) != 1:
                    return False
            elif frozenset((v, y)) not in p['edges']:
                return False
        return True
    if mode == 'patt':
        # the pattern is read along +(d1,d2), so position 0 sits at (t-d1,u-d2) and position
        # 2 at (t+d1,u+d2). A transposed name can leave d1 NEGATIVE, and taking `above` for
        # the first position regardless was wrong for exactly those.
        pat = p['pat']
        for dt, du in p['offs']:
            back = cur if dt == 0 else (above if dt > 0 else below)
            fwd = cur if dt == 0 else (below if dt > 0 else above)
            if len(pat) == 2:
                uu = u + du
                if not (0 <= uu < W) or fwd is None:
                    continue
                if v == pat[0] and fwd[uu] == pat[1]:
                    return False
            else:
                ub, uf = u - du, u + du
                if not (0 <= ub < W and 0 <= uf < W):
                    continue
                if back is None or fwd is None:
                    continue
                if v == pat[1] and back[ub] == pat[0] and fwd[uf] == pat[2]:
                    return False
        return True
    if mode == 'modnext':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return any(y == p['f'](v) for y in vals)
    if mode == 'cmpself':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return v == sum(1 for y in vals if p['cmpf'](y, v))
    if mode == 'both':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return any(y == v for y in vals) and any(y != v for y in vals)
    if mode == 'plusmod':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return any(y == (v + p['d']) % p['mod'] for y in vals)
    if mode == 'shift':
        vals = _nbvals(above, cur, below, u, W, p['offs'])
        return all(y != (v + p['d']) % p['mod'] for y in vals)
    if p['mode'] == 'value' and v != p['val']:
        return True
    eq = 0
    for dt, du in p['offs']:
        uu = u + du
        if not (0 <= uu < W):
            continue
        L = cur if dt == 0 else (above if dt < 0 else below)
        if L is None:
            continue
        if p['mode'] == 'value':
            if L[uu] == p['val']:
                eq += 1
        elif L[uu] == v:
            eq += 1
        elif p.get('uneq'):
            eq += 0
    if p['mode'] in ('self', 'count') and p.get('uneq'):
        tot = 0
        for dt, du in p['offs']:
            uu = u + du
            if not (0 <= uu < W):
                continue
            L = cur if dt == 0 else (above if dt < 0 else below)
            if L is None:
                continue
            tot += 1
        eq = tot - eq
    if p['mode'] == 'self':
        return v == eq
    return eq in p['set']


def line_ok(above, cur, below, W, p):
    return all(cell_ok(above, cur, below, u, W, p) for u in range(W))


def build(p, cap=200000):
    """Digraph on lines or on pairs of lines, whichever the offsets require.

    A condition whose offsets all point one way needs only ONE line of state: the cells of a
    line are settled by that line and its successor (or its predecessor). Only a condition
    reaching both up and down needs a pair. That is not a refinement for its own sake -- the
    graph-colouring names run over a nine-letter alphabet, where a pair state is 9^(2W) and a
    single line 9^W.
    """
    W, al = p['fixed'], p['alpha']
    lines = list(product(range(al + 1), repeat=W))
    offs = p['offs']
    # a length-three forbidden pattern is tested at its MIDDLE cell, so it reads one step in
    # each direction whatever the sign of the stated offset: the span, not the offset list,
    # decides how many lines of state are needed. Using the offsets here made every such
    # entry return the unconstrained count.
    if p['mode'] == 'patt' and len(p['pat']) == 3:
        offs = offs + [(-dt, -du) for dt, du in offs]
    fwd = all(dt >= 0 for dt, _ in offs)
    bwd = all(dt <= 0 for dt, _ in offs)
    if fwd or bwd:
        if len(lines) > cap:
            return None
        idx = {r: i for i, r in enumerate(lines)}
        adj, start, end = [], [], []
        for r in lines:
            row = []
            for s in lines:
                ok = line_ok(None, r, s, W, p) if fwd else line_ok(r, s, None, W, p)
                if ok:
                    row.append(idx[s])
            adj.append(row)
            uv = p.get('ulval')
            uv = 0 if (uv is None and p['ul0']) else uv
            if fwd:
                start.append(1 if (uv is None or r[0] == uv) else 0)
                end.append(1 if line_ok(None, r, None, W, p) else 0)
            else:
                start.append(1 if (line_ok(None, r, None, W, p)
                                   and (uv is None or r[0] == uv)) else 0)
                end.append(1)
        p['wlen'] = 1
        return adj, start, end, lines
    if len(lines) ** 2 > cap:
        return None
    idx, st = {}, []
    for a in lines:
        for b in lines:
            idx[(a, b)] = len(st)
            st.append((a, b))
    adj, start, end = [], [], []
    for (a, b) in st:
        row = []
        for x in lines:
            if line_ok(a, b, x, W, p):
                row.append(idx[(b, x)])
        adj.append(row)
        uv = p.get('ulval')
        uv = 0 if (uv is None and p['ul0']) else uv
        s = line_ok(None, a, b, W, p) and (uv is None or a[0] == uv)
        start.append(1 if s else 0)
        end.append(1 if line_ok(a, b, None, W, p) else 0)
    p['wlen'] = 2
    return adj, start, end, st


def matvec(adj, v):
    return [sum(v[t] for t in row) for row in adj]


def singles(p):
    W, al = p['fixed'], p['alpha']
    n = 0
    uv = p.get('ulval')
    uv = 0 if (uv is None and p['ul0']) else uv
    for r in product(range(al + 1), repeat=W):
        if line_ok(None, r, None, W, p) and (uv is None or r[0] == uv):
            n += 1
    return n


def avals(adj, start, end, p, nmax):
    mult, base, wl = p['mult'], p['base'], p.get('wlen', 2)
    Lmax = mult * nmax + base
    # an array with no lines: the empty array, counted once, which is what the entries with
    # offset 0 record as a(0)
    vals = {0: p['frac'], 1: singles(p)}
    g = end[:]
    L = wl
    while L <= Lmax:
        vals[L] = sum(s * x for s, x in zip(start, g) if s)
        g = matvec(adj, g)
        L += 1
    return [vals.get(mult * n + base) if mult * n + base >= 0 else None
            for n in range(nmax + 1)]


def threshold(adj, start, end, coeffs, order, p):
    import time as _t
    mult, base, wl = p['mult'], p['base'], p.get('wlen', 2)
    S = len(adj)
    n_lo = 0
    while mult * n_lo + base < wl:
        n_lo += 1
    o = mult * n_lo + base - wl
    h = end[:]
    for _ in range(o):
        h = matvec(adj, h)
    powers = [h]
    for _ in range(order):
        for _ in range(mult):
            h = matvec(adj, h)
        powers.append(h)
    w = powers[order][:]
    for i, c in coeffs.items():
        pw = powers[order - i]
        for j in range(S):
            w[j] -= c * pw[j]
    t0 = _t.time()
    us, zeros, j = [], 0, 0
    while zeros < S + 1 and j <= 2 * S + order + 8:
        if _t.time() - t0 > 420:
            return None
        u = sum(s * x for s, x in zip(start, w) if s)
        us.append(u)
        zeros = zeros + 1 if u == 0 else 0
        if not any(w):
            zeros = S + 1
            break
        for _ in range(mult):
            w = matvec(adj, w)
        j += 1
    if zeros < S + 1:
        return None
    last = max((i for i, u in enumerate(us) if u != 0), default=-1)
    return n_lo + order + last
