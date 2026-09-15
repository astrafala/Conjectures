#!/usr/bin/env python3
"""Of the 18,142 entries with an empirical statement, how many can be attacked?

An empirical formula is a conjecture, so it cannot serve as its own justification, and
Colin Barker's entries typically post an empirical recurrence AND an empirical generating
function together -- neither usable as the known side. What makes an entry tractable is
something stated as FACT: a posted formula that is not labelled empirical or conjectural,
or a NAME that is itself a definition ("Expansion of ...", "a(n) = ...").
"""
import json, os, re
from collections import Counter

ROOT = "/home/user/oeis/oeisdata/seq"
EMP = re.compile(r"^\s*Empirical\s*[:.]?\s*", re.I)
HEADS = re.compile(r"\(\s*Start\s*\)\s*$", re.I)
ENDS = re.compile(r"\(\s*End\s*\)", re.I)
GUESS = re.compile(r"empirical|conjectur|apparent|it seems|probably|appears", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct|Theorem", re.I)
GF = re.compile(r"^\s*(o\.?)?g\.?f\.?\s*[:.]|^\s*e\.?g\.?f\.?\s*[:.]", re.I)
CF = re.compile(r"^\s*a\(n\)\s*=(?!=)")
NAMEGF = re.compile(r"^\s*Expansion of\b", re.I)
NAMECF = re.compile(r"^\s*a\(n\)\s*=", re.I)


def empirical_lines(F):
    """(raw lines that are empirical, the statements with the label removed).

    Two sets, deliberately. The RAW lines are what a known-side detector must exclude;
    the STATEMENTS are what the engine tries to prove. Using one for both was wrong in
    each direction: matching "G.f.:" against a line that still reads "Empirical: G.f.:"
    finds nothing, and excluding by the cleaned text misses the raw line.
    """
    raw, stmt, inside = set(), set(), False
    for l in F:
        if EMP.match(l):
            raw.add(l.strip())
            if HEADS.search(l):
                inside = True
                continue
            stmt.add(EMP.sub("", l).strip())
            continue
        if inside:
            raw.add(l.strip())
            body = ENDS.sub("", l).strip()
            raw.add(body)
            if body:
                stmt.add(body)
            if ENDS.search(l):
                inside = False
    return raw, stmt


def main():
    rows, cnt = [], Counter()
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            txt = open(os.path.join(dd, fn), errors="ignore").read()
            if "mpirical" not in txt:
                continue
            a = "A" + fn[1:7]
            F, name, S = [], "", []
            for l in txt.split("\n"):
                if len(l) < 4:
                    continue
                body = re.sub(r"^%.\s+A\d{6}\s*", "", l)
                if l[1] in "FCe":
                    F.append(body)
                elif l[1] == "N":
                    name = body
                elif l[1] in "STU":
                    S.append(body)
            try:
                data = [int(v) for v in "".join(S).split(",") if v.strip()]
            except ValueError:
                continue
            if len(data) < 8:
                continue
            emp, stmts = empirical_lines(F)
            targets = [l for l in stmts
                       if GF.match(l) or (CF.match(l) and "a(n-" in l.replace(" ", ""))
                       or CF.match(l)]
            if not targets:
                continue
            if any(SETTLED.search(l) for l in F):
                cnt["something on the entry already settles it"] += 1
                continue
            outside = [l for l in F if l.strip() not in emp and not GUESS.search(l)]
            has_gf = any(GF.match(l) for l in outside)
            has_cf = any(CF.match(l) for l in outside)
            name_gf = bool(NAMEGF.match(name))
            name_cf = bool(NAMECF.match(name))
            if has_gf:
                k = "a posted generating function"
            elif has_cf:
                k = "a posted closed form"
            elif name_gf:
                k = "the NAME is 'Expansion of ...'"
            elif name_cf:
                k = "the NAME is a formula"
            else:
                cnt["nothing stated as fact to work from"] += 1
                continue
            cnt[k] += 1
            rows.append({"anum": a, "known": k, "targets": len(targets)})
    json.dump([r["anum"] for r in rows], open("emp-todo.json", "w"), indent=1)
    json.dump(rows, open("emp-cands.json", "w"), indent=1)
    print(f"{len(rows)} entries have an empirical statement AND something to prove it from")
    for k, c in cnt.most_common():
        print(f"{c:7d}  {k}")
    print(f"\nstatements to attack: {sum(r['targets'] for r in rows)}")


if __name__ == "__main__":
    main()
