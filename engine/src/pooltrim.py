#!/usr/bin/env python3
"""Remove from a candidate pool every entry that is not actually unsettled.

The pool of "entries with conjectural wording" is built by grepping the clone, and that is too
loose in two ways that both showed up at once on the 229 circular-digit entries: an entry can
carry the word "Empirical" on a comment that is not the conjecture anyone would settle, and an
entry can carry a LINK TO A PUBLISHED PROOF while still using the old wording. All 229 of those
had a 2026 paper linked from the entry proving exactly the recurrences and generating functions
a sweep would have gone after. Checking the pool before working it costs seconds; not checking
it would have cost 229 papers that were not mine to write.

    python3 src/pooltrim.py deep-check/unread-unsettled.txt
"""
import os
import re
import sys

ROOT = '/home/user/oeis/oeisdata/seq'
# a link whose title says a proof, or a comment saying the conjecture is now proved
PROOFLINK = re.compile(r'^%H .*(proof|proved|proves|proving)', re.I | re.M)
SETTLED = re.compile(r'^%[CF] .*(this is now (a )?(proved|theorem)|no longer a conjecture|'
                     r'proof of the conjecture|conjecture is (now )?(proved|true))', re.I | re.M)
# the conjecture wording that is worth a sweep: a recurrence, a g.f., or an order line
REAL = re.compile(r'^%[CF] .*(Conjectur|Empirical).*'
                  r'(a\(n\)\s*=|g\.f\.|recurrence of order)', re.I | re.M)


def keep(a):
    p = os.path.join(ROOT, a[:4], a + '.seq')
    try:
        t = open(p, errors='ignore').read()
    except OSError:
        return False, 'entry not in the clone'
    if PROOFLINK.search(t):
        return False, 'entry links a published proof'
    if SETTLED.search(t):
        return False, 'entry says the conjecture is settled'
    if not REAL.search(t):
        return False, 'no conjectured recurrence, g.f. or order line'
    return True, ''


if __name__ == '__main__':
    src = sys.argv[1]
    anums = [a for a in open(src).read().split() if a.startswith('A')]
    kept, why = [], {}
    for a in anums:
        ok, w = keep(a)
        if ok:
            kept.append(a)
        else:
            why[w] = why.get(w, 0) + 1
    out = src.replace('.txt', '-trimmed.txt')
    open(out, 'w').write('\n'.join(kept) + '\n')
    print(f'{len(anums)} in, {len(kept)} kept -> {out}')
    for w, n in sorted(why.items(), key=lambda x: -x[1]):
        print(f'  {n:6d}  {w}')
