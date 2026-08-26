#!/usr/bin/env python3
"""Live confirmation that a specific conjecture on a specific entry is still open.

Stricter than recheck.py: it looks for the exact conjecture line we settled, and it
flags ANY settlement wording anywhere on the entry, printing the hit so a human can
judge whether it refers to this conjecture or to a different one.
"""
import json, re, subprocess, sys, time

PROOF = re.compile(r"\bproof\b|\bproved\b|\bproven\b|is true|Kauers|Koutschan|"
                   r"has been shown|follows from|confirm\w*|verified|checked using|"
                   r"establish\w*|settled|no longer a conjecture|follows from the fact|"
                   r"immediate consequence|can be deduced|is a corollary", re.I)


def fetch(a):
    out = subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0",
                          f"https://oeis.org/search?q=id:{a}&fmt=json"],
                         capture_output=True, text=True, timeout=90).stdout
    return json.loads(out)[0]


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def check(a, conj):
    e = fetch(a)
    lines = []
    for k in ("comment", "formula", "link", "ext", "example"):
        lines += e.get(k) or []
    present = any(norm(conj) in norm(l) for l in lines)
    hits = [l[:160] for l in lines
            if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I)]
    return present, hits, e["time"][:10], e["revision"], e["name"], e.get("author", ""), \
        [int(v) for v in e["data"].split(",")], int(e["offset"].split(",")[0])


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))          # {anum: conjecture text}
    out = {}
    for a, conj in sorted(todo.items()):
        try:
            present, hits, t, rev, name, auth, data, off = check(a, conj)
        except Exception as ex:
            print(f"{a}  FETCH FAILED {ex}")
            continue
        time.sleep(0.3)
        st = "OPEN" if (present and not hits) else ("GONE" if not present else "SETTLED?")
        print(f"{a}  {st}")
        for h in hits:
            print(f"      hit: {h}")
        if st == "OPEN":
            out[a] = {"conj": conj, "time": t, "revision": rev, "name": name,
                      "author": auth, "data": data, "offset": off}
    json.dump(out, open("open-check.json", "w"), indent=1, sort_keys=True)
    print(f"\nstill open: {len(out)} of {len(todo)}")
