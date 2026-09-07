#!/usr/bin/env python3
"""Deep check, Phase 0: freeze the corpus and record exactly what is being checked.

Every later phase reads the frozen roster rather than the live one, so the thing being
checked cannot shift underneath the check while it runs. The snapshot also records the
machine and the library versions, because a result that only holds on one version of a
library is not a result.

Writes deep-check/frozen-roster.json and deep-check/phase0.json. Re-running it refuses to
overwrite an existing freeze unless --refreeze is given: a check that re-freezes halfway
through is checking two different corpora and reporting one number.

    python3 src/dc_phase0.py [--refreeze]
"""
import hashlib
import json
import os
import platform
import subprocess
import sys

import repopaths

OUT = os.path.join(repopaths.ROOT, 'deep-check')
FROZEN = os.path.join(OUT, 'frozen-roster.json')
SNAP = os.path.join(OUT, 'phase0.json')
LIBS = ['sympy', 'pdfminer', 'numpy']


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(FROZEN) and '--refreeze' not in sys.argv:
        print(f'already frozen: {FROZEN} exists. Use --refreeze only to start a new check.')
        return 1
    root = repopaths.ROOT
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root,
                            capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=root,
                           capture_output=True, text=True).stdout.strip()
    files = subprocess.run(['git', 'ls-files'], cwd=root,
                           capture_output=True, text=True).stdout.split()
    roster = json.load(open('paper-engines.json'))
    json.dump(roster, open(FROZEN, 'w'), indent=1, sort_keys=True)

    digests = {}
    for f in files:
        p = os.path.join(root, f)
        if os.path.exists(p):
            digests[f] = sha256(p)

    libs = {}
    for name in LIBS:
        try:
            m = __import__(name)
            libs[name] = getattr(m, '__version__', 'unknown')
        except Exception:
            libs[name] = 'absent'

    snap = {
        'commit': commit,
        'working_tree_clean': dirty == '',
        'roster_papers': len(roster),
        'roster_entries': len({v['anum'] for v in roster.values()}),
        'tracked_files': len(files),
        'python': sys.version.split()[0],
        'platform': platform.platform(),
        'libraries': libs,
        'file_sha256': digests,
    }
    json.dump(snap, open(SNAP, 'w'), indent=1, sort_keys=True)
    print(f"frozen at {commit[:12]}"
          f"{'' if snap['working_tree_clean'] else ' (WORKING TREE NOT CLEAN -- a defect)'}")
    print(f"{snap['roster_papers']} papers, {snap['roster_entries']} entries, "
          f"{len(files)} tracked files hashed")
    print(f"python {snap['python']}, libraries: "
          + ', '.join(f'{k} {v}' for k, v in sorted(libs.items())))
    return 0 if snap['working_tree_clean'] else 1


if __name__ == '__main__':
    sys.exit(main())
