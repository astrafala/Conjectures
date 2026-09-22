#!/usr/bin/env python3
"""Defect 60, as a test: a re-ranking must not destroy the source of a paper whose build
directory is gone.

    python3 src/test_sync_sources.py

Builds a four-paper repository in a temporary directory -- one paper with a surviving build
directory, three without -- then inserts a paper at rank 2 so every later rank shifts by one,
and runs sync_sources against the shifted ranking. Before the fix, the three shifted sources
were found to name the wrong paper and deleted; the whole paper-sources tree for papers with
no build directory was lost one rank-shift at a time. Now they are carried by `was`.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

SRC = os.path.dirname(os.path.abspath(__file__))


def tex(anum):
    return ('\\documentclass{article}\\title{A note on OEIS %s}\n'
            '\\begin{document}\\maketitle\\end{document}\n' % anum)


def pdf(anum):
    # not a real PDF; sync_sources only ever hashes it
    return ('%%PDF-1.4 fake paper for %s\n' % anum).encode()


def rmap(pairs):
    """pairs: (rank, was, anum) -> a rank-map the way rank.py writes one"""
    return [{'rank': r, 'was': w, 'anum': a, 'verdict': 'PROOF',
             'engine': 'test', 'path': 'papers/%05d-%05d/%05d-PROOF.pdf'
             % ((r - 1) // 500 * 500 + 1, (r - 1) // 500 * 500 + 500, r)}
            for r, w, a in pairs]


def write_tree(root, mapping, builds):
    for m in mapping:
        band = '%05d-%05d' % ((m['rank'] - 1) // 500 * 500 + 1,
                              (m['rank'] - 1) // 500 * 500 + 500)
        d = os.path.join(root, 'papers', band)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, '%05d-PROOF.pdf' % m['rank']), 'wb').write(pdf(m['anum']))
        d = os.path.join(root, 'paper-sources', band)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, '%05d-PROOF.tex' % m['rank']), 'w').write(tex(m['anum']))
    for anum in builds:
        d = os.path.join(root, 'engine', 'build', 'x' + anum)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'p.pdf'), 'wb').write(pdf(anum))
        open(os.path.join(d, 'p.tex'), 'w').write(tex(anum))


def main():
    root = tempfile.mkdtemp(prefix='syncsrc-')
    try:
        os.makedirs(os.path.join(root, 'engine'))
        os.symlink(SRC, os.path.join(root, 'engine', 'src'))
        before = rmap([(1, 11, 'A000001'), (2, 12, 'A000002'),
                       (3, 13, 'A000003'), (4, 14, 'A000004')])
        # only A000001 keeps a build directory; the other three exist solely as sources
        write_tree(root, before, ['A000001'])
        eng = os.path.join(root, 'engine')
        json.dump(before, open(os.path.join(eng, 'rank-map-prev.json'), 'w'))

        # a paper is inserted at rank 2 and everything after it shifts by one
        after = rmap([(1, 11, 'A000001'), (2, 15, 'A000005'), (3, 12, 'A000002'),
                      (4, 13, 'A000003'), (5, 14, 'A000004')])
        for m in after:
            band = '%05d-%05d' % ((m['rank'] - 1) // 500 * 500 + 1,
                                  (m['rank'] - 1) // 500 * 500 + 500)
            p = os.path.join(root, 'papers', band, '%05d-PROOF.pdf' % m['rank'])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'wb').write(pdf(m['anum']))
        json.dump(after, open(os.path.join(eng, 'rank-map.json'), 'w'))

        r = subprocess.run([sys.executable, 'src/sync_sources.py'], cwd=eng,
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        if r.returncode != 0:
            print('FAIL: sync_sources exited %d' % r.returncode)
            return 1

        bad = []
        for m in after:
            band = '%05d-%05d' % ((m['rank'] - 1) // 500 * 500 + 1,
                                  (m['rank'] - 1) // 500 * 500 + 500)
            p = os.path.join(root, 'paper-sources', band, '%05d-PROOF.tex' % m['rank'])
            if m['anum'] == 'A000005':
                continue          # genuinely new, no source anywhere: rightly absent
            if not os.path.exists(p):
                bad.append('rank %d (%s): source lost' % (m['rank'], m['anum']))
            elif m['anum'] not in open(p).read():
                bad.append('rank %d (%s): source names another paper' % (m['rank'], m['anum']))
        for b in bad:
            print('  FAIL', b)
        if bad:
            return 1
        print('  ok  all four sources survived a rank shift, each naming its own paper')
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    raise SystemExit(main())
