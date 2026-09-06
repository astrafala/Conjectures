"""Compile a batch of papers in parallel; one pdflatex per core."""
import json, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

PREFIX, HITS = sys.argv[1], sys.argv[2]


def one(a):
    dd = f"build/{PREFIX}{a}"
    # a sweep may still be appending to the hits file while this runs, so a hit whose paper
    # has not been written yet is skipped rather than allowed to kill the whole pool
    if not os.path.isdir(dd):
        return (a, None)
    p = f"{dd}/p.pdf"
    if os.path.exists(p) and os.path.getsize(p) > 50000:
        return (a, True)
    try:
        for _ in range(2):
            subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'],
                           cwd=dd, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return (a, False)
    return (a, os.path.exists(p) and os.path.getsize(p) > 50000)


if __name__ == "__main__":
    jobs = [h['anum'] for h in json.load(open(HITS)) if not h.get('FAILS')]
    ok = bad = 0
    with ProcessPoolExecutor(max_workers=4) as ex:
        for a, good in ex.map(one, jobs):
            if good:
                ok += 1
            elif good is None:
                pass
            else:
                bad += 1
                print('FAILED', a, flush=True)
    print(len(jobs), 'jobs', ok, 'ok', bad, 'bad')
