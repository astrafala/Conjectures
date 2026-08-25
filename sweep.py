#!/usr/bin/env python3
"""Sweep the OEIS API for entries carrying a literal `Conjecture:` label.

Section 2 of the ledger: OEIS search ignores quotes, so the label cannot be
isolated server-side. Pull results in bulk, then filter locally on the literal
label. Results are cached so a session never re-sweeps covered ground.
"""
import json, os, re, subprocess, sys, time

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sweep-cache.json")
UA = "Mozilla/5.0"

# Entries already settled, already held, or already taken (ledger Sections 3, 4, 7).
HELD = """A047926 A008365 A000040 A008364 A059324 A061002 A063305 A000071 A000139
A000364 A059970 A036284 A092287 A129454 A129365 A037096 A037097 A087726 A063321
A063337 A005329 A129364 A062368""".split()
DEAD = """A050295 A067274 A072592 A067793 A067745 A063170 A092143 A005251 A039004
A034496 A070226 A098016 A000010 A006519 A000215 A051190 A224479 A036286 A059971
A364812 A224497 A027871 A062367 A136380 A136378 A136379 A136381 A136382 A136383
A136384 A136385 A136386 A063318 A063369 A063224 A129439 A129453 A129455 A090494
A176898 A010051 A063289""".split()
HARD = """A051924 A000984 A000006 A001146 A049048 A054979 A082613 A036840 A036845
A057856 A060318 A001227""".split()
TAKEN = """A002627 A025166 A176677 A214615 A045406 A001711 A348410""".split()

SKIP = set(HELD) | set(DEAD) | set(HARD) | set(TAKEN)

LABEL = re.compile(r"(?:^|(?<=[.;]\s))\s*Conjecture\b\s*[:.]", re.I)


def fetch(query, start):
    url = f"https://oeis.org/search?q={query}&fmt=json&start={start}"
    out = subprocess.run(["curl", "-sS", "-A", UA, url],
                         capture_output=True, text=True, timeout=60).stdout
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        return []
    return d if isinstance(d, list) else (d.get("results") or [])


def labelled(entry):
    """Return the conjecture lines that carry the literal label."""
    hits = []
    for field in ("comment", "formula", "example"):
        for line in entry.get(field) or []:
            if LABEL.search(line):
                hits.append((field, line))
    return hits


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            return json.load(fh)
    return {"seen": {}, "queries": {}}


def sweep(query, pages, cache):
    done = cache["queries"].get(query, 0)
    found = []
    for page in range(pages):
        start = page * 10
        if start < done:
            continue
        for e in fetch(query, start):
            anum = "A%06d" % e["number"]
            if anum in SKIP or anum in cache["seen"]:
                continue
            hits = labelled(e)
            if not hits:
                cache["seen"][anum] = None
                continue
            rec = {"name": e.get("name", ""), "keyword": e.get("keyword", ""),
                   "hits": hits}
            cache["seen"][anum] = rec
            found.append((anum, rec))
        time.sleep(0.4)
    cache["queries"][query] = max(done, pages * 10)
    return found


def main():
    cache = load_cache()
    queries = sys.argv[1:] or ["conjecture+valuation"]
    total = []
    for q in queries:
        hits = sweep(q, pages=8, cache=cache)
        print(f"[{q}] {len(hits)} newly labelled")
        total += hits
    with open(CACHE, "w") as fh:
        json.dump(cache, fh, indent=1, sort_keys=True)
    print(f"\n{len(total)} candidates, {len(cache['seen'])} entries examined so far\n")
    for anum, rec in total:
        print(f"{anum}  [{rec['keyword']}]  {rec['name'][:78]}")
        for field, line in rec["hits"][:2]:
            print(f"    ({field}) {line[:230]}")


if __name__ == "__main__":
    main()
