#!/usr/bin/env python3
"""What do the 39,487 conjectural lines actually SAY?

Every engine so far was built for a shape I had already seen. This asks the opposite
question: sort all of them by shape first, and see which classes are large and untouched.
Classification is by the leading construct of the statement, tried in order, so each line
lands in exactly one bucket.
"""
import os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*[:,]?\s*", re.I)
ATTRIB = re.compile(r"-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d")
TABLE = re.compile(r"^[\s|+*=-]*$|^[-=]{4,}")

SHAPES = [
    (re.compile(r"^(D-finite with recurrence\s*)?[-+0-9(].*\ba\(n\).*=\s*0\s*\.?$"), "recurrence, = 0 form"),
    (re.compile(r"^a\(n\)\s*=.*\ba\(n-\d", re.I), "recurrence, a(n) = ... form"),
    (re.compile(r"^(o\.)?g\.f\.\s*[:=]", re.I), "generating function"),
    (re.compile(r"^e\.g\.f\.\s*[:=]", re.I), "exponential g.f."),
    (re.compile(r"^a\(n\)\s*=\s*Sum_", re.I), "a(n) = a sum"),
    (re.compile(r"^a\(n\)\s*=\s*Product_", re.I), "a(n) = a product"),
    (re.compile(r"^a\(n\)\s*=\s*\[?x\^", re.I), "coefficient extraction"),
    (re.compile(r"^a\(n\)\s*=\s*A\d{6}\(", re.I), "a(n) = another entry"),
    (re.compile(r"^a\(n\)\s*=.*\bA\d{6}\b", re.I), "a(n) = involves another entry"),
    (re.compile(r"^a\(n\)\s*[=~]"), "a(n) = closed form"),
    (re.compile(r"^(Sum|Product)_", re.I), "an identity between sums"),
    (re.compile(r"\b(mod|divides|divisible|congruen)", re.I), "congruence / divisibility"),
    (re.compile(r"(lim|asymptot|~|approaches|tends)", re.I), "asymptotics / limits"),
    (re.compile(r"^(a\(n\)|T\(n,k\)).*[<>]"), "an inequality"),
    (re.compile(r"^T\(n,\s*k\)", re.I), "a triangle entry"),
    (re.compile(r"\b(prime|composite|squarefree|perfect|infinite\w*)\b", re.I), "number-theoretic prose"),
    (re.compile(r"^(this|the|there|it|all|every|no |for )", re.I), "prose"),
]

cnt, ex = Counter(), {}
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
            if not MARK.match(body) or TABLE.match(body):
                continue
            s = ATTRIB.split(MARK.sub("", body))[0].strip()
            s = re.sub(r"\(Start\)|\(End\)", "", s).strip()
            if not s:
                continue
            for pat, name in SHAPES:
                if pat.search(s):
                    cnt[name] += 1
                    ex.setdefault(name, []).append((a, s[:110]))
                    break
            else:
                cnt["UNCLASSIFIED"] += 1
                ex.setdefault("UNCLASSIFIED", []).append((a, s[:110]))

tot = sum(cnt.values())
print(f"{tot} conjectural statements\n")
for k, v in cnt.most_common():
    print(f"{v:7d}  {k}")
print()
import sys
for k in sys.argv[1:]:
    print("---", k)
    for a, s in ex.get(k, [])[:20]:
        print(f"  {a}  {s}")
