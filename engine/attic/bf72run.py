import json, os, sys, time, signal
import bf72


class TO(Exception):
    pass


signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TO()))
D = 'bf72_done.json'
done = json.load(open(D)) if os.path.exists(D) else {}
hits = [h for h in json.load(open('uniall_hits.json'))
        if h.get('engine') == 'transfer72' and not h.get('FAILS')]
t0 = time.time()
for h in sorted(hits, key=lambda x: x['anum']):
    a = h['anum']
    if a in done:
        continue
    if time.time() - t0 > float(sys.argv[1] if len(sys.argv) > 1 else 100):
        break
    r = None
    for rows in (3, 2):
        try:
            signal.alarm(70)
            r = bf72.check(a, steps=rows)
            signal.alarm(0)
            break
        except TO:
            signal.alarm(0)
            r = (a, 'too slow', rows)
    done[a] = [r[1], r[2]]
    json.dump(done, open(D, 'w'))
    if r[1] != 'OK':
        print('BAD', *r)
import collections
print(len(done), 'of', len(hits), collections.Counter(v[0] for v in done.values()))
