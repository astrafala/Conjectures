import json, os, subprocess
jobs=[h['anum'] for h in json.load(open('table_hits.json'))]
ok=bad=0
for a in jobs:
    dd=f"build/tb2{a}"
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1; continue
    try:
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','p.tex'],cwd=dd,capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        bad+=1; print('timeout',a); continue
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1
    else: bad+=1; print('nopdf',a)
print(len(jobs),'jobs',ok,'ok',bad,'bad')
open('compile_tb2.done','w').write('1')
