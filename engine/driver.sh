#!/bin/bash
# Continuous pipeline: collect -> prove -> (audit/recheck/build are run separately).
# Safe to run repeatedly; every stage is incremental and resumable.
cd /home/user/Conjectures

while true; do
  # 1. collect: next batch of unrun queries
  python3 - <<'PY'
import json
c = json.load(open('rec-cache.json'))
done = set(c['q'])
qs = [q.strip() for q in open('qall.txt') if q.strip()]
todo = [q for q in qs if q not in done]
open('qtodo.txt', 'w').write('\n'.join(todo))
print('queries left:', len(todo))
PY
  N=$(wc -l < qtodo.txt)
  if [ "$N" -gt 0 ]; then
    PAGES=6 timeout 900 python3 src/collect_rec.py $(head -40 qtodo.txt | tr '\n' ' ') >> collect.log 2>&1
  fi

  # 2. prove: everything not yet attempted
  python3 - <<'PY'
import json
c = json.load(open('rec-cache.json'))['seen']
r = json.load(open('rec-results.json'))
p = sorted(a for a, v in c.items() if v and v['gfs'] and not v['proof'] and a not in r)
open('pend.txt', 'w').write('\n'.join(p))
print('pending:', len(p))
PY
  for a in $(head -60 pend.txt); do
    timeout 14 python3 src/prove_rec.py "$a" > /dev/null 2>&1
  done

  python3 -c "
import json;r=json.load(open('rec-results.json'))
print('PROVED', sum(1 for v in r.values() if v['status']=='PROVED'), 'of', len(r))" >> driver.log

  if [ "$N" -eq 0 ] && [ ! -s pend.txt ]; then
    echo "PIPELINE IDLE" >> driver.log
    break
  fi
done
