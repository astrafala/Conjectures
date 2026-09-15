import json, os, subprocess
jobs=[]
for f,tag in (('transfer4_hits.json','pa'),('transfer5_hits.json','nb')):
    for h in json.load(open(f)):
        if not h.get('FAILS'): jobs.append((tag,h['anum']))
ok=bad=0
for tag,a in jobs:
    dd=f"build/{tag}{a}"
    try:
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','p.tex'],cwd=dd,
                           capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        bad+=1; print('timeout',a); continue
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1
    else: bad+=1; print('nopdf',a)
print(len(jobs),'jobs',ok,'ok',bad,'bad')
open('recompile45.done','w').write('1')
