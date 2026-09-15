#!/usr/bin/env python3
"""One bounded slice of the expansion-name sweep. Run repeatedly until it reports done."""
import json, sys
sys.path.insert(0, ".")
import runpool
from expname_run import attack


def report(it, res):
    st, val = res
    if st != "ok" or not val or val[0] != "ok":
        return
    for status, cl, rec in val[1]:
        if status in ("PROVED", "DISPROVED"):
            print(f"  {status:9s} {it[0]}  {cl[:60]}", flush=True)


if __name__ == "__main__":
    items = [tuple(x) for x in json.load(open("expname_cands.json"))]
    done = runpool.run(attack, items, lambda it: it[0], "expname_progress.json",
                       per_item=150, budget=int(sys.argv[1]) if len(sys.argv) > 1 else 540,
                       workers=4, report=report)
    if len(done) >= len(items):
        hits, dis = [], []
        for a, (st, val) in done.items():
            if st != "ok" or not val or val[0] != "ok":
                continue
            nm = next(x[1] for x in items if x[0] == a)
            for status, cl, rec in val[1]:
                if status == "PROVED":
                    hits.append({"anum": a, "conj": cl, "name": nm, **rec})
                elif status == "DISPROVED":
                    dis.append({"anum": a, "conj": cl, "name": nm, **rec})
        json.dump(hits, open("expname_hits.json", "w"), indent=1)
        json.dump(dis, open("expname_dis.json", "w"), indent=1)
        print(f"\nSWEEP COMPLETE: {len(hits)} proved, {len(dis)} disproved")
