"""Sweep the pattern-avoidance family. Saves after every item so a restart resumes."""
import json, re, os, collections
import localentry as LE, transfer4 as T4, transfer2 as T, ratrec, openness

OUT='transfer4_hits.json'; DONE='transfer4_done.json'
MARK=re.compile(r'onjectur|Empirical', re.I)
hits=json.load(open(OUT)) if os.path.exists(OUT) else []
done=set(json.load(open(DONE))) if os.path.exists(DONE) else set()
fam=json.load(open('hardin_families.json'))['avoiding ... horizontally/vertically']
print('candidates:', len(fam), 'already done:', len(done), flush=True)

def save():
    json.dump(hits, open(OUT,'w'), indent=1); json.dump(sorted(done), open(DONE,'w'))

res=collections.Counter()
for a in fam:
    if a in done: continue
    e=LE.get(a); nm=e['name']
    p=T4.parse_name(nm)
    if not p: res['name unparsed']+=1; done.add(a); save(); continue
    K,alpha,H,V,L=p
    nrows=(alpha+1)**K
    if nrows**(L-1) > 30000: res['state space too large']+=1; done.add(a); save(); continue
    op,_=openness.status(a)
    if not op: res['not open']+=1; done.add(a); save(); continue
    F=e['comment']+e['formula']
    recs=[r for r in (ratrec.parse_rec(L2) for L2 in F if MARK.search(L2)) if r]
    if not recs: res['no parsable recurrence']+=1; done.add(a); save(); continue
    d=[int(v) for v in e['data'].split(',') if v.strip()]
    rows=T4.rows_ok(K,alpha,H,L)
    st,adj=T4.build(K,alpha,H,V,L)
    if not st: res['empty state space']+=1; done.add(a); save(); continue
    walk=T.terms(adj,len(st),len(d)+3)
    model=[len(rows)]+walk
    if model[:len(d)]!=d: res['model does not match DATA']+=1; done.add(a); save(); continue
    coeffs,dd=recs[0]; order=max(coeffs)
    thr=T.threshold(adj,len(st),coeffs,order)
    if thr is not None:
        res['PROVED']+=1
        hits.append({'anum':a,'K':K,'alpha':alpha,'H':[list(x) for x in H],
                     'V':[list(x) for x in V],'L':L,'nrows':len(rows),'S':len(st),
                     'coeffs':{int(k):str(v) for k,v in coeffs.items()},'order':order,
                     'nterms':len(d),'name':nm,'threshold':thr,'claimed':dd})
    else:
        res['recurrence FAILS']+=1; hits.append({'anum':a,'FAILS':True,'name':nm})
    done.add(a); save()
    print('done',a,res['PROVED'],flush=True)
save(); print(dict(res))
print('PROVED entries:', sum(1 for h in hits if not h.get('FAILS')))
