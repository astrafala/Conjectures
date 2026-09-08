#!/usr/bin/env python3
"""Write the one file that settles a priority dispute.

MANIFEST.tsv lists every result in the roster with the OEIS entry it settles, the verdict,
the date the paper prints, and the SHA-256 of the PDF as it stands in this commit. Anyone can
recompute those hashes from the repository and check that the file is honest; and because the
manifest itself is committed and can be stamped, the whole roster is fixed to a date by one
short file rather than by eleven thousand.

    python3 src/manifest.py
"""
import hashlib
import json
import os

import repopaths


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    rank = json.load(open('rank-map.json'))
    dates = json.load(open('paper-dates.json')) if os.path.exists('paper-dates.json') else {}
    rows = []
    for r in sorted(rank, key=lambda x: x['rank']):
        p = r['path']
        if not os.path.exists(p):
            continue
        rel = os.path.relpath(p, repopaths.ROOT)
        rows.append((r['rank'], r['anum'], r['verdict'], r['engine'],
                     dates.get(rel, ''), rel, sha(p)))
    out = os.path.join(repopaths.ROOT, 'MANIFEST.tsv')
    with open(out, 'w') as fh:
        fh.write('rank\tA-number\tverdict\targument\tpaper date\tpath\tsha256\n')
        for row in rows:
            fh.write('\t'.join(str(x) for x in row) + '\n')
    digest = hashlib.sha256(open(out, 'rb').read()).hexdigest()
    with open(os.path.join(repopaths.ROOT, 'MANIFEST.sha256'), 'w') as fh:
        fh.write(f'{digest}  MANIFEST.tsv\n')
    print(f'{len(rows)} results listed in MANIFEST.tsv')
    print(f'MANIFEST.tsv sha256 = {digest}')
    print('The roster has changed, so the previous stamp no longer covers it. Keep the old')
    print('manifest AND its .ots together in stamps/ -- a proof of a hash is worthless')
    print('without the file that hashes to it -- then:  ots stamp MANIFEST.tsv')


if __name__ == '__main__':
    main()
