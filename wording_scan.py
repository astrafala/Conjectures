#!/usr/bin/env python3
"""Re-scan every entry behind the roster for settlement wording, with a widened pattern.

The pattern that built the roster matched "verified" but not "verifies", and a note
reading "the Maple command sumrecursion ... verifies this recurrence" is a settlement.
Anything this flags is printed in full and read; the wording decides, not the match.
"""
import glob, json, os, re, sys

WIDE = re.compile(
    r"\bproof\b|prove[sndg]?\b|proving|\bproven\b|is true|Kauers|Koutschan|"
    r"has been shown|\bshown\b|\bshows\b|follows from|confirm\w*|verif\w*|checked using|"
    r"establish\w*|settled|no longer a conjecture|immediate consequence|can be deduced|"
    r"deduce\w*|is a corollary|is now a theorem|now a theorem|this is a theorem|"
    r"has been established|resolved by|closed by|is correct|are correct|follows easily|"
    r"follows at once|follows immediately|derives from|is a consequence|sumrecursion|"
    r"Zeilberger|holonomic guess|implies the|by induction|can be obtained|"
    r"may be obtained|obtained from the|follows by|is implied by|implies _?R\. ?J|"
    r"implies the conjecture|short proof|we can obtain the recurrence", re.I)

SEQ = "/home/user/oeis/oeisdata/seq"


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def roster():
    """rank -> (anum, conjecture text or None)."""
    rm = json.load(open("rank-map.json"))
    bynum = {}
    for f in sorted(glob.glob("*.json")):
        try:
            rows = json.load(open(f))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for s in rows:
            if isinstance(s, dict) and "num" in s and "conj" in s and "anum" in s:
                bynum.setdefault(s["num"], (s["anum"], s["conj"]))
    byanum = {}
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json",
              "open-check.json"):
        if os.path.exists(f):
            try:
                for a, v in json.load(open(f)).items():
                    if isinstance(v, dict) and v.get("conj"):
                        byanum.setdefault(a, v["conj"])
            except Exception:
                pass
    out = {}
    for r in rm:
        a, was = r["anum"], r["was"]
        c = None
        if was in bynum and bynum[was][0] == a:
            c = bynum[was][1]
        if c is None:
            c = byanum.get(a)
        out[r["rank"]] = (a, c)
    return out


def lines_of(a):
    p = f"{SEQ}/{a[:4]}/{a}.seq"
    if not os.path.exists(p):
        return None
    out = []
    for l in open(p, errors="ignore"):
        m = re.match(r"^%([CFHeta])\s+A\d+\s*(.*)$", l.rstrip("\n"))
        if m:
            out.append(m.group(2))
    return out


def main():
    todo = roster()
    flagged, missing, noconj = [], [], []
    for num, (a, conj) in sorted(todo.items()):
        ls = lines_of(a)
        if ls is None:
            missing.append((num, a)); continue
        if conj is None:
            noconj.append((num, a))
        hits = []
        for l in ls:
            if not WIDE.search(l):
                continue
            if conj is not None and norm(conj)[:70] in norm(l):
                hits.append(("SELF", l))          # wording inside our own conjecture line
            elif re.search(r"conjectur|recurrence", l, re.I):
                hits.append(("NEAR", l))
        if hits:
            flagged.append((num, a, conj, hits))
    json.dump([{"num": n, "anum": a, "conj": c,
                "hits": [{"kind": k, "line": l} for k, l in h]}
               for n, a, c, h in flagged], open("wording-hits.json", "w"), indent=1)
    print(f"{len(todo)} papers, {len(flagged)} with settlement wording to read, "
          f"{len(missing)} entries not in the local clone, {len(noconj)} with no text on file")
    if missing:
        print("  not in clone:", missing[:10])
    if noconj:
        print("  no conjecture text:", noconj[:20], "..." if len(noconj) > 20 else "")


if __name__ == "__main__":
    main()
