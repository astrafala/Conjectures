import json, os, shutil
hits=[h for h in json.load(open('uniall_hits.json'))
      if h.get('engine')=='transfer40' and not h.get('FAILS')]
eng={int(k):v for k,v in json.load(open('paper-engines.json')).items()}
have={v['anum'] for v in eng.values()}
nxt=max(eng)+1
added,skipped=[],[]
for h in sorted(hits,key=lambda x:x['anum']):
    a=h['anum']; src=f"build/t40{a}/p.pdf"
    if a in have or not (os.path.exists(src) and os.path.getsize(src)>50000):
        skipped.append(a); continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt]={'engine':'subblock-neighbour','order':h['order'],'degree':h['S'],
              'anum':a,'disproof':False}
    have.add(a); added.append((nxt,a)); nxt+=1
json.dump({str(k):v for k,v in eng.items()},open('paper-engines.json','w'),indent=1,sort_keys=True)
d=json.load(open('engine_desc.json'))
d['subblock-neighbour|PROOF']=("a subblock statistic compared with its neighbours': none equal, some "
                               "equal, exactly one or two equal, or bounded difference")
json.dump(d,open('engine_desc.json','w'),indent=1,sort_keys=True)
print('added',len(added),'skipped',len(skipped),skipped[:5])
