"""Sweep the neighbour-count family. Saves after every item so a restart resumes."""
import json, re, os, collections
import localentry as LE, transfer5 as T5, ratrec, openness

OUT='transfer5_hits.json'; DONE='transfer5_done.json'
MARK=re.compile(r'onjectur|Empirical', re.I)
hits=json.load(open(OUT)) if os.path.exists(OUT) else []
done=set(json.load(open(DONE))) if os.path.exists(DONE) else set()

fam=json.load(open('hardin_families.json'))
have={r['anum'] for r in json.load(open('rank-map.json'))}
pool=sorted({a for k in ('subblock sum <= / >=','nXk 0..m arrays (any)') for a in fam[k]} - have)
print('pool:', len(pool), 'already done:', len(done), flush=True)

def save():
    json.dump(hits, open(OUT,'w'), indent=1); json.dump(sorted(done), open(DONE,'w'))

res=collections.Counter(); n=0
for a in pool:
    if a in done: continue
    e=LE.get(a)
    p=T5.parse_name(e['name'])
    if not p: done.add(a); continue          # not this family; no counter noise
    K,alpha,same,counts,nb,ul0=p
    S=((alpha+1)**K)**2
    if S > 30000: res['state space too large']+=1; done.add(a); save(); continue
    if not openness.status(a)[0]: res['not open']+=1; done.add(a); save(); continue
    F=e['comment']+e['formula']
    recs=[r for r in (ratrec.parse_rec(x) for x in F if MARK.search(x)) if r]
    if not recs: res['no parsable recurrence']+=1; done.add(a); save(); continue
    d=[int(v) for v in e['data'].split(',') if v.strip()]
    st,adj,start,end=T5.build(K,alpha,same,counts,nb,ul0)
    model=[T5.one_row(K,alpha,same,counts,nb,ul0)]+T5.terms(adj,start,end,len(d)+3)
    if model[:len(d)]!=d:
        res['model does not match DATA']+=1; done.add(a); save(); continue
    coeffs,dd=recs[0]; order=max(coeffs)
    thr=T5.threshold(adj,start,end,coeffs,order,len(st))
    if thr is not None:
        res['PROVED']+=1
        hits.append({'anum':a,'K':K,'alpha':alpha,'same':same,'counts':sorted(counts),
                     'nb':len(nb),'ul0':ul0,'S':len(st),
                     'coeffs':{int(k):str(v) for k,v in coeffs.items()},'order':order,
                     'nterms':len(d),'name':e['name'],'threshold':thr,'claimed':dd})
    else:
        res['recurrence FAILS']+=1; hits.append({'anum':a,'FAILS':True,'name':e['name']})
    done.add(a); save(); n+=1
    if n%10==0: print('progress',n,dict(res),flush=True)
save(); print(dict(res))
print('PROVED entries:', sum(1 for h in hits if not h.get('FAILS')))
