#!/usr/bin/env python3
"""Every recurrence conjecture on every entry that posts a generating function.

The original extractor kept only ONE conjecture per entry (the longest line), so an
entry carrying two or three conjectured recurrences had the rest silently dropped.
This collects all of them, minus the ones already attempted.
"""
import json, os, re

ROOT = "/home/user/oeis/oeisdata/seq"


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def main():
    attempted = {}
    for f, key in (("rec-cache.json", "seen"), ("egf-cache.json", None),
                   ("local-cache.json", None)):
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        if key:
            d = d[key]
        for a, v in d.items():
            if v and v.get("conj"):
                attempted.setdefault(a, set()).add(norm(v["conj"]))
    for f in ("extra-conj.json",):
        if os.path.exists(f):
            for a, v in json.load(open(f)).items():
                for c in v["others"]:
                    attempted.setdefault(a, set()).add(norm(c))

    out = {}
    for a in sorted(attempted):
        p = f"{ROOT}/{a[:4]}/{a}.seq"
        if not os.path.exists(p):
            continue
        f = {}
        for line in open(p, errors="ignore"):
            if line.startswith("%"):
                f.setdefault(line[1], []).append(
                    re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
        conjs = []
        for tag in ("C", "F", "e"):
            for l in f.get(tag, []):
                if not re.match(r"Conjectur", l, re.I):
                    continue
                s = l.replace(" ", "")
                if "a(n-" not in s or "=0" not in s:
                    continue
                if norm(l) in attempted[a] or any(norm(l) == norm(o) for o in conjs):
                    continue
                conjs.append(l)
        if not conjs:
            continue
        gfs = [re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I).group(1).strip()
               for l in f.get("F", [])
               if re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I)]
        egfs = [re.match(r"E\.g\.f\.\s*:?\s*(.+)", l.strip(), re.I).group(1).strip()
                for l in f.get("F", [])
                if re.match(r"E\.g\.f\.\s*:?\s*(.+)", l.strip(), re.I)]
        if not (gfs or egfs):
            continue
        data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
        try:
            terms = [int(t) for t in data.split(",") if t.strip()]
        except ValueError:
            continue
        if len(terms) < 8:
            continue
        out[a] = {"name": (f.get("N") or [""])[0],
                  "offset": int((f.get("O") or ["0"])[0].split(",")[0]),
                  "data": terms, "conjs": conjs, "gfs": gfs, "egfs": egfs,
                  "proof": None, "time": "", "revision": 0}
    json.dump(out, open("allconj-cache.json", "w"), indent=1, sort_keys=True)
    print(f"{len(out)} entries carry {sum(len(v['conjs']) for v in out.values())} "
          f"never-attempted recurrence conjectures with a g.f. posted")


if __name__ == "__main__":
    main()
