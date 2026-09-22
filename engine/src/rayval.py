#!/usr/bin/env python3
"""Extend the exceptional set along its rays past the patch, and re-check the published terms.

If the leftovers really are rays k*v with d affine in k, extending them changes nothing inside
the patch and adds points outside it. The published terms only reach n ~ 35 and the patch
radius is 50, so a term that CHANGES under extension is a term the finite list was getting
right by accident.
"""
import sys, math, collections
sys.path.insert(0,'src')
import galfit, galcoord, galehr, localentry as LE

def rays_of(E):
    """group an exceptional list into primitive directions with d affine in k, or None"""
    dirs = collections.defaultdict(list)
    for m, n, d in E:
        g = math.gcd(abs(m), abs(n)) or 1
        dirs[(m // g, n // g)].append((g, d))
    out = []
    for v, ks in dirs.items():
        ks.sort()
        if len(ks) < 2:
            return None
        steps = {ks[i+1][1]-ks[i][1] for i in range(len(ks)-1)}
        gaps  = {ks[i+1][0]-ks[i][0] for i in range(len(ks)-1)}
        if len(steps) != 1 or len(gaps) != 1 or gaps != {1} or ks[0][0] != 1:
            return None
        out.append((v, ks[0][1], steps.pop()))      # d(k) = d1 + (k-1)*step
    return out

import os
ENTS = sys.argv[1:] or ['A310039','A310007','A310019','A310018','A310025']
for a in ENTS:
    p = galcoord.parse_name(LE.get(a)['name'])
    d, why = galfit.data(p['u'], p['t'], p['v'], radius=galcoord.RADIUS, exc=True)
    if not d: print('== %-9s refused'%a); continue
    planes, exc = d['planes'], d['exc']
    rr = [rays_of(E) if E else [] for E in exc]
    nray = sum(1 for i, E in enumerate(exc) if E and rr[i] is not None)
    nscat = sum(1 for i, E in enumerate(exc) if E and rr[i] is None)
    terms=[int(x) for x in LE.get(a)['data'].split(',') if x.strip()]
    N=min(len(terms),36)
    def ball(t, extend):
        tot=0
        for P,E,R in zip(planes,exc,rr):
            tot+=galehr.count(P,t)
            if extend and R is not None:
                for (v,d1,st) in R:
                    k=1
                    while True:
                        m,n=v[0]*k, v[1]*k
                        lo=max(A*m+B*n+C for A,B,C in P)
                        if lo> t: break
                        if lo <= t < d1+(k-1)*st: tot-=1
                        k+=1
            else:
                for (m,n,dt) in E:
                    if max(A*m+B*n+C for A,B,C in P) <= t < dt: tot-=1
        return tot
    fin=[ball(n,False)-ball(n-1,False) for n in range(1,N)]
    ext=[ball(n,True)-ball(n-1,True) for n in range(1,N)]
    want=terms[1:N]
    print('== %-9s classes with ray-shaped exc: %d, scattered: %d | finite %d/%d | ray-extended %d/%d'
          % (a, nray, nscat,
             sum(1 for x,y in zip(fin,want) if x==y), len(want),
             sum(1 for x,y in zip(ext,want) if x==y), len(want)), flush=True)
