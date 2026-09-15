#!/usr/bin/env python3
"""audit_deep across the four cores: each worker takes every k-th A-number and writes its
own shard, so a killed run loses nothing and the shards merge by simple union."""
import json, os, sys, subprocess, glob

N = 4


def merge():
    out = json.load(open('audit_deep.json')) if os.path.exists('audit_deep.json') else {}
    for f in glob.glob('audit_deep_w*.json'):
        out.update(json.load(open(f)))
    json.dump(out, open('audit_deep.json', 'w'))
    return out


if __name__ == '__main__':
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    base = merge()
    ps = []
    for w in range(N):
        ps.append(subprocess.Popen([sys.executable, 'audit_deep_worker.py',
                                    str(w), str(N), str(budget)]))
    for p in ps:
        p.wait()
    out = merge()
    import collections
    print(len(out), dict(collections.Counter(v['v'] for v in out.values())))
