import json, os, subprocess
# A run on a different hits file must build into its own directory, or two pools write
# their papers over each other under one name.
PREFIX = os.environ.get('CFPREFIX', 'cf')
jobs=[h['anum'] for h in json.load(open(os.environ.get('HITS', 'cf_hits.json'))) if not h.get('FAILS')]
ok=bad=0
for a in jobs:
    dd=f"build/{PREFIX}{a}"
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1; continue
    try:
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','p.tex'],cwd=dd,capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        bad+=1; print('timeout',a); continue
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1
    else: bad+=1; print('nopdf',a)
print(len(jobs),'jobs',ok,'ok',bad,'bad')
