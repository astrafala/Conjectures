import json, os, subprocess
hits=[h for h in json.load(open('uniall_hits.json'))
      if h.get('engine')=='transfer34' and not h.get('FAILS')]
ok=bad=0
for h in hits:
    dd=f"build/t34{h['anum']}"
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000:
        ok+=1; continue
    try:
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','p.tex'],cwd=dd,
                           capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        bad+=1; print('timeout',h['anum']); continue
    if os.path.exists(f"{dd}/p.pdf") and os.path.getsize(f"{dd}/p.pdf")>50000: ok+=1
    else: bad+=1; print('nopdf',h['anum'])
print(len(hits),'jobs',ok,'ok',bad,'bad')
