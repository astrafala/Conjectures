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
    m = re.match(r'(\d+)\s+([A-Za-z]+)\s+(\d{4})', d or '')
    return (int(m.group(3)), MONTH.get(m.group(2), 0), int(m.group(1))) if m else (9999, 0, 0)


def dates_and_papers():
    rm = json.load(open('rank-map.json'))
    by = collections.defaultdict(list)
    for m in rm:
        rel = f"papers/{P.band(m['rank'])}/{P.name(m['rank'], m['verdict'])}"
        tex = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
               f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
        d = None
        if os.path.exists(tex):
            mm = re.search(r'\\date\{([^}]*)\}', open(tex, errors='ignore').read())
            if mm:
                d = mm.group(1).strip()
        by[m['anum']].append({'rank': m['rank'], 'path': rel, 'date': d})
    return by


def main():
    comments = json.load(open('oeis-comments.json'))
    papers = dates_and_papers()
    rows = []
    for a in sorted(set(comments) | set(papers)):
        recs = [r for r in comments.get(a, []) if r.get('comment')]
        ps = sorted(papers.get(a, []), key=lambda x: sortable(x['date']))
        rows.append({'anum': a, 'recs': recs, 'papers': ps,
                     'date': ps[0]['date'] if ps else None})
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
                L.append(f"Result obtained: **{r['date']}**  ")
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
           'in.', '',
           '| Entries | Count |', '| --- | ---: |']
    for ch in chunks:
        idx.append(f"| [{ch[0]['anum']} – {ch[-1]['anum']}]"
                   f"({ch[0]['anum']}-{ch[-1]['anum']}.md) | {len(ch)} |")
    open(f'{out}/README.md', 'w').write('\n'.join(idx) + '\n')
    print(f'{len(rows)} entries, {withc} with a comment, in {len(chunks)} files')


if __name__ == '__main__':
    main()
