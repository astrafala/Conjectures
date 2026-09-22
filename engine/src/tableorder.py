#!/usr/bin/env python3
"""Tables that name an order their own column entries contradict.

    python3 src/tableorder.py            # scan, write deep-check/tableorder.json
    python3 src/tableorder.py --report   # re-read the scan and print it

A269637 is where this came from. Its parent table A269640 prints, in one block,

    Empirical for column k:
    k=1: a(n) = 2*a(n-1) -2*a(n-3) +a(n-4)
    ...
    k=5: [order 13]

--- the full line where it is short, a PLACEHOLDER naming only the order where it is long.
A269637 is column 5 of that table and publishes an order-10 line. Two places on the OEIS
disagree about the same recurrence, and the disagreement is visible without computing
anything: the column entry's line failed at all ten indices its own published DATA could
test it, and 13 is the right answer.

So the scan is: for every table that names an order for column k (or row n), find the entry
that says it IS column k of that table, and compare. A mismatch is not a disproof --- it is
a place where one of two published statements must be wrong, which is exactly the shape that
is worth an hour of hand-checking. The cost is one pass over the clone and no arithmetic.

Three kinds of disagreement are reported separately, because they are not equally strong:

  ORDER     the table says [order N], the member's own line has a different order
  COEFF     both print a full line for the same thing and the coefficients differ
  ABSENT    the table names an order and the member entry carries no recurrence at all
            (not a contradiction --- a conjecture nobody wrote down, and the table says
            what order to look for)
"""
import json
import os
import re
import sys

SEQ = '/home/user/oeis/oeisdata/seq'
OUT = 'deep-check/tableorder.json'

# "%F A269640 k=5: [order 13]"  /  "%F A269640 k=1: a(n) = 2*a(n-1) -2*a(n-3) +a(n-4)"
FLINE = re.compile(r'^%F (A\d{6}) ([kn])=(\d+):\s*(.*)$')
# "%C A269637 Column 5 of A269640."
MEMBER = re.compile(r'^%C (A\d{6}) (Column|Row) (\d+) of (A\d{6})')
# the placeholder is written four ways: "[order 13]" (4974 of them), "[linear recurrence of
# order 11]" (423), "[same order 9]" (79) and "[same linear recurrence of order 7]" (19). Only
# the first was matched at first, which silently dropped 521 pairs -- among them the k=1 line
# of the very block that carries the one new candidate this scan found.
ORDERPH = re.compile(r'^\[(?:same )?(?:linear recurrence of )?order (\d+)[\],;]')
# "[polynomial of degree 6]" is a different claim, not an order, and is not read here.
TERM = re.compile(r'([+-]?)\s*(\d*)\s*\*?\s*a\(n-(\d+)\)')


PROSE = re.compile(r'\brecurrence of order (\d+)', re.I)


def rec_order(rhs):
    """the order of a recurrence written the way the OEIS writes one, or None

    A column entry does not always print its recurrence. When the line is long the entry
    writes prose instead --- A269765 carries "Empirical recurrence of order 26 (see link
    above)" and nothing else --- and reading only lines that contain a(n-k) counted those
    entries as carrying no conjecture at all. They carry the same conjecture the table does.
    """
    p = PROSE.search(rhs)
    if p:
        return int(p.group(1))
    m = re.search(r'a\(n\)\s*=\s*(.*)', rhs)
    if not m:
        return None
    body = re.split(r'\bfor\s+n\s*[><=]', m.group(1))[0]
    ks = [int(k) for _, _, k in TERM.findall(body)]
    return max(ks) if ks else None


def readings(stated, g):
    """every order the table's placeholder can reasonably be naming.

    A table block is not always written in the column entry's own units. A263913's columns
    alternate with zeros, so its lines are written in a(n-2), a(n-4), ... and its column
    entries count (2n+2)X(k+2) arrays --- one term per two rows --- so "[order 12]" there is
    order 6 on the entry. Read raw, all four of its columns looked like a contradiction of
    exactly a factor of two.

    Dividing by the stride unconditionally is the same mistake in the other direction: it
    turned fourteen agreeing pairs into disagreements, because a short column can have only
    even lags without the block being in double units at all. So this follows the rule the
    index convention already forced (defect 59): report a contradiction only when NO
    reasonable reading agrees.
    """
    r = {stated}
    if g > 1:
        r.add(stated * g)
        if stated % g == 0:
            r.add(stated // g)
    return r


def step(block):
    """the stride of a table block, which is not always 1.

    A263913's columns alternate with zeros, so its table lines are written in a(n-2),
    a(n-4), ... and a placeholder "[order 12]" there means order 6 in the COLUMN ENTRY's own
    indexing --- the column entry counts (2n+2)X(4+2) arrays, one term per two rows of the
    table. Reported raw, all four of its columns looked like contradictions of exactly a
    factor of two, and every one was this. The stride is visible in the block itself: take
    the gcd of the lags of the lines the table does print in full.
    """
    g = 0
    for rhs in block.values():
        for k in (coeffs(rhs) and [i + 1 for i, c in enumerate(coeffs(rhs)) if c] or []):
            g = k if not g else _gcd(g, k)
    return g or 1


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def coeffs(rhs):
    m = re.search(r'a\(n\)\s*=\s*(.*)', rhs)
    if not m:
        return None
    body = re.split(r'\bfor\s+n\s*[><=]', m.group(1))[0]
    co = {}
    for sgn, num, k in TERM.findall(body):
        c = int(num) if num else 1
        co[int(k)] = co.get(int(k), 0) + (-c if sgn == '-' else c)
    if not co:
        return None
    return [co.get(i, 0) for i in range(1, max(co) + 1)]


def scan():
    tables, member, own, name = {}, {}, {}, {}
    nfile = 0
    for d in sorted(os.listdir(SEQ)):
        dp = os.path.join(SEQ, d)
        if not os.path.isdir(dp):
            continue
        for f in sorted(os.listdir(dp)):
            if not f.endswith('.seq'):
                continue
            nfile += 1
            a = f[:-4]
            for line in open(os.path.join(dp, f), errors='ignore'):
                if line.startswith('%F '):
                    m = FLINE.match(line.rstrip('\n'))
                    if m:
                        tables.setdefault(m.group(1), {})[(m.group(2), int(m.group(3)))] = \
                            m.group(4).strip()
                    elif 'a(n-' in line or PROSE.search(line):
                        own.setdefault(a, []).append(line.split(None, 2)[2].strip())
                elif line.startswith('%C '):
                    m = MEMBER.match(line.rstrip('\n'))
                    if m:
                        axis = 'k' if m.group(2) == 'Column' else 'n'
                        member[(m.group(4), axis, int(m.group(3)))] = m.group(1)
                elif line.startswith('%N '):
                    name[a] = line.split(None, 2)[2].strip()
    print('%d files, %d tables with per-column lines, %d column/row members'
          % (nfile, len(tables), len(member)))
    return tables, member, own, name


def main():
    tables, member, own, name = scan()
    hits = {'ORDER': [], 'COEFF': [], 'ABSENT': []}
    pairs = 0
    for t, block in tables.items():
        for (axis, idx), rhs in block.items():
            a = member.get((t, axis, idx))
            if not a:
                continue
            pairs += 1
            mine = own.get(a) or []
            ph = ORDERPH.match(rhs)
            if ph:
                stated = int(ph.group(1))
                orders = [o for o in (rec_order(l) for l in mine) if o]
                if not orders:
                    hits['ABSENT'].append({'table': t, 'axis': axis, 'idx': idx,
                                           'anum': a, 'stated': stated,
                                           'stride': step(block),
                                           'name': name.get(a, '')})
                elif not (readings(stated, step(block)) & set(orders)):
                    hits['ORDER'].append({'table': t, 'axis': axis, 'idx': idx,
                                          'anum': a, 'stated': stated, 'own': orders,
                                          'lines': mine, 'name': name.get(a, '')})
            else:
                tc = coeffs(rhs)
                if tc is None:
                    continue
                mc = [c for c in (coeffs(l) for l in mine) if c]
                if mc and tc not in mc:
                    hits['COEFF'].append({'table': t, 'axis': axis, 'idx': idx, 'anum': a,
                                          'table_line': rhs, 'lines': mine,
                                          'name': name.get(a, '')})
    os.makedirs('deep-check', exist_ok=True)
    json.dump(hits, open(OUT, 'w'), indent=1, sort_keys=True)
    print('%d table/member pairs compared' % pairs)
    for k in ('ORDER', 'COEFF', 'ABSENT'):
        print('  %-7s %d' % (k, len(hits[k])))
    print('-> ' + OUT)
    for h in hits['ORDER'][:15]:
        print('   %s is %s=%d of %s: table says order %d, entry says %s'
              % (h['anum'], h['axis'], h['idx'], h['table'], h['stated'], h['own']))


if __name__ == '__main__':
    if '--report' in sys.argv:
        h = json.load(open(OUT))
        for k in ('ORDER', 'COEFF', 'ABSENT'):
            print('%s: %d' % (k, len(h[k])))
    else:
        main()
