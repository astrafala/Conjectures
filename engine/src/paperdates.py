#!/usr/bin/env python3
"""The date each paper was written, taken from the paper itself.

The date a result was obtained is what shows the work came first, so it has to be
available for every paper --- including the 181 whose LaTeX source is not in the
repository. Every paper prints its date under the author, so the paper is the source of
record and the .tex is only a convenience. Reading it out of the PDF also means the date
cannot drift away from what the paper actually says.
"""
import csv
import json
import os
import re
import sys

import pypdf

import repopaths
import singleton

CACHE = os.path.join(repopaths.ROOT, 'engine', 'paper-dates.json')
MONTHS = ('January February March April May June July August September October '
          'November December').split()
DATE = re.compile(r'\b(?:([0-9]{1,2})\s+)?(' + '|'.join(MONTHS) + r')\s+(20[0-9]{2})\b')
BYLINE = re.compile(r'Independent [Rr]esearcher')


def from_pdf(path):
    """the date line a paper prints under its author, or None"""
    try:
        page = pypdf.PdfReader(path).pages[0].extract_text() or ''
    except Exception as e:                      # a PDF that will not open is a defect,
        print(f'  unreadable {path}: {e}')      # but it is Phase 1's defect, not this one
        return None
    page = page.replace('\n', ' ')
    by = BYLINE.search(page)        # the date in the title block, not the first date on
    if by:                          # the page: nine papers quote a contributor's date
        page = page[by.end():]      # in the abstract, and it was winning the race
    m = DATE.search(page)
    if not m:
        return None
    day, month, year = m.groups()
    return '%d %s %s' % (int(day), month, year) if day else '%s %s' % (month, year)


def rows():
    """the published index of papers: rank, A-number, verdict, engine, file

    Keyed on the index rather than on engine/paper-engines.json, whose keys are the
    internal numbering a paper was given when it was built and not its rank. Reading the
    roster as though its keys were ranks reports nine thousand mismatches that are not
    there.
    """
    with open(os.path.join(repopaths.ROOT, 'papers', 'index.csv')) as f:
        return list(csv.DictReader(f))


# The date belongs to the PAPER, not to the slot it currently sits in. Keying the cache by
# file path meant every re-ranking moved every paper and forced all ten thousand PDFs to be
# read again -- many minutes of work to recover dates that had not changed. This second cache
# is keyed by A-number and verdict, which a re-ranking does not touch, so a run after a
# ranking reads only the papers that are new.
BYPAPER = os.path.join(repopaths.ROOT, 'engine', 'paper-dates-by-anum.json')


def build(index):
    """paper path (repository-relative) -> the date printed in that paper"""
    known = json.load(open(BYPAPER)) if os.path.exists(BYPAPER) else {}
    out, fresh = {}, 0
    for row in index:
        key = f"{row['anum']}-{row['verdict']}"
        d = known.get(key)
        if d is None:
            d = from_pdf(os.path.join(repopaths.ROOT, row['file']))
            fresh += 1
            if d:
                known[key] = d
        if d:
            out[row['file']] = d
    json.dump(known, open(BYPAPER, 'w'), indent=0, sort_keys=True)
    print(f'  {fresh} read from the PDF, {len(out) - fresh} taken from the cache')
    return out


def load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}


if __name__ == '__main__':
    singleton.claim('paperdates')
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 10 ** 9)
    part = [r for r in rows() if lo <= int(r['rank']) <= hi]
    got = build(part)
    out = CACHE if lo == 1 and hi > 10 ** 6 else CACHE.replace('.json', f'-{lo}.json')
    json.dump(got, open(out, 'w'), indent=0, sort_keys=True)
    print(f'{len(got)} of {len(part)} papers dated -> {os.path.basename(out)}')
