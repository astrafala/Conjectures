#!/usr/bin/env python3
"""Hard Rule 2 / Hard Rule 3 pass: re-fetch each entry live and confirm it is still open.

Drops anything whose conjecture label has gone, that now carries a proof link or a
"this is true / proved" annotation, or that appears on the DeepMind formal-conjectures
list.
"""
import json, re, subprocess, time

PROOF = re.compile(r"\bproof\b|\bproved\b|\bproven\b|is true|Kauers|Koutschan|"
                   r"has been shown|follows from|confirm\w*|verified|checked using|"
                   r"establish\w*|settled|no longer a conjecture|follows from the fact|"
                   r"immediate consequence|can be deduced|is a corollary|"
                   r"is now a theorem|now a theorem|this is a theorem|"
                   r"has been established|resolved by|closed by", re.I)


def fetch(anum):
    out = subprocess.run(
        ["curl", "-sS", "-A", "Mozilla/5.0",
         f"https://oeis.org/search?q=id:{anum}&fmt=json"],
        capture_output=True, text=True, timeout=90).stdout
    return json.loads(out)[0]


def main():
    good = json.load(open("rec-verified.json"))
    exposed = set(open("exposed.txt").read().split()) if __import__("os").path.exists("exposed.txt") else set()
    kept, dropped = {}, {}
    for a, r in sorted(good.items()):
        try:
            e = fetch(a)
        except Exception as ex:
            dropped[a] = f"refetch failed: {ex}"
            continue
        time.sleep(0.25)
        blob = " || ".join(
            (e.get(k) or []) if isinstance(e.get(k), list) else [str(e.get(k) or "")]
            for k in ()) if False else ""
        lines = []
        for k in ("comment", "formula", "link", "ext", "example"):
            lines += e.get(k) or []
        # the conjecture must still be labelled
        conj = [l for l in lines
                if re.match(r"\s*Conjecture", l, re.I) and "a(n-" in l]
        if not conj:
            dropped[a] = "conjecture label no longer present"
            continue
        # no proof anywhere referring to a recurrence/conjecture
        hits = [l[:100] for l in lines
                if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I)]
        if hits:
            dropped[a] = f"proof marker now on entry: {hits[0]}"
            continue
        if a in exposed:
            dropped[a] = "on the formal-conjectures benchmark list"
            continue
        kept[a] = {**r, "conj": max(conj, key=len),
                   "time": e["time"][:10], "revision": e["revision"],
                   "name": e["name"], "author": e.get("author", ""),
                   "data": [int(v) for v in e["data"].split(",")],
                   "offset": int(e["offset"].split(",")[0])}
    for a, why in sorted(dropped.items()):
        print(f"DROP {a}: {why}")
    print(f"\nstill open: {len(kept)}   dropped: {len(dropped)}")
    json.dump(kept, open("rec-open.json", "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
