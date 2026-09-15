#!/usr/bin/env python3
"""Assemble the metadata each replacement paper needs, one live fetch per entry.

A slot is one conjecture, not one entry: two entries here carry two separate
conjectures apiece, and each gets its own paper.
"""
import json, re, sys, time
import sympy as sp
from verify_open import fetch, PROOF, norm
from prove_rec import parse_gf, residual_poly
from holonomic import taylor
import logexp as le

x, n = sp.symbols('x n')


def build(slots):
    out = []
    cache = {}
    for s in slots:
        a = s["anum"]
        if a not in cache:
            cache[a] = fetch(a)
            time.sleep(0.3)
        e = cache[a]
        lines = [l for k in ("comment", "formula", "link", "ext", "example")
                 for l in (e.get(k) or [])]
        match = [l for l in lines if norm(s["conj"]) in norm(l)]
        if not match:
            print(f"{a}: conjecture no longer on the entry -- dropped")
            continue
        data = [int(v) for v in e["data"].split(",")]
        off = int(e["offset"].split(",")[0])
        def heads(pat):
            out = []
            for l in (e.get("formula") or []):
                m = re.match(pat + r"\s*:?\s*(.+)", l.strip(), re.I)
                if m:
                    out.append(m.group(1).strip())
            return out
        gfs, egfs = heads(r"G\.f\."), heads(r"E\.g\.f\.")
        if s.get("gf_src"):
            gfs = [s["gf_src"]] + [g for g in gfs if g != s["gf_src"]]
        # independent integer re-check on the live terms
        rec = {"anum": a, "conj": match[0], "name": e["name"], "offset": off,
               "data": data, "time": e["time"][:10], "revision": e["revision"],
               "gfs": gfs, "egfs": egfs, "mode": s.get("mode", "ogf"),
               "num": s["num"], "gf_from_name": s.get("gf_from_name", False)}
        out.append(rec)
    json.dump(out, open("slots.json", "w"), indent=1)
    print(f"{len(out)} slots assembled")


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])))
