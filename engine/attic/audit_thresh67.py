"""Threshold recomputation for the two engines whose term function is not avals."""
import json, re, collections
from math import factorial
import localentry as LE, ratrec, transfer6 as T6, transfer7 as T7
MARK=re.compile(r'onjectur|Empirical', re.I)
res=collections.Counter(); out={}
for f,eng in (('transfer6_hits.json','t6'),('transfer7_hits.json','t7')):
    for h in json.load(open(f)):
        if h.get('FAILS'): continue
        a=h['anum']; e=LE.get(a)
        d=[int(v) for v in e['data'].split(',') if v.strip()]
        off=int(e['offset'].split(',')[0])
        recs=[r for r in (ratrec.parse_rec(L) for L in e['comment']+e['formula']
                          if MARK.search(L)) if r]
        if not recs: res['no rec']+=1; continue
        coeffs,dd=recs[0]; order=max(coeffs)
        N=len(d)+35
        try:
            if eng=='t6':
                p=T6.parse_name(e['name'])
                if not p: res['unparsed']+=1; continue
                st,adj=T6.build(p)
                t=[x//p['frac'] for x in T6.terms(adj,len(st),N)]
            else:
                p=T7.parse_name(e['name']); kind='sub'
                if not p: p=T7.parse_nb(e['name']); kind='nb'
                if not p: res['unparsed']+=1; continue
                adj,start,pl=T7.build_lumped(p,kind)
                fac=factorial(p['K'])*p['frac']
                t=[x//fac if x%fac==0 else None for x in T7.lterms(adj,start,N,p,kind)]
        except Exception:
            res['build/eval failed']+=1; continue
        shift=next((s for s in range(0,4) if t[s:s+len(d)]==d), None)
        if shift is None: res['DATA MISMATCH']+=1; continue
        base=shift-off                       # t[base+n] = a(n)
        first=off+order
        worst=first-1
        for n in range(first, off+len(d)+30):
            j=base+n
            if j>=len(t) or t[j] is None: continue
            if any(base+n-i<0 or t[base+n-i] is None for i in coeffs): continue
            if t[j]!=sum(c*t[base+n-i] for i,c in coeffs.items()): worst=n
        old=h.get('nthr', h.get('threshold'))
        if old is None: res['no old']+=1; continue
        out[a]={'old':old,'true':worst,'engine':eng}
        if worst<old: res['UNDERSTATED']+=1
        elif worst>old: res['OVERSTATED']+=1
        else: res['exact']+=1
json.dump(out, open('audit_thresh_67.json','w'))
print(dict(res))
