#!/usr/bin/env python3
"""Pull, for each entry, the exact conjecture sentence, who posted it, when, and the
entry's own last-modified line -- all straight from the .seq file, never paraphrased."""
import re, json

SEQ = "/home/user/oeis/oeisdata/seq/{0}/{1}.seq"
PHI = re.compile(r"dividing phi ?\(k\)")


def meta(anum):
    txt = open(SEQ.format(anum[:4], anum)).read()
    m = re.search(r"^%I .*?#(\d+) (.+)$", txt, re.M)
    rev, mod = (m.group(1), m.group(2).strip()) if m else ("?", "?")
    lines = txt.split("\n")
    conj = None
    author = None
    # walk the %C/%F lines; attribution may be on the line itself or on an
    # enclosing "From _Name_, Date: (Start)" block header
    block = None
    for L in lines:
        mm = re.match(r"^%[CF] A\d+ (.*)$", L)
        if not mm:
            continue
        body = mm.group(1)
        hb = re.match(r"^(?:From|Conjectures? from) _([^_]+)_, ([A-Z][a-z]{2} \d{1,2},? \d{4}):?\s*\(Start\)", body)
        if hb:
            block = (hb.group(1), hb.group(2))
        if body.strip().endswith("(End)"):
            after = block
            block = None if conj else block
        if PHI.search(body) and conj is None:
            conj = body
            tail = re.search(r"- _([^_]+)_, ([A-Z][a-z]{2} \d{1,2},? \d{4})", body)
            if tail:
                author = (tail.group(1), tail.group(2))
                conj = body[:tail.start()].strip().rstrip("-").strip()
            elif block:
                author = block
    return {"anum": anum, "rev": rev, "modified": mod, "conj": conj,
            "author": author[0] if author else None,
            "date": author[1] if author else None}


if __name__ == "__main__":
    import phispec
    out = {}
    for a in phispec.SPEC:
        out[a] = meta(a)
        r = out[a]
        print(f"{a}  rev{r['rev']} {r['modified']}  by {r['author']} ({r['date']})")
        print(f"    {str(r['conj'])[:150]}")
    json.dump(out, open("phimeta.json", "w"), indent=1)
