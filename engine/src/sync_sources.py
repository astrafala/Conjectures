#!/usr/bin/env python3
"""Keep ../paper-sources in step with ../papers.

Each paper is compiled from a p.tex in a build directory, and the build tree is working state
that is not stored. The source IS worth storing, so after every batch the new papers' .tex
files are copied into paper-sources/, named and banded exactly as the papers are.

A paper is matched to its source by the CONTENT of the PDF rather than by remembering which
build directory produced it: the build directory names carry an engine prefix and an A-number,
not a rank, and an A-number can carry two papers. The hash cannot mismatch.
"""
import os, sys, json, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperpath as P
import repopaths

ROOTS = ['build', 'build_rec', 'build_cf', 'build_egf', 'build_logexp']


def index_sources():
    h2t = {}
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for d in os.listdir(root):
            pdf, tex = f'{root}/{d}/p.pdf', f'{root}/{d}/p.tex'
            if os.path.exists(pdf) and os.path.exists(tex):
                h2t[hashlib.md5(open(pdf, 'rb').read()).hexdigest()] = tex
    return h2t


def main():
    h2t = index_sources()
    rm = json.load(open('rank-map.json'))
    added = have = miss = 0
    present = set()
    for m in rm:
        dst = f"{repopaths.SOURCES}/{P.band(m['rank'])}/{P.name(m['rank'], m['verdict'])[:-4]}.tex"
        present.add(os.path.abspath(dst))
        if os.path.exists(dst):
            have += 1
            continue
        pdf = P.path(m['rank'], m['verdict'])
        t = h2t.get(hashlib.md5(open(pdf, 'rb').read()).hexdigest())
        if not t:
            miss += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(t, dst)
        added += 1
    # a re-ranking moves papers, so sources that no longer answer to any rank are stale
    stale = 0
    for dirpath, _, files in os.walk(repopaths.SOURCES):
        for f in files:
            if not f.endswith('.tex'):
                continue
            p = os.path.abspath(os.path.join(dirpath, f))
            if p not in present:
                os.remove(p)
                stale += 1
    missing = [m for m in rm
               if not os.path.exists(f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
                                     f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")]
    open(f'{repopaths.SOURCES}/MISSING.txt', 'w').write(
        "The LaTeX source of these papers is not in the repository. Their build directories\n"
        "were removed before sources were archived; the papers themselves are in papers/ and\n"
        "each is self-contained. The generator that produced them is in engine/src.\n\n"
        + '\n'.join(f"{m['rank']}  {m['anum']}  {m['engine']}" for m in missing) + '\n')
    print(f'sources: {have} already present, {added} added, {stale} stale removed, '
          f'{len(missing)} with no surviving build directory')


if __name__ == '__main__':
    main()
