import json, os, subprocess
roster={x['anum'] for x in json.load(open('rank-map.json'))}
jobs=[(('tg'),h['anum']) for h in json.load(open('transfer16_hits.json'))
      if not h.get('FAILS') and h['anum'] not in roster]
ok=bad=0
for tag,a in jobs:
    dd=f"build/{tag}{a}"
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1; continue
    try:
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','p.tex'],cwd=dd,capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        bad+=1; continue
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1
    else: bad+=1; print('nopdf',a)
print(len(jobs),'jobs',ok,'ok',bad,'bad')
open('compile_g.done','w').write('1')
