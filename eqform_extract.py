#!/usr/bin/env python3
"""Recurrence conjectures posted as a plain equation, "a(n) = ...", rather than in
the "... = 0" form the main extractor required.

This whole class was invisible to the earlier pipeline: the extractor insisted on a
right-hand side of 0, so several hundred conjectures -- most of them constant-
coefficient -- were never even attempted.
"""
import json, os, re

ROOT = "/home/user/oeis/oeisdata/seq"


def parse(path):
    f = {}
    for line in open(path, errors="ignore"):
        if not line.startswith("%"):
            continue
        f.setdefault(line[1], []).append(re.sub(r"^A\d{6}\s*", "", line[3:].strip()))
    return f


def clean_body(body):
    """Strip the trailing validity range and any prose tail, keep the equation."""
    b = body.split(" - _")[0]
    b = re.sub(r"\bfor\s+n\s*[><=].*$", "", b)
    b = re.sub(r",?\s*(with|where|and|G\.f\.|see|Cf\.)\s.*$", "", b, flags=re.I)
    b = b.strip().rstrip(".").strip().rstrip(",").strip()
    # a chained statement "a(n) = <recurrence> = <closed form>" asserts both halves;
    # the recurrence is the first equation
    parts = re.split(r"(?<![<>=!])=(?!=)", b)
    if len(parts) > 2:
        b = "=".join(parts[:2])
    return b.strip()


def is_pure(b):
    core = re.sub(r"a\(n(-\d+)?\)", "", b)
    core = re.sub(r"[0-9n\s+\-*/()^=.,]", "", core)
    return not core and "=" in b and "a(n-" in b.replace(" ", "")


def main():
    out = {}
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            p = os.path.join(dd, fn)
            head = open(p, errors="ignore").read()
            if "Conjecture" not in head or "a(n-" not in head:
                continue
            f = parse(p)
            anum = "A" + fn[1:7]
            conjs = []
            for tag in ("C", "F", "e"):
                for l in f.get(tag, []):
                    if not re.match(r"Conjecture", l, re.I):
                        continue
                    body = re.sub(r"^Conjecture[s]?[:.]?\s*", "", l, flags=re.I)
                    if re.search(r"=\s*0\s*\.?\s*$", body.split(" - _")[0].strip()):
                        continue          # already handled by the main extractor
                    b = clean_body(body)
                    if is_pure(b):
                        conjs.append((l, b))
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
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) < 8:
                continue
            off = int((f.get("O") or ["0"])[0].split(",")[0])
            out[anum] = {"name": (f.get("N") or [""])[0], "offset": off,
                         "data": terms, "conjs": conjs, "gfs": gfs, "egfs": egfs,
                         "proof": None, "time": "", "revision": 0}
    json.dump(out, open("eqform-cache.json", "w"), indent=1, sort_keys=True)
    ng = sum(1 for v in out.values() if v["gfs"] or v["egfs"])
    print(f"{len(out)} entries, {sum(len(v['conjs']) for v in out.values())} conjectures; "
          f"{ng} entries post a g.f. or e.g.f.")


if __name__ == "__main__":
    main()
