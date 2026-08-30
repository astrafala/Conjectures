#!/usr/bin/env python3
"""Which conjectural lines are TRUNCATED -- split across two records so that what an
engine reads is only half the statement?

The counts wrapcheck.py produced were inflated the same way coverage.py's were: the
character class for "ends on an operator" contains '-', which matches every rule of every
ASCII table in the corpus, and every attribution line "- _Name_, date".

The sharp test needs no guess about the following line. A statement I would actually feed
to an engine is truncated exactly when it cannot stand alone: its parentheses do not
balance, or it ends on an operator that demands a right operand. Prose does not do that.
So this counts the conjectural lines that are themselves incomplete, which is the only
case where reading half a conjecture as a whole one can happen.
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur|Empirical)", re.I)
TABLE = re.compile(r"^[\s|+*=-]*$|^[-=]{4,}")
ATTRIB = re.compile(r"-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d")
ENDOP = re.compile(r"[+*/=^]\s*$")          # '-' left out on purpose: see above

cnt = Counter()
ex = []
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        a = "A" + fn[1:7]
        for line in open(os.path.join(dd, fn), errors="ignore"):
            line = line.rstrip("\n")
            if len(line) < 4 or line[0] != "%" or line[1] not in "FCN":
                continue
            body = re.sub(r"^%.\s+A\d{6}\s*", "", line)
            if not MARK.search(body) or TABLE.match(body):
                continue
            cnt["conjectural lines"] += 1
            b = ATTRIB.split(body)[0]
            b = re.sub(r"\(Start\)|\(End\)", "", b)
            bad = []
            if b.count("(") != b.count(")"):
                bad.append("parens")
            if b.count("[") != b.count("]"):
                bad.append("brackets")
            if ENDOP.search(b) and not b.rstrip().endswith("..."):
                bad.append("ends on an operator")
            if bad:
                cnt["INCOMPLETE: " + ", ".join(bad)] += 1
                ex.append((a, line[1], body[:150]))

for k, v in cnt.most_common():
    print(f"{v:8d}  {k}")
print(f"\n{len(ex)} incomplete; first 25:")
for a, tag, b in ex[:25]:
    print(f"  {a} %{tag}  {b}")
