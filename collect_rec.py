#!/usr/bin/env python3
"""Collect OEIS entries carrying a conjectured P-recursive recurrence AND an
explicit algebraic generating function, ready for holonomic.py to settle.
"""
import json, os, re, subprocess, sys, time

CACHE = "rec-cache.json"
REC = re.compile(r"Conjecture[:.]\s*(.*?a\(n-\d+\).*?)(?:\.\s*-\s*_|$)", re.S)
GF = re.compile(r"^G\.f\.\s*:?\s*(.+)$", re.I)


def fetch(query, start):
    url = f"https://oeis.org/search?q={query}&fmt=json&start={start}"
    out = subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0", url],
                         capture_output=True, text=True, timeout=90).stdout
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        return []
    if d is None:
        return []
    return d if isinstance(d, list) else (d.get("results") or [])


def rec_conjecture(e):
    for k in ("formula", "comment"):
        for l in e.get(k) or []:
            if not re.match(r"\s*Conjecture", l, re.I):
                continue
            if "a(n-" not in l:
                continue
            if "=0" in l.replace(" ", "") or "= 0" in l:
                return l
    return None


def gfs(e):
    out = []
    for l in e.get("formula") or []:
        m = GF.match(l.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def proof_link(e):
    for l in e.get("link") or []:
        if re.search(r"proof|proved|Kauers|Koutschan", l, re.I):
            return l[:120]
    for k in ("comment", "formula", "ext"):
        for l in e.get(k) or []:
            if re.search(r"\bprove[dn]?\b|proof of the (above )?conjecture", l, re.I):
                return l[:120]
    return None


def main():
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {"seen": {}, "q": {}}
    pages = int(os.environ.get("PAGES", "12"))
    for q in sys.argv[1:]:
        done = cache["q"].get(q, 0)
        new = 0
        for page in range(pages):
            s = page * 10
            if s < done:
                continue
            batch = fetch(q, s)
            if not batch:
                break
            for e in batch:
                a = "A%06d" % e["number"]
                if a in cache["seen"]:
                    continue
                conj = rec_conjecture(e)
                if not conj:
                    cache["seen"][a] = None
                    continue
                cache["seen"][a] = {
                    "name": e.get("name", ""), "offset": int(e["offset"].split(",")[0]),
                    "data": [int(v) for v in e["data"].split(",")],
                    "conj": conj, "gfs": gfs(e), "proof": proof_link(e),
                    "time": e["time"][:10], "revision": e["revision"],
                }
                new += 1
            time.sleep(0.3)
            if len(batch) < 10:
                break
        cache["q"][q] = max(done, pages * 10)
        print(f"[{q}] +{new}")
    json.dump(cache, open(CACHE, "w"), indent=1, sort_keys=True)
    hits = {a: v for a, v in cache["seen"].items() if v}
    withgf = {a: v for a, v in hits.items() if v["gfs"] and not v["proof"]}
    print(f"\nrecurrence conjectures: {len(hits)}")
    print(f"  ... with an explicit G.f. and no proof marker: {len(withgf)}")
    for a, v in sorted(withgf.items())[:200]:
        print(f"{a}  gf: {v['gfs'][0][:74]}")
        print(f"       {v['conj'][:120]}")


if __name__ == "__main__":
    main()
