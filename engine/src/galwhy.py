#!/usr/bin/env python3
"""Why galcoord declines each of its 355 entries.

    python3 src/galwhy.py     # resumable; writes deep-check/galcoord-why.json

Every one of those declines used to be the same bare None, which every caller reads as "too
big". `galcoord.LAST_WHY` now says which of the five refusal paths it was -- and two of them
were already computing a reason and dropping it into an underscore. This walks the list and
tallies them, so the largest block on this project's frontier is a distribution of specific
engine limitations rather than one word.
"""
import sys, json, collections, signal
sys.path.insert(0,'src')
import galcoord, localentry as LE
class TO(BaseException): pass
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TO()))
import os
decl=json.load(open('uniall_declined.json'))
# resumable: each build can take a minute, so a round that is cut short must not start over
prev = (json.load(open('deep-check/galcoord-why.json'))
        if os.path.exists('deep-check/galcoord-why.json') else {})
gal=[a for a in sorted(a for a,e in decl.items() if e=='galcoord') if a not in prev]
print('galcoord declines: %d'%len(gal), flush=True)
c=collections.Counter(); detail=dict(prev)
for i,a in enumerate(gal):
    try:
        p=galcoord.parse_name(LE.get(a)['name'])
        if not p: c['name does not parse']+=1; continue
        signal.alarm(60); b=galcoord.build(p); signal.alarm(0)
        w = 'BUILT' if b is not None else (galcoord.LAST_WHY[0] or 'None with no reason')
    except TO:
        signal.alarm(0); w='timed out at 60s'
    except Exception as ex:
        signal.alarm(0); w='raised %s'%type(ex).__name__
    finally:
        signal.alarm(0)
    c[w[:70]]+=1; detail[a]=w
    if i%20==19:
        print('%d/%d %s'%(i+1,len(gal),dict(c)), flush=True)
        json.dump(detail, open('deep-check/galcoord-why.json','w'), indent=1, sort_keys=True)
json.dump(detail, open('deep-check/galcoord-why.json','w'), indent=1, sort_keys=True)
print('FINAL', flush=True)
for k,v in c.most_common(): print('   %-72s %d'%(k,v))
