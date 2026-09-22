#!/usr/bin/env python3
"""How many of galcoord's declines have a RAY-shaped exceptional set?

    python3 src/galrays.py            # every galcoord decline, resumable
    python3 src/galrays.py A310039    # named entries

`galhull.pieces` refuses a class when the distance is not a max of affine pieces, and until
today that refusal was one word. It is not one problem. Measured on five entries, four have
their leftovers on a pair of opposite RAYS through the origin with the distance affine along
the ray -- A310039 at +/-(1,-2), distances 13, 25, 37; A310007 and A310025 at +/-(1,-1),
9, 17, 25, 33, 41; A310019 at +/-(1,0), 5, 9, ..., 41 -- and one, A310018, is scattered
across about thirty directions with one point each.

The distinction decides the work. A ray correction to the ball count is quasi-linear in t, so
it leaves a(n) quasi-linear and the existing Ehrhart fit and certificate absorb it with one
extra term (IDEAS section A11). A scatter does not. This counts which is which.
"""
import sys, collections, math
sys.path.insert(0,'src')
import galfit, galhull, galcoord, localentry as LE
def leftovers(a):
    p=galcoord.parse_name(LE.get(a)['name'])
    rec=[]; orig=galhull.pieces
    def spy(pts, tries=None, margin=6):
        pl,left=orig(pts,tries,margin); rec.append((len(pts),len(pl),list(left))); return pl,left
    galhull.pieces=spy
    try: galfit.data(p['u'],p['t'],p['v'],radius=galcoord.RADIUS,refine=(1,1))
    finally: galhull.pieces=orig
    return p, rec
def describe(left):
    """is the leftover set a union of rays through the origin?"""
    dirs=collections.defaultdict(list)
    for m,n,d in left:
        g=math.gcd(abs(m),abs(n)) or 1
        dirs[(m//g, n//g)].append((g, int(d)))
    out=[]
    for dv,ks in sorted(dirs.items()):
        ks.sort()
        steps={ks[i+1][1]-ks[i][1] for i in range(len(ks)-1)}
        out.append('%s x%d d=%s%s'%(str(dv), len(ks), [k[1] for k in ks],
                   ' step %s'%steps.pop() if len(steps)==1 else ''))
    return out
def shape(left):
    """'ray' when every leftover lies on a ray k*v with D affine in k, else 'scatter'."""
    dirs = collections.defaultdict(list)
    for m, n, d in left:
        g = math.gcd(abs(m), abs(n)) or 1
        dirs[(m // g, n // g)].append((g, int(d)))
    if not dirs:
        return 'none', {}
    for dv, ks in dirs.items():
        if len(ks) < 2:
            return 'scatter', dirs
        ks.sort()
        steps = {ks[i + 1][1] - ks[i][1] for i in range(len(ks) - 1)}
        if len(steps) != 1:
            return 'scatter', dirs
    return 'ray', dirs


def main():
    import json, os, signal
    class TO(BaseException):
        pass
    signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TO()))
    OUT = 'deep-check/galrays.json'
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    if sys.argv[1:]:
        todo = sys.argv[1:]
    else:
        why = (json.load(open('deep-check/galcoord-why.json'))
               if os.path.exists('deep-check/galcoord-why.json') else {})
        decl = json.load(open('uniall_declined.json'))
        todo = [a for a, e in sorted(decl.items())
                if e == 'galcoord' and a not in out
                and (not why or why.get(a, '').startswith('galfit: distance is not a max'))]
    print('%d galcoord entries to classify' % len(todo), flush=True)
    tally = collections.Counter(v['shape'] for v in out.values())
    for i, a in enumerate(todo):
        try:
            signal.alarm(120)
            p, rec = leftovers(a)
            signal.alarm(0)
        except TO:
            signal.alarm(0); tally['timed out'] += 1; continue
        except Exception as ex:
            signal.alarm(0); tally['raised %s' % type(ex).__name__] += 1; continue
        finally:
            signal.alarm(0)
        allleft = [x for _, _, l in rec for x in l]
        if not allleft:
            tally['no leftovers (declines elsewhere)'] += 1
            out[a] = {'shape': 'none', 'n': 0}
            continue
        sh, dirs = shape(allleft)
        tally[sh] += 1
        out[a] = {'shape': sh, 'n': len(allleft),
                  'dirs': {str(k): [list(x) for x in v] for k, v in list(dirs.items())[:4]}}
        if i % 10 == 9:
            print('%d/%d %s' % (i + 1, len(todo), dict(tally)), flush=True)
            json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
    json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
    print('FINAL', dict(tally), flush=True)
    print('-> ' + OUT)


if __name__ == '__main__':
    main()
