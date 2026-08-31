import json, re, collections
import localentry as LE, transfer2 as T, ratrec, openness
MARK=re.compile(r'onjectur|Empirical', re.I)
fam=json.load(open('hardin_families.json'))['subblock summing to c']
res=collections.Counter(); hits=[]; unparsed=[]
for a in fam:
    e=LE.get(a); nm=e['name']
    if nm.strip().startswith('T(n,k)'):
        res['triangle (2-D), skipped']+=1; continue
    p=T.parse_name(nm)
    if not p: res['name unparsed']+=1; unparsed.append((a,nm[:90])); continue
    cols,alpha,sums,extra=p
    S=(alpha+1)**cols
    if S>20000: res['state space > 20000']+=1; continue
    op,_=openness.status(a)
    if not op: res['not open']+=1; continue
    F=e['comment']+e['formula']
    recs=[r for r in (ratrec.parse_rec(L) for L in F if MARK.search(L)) if r]
    if not recs: res['no parsable recurrence']+=1; continue
    d=[int(v) for v in e['data'].split(',') if v.strip()]
    st,adj=T.build(cols,alpha,sums,extra)
    t=T.terms(adj,len(st),len(d)+3)
    shift=next((s for s in range(0,3) if t[s:s+len(d)]==d), None)
    if shift is None: res['transfer does not match DATA']+=1; continue
    coeffs,dd=recs[0]; order=max(coeffs)
    thr=T.threshold(adj,len(st),coeffs,order)
    if thr is not None:
        res['PROVED']+=1
        hits.append({'anum':a,'cols':cols,'alpha':alpha,'sums':sums,'extra':extra,
                     'S':len(st),'coeffs':{int(k):str(v) for k,v in coeffs.items()},
                     'order':order,'shift':shift,'nterms':len(d),'name':nm,
                     'threshold':thr,'claimed':dd})
    else:
        res['recurrence FAILS']+=1; hits.append({'anum':a,'FAILS':True,'name':nm})
    print('done', a, flush=True)
print(dict(res))
for a,nm in unparsed: print('UNPARSED', a, nm)
json.dump(hits, open('transfer_hits.json','w'), indent=1)
print('PROVED entries:', sum(1 for h in hits if not h.get('FAILS')))
