#!/usr/bin/env python3
"""What is inside the multi-line conjecture blocks?

OEIS often writes

    %F Axxxxxx Conjectures from _Someone_, date: (Start)
    %F Axxxxxx a(n) = ... ;
    %F Axxxxxx G.f.: ... ;
    %F Axxxxxx (End)

Every sweep in this project reads one line at a time and selects lines beginning with
"Conjecture". The statements inside such a block do not begin with that word, so they have
been invisible to every engine from the start -- 3,421 headings' worth. This asks what is
actually in them.
"""
import os, re
from collections import Counter
ROOT = "/home/user/oeis/oeisdata/seq"
HEAD = re.compile(r"^\s*Conjectur\w*.*\(\s*Start\s*\)\s*$", re.I)
END = re.compile(r"\(\s*End\s*\)", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)

cnt, ex = Counter(), {}
entries = blocks = 0
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    for fn in sorted(os.listdir(dd)):
        if not fn.endswith(".seq"):
            continue
        txt = open(os.path.join(dd, fn), errors="ignore").read()
        if "Start" not in txt or "Conjectur" not in txt:
            continue
        a = "A" + fn[1:7]
        lines = [(l[:2], re.sub(r"^A\d{6}\s*", "", l[3:].strip()))
                 for l in txt.split("\n") if l[:2] in ("%F", "%C", "%e")]
        inside, used = False, False
        for tag, l in lines:
            if HEAD.match(l):
                inside, used = True, True
                blocks += 1
                continue
            if inside and END.search(l):
                inside = False
                l = END.sub("", l).strip()
                if not l:
                    continue
            if not inside and not l:
                continue
            if not inside:
                continue
            if SETTLED.search(l) or len(l) < 8:
                continue
            nb = l.replace(" ", "")
            if "a(n-" in nb and "=0" in nb:
                k = "a linear recurrence, = 0"
            elif re.match(r"a\(n\)\s*=", l) and "a(n-" in nb:
                k = "a linear recurrence, a(n) = ..."
            elif re.match(r"(o\.?)?g\.?f\.?\s*[:.]", l, re.I):
                k = "a generating function"
            elif re.match(r"e\.?g\.?f\.?\s*[:.]", l, re.I):
                k = "an exponential generating function"
            elif re.match(r"a\(n\)\s*=", l):
                k = "a closed form for a(n)"
            elif re.search(r"\bmod\b|\(mod|congruen", l, re.I):
                k = "a congruence"
            elif re.search(r"~|asymptot", l, re.I):
                k = "asymptotics"
            else:
                k = "something else"
            cnt[k] += 1
            ex.setdefault(k, []).append((a, l[:120]))
        entries += used
print(f"{entries} entries contain a conjecture block; {blocks} blocks; "
      f"{sum(cnt.values())} statements inside them\n")
for k, c in cnt.most_common():
    print(f"{c:6d}  {k}")
    for a, l in ex[k][:3]:
        print(f"          {a}  {l}")
