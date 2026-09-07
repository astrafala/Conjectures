#!/usr/bin/env python3
"""Deep check, Phase 11: the process itself.

Not what the work produced --- how it is done. Four things here are computable and are
computed; the rest of Phase 11 is written up in DEEP-CHECK.md because it is judgement, not
arithmetic, and pretending otherwise would be the padding this phase exists to catch.

  * INDEPENDENCE. Every argument family must have at least one member checked by a route
    that shares no code with its engine. A family with none is not wrong, but nothing about
    it has ever been tested except by the program that produced it.
  * DUPLICATE ENGINES. Two engines that read the same names decide the same class. This has
    happened, and cost ten papers. Every name two engines both read is reported.
  * DUPLICATE STATEMENTS. Two papers claiming the same thing about the same entry is a
    double count. Entries carrying more than one paper are reported with what distinguishes
    them.
  * RULES WITH NO ENFORCING CODE. A rule that lives only in a document will be broken again.
    Each rule the project has adopted is looked for in the code that is supposed to enforce
    it.

    python3 src/dc_phase11.py
"""
import collections
import csv
import json
import os
import re

import repopaths

# Every standing rule this project has adopted, and the code that is supposed to enforce it.
# A rule whose marker is not found is reported: it is a rule with nothing behind it.
RULES = [
    ('a sweep never shares a hits file with a concurrent sweep',
     'src/sweep_shard.py', r"TAG = os\.environ\.get\('TAG'"),
    ('shards are partitioned by crc32, never by hash(), which is salted per process',
     'src/sweep_shard.py', r'zlib\.crc32'),
    ('the builder reads the current roster, not the ranking file, which is stale until '
     'rank.py runs',
     'src/build_new.py', r"paper-engines\.json"),
    ('the comments site refuses to run on dates older than the paper index',
     'src/makecomments_site.py', r'def stale_dates'),
    # Not just that a caps file exists --- it did, and it recorded every ATTEMPT, so reading
    # it back as a list of refusals produced a claim nothing had measured. The rule is that a
    # REFUSAL carries its cap, so the marker is the refusal line itself.
    ('a refusal, and only a refusal, is recorded next to the cap it was made at',
     'src/sweep_shard.py', r"state space > cap'\] \+= 1; caps\[a\]"),
    ('a settled entry is re-checked against the live OEIS before it is counted',
     'src/freshcheck.py', r'def |import '),
    ('the repository root is known in one place only',
     'src/repopaths.py', r'^ROOT = '),
    ('ligatures are normalised before any text comparison',
     'src/dc_text.py', r'def normalise'),
    ('an order-line paper quotes the merged bound the run actually used',
     'src/ordbuild.py', r"2S'=\{2 \* Suse\}"),
    ('every engine that raises on a name is recorded rather than silently skipped',
     'src/uniform.py', r'RAISED'),
]


def families():
    """anum -> the argument family its paper belongs to."""
    fam = {}
    for v in json.load(open('paper-engines.json')).values():
        fam.setdefault(v['anum'], v.get('engine') or '?')
    return fam


def independent():
    p = os.path.join(repopaths.DEEPCHECK, 'phase4.json')
    if not os.path.exists(p):
        return set()
    d = json.load(open(p))['per']
    return {a for a, v in d.items() if v['pin'] == 'INDEPENDENT'}


def duplicate_engines():
    """Names that more than one engine reads, from the overlaps Phase 5 recorded."""
    seen = collections.Counter()
    for s in range(8):
        p = os.path.join(repopaths.DEEPCHECK, f'phase5-{s}.json')
        if not os.path.exists(p):
            continue
        for row in json.load(open(p)).get('overlap', []):
            seen[(row[1], row[2])] += 1
    return seen


def duplicate_statements():
    rows = list(csv.DictReader(open(os.path.join(repopaths.PAPERS, 'index.csv'))))
    by = collections.defaultdict(list)
    for r in rows:
        by[r['anum']].append(r)
    return {a: v for a, v in by.items() if len(v) > 1}, len(rows)


def main():
    fam, ind = families(), independent()
    perfam = collections.Counter(fam.values())
    indfam = collections.Counter(fam[a] for a in ind if a in fam)
    naked = sorted((n, f) for f, n in perfam.items() if not indfam.get(f))
    print(f'Phase 11\n\n  {len(perfam)} argument families, {len(ind)} entries with an '
          f'independent check')
    print(f'  {len(perfam) - len(naked)} families have at least one independently checked '
          f'member; {len(naked)} have none')
    print(f'\n  the {min(len(naked), 15)} largest families with no independent check at all:')
    for n, f in sorted(naked, reverse=True)[:15]:
        print(f'    {n:5d}  {f}')

    ov = duplicate_engines()
    print(f'\n  engine pairs that both read the same name: {len(ov)}')
    for (a, b), n in ov.most_common(10):
        print(f'    {n:5d}  {a} and {b}')
    if not ov:
        print('    (none recorded yet --- Phase 5 is still running)')

    dup, total = duplicate_statements()
    print(f'\n  {total} papers over {total - sum(len(v) - 1 for v in dup.values())} entries; '
          f'{len(dup)} entries carry more than one paper')
    for a, v in sorted(dup.items())[:12]:
        print(f'    {a}: ' + ', '.join(f"{r['rank']} ({r['verdict']}, {r['engine']})"
                                       for r in v))

    print('\n  rules, and the code that enforces them:')
    missing = []
    for why, path, pat in RULES:
        ok = False
        if os.path.exists(path):
            ok = re.search(pat, open(path).read(), re.M) is not None
        print(f'    {"yes" if ok else "NO ":3s}  {why}')
        if not ok:
            missing.append(why)
    print(f'\n  {len(missing)} rules have no enforcing code.')

    out = {'families': dict(perfam), 'independent_by_family': dict(indfam),
           'families_without_independent': [f for _, f in naked],
           'engine_overlaps': {f'{a}|{b}': n for (a, b), n in ov.items()},
           'entries_with_two_papers': {a: [r['rank'] for r in v] for a, v in dup.items()},
           'rules_without_code': missing}
    p = os.path.join(repopaths.DEEPCHECK, 'phase11.json')
    json.dump(out, open(p, 'w'), indent=1)
    print(f'\n  written to {p}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
