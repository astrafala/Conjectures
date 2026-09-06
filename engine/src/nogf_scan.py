#!/usr/bin/env python3
"""Recurrence conjectures on entries that post no G.f. line.

For many of these the generating function is still available: the entry's NAME says
"Expansion of <expr>", or the formula field gives a non-conjectural closed form for
a(n). Both are enough to run the residual test.
"""
import json, os, re

ROOT = "/home/user/oeis/oeisdata/seq"
LABEL = re.compile(r"^\s*(Conjecture[sd]?\b|Conjectured\b)", re.I)
EXPAND = re.compile(r"^(?:Expansion|E\.g\.f\.|G\.f\.|Generating function)\s*(?:of|:)\s*(.+)",
                    re.I)


def fields(path):
    f = {}
    for line in open(path, errors="ignore"):
        if line.startswith("%"):
            f.setdefault(line[1], []).append(
                re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def main():
    have = set(json.load(open("scan-cache.json")))
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
            anum = "A" + fn[1:7]
            if anum in have:
                continue
            p = os.path.join(dd, fn)
            head = open(p, errors="ignore").read()
            if "Conjectur" not in head or "a(n-" not in head:
                continue
            f = fields(p)
            conjs = [l for tag in ("C", "F", "e") for l in f.get(tag, [])
                     if LABEL.match(l) and "a(n-" in l.replace(" ", "")
                     and "=0" in l.replace(" ", "")]
            if not conjs:
                continue
            name = (f.get("N") or [""])[0]
            m = EXPAND.match(name)
            src = m.group(1).strip() if m else None
            if not src:
                continue
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            out[anum] = {"name": name, "src": src, "conjs": conjs,
                         "offset": int((f.get("O") or ["0"])[0].split(",")[0]),
                         "data": terms,
                         "egf": bool(re.match(r"E\.g\.f\.", name, re.I))}
        print(f"  scanned {scanned}", end="\r", flush=True)
    print()
    json.dump(out, open("nogf-cache.json", "w"), indent=1, sort_keys=True)
    print(f"{len(out)} entries whose NAME gives the generating function, "
          f"{sum(len(v['conjs']) for v in out.values())} conjectures")


if __name__ == "__main__":
    main()
