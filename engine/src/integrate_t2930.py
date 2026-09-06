import json, os, shutil
NAMES={'transfer29':'order-statistic','transfer30':'subblock-coloring'}
hits=[h for h in json.load(open('uniall_hits.json'))
      if not h.get('FAILS') and h.get('engine') in NAMES]
eng={int(k):v for k,v in json.load(open('paper-engines.json')).items()}
have={v['anum'] for v in eng.values()}
nxt=max(eng)+1
added,skipped=[],[]
for h in sorted(hits,key=lambda x:x['anum']):
    a=h['anum']; src=f"build/{h['engine'][-2:]}{a}/p.pdf"
    if a in have or not (os.path.exists(src) and os.path.getsize(src)>50000):
        skipped.append(a); continue
    shutil.copy(src, f"papers-old-numbering/{nxt}-PROOF.pdf")
    eng[nxt]={'engine':NAMES[h['engine']],'order':h['order'],'degree':h['S'],
              'anum':a,'disproof':False}
    have.add(a); added.append((nxt,a)); nxt+=1
json.dump({str(k):v for k,v in eng.items()},open('paper-engines.json','w'),indent=1,sort_keys=True)
d=json.load(open('engine_desc.json'))
d['order-statistic|PROOF']=("a signed sum of the order statistics of every 2 X 2 subblock "
                            "taking one common value")
d['subblock-coloring|PROOF']=("the 2 X 2 subblocks properly coloured by a statistic of their "
                              "entries: neighbours must differ")
json.dump(d,open('engine_desc.json','w'),indent=1,sort_keys=True)
print('added',len(added),'skipped',len(skipped),skipped[:5])
