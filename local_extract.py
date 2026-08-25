#!/usr/bin/env python3
"""Extract recurrence-conjecture candidates straight from the local OEIS clone.

The clone holds every entry, so this replaces search entirely: no 200-result cap,
no login, no query guessing. Output is written in exactly the shape rec-cache.json
already uses, so the existing prover/auditor run unchanged.
"""
import json, os, re, sys

ROOT = "/home/user/oeis/oeisdata/seq"

REC = re.compile(r"Conjecture[: ].*?a\(n-\d+\)", re.I)
ZERO = re.compile(r"=\s*0\s*\.?\s*$|=\s*0\s*\.?\s*-")
PROOF = re.compile(r"\bproved\b|\bproof\b|\bproven\b|is true|Kauers|Koutschan|"
                   r"follows from the differential|has been shown", re.I)


def parse(path):
    fields = {}
    for line in open(path, errors="ignore"):
        if not line.startswith("%"):
            continue
        tag = line[1]
        rest = line[3:].strip()
        # strip the A-number that follows the tag
        rest = re.sub(r"^A\d{6}\s*", "", rest)
        fields.setdefault(tag, []).append(rest)
    return fields


def entry(path):
    f = parse(path)
    anum = "A" + os.path.basename(path)[1:7]
    name = (f.get("N") or [""])[0]
    data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
    try:
        terms = [int(t) for t in data.split(",") if t.strip()]
    except ValueError:
        return None
    if len(terms) < 8:
        return None
    off = (f.get("O") or ["0"])[0].split(",")[0]
    try:
        off = int(off)
    except ValueError:
        off = 0

    conj = None
    for tag in ("C", "F", "e"):
        for l in f.get(tag, []):
            if REC.search(l) and ("=0" in l.replace(" ", "") or "= 0" in l):
                if conj is None or len(l) > len(conj):
                    conj = l
    if not conj:
        return None

    gfs = []
    for l in f.get("F", []):
        m = re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I)
        if m:
            gfs.append(m.group(1).strip())
    if not gfs:
        return None

    proof = None
    for tag in ("C", "F", "H", "e"):
        for l in f.get(tag, []):
            if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I):
                proof = l[:140]
                break
        if proof:
            break

    return anum, {"name": name, "offset": off, "data": terms, "conj": conj,
                  "gfs": gfs, "proof": proof, "time": "", "revision": 0}


def main():
    out = {}
    n = 0
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            n += 1
            try:
                r = entry(os.path.join(dd, fn))
            except Exception:
                continue
            if r:
                out[r[0]] = r[1]
        print(f"  scanned {n} files, {len(out)} candidates", end="\r", flush=True)
    print()
    withgf = {a: v for a, v in out.items() if not v["proof"]}
    print(f"total recurrence conjectures with a G.f.: {len(out)}")
    print(f"  ... and no proof marker on the entry:   {len(withgf)}")
    json.dump(out, open("local-cache.json", "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
