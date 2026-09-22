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


# The build tree now holds twelve thousand directories and every run re-read and re-hashed
# every PDF in it, several minutes of work to recover hashes that had not changed. A build
# directory's PDF is written once and not touched again, so its hash is cached against the
# file's size and modification time and only genuinely new builds are read.
HCACHE = 'sync-hash-cache.json'


def index_sources():
    try:
        cache = json.load(open(HCACHE))
    except Exception:
        cache = {}
    h2t, fresh = {}, 0
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for d in os.listdir(root):
            pdf, tex = f'{root}/{d}/p.pdf', f'{root}/{d}/p.tex'
            try:
                st = os.stat(pdf)
            except OSError:
                continue
            if not os.path.exists(tex):
                continue
            key = f'{pdf}:{st.st_size}:{int(st.st_mtime)}'
            h = cache.get(key)
            if h is None:
                h = hashlib.md5(open(pdf, 'rb').read()).hexdigest()
                cache[key] = h
                fresh += 1
            h2t[h] = tex
    json.dump(cache, open(HCACHE, 'w'))
    print(f'  source index: {len(h2t)} builds, {fresh} hashed fresh')
    return h2t


def main():
    h2t = index_sources()
    rm = json.load(open('rank-map.json'))
    # one at a time. Two copies of this script racing deleted each other's freshly written
    # sources and then died on a file the other had just removed; the same mistake broke
    # rank.py in the same session, and both now refuse rather than interleave.
    lock = f'{repopaths.SOURCES}/.sync.lock'
    os.makedirs(repopaths.SOURCES, exist_ok=True)
    if os.path.exists(lock):
        try:
            other = int(open(lock).read().strip())
        except Exception:
            other = None
        if other is not None and os.path.exists(f'/proc/{other}'):
            raise SystemExit(f'sync_sources (pid {other}) is running; refusing to start')
    open(lock, 'w').write(str(os.getpid()))

    # Defect 60. For 714 papers no build directory survives, so the hash match below finds
    # nothing and the ONLY copy of the source is the file sitting under that paper's previous
    # rank. A re-ranking shifts ranks; the old code then found a stranger's source under the
    # new name and deleted it, never looking one name away at the paper's own. Inserting a
    # single paper at rank 1619 destroyed 104 sources. `was` -- the slot id -- is stable
    # across rankings, so the previous rank-map says exactly where each source went.
    # the count this run starts from. The loss below was invisible for as long as it was
    # because every number this script printed only ever went up; a before against an after
    # is the one line that would have caught it.
    was_there = sum(1 for _, _, fs in os.walk(repopaths.SOURCES) for f in fs
                    if f.endswith('.tex'))

    prev = {}
    try:
        for m in json.load(open('rank-map-prev.json')):
            prev[m['was']] = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
                              f"{P.name(m['rank'], m['verdict'])[:-4]}.tex", m['anum'])
    except Exception:
        pass

    # Pass 1 decides, reading only. Nothing is written or deleted until every source that has
    # to be carried is in memory: the destinations overlap the old locations, so writing while
    # still reading would overwrite a source before it had been carried.
    digest, carried = {}, {}
    for m in rm:
        dst = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
               f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
        h = hashlib.md5(open(P.path(m['rank'], m['verdict']), 'rb').read()).hexdigest()
        digest[m['rank']] = h
        if h in h2t:
            continue
        if os.path.exists(dst) and m['anum'] in open(dst, errors='ignore').read(6000):
            continue
        src = prev.get(m['was'])
        if not src or not os.path.exists(src[0]):
            continue
        body = open(src[0], 'rb').read()
        # the carried file must name the paper it is about to sit under, exactly as the
        # final check below demands; a source that does not is not carried, it is dropped
        if m['anum'].encode() in body[:6000]:
            carried[m['rank']] = body

    written = kept = dropped = moved = 0
    present = set()
    for m in rm:
        dst = (f"{repopaths.SOURCES}/{P.band(m['rank'])}/"
               f"{P.name(m['rank'], m['verdict'])[:-4]}.tex")
        present.add(os.path.abspath(dst))
        t = h2t.get(digest[m['rank']])
        if t:
            # ALWAYS rewrite from the hash match. A rank is a position in an ordering that is
            # re-derived whenever the roster changes, so the paper sitting at a given rank
            # changes under you. An earlier version of this script skipped any destination that
            # already existed, and so left the source of a DIFFERENT entry under that name.
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(t, dst)
            written += 1
        elif m['rank'] in carried:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'wb').write(carried[m['rank']])
            moved += 1
        elif os.path.exists(dst):
            # no build directory survives and nothing was carried; keep what is there only if
            # it is demonstrably this paper's, and delete it otherwise rather than let it
            # mislead
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
    # a band RENAME leaves the old band directories behind, empty: widening the rank padding
    # from four digits to five renamed all 22 of them and paper-sources was left showing 44,
    # half of them empty. An empty directory under here is never meaningful.
    for dirpath, dirnames, files in os.walk(repopaths.SOURCES, topdown=False):
        if dirpath != repopaths.SOURCES and not os.listdir(dirpath):
            os.rmdir(dirpath)

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
    try:
        os.remove(lock)
    except OSError:
        pass
    now_there = sum(1 for _, _, fs in os.walk(repopaths.SOURCES) for f in fs
                    if f.endswith('.tex'))
    print(f'  sources on disk: {was_there} before, {now_there} after '
          f'({now_there - was_there:+d})')
    print(f'sources: {written} written from a hash match, {moved} carried across the '
          f'ranking, {kept} kept and confirmed, '
          f'{dropped} dropped as belonging to another paper, {stale} stale removed, '
          f'{len(missing)} with no source')


if __name__ == '__main__':
    main()
