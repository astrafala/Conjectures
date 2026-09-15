"""Re-check the array papers the first two audits could not route, using each engine's own
term function: transfer6 exposes terms(adj,S,N) and transfer7 lterms(...), not avals.

SUPERSEDED. This carries its own list of engines, which was the whole set when it
was written and is eleven of eighty-three now, so it can only re-check papers from
those eleven. `audit_deep.py` does the same job through `uniform`, which knows all of
them, and covers 8,667 entries. Kept for the record; do not run it and do not read its
output as coverage.
"""
import json, re, importlib, collections
from math import factorial
import localentry as LE, ratrec, openness
ENG=['transfer9','transfer6','transfer16','transfer12','transfer10','transfer8',
     'transfer14','transfer11','transfer15','transfer13','transfer7']
M={e:importlib.import_module(e) for e in ENG}
SCALED=('transfer7','transfer8','transfer10','transfer12','transfer16')
MARK=re.compile(r'onjectur|Empirical', re.I)
names=json.load(open('/tmp/claude-0/-home-user-Conjectures/'
                     'a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad/all_names.json'))
left=json.load(open('audit_left.json'))
res=collections.Counter(); out={}; unparsed=[]
for a in left:
    nm=names.get(a)
    if nm is None:
        res['no name']+=1; unparsed.append((a,'NO NAME')); continue
    p=eng=None
    for e in ENG:
        try: q=M[e].parse_name(nm)
        except Exception: q=None
        if q: p,eng=q,e; break
    if p is None:
        try:
            q=M['transfer7'].parse_nb(nm)
            if q: p,eng=q,'transfer7nb'
        except Exception: pass
    if p is None:
        res['unparsed']+=1; unparsed.append((a,nm[:90])); continue
    e0=eng.replace('nb','')
    try:
        try: b=M[e0].build(p,cap=400000)
        except TypeError: b=M[e0].build(p)
    except Exception as ex:
        res['build failed']+=1; continue
    if b is None: res['too big']+=1; continue
    ent=LE.get(a)
    d=[int(v) for v in ent['data'].split(',') if v.strip()]
    off=int(ent['offset'].split(',')[0])
    recs=[r for r in (ratrec.parse_rec(L) for L in ent['comment']+ent['formula']
                      if MARK.search(L)) if r]
    if not recs: res['no recurrence']+=1; continue
    coeffs,dd=recs[0]; order=max(coeffs)
    N=len(d)+50
    try:
        if e0=='transfer6':
            st,adj=b; t=M[e0].terms(adj,len(st),N)
            t=[x//p['frac'] for x in t]
            shift=next((s for s in range(0,4) if t[s:s+len(d)]==d), None)
            if shift is None: res['DATA MISMATCH']+=1; out[a]={'v':'PROBLEM'}; continue
            got=[None]*off+[None]*0
            got=t; base=shift-off        # got[base+n] = a(n)
            idx=lambda n: base+n
        elif e0=='transfer7':
            kind='sub' if 'ptab' in p else 'nb'
            adj,start,pl=M[e0].build_lumped(p,kind)
            t=M[e0].lterms(adj,start,N,p,kind)
            f=factorial(p['K'])*p['frac']
            t=[x//f if x%f==0 else None for x in t]
            shift=next((s for s in range(0,4) if t[s:s+len(d)]==d), None)
            if shift is None: res['DATA MISMATCH']+=1; out[a]={'v':'PROBLEM'}; continue
            got=t; base=shift-off
            idx=lambda n: base+n
        else:
            res['other engine']+=1; continue
    except Exception as ex:
        res['eval failed: '+str(ex)[:40]]+=1; continue
    lo=off+order
    if dd is not None: lo=max(lo,int(dd)+1)
    bad=[]
    for n in range(lo, off+len(d)+45):
        j=idx(n)
        if j>=len(got) or got[j] is None: continue
        if any(idx(n-i)<0 or got[idx(n-i)] is None for i in coeffs): continue
        if got[j]!=sum(c*got[idx(n-i)] for i,c in coeffs.items()): bad.append(n)
    op,_=openness.status(a)
    if bad: res['RECURRENCE FAILS']+=1; out[a]={'v':'PROBLEM','bad':bad[:4]}
    elif not op: res['not open']+=1; out[a]={'v':'NOT OPEN'}
    else: res['ok']+=1; out[a]={'v':'ok','nterms':len(d)}
json.dump(out, open('audit_left2.json','w'))
print(dict(res))
for u in unparsed[:20]: print('UNPARSED', u)
