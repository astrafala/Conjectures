#!/usr/bin/env python3
"""Build ../comments — the proposed OEIS comments, one section per entry.

These are NOT in the papers, and should not be: a paper is a proof and stays a proof. This is
the separate place where each result is written out as a comment that could be posted on the
OEIS entry it settles, together with the entry it belongs to, the date the result was obtained,
and a link to the paper that proves it.

The date matters. A comment posted on an OEIS entry is stamped with the day it is posted, not
the day the result was found; recording the date here is what shows the work came first.
"""
import os, re, sys, json, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperpath as P
import paperdates
import repopaths
import localentry as LE

CHUNK = 400
MARK = re.compile(r'onjectur|Empirical', re.I)
MONTH = {m: i for i, m in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
     'September', 'October', 'November', 'December'], 1)}


def conj_lines(a):
    """the entry's own unsettled lines, verbatim from the OEIS text"""
    try:
        e = LE.get(a)
    except Exception:
        return []
    return [' '.join(L.split()) for L in e['comment'] + e['formula'] if MARK.search(L)][:3]


def sortable(d):
    """a date, orderable; a month with no day sorts before every dated day in that month

    Nine of the earliest papers print only a month. Treating those as undated sent the very
    first work in the project to the bottom of a list whose whole purpose is to show what came
    first, so a month-only date sorts at day 0 of its month.
    """
    m = re.match(r'(\d+)\s+([A-Za-z]+)\s+(\d{4})', d or '')
    if m:
        return (int(m.group(3)), MONTH.get(m.group(2), 0), int(m.group(1)))
    m = re.match(r'([A-Za-z]+)\s+(\d{4})', d or '')
    return (int(m.group(2)), MONTH.get(m.group(1), 0), 0) if m else (9999, 0, 0)


def dates_and_papers():
    """A-number -> the papers settling it, each with the date it was written.

    The date is read out of the paper itself (engine/paper-dates.json), because the paper
    is what is published and 181 papers have no LaTeX source left. The source is consulted
    only to corroborate; if the two disagree the paper wins and the disagreement is
    printed, since a date that cannot be corroborated is worth less than no date at all.
    """
    rm = json.load(open('rank-map.json'))
    printed = paperdates.load()
    # nine of the earliest papers print a month with no day. The day is not guessed: the
    # first commit that carries the paper bounds it, and that bound is recorded instead.
    gitday = (json.load(open(os.path.join(repopaths.ROOT, 'engine', 'paper-dates-git.json')))
              if os.path.exists(os.path.join(repopaths.ROOT, 'engine',
                                             'paper-dates-git.json')) else {})
    by = collections.defaultdict(list)
    clash = 0
    for m in rm:
        rel = f"papers/{P.band(m['rank'])}/{P.name(m['rank'], m['verdict'])}"
        tex = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
               f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
        d = printed.get(rel)
        if os.path.exists(tex):
            mm = re.search(r'\\date\{([^}]*)\}', open(tex, errors='ignore').read())
            if mm and d and ' '.join(mm.group(1).split()) != d:
                clash += 1
            elif mm and not d:
                d = mm.group(1).strip()
        seen = gitday.get(rel) if d and len(d.split()) == 2 else None
        by[m['anum']].append({'rank': m['rank'], 'path': rel, 'date': d, 'since': seen})
    if clash:
        print(f'  {clash} papers whose source disagrees with the date the paper prints')
    return by


def main():
    comments = json.load(open('oeis-comments.json'))
    papers = dates_and_papers()
    rows = []
    for a in sorted(set(comments) | set(papers)):
        recs = [r for r in comments.get(a, []) if r.get('comment')]
        ps = sorted(papers.get(a, []), key=lambda x: sortable(x['date']))
        rows.append({'anum': a, 'recs': recs, 'papers': ps,
                     'date': ps[0]['date'] if ps else None,
                     'since': ps[0].get('since') if ps else None})
    out = repopaths.doc('comments')
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(('.md', '.csv')):
            os.remove(os.path.join(out, f))
    chunks = [rows[i:i + CHUNK] for i in range(0, len(rows), CHUNK)]
    names = {}
    for ch in chunks:
        nm = f"{ch[0]['anum']}-{ch[-1]['anum']}.md"
        for r in ch:
            names[r['anum']] = nm
    with open(f'{out}/index.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['entry', 'date_result_obtained', 'papers', 'comment_available', 'file'])
        for r in rows:
            w.writerow([r['anum'], r['date'] or '',
                        ' '.join(p['path'] for p in r['papers']),
                        'yes' if r['recs'] else 'no', 'comments/' + names[r['anum']]])
    # A second view of the same rows, ordered by the day the result was obtained rather
    # than by A-number. This is the priority record: the earliest work is at the top, and
    # everything found before this repository existed sits in the first block.
    order = sorted(rows, key=lambda r: (sortable(r['date']), r['anum']))
    D = ['# What was found, and when', '',
         'Every settled entry in the order it was settled, earliest first. The date is the '
         'date printed on the paper, which is the day the proof was written --- not the day '
         'anything was posted anywhere.', '',
         'The first block is the earliest work, done before this repository was started; the '
         'nine papers there print a month rather than a day, so the day is not guessed and '
         'the first commit carrying the paper is given as the bound instead.', '',
         'A comment posted on an OEIS entry is stamped with the day it is posted. This file '
         'is the record of when the work was actually done, and it is what shows the result '
         'came first.', '']
    cur = None
    for r in order:
        if r['date'] != cur:
            cur = r['date']
            n = sum(1 for x in order if x['date'] == cur)
            D += ['', f'## {cur}  ({n} {"entry" if n == 1 else "entries"})', '']
        ps = ', '.join(f"[{q['rank']}](../{q['path']})" for q in r['papers'])
        note = f" --- in the repository since {r['since']}" if r.get('since') else ''
        D.append(f"- [{r['anum']}](https://oeis.org/{r['anum']})"
                 f" --- paper {ps}{note}")
    open(f'{out}/by-date.md', 'w').write('\n'.join(D) + '\n')

    withc = sum(1 for r in rows if r['recs'])
    for ch in chunks:
        nm = f"{ch[0]['anum']}-{ch[-1]['anum']}.md"
        L = [f"# Proposed OEIS comments: {ch[0]['anum']} to {ch[-1]['anum']}", '',
             'One section per OEIS entry: the date the result was obtained, the paper that '
             'proves it, what the entry still records as unsettled, and the text proposed for '
             'posting on that entry.', '',
             '**Nothing here has been posted.** See [../SUBMITTING.md](../SUBMITTING.md).',
             '', '---', '']
        for r in ch:
            a = r['anum']
            L += [f'## {a}', '', f'OEIS entry: <https://oeis.org/{a}>  ']
            if r['date']:
                extra = (f" (in the repository since {r['since']})" if r.get('since') else '')
                L.append(f"Result obtained: **{r['date']}**{extra}  ")
            if r['papers']:
                L.append('Paper: ' + ', '.join(f"[{p['rank']}](../{p['path']})"
                                               for p in r['papers']))
            L.append('')
            cj = conj_lines(a)
            if cj:
                L += ['What the entry records as unsettled:', '']
                L += [f'> {c}' for c in cj]
                L.append('')
            if not r['recs']:
                L += ['*No comment drafted for this entry.*', '']
            for rec in r['recs']:
                L += ['Proposed OEIS comment:', '', '```', rec['comment'], '```', '']
            L += ['---', '']
        open(f'{out}/{nm}', 'w').write('\n'.join(L) + '\n')
    idx = ['# Proposed OEIS comments', '',
           f'A proposed comment for each of the **{withc}** settled entries, written to be '
           'posted on the OEIS entry it belongs to. They are kept here rather than in the '
           'papers: a paper is a proof and stays a proof.', '',
           'Each section names the entry, **the date the result was obtained**, the paper that '
           'proves it, and what the entry still records as unsettled. The date is the point: an '
           'OEIS comment is stamped with the day it is posted, so the date here is what shows '
           'when the work was actually done.', '',
           '**None of these has been posted.** How to post them, and why not all at once, is in '
           '[../SUBMITTING.md](../SUBMITTING.md).', '',
           '`index.csv` lists every entry with its date, its paper and the file its comment is '
           'in. **[by-date.md](by-date.md)** lists every entry in the order it was settled, '
           'earliest first --- the priority record, with the work done before this repository '
           'existed at the top.', '',
           'If a conjecture is settled by somebody else after the date recorded here, nothing '
           'is removed: the date stands, and the result was still obtained first. A result is '
           'withdrawn only if it turns out to have been settled BEFORE that date, which would '
           'mean it was never ours to claim.', '',
           '| Entries | Count |', '| --- | ---: |']
    for ch in chunks:
        idx.append(f"| [{ch[0]['anum']} – {ch[-1]['anum']}]"
                   f"({ch[0]['anum']}-{ch[-1]['anum']}.md) | {len(ch)} |")
    open(f'{out}/README.md', 'w').write('\n'.join(idx) + '\n')
    print(f'{len(rows)} entries, {withc} with a comment, in {len(chunks)} files')


if __name__ == '__main__':
    main()
