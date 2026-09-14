#!/usr/bin/env python3
"""The conjecture that is not in the entry.

228 entries outside the roster say only

    Empirical recurrence of order 42 (see link above).
    Empirical polynomial of degree 26 (see link above)

and the recurrence itself is in a linked a-file, `https://oeis.org/A279654/a279654.txt`:

    Empirical: a(n)=573*a(n-1)-130179*a(n-2)+... -35184372088832*a(n-42) for n>43

Every reader in this repository looks only at the entry's own text, so all 228 were refused
with "no parsable recurrence" -- and every one of them has a name an engine already reads.
That is the whole of the defect: not a missing engine, a missing fetch.

The local clone DOES carry these files, at `oeisdata/files/A279/a279654.txt`, but as Git LFS
pointers:

    version https://git-lfs.github.com/spec/v1
    oid sha256:dda0b1751a5304cc44ea590739d4db64f5dea0a9dbc1056ded6dd060

so opening the clone's copy settles nothing and, worse, looks like a file that is simply not a
recurrence. They are fetched once into `afiles/` and read from there; `ratrec.parse_rec` reads
the fetched line unchanged, at order 96 as readily as at order 2.
"""
import os
import re
import subprocess
import time

import ratrec

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'afiles')
DIR = os.path.normpath(DIR)
POINTS = re.compile(r'\(see link(?: above)?\)', re.I)
STATED = re.compile(r'Empirical\s+(recurrence|polynomial)\s+of\s+(?:order|degree)\s+(\d+)', re.I)
LFS = 'git-lfs.github.com'


def points_at_link(line):
    """does this conjectural line defer to the linked file?"""
    return bool(POINTS.search(line))


def stated(line):
    """('recurrence', 42) or ('polynomial', 26), as the entry itself states it, or None"""
    m = STATED.search(line)
    return (m.group(1).lower(), int(m.group(2))) if m else None


def path(a):
    return os.path.join(DIR, f'{a.lower()}.txt')


def text(a, fetch=False):
    """the a-file's contents, or None. Never returns an LFS pointer."""
    p = path(a)
    if os.path.exists(p):
        s = open(p, errors='replace').read()
        if s.strip() and LFS not in s[:80]:
            return s
    if not fetch:
        return None
    out = subprocess.run(['curl', '-sS', '-A', 'Mozilla/5.0',
                          f'https://oeis.org/{a}/{a.lower()}.txt'],
                         capture_output=True, text=True, timeout=120).stdout
    time.sleep(0.7)
    if not out or LFS in out[:80] or len(out) < 40:
        return None
    os.makedirs(DIR, exist_ok=True)
    open(p, 'w').write(out)
    return out


def recurrence(a, fetch=False):
    """(coeffs, first index claimed) from the linked file, or None.

    Only the FIRST line is read. The a-files in this family hold exactly one statement; a file
    that held several would need the caller to say which the entry means, and guessing which
    is the conjecture is precisely the mistake this module exists to stop making.
    """
    s = text(a, fetch)
    if not s:
        return None
    return ratrec.parse_rec(s.strip().split('\n')[0])


def agrees(a, line, rec=None):
    """does the linked recurrence have the order the ENTRY says it has?

    The entry's sentence and the linked file are two statements and they are not automatically
    the same one. If the file gives order 42 and the entry says 37, something is being read
    that the entry does not mean, and the pair is refused rather than reconciled.
    """
    rec = rec if rec is not None else recurrence(a)
    st = stated(line)
    if not rec or not st:
        return False
    kind, k = st
    return kind == 'recurrence' and max(rec[0]) == k
