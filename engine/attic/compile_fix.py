"""Recompile only the papers whose log showed a LaTeX error, after the template fixes."""
import json, os, subprocess, sys
targets = json.load(open('tex_err_anums.json'))
dirs = sorted({d for v in targets.values() for d in v})
ok = bad = 0
budget = int(sys.argv[1]) if len(sys.argv) > 1 else 500
import time
t0 = time.time()
done = set(json.load(open('compile_fix_done.json'))) if os.path.exists('compile_fix_done.json') else set()
for dd in dirs:
    if dd in done:
        continue
    if time.time() - t0 > budget:
        break
    try:
        for _ in range(2):
            subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                           capture_output=True, timeout=90)
    except subprocess.TimeoutExpired:
        bad += 1; print('timeout', dd); continue
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf") > 50000:
        ok += 1
    else:
        bad += 1; print('nopdf', dd)
    done.add(dd)
    json.dump(sorted(done), open('compile_fix_done.json', 'w'))
print(len(dirs), 'targets', len(done), 'done', ok, 'ok this run', bad, 'bad')
