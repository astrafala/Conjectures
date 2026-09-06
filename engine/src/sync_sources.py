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
    written = kept = dropped = 0
    present = set()
    for m in rm:
        dst = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
               f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
        present.add(os.path.abspath(dst))
        pdf = P.path(m['rank'], m['verdict'])
        t = h2t.get(hashlib.md5(open(pdf, 'rb').read()).hexdigest())
        if t:
            # ALWAYS rewrite from the hash match. A rank is a position in an ordering that is
            # re-derived whenever the roster changes, so the paper sitting at a given rank
            # changes under you. An earlier version of this script skipped any destination that
            # already existed, and so left the source of a DIFFERENT entry under that name.
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(t, dst)
            written += 1
        elif os.path.exists(dst):
            # no build directory survives; keep what is there only if it is demonstrably this
            # paper's, and delete it otherwise rather than let it mislead
            if m['anum'] in open(dst, errors='ignore').read(6000):
                kept += 1
            else:
                os.remove(dst)
                present.discard(os.path.abspath(dst))
                dropped += 1

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
    # verify rather than assume: every source must name the paper it sits under
    wrong = [m for m in rm
             if os.path.exists(f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
                               f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
             and m['anum'] not in open(
                 f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
                 f"{P.name(m['rank'], m['verdict'])[:-4]}.tex", errors='ignore').read(6000)]
    if wrong:
        raise SystemExit(f'{len(wrong)} sources do not name their paper, first '
                         f'{wrong[0]["rank"]} ({wrong[0]["anum"]}) -- refusing to finish')
    print(f'sources: {written} written from a hash match, {kept} kept and confirmed, '
          f'{dropped} dropped as belonging to another paper, {stale} stale removed, '
          f'{len(missing)} with no source')


if __name__ == '__main__':
    main()
