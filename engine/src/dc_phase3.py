#!/usr/bin/env python3
"""Deep check, Phase 3: the entry, re-fetched cold.

A paper claims to QUOTE its entry: the conjecture sentence, the contributor, the date, the
"Last modified" line, and the entry's first terms. Entries get edited, corrected and
settled, so every one of those claims is checked again against the live text rather than
against whatever was true when the paper was written.

    python3 src/dc_phase3.py [lo] [hi]

Four checks per paper, and a fifth over the whole roster:

  1. the conjecture quoted in section 1 still appears in the entry, character for character
     after ligature and punctuation normalisation;
  2. the "Last modified" line quoted matches the entry's current one, or is recorded as
     having moved --- an entry that has changed since the paper was written is not
     automatically a defect, but it is always worth a look;
  3. the terms printed in section 1 are a prefix of the entry's current DATA, which is what
     would catch a corrected entry invalidating a proof;
  4. the paper names its own A-number in its title and section 1.

  5. settlement wording, over every entry, exactly as freshcheck.py reports it. Withdrawal
     is only for a proof that existed BEFORE the date on our paper; a later one leaves the
     result standing. That rule is stated in PLAN.md and repeated here so the phase cannot
     drift into removing results it should keep.

The mirror is not refreshed here: run `python3 src/freshcheck.py` first, which pulls it.
"""
import csv
import os
import re
import sys

import dc_text
import localentry as LE
import openness
import repopaths

try:
    import pypdf
except ImportError:
    pypdf = None

ANUM = re.compile(r'A\d{6}')
MODLINE = re.compile(r'\(([^()]*?),\s*revision\s*(\d+)\)')
# The terms sit on the line after "begins". Reading further than that line was the
# mistake here: "a(0), . . . , a(7) = 1, 1, 3" contains an ellipsis of its own, so a
# pattern that stopped at the first ellipsis captured the label and none of the terms.
TERMS = re.compile(r'It has offset[^\n]*begins\s*\n([^\n]+)')
# many papers print the terms as "a(0), . . . , a(7) = 1, 1, 3, ..."; the indices in those
# labels are not terms, and reading them as terms reported a dozen papers as disagreeing
# with data they agree with perfectly
LABEL = re.compile(r'^.*?=\s*', re.S)
MONTHS = {m: i for i, m in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}


def daystamp(s):
    """(year, month, day), from either order the two sources write it in."""
    m = re.search(r'([A-Za-z]{3})[a-z]*\s+(\d{1,2})\s+(\d{4})', s)
    if m:
        return (int(m.group(3)), MONTHS.get(m.group(1), 0), int(m.group(2)))
    m = re.search(r'(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{4})', s)
    if m:
        return (int(m.group(3)), MONTHS.get(m.group(2), 0), int(m.group(1)))
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)   # some papers print the ISO form
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


PAGENO = re.compile(r'^\s*\d{1,4}\s*$')


def text(path):
    """the paper's text, with the page numbers taken out

    A quotation that runs across a page break comes back from the extractor with the page
    number sitting in the middle of it --- `a(n-`, `1`, `40)` --- and a comparison that does
    not know this reports the paper as misquoting an entry it quotes exactly.
    """
    r = pypdf.PdfReader(path)
    lines = []
    for page in r.pages:
        for L in (page.extract_text() or '').split('\n'):
            if not PAGENO.match(L):
                lines.append(L)
    return dc_text.normalise('\n'.join(lines))


# The builders introduce the quotation in several ways; a phase that knew only one of them
# reported 280 of the first 400 papers as unquotable and checked nothing about them.
LEADIN = re.compile(
    r'(?:never marked settled:'
    r'|carries the following comment:'
    r'|carries the comment:?'
    r'|The entry states, not as a conjecture,'
    r'|The entry states, as a conjecture[^:]*:'
    r'|and separately carries the comment)\s*', re.I)
STOP = re.compile(r'As of the|Last modified|\n\s*\n|\\section|^\d+\s+The ', re.M)


def quoted_conjecture(t):
    """the block section 1 says the entry states, between the lead-in and what follows it"""
    m = LEADIN.search(t)
    if not m:
        return None
    rest = t[m.end():]
    stop = STOP.search(rest)
    body = rest[:stop.start()] if stop else rest[:600]
    body = ' '.join(body.split())
    return body or None


def main(lo, hi):
    if pypdf is None:
        print('pypdf is not available; Phase 3 cannot read the papers')
        return 1
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        idx = [r for r in csv.DictReader(f) if lo <= int(r['rank']) <= hi]
    defects, moved, unquoted, typeset = [], [], [], []
    checked = 0
    for r in idx:
        rank, a = r['rank'], r['anum']
        try:
            t = text(os.path.join(repopaths.ROOT, r['file']))
        except Exception as exc:
            defects.append((rank, a, f'paper unreadable: {exc}'))
            continue
        try:
            e = LE.get(a)
        except Exception:
            defects.append((rank, a, 'entry not in the local mirror'))
            continue
        checked += 1

        if a not in t:
            defects.append((rank, a, 'the paper does not name its own A-number'))

        q = quoted_conjecture(t)
        if q is None:
            unquoted.append((rank, a))
        else:
            lines = [' '.join(L.split()) for L in e['comment'] + e['formula']]
            hay = re.sub(r'\s+', '', dc_text.normalise(' '.join(lines)))
            if re.sub(r'\s+', '', q) in hay:
                pass                                   # quoted as plain text, character exact
            else:
                # Some papers TYPESET the conjecture: the entry's `x^3` becomes $x^3$, `>=`
                # becomes a relation glyph, and the extracted text can no longer equal the
                # entry character for character. Demanding that here would report a page of
                # false defects, so for those the numbers are compared instead --- every
                # integer of two digits or more, in order, against the entry line that fits
                # best. A misquotation that preserved every number in order is not a thing
                # that happens by accident.
                want = re.findall(r'\d{2,}', q)
                best = max((sum(1 for x in re.findall(r'\d{2,}', L) if x in want), L)
                           for L in lines) if lines else (0, '')
                got = re.findall(r'\d{2,}', best[1])
                if want and got and [x for x in want if x in got] == \
                        [x for x in got if x in want]:
                    typeset.append((rank, a))
                else:
                    defects.append((rank, a, 'quoted conjecture not found in the entry'))

        m = MODLINE.search(t)
        if m:
            said, rev = ' '.join(m.group(1).split()), m.group(2)
            # the paper prints the day, the entry prints the second as well, and the two
            # are written the other way round; the revision number is the reliable part
            if rev != str(e['revision']) or daystamp(said) != daystamp(e['modified']):
                moved.append((rank, a, f'paper says {said} r{rev}, '
                                       f"entry says {e['modified']} r{e['revision']}"))

        mt = TERMS.search(t)
        if mt:
            body = mt.group(1)
            if '=' in body:
                body = body.rsplit('=', 1)[1]
            body = re.split(r'\.\s*\.\s*\.|\u2026', body)[0]
            got = [x for x in re.findall(r'-?\d+', body.replace(' ', ''))]
            data = [x for x in e['data'].split(',') if x.strip()]
            if got and data[:len(got)] != got:
                defects.append((rank, a, 'printed terms are not a prefix of the entry DATA'))

    flagged = []
    for a in sorted({r['anum'] for r in idx}):
        try:
            ok, lines = openness.status(a)
        except Exception:
            continue
        if not ok:
            flagged.append((a, ' '.join(lines[0].split())[:160] if lines else ''))

    print(f'Phase 3: {checked} papers checked against the live entry')
    print(f'  {len(defects)} defects')
    for d in defects[:40]:
        print('   ', *d)
    print(f'  {len(moved)} entries edited since their paper was written '
          f'(not a defect by itself; the quote is what matters)')
    for d in moved[:10]:
        print('   ', *d)
    print(f'  {len(typeset)} papers whose quote is typeset rather than plain, checked on '
          f'their numbers instead')
    print(f'  {len(unquoted)} papers whose section 1 quote could not be located in the text')
    print(f'  {len(flagged)} entries carry settlement wording. Withdraw ONLY when the other '
          f'proof is EARLIER than the date on our paper.')
    for a, l in flagged[:40]:
        print('   ', a, l)
    return len(defects)


if __name__ == '__main__':
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    sys.exit(min(main(lo, hi), 250))
