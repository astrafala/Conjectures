#!/usr/bin/env python3
"""Does the OEIS actually split a formula across two records of the same tag?

coverage.py counted 86,673 "wrapped" lines, but its test was weak: unbalanced parentheses
OR a trailing comma. A trailing comma ends thousands of perfectly complete lines (lists of
values, "a(n) = 1, 2, 3, ..."), and parentheses go unbalanced inside prose ("(see A000045").

The honest test for a continuation is that the FIRST line cannot stand alone -- it ends on
a binary operator or an equals sign -- or that the SECOND line begins where an expression
was left hanging. Anything else is two separate statements that happen to share a tag.
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
HANG = re.compile(r"[-+*/=^,(]\s*$")           # ends on an operator: cannot stand alone
OPSTART = re.compile(r"^\s*[-+*/=^)]")          # begins on an operator: cannot stand alone
CONT = re.compile(r"^\s*(where|with|and|for|if|\.\.\.)\b", re.I)

kinds = Counter()
ex = {}
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        a = "A" + fn[1:7]
        prev = None
        for line in open(os.path.join(dd, fn), errors="ignore"):
            line = line.rstrip("\n")
            if len(line) < 4 or line[0] != "%":
                prev = None
                continue
            tag = line[1]
            body = re.sub(r"^%.\s+A\d{6}\s*", "", line)
            if tag not in "FCe":
                prev = None
                continue
            if prev is not None and prev[0] == tag:
                pb = prev[1]
                if HANG.search(pb) and not pb.rstrip().endswith(","):
                    kinds["first line ends on an operator"] += 1
                    ex.setdefault("op", []).append((a, tag, pb[-70:], body[:70]))
                elif OPSTART.match(body):
                    kinds["second line begins on an operator"] += 1
                    ex.setdefault("start", []).append((a, tag, pb[-70:], body[:70]))
                elif pb.count("(") > pb.count(")") and not CONT.match(body):
                    kinds["unclosed parenthesis, no prose cue"] += 1
                    ex.setdefault("paren", []).append((a, tag, pb[-70:], body[:70]))
            prev = (tag, body)

for k, v in kinds.most_common():
    print(f"{v:8d}  {k}")
print()
for k in ("op", "start", "paren"):
    print("---", k)
    for a, tag, p, b in ex.get(k, [])[:8]:
        print(f"  {a} %{tag}  ...{p!r}")
        print(f"           -> {b!r}")
