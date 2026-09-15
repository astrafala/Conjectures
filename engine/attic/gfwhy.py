#!/usr/bin/env python3
"""What defeats the generating-function parser on the 109 entries it cannot read.

Same discipline as the summation census: find out what the notation actually is before
writing anything to handle it.
"""
import json, re, signal
from collections import Counter
import sympy as sp
from diagnose import entry, GFL, TO
from prove_rec import parse_gf

signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))

PAT = [
    (r"Series_Reversion|series reversion", "series reversion"),
    (r"\bA\d{6}\b", "refers to another sequence"),
    (r"Sum_\{|Product_\{", "infinite sum or product"),
    (r"satisfies|implicit|where A\(x\)|A\(x\)\s*=.*A\(x\)", "implicit equation"),
    (r"\bexp\(|\blog\(|\bsin\(|\bcos\(|Bessel|hypergeom|LambertW|Gamma\(|\bpsi\(",
     "transcendental"),
    (r"G\(k\)|U\(k\)|Q\(k\)|W\(k\)|E\(k\)|continued fraction", "continued fraction"),
    (r"Integral", "integral"),
    (r"\bfloor\(|\bceiling\(", "floor/ceiling"),
    (r"\bif\b|\bfor n\b|\botherwise\b", "conditional / prose"),
    (r"=", "an equation, not an expression"),
]

rows, cnt, ex = {}, Counter(), {}
todo = [a for a, r in json.load(open("diagnose.json")).items()
        if r == "g.f. does not parse"]
for a in todo:
    F, data, off = entry(a)
    gfs = [l for l in F if GFL.match(l)]
    label = "no g.f. line"
    for g in gfs:
        raw = (g.split(":", 1)[-1] if ":" in g else g).split(" - _")[0].strip()
        lab = None
        for pat, name in PAT:
            if re.search(pat, raw, re.I):
                lab = name
                break
        if lab is None:
            try:
                signal.alarm(20)
                parse_gf(raw, 'x', raw=raw)
                signal.alarm(0)
                lab = "PARSES NOW"
            except TO:
                signal.alarm(0); lab = "timeout"
            except Exception as e:
                signal.alarm(0); lab = f"sympy: {str(e)[:45]}"
        label = lab
        if lab == "PARSES NOW":
            break
    cnt[label] += 1
    rows[a] = label
    ex.setdefault(label, (a, (gfs[0][:120] if gfs else "")))
json.dump(rows, open("gfwhy.json", "w"), indent=1, sort_keys=True)
for l, c in cnt.most_common():
    print(f"{c:5d}  {l}")
    print(f"        {ex[l][0]}  {ex[l][1]}")
