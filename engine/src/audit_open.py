import json, collections, openness
rm=json.load(open('rank-map.json'))
res=collections.Counter(); flagged=[]
for m in rm:
    op,lines=openness.status(m['anum'])
    res['open' if op else 'FLAGGED not open']+=1
    if not op: flagged.append((m['rank'],m['anum'],m['engine'],[l[:110] for l in lines[:2]]))
print(dict(res))
json.dump(flagged, open('audit_open_flagged.json','w'), indent=1)
for f in flagged[:25]: print(f)
