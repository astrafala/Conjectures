import json, os, subprocess, sys
hits=[h for h in json.load(open('transfer6_hits.json')) if not h.get('FAILS')]
ok=[]; bad=[]
for h in hits:
    d=f"build/t6{h['anum']}"
    if os.path.exists(f"{d}/p.pdf") and os.path.getsize(f"{d}/p.pdf")>50000:
        ok.append(h['anum']); continue
    try:
        for _ in range(2):
            r=subprocess.run(['pdflatex','-interaction=nonstopmode','p.tex'],cwd=d,
                             capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        bad.append((h['anum'],'timeout')); continue
    if os.path.exists(f"{d}/p.pdf") and os.path.getsize(f"{d}/p.pdf")>50000: ok.append(h['anum'])
    else: bad.append((h['anum'],'no pdf'))
print(len(ok),'ok',len(bad),'bad')
for b in bad[:20]: print(b)
json.dump(ok,open('t6_compiled.json','w'))
