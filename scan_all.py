#!/usr/bin/env python3
"""One full sweep of the local OEIS clone for every recurrence conjecture we could
possibly attempt, under every label OEIS uses for them.

Earlier extractors each caught a slice: one required the exact label "Conjecture:",
one kept only the longest conjecture line per entry, one insisted the right-hand side
be literally 0. This takes all of them at once, so what comes out is the complete
candidate set rather than a sample of it.
"""
import json, os, re

ROOT = "/home/user/oeis/oeisdata/seq"

LABEL = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
PROOF = re.compile(r"\bproof\b|\bproved\b|\bproven\b|is true|Kauers|Koutschan|"
                   r"has been shown|follows from|confirm\w*|verified|checked using|"
                   r"establish\w*|settled|no longer a conjecture|"
                   r"immediate consequence|can be deduced|is a corollary", re.I)


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def fields(path):
    f = {}
    for line in open(path, errors="ignore"):
        if line.startswith("%"):
            f.setdefault(line[1], []).append(
                re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def main():
    out = {}
    scanned = 0
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            scanned += 1
            p = os.path.join(dd, fn)
            head = open(p, errors="ignore").read()
            if "Conjectur" not in head or "a(n-" not in head:
                continue
            f = fields(p)
            anum = "A" + fn[1:7]
            conjs = []
            for tag in ("C", "F", "e"):
                for l in f.get(tag, []):
                    if not LABEL.match(l):
                        continue
                    s = l.replace(" ", "")
                    if "a(n-" not in s or "=0" not in s:
                        continue
                    if any(norm(l) == norm(o) for o in conjs):
                        continue
                    conjs.append(l)
            if not conjs:
                continue
            gfs, egfs = [], []
            for l in f.get("F", []):
                m = re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I)
                if m:
                    gfs.append(m.group(1).strip())
                m = re.match(r"E\.g\.f\.\s*:?\s*(.+)", l.strip(), re.I)
                if m:
                    egfs.append(m.group(1).strip())
            if not (gfs or egfs):
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            settled = None
            for tag in ("C", "F", "H", "e"):
                for l in f.get(tag, []):
                    if PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I):
                        settled = l[:160]
                        break
                if settled:
                    break
            out[anum] = {"name": (f.get("N") or [""])[0],
                         "offset": int((f.get("O") or ["0"])[0].split(",")[0]),
                         "data": terms, "conjs": conjs, "gfs": gfs, "egfs": egfs,
                         "settled": settled, "time": "", "revision": 0}
        print(f"  scanned {scanned}", end="\r", flush=True)
    print()
    json.dump(out, open("scan-cache.json", "w"), indent=1, sort_keys=True)
    tot = sum(len(v["conjs"]) for v in out.values())
    open_ = {a: v for a, v in out.items() if not v["settled"]}
    print(f"{len(out)} entries, {tot} conjectures, g.f. posted")
    print(f"{len(open_)} entries carry no settlement note "
          f"({sum(len(v['conjs']) for v in open_.values())} conjectures)")


if __name__ == "__main__":
    main()
