#!/usr/bin/env python3
"""Fill the b-file cache, one request at a time.

Nothing clever here on purpose. bfile.fetch enforces a 1.2 second gap between requests and
this calls it in a single process, because a four-worker version of this script is what got
the address blocked. Roughly 400 files per slice; the queue is worked through over as many
sessions as it takes.
"""
import json, os, sys, time
sys.path.insert(0, ".")
import bfile

if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    q = json.load(open("bsweep_queue.json"))
    todo = [a for a in q
            if not os.path.exists(os.path.join(bfile.CACHE, "b" + a[1:] + ".txt"))]
    t0, got, miss = time.time(), 0, 0
    for a in todo:
        if time.time() - t0 > budget:
            break
        r = bfile.fetch(a)
        if r == "BLOCKED":
            # stop at once rather than keep asking a service that has said no
            print("  the service is throttling; stopping this slice early", flush=True)
            break
        if r is None:
            miss += 1
        else:
            got += 1
    have = sum(1 for a in q
               if os.path.exists(os.path.join(bfile.CACHE, "b" + a[1:] + ".txt")))
    print(f"  fetched {got}, unavailable {miss} this slice; cache now holds {have}/{len(q)}")
