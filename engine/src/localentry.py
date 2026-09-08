#!/usr/bin/env python3
"""Read an OEIS entry from the local oeisdata clone -- no network, no rate limit."""
import re, os

ROOT = "/home/user/oeis/oeisdata/seq"


def path(anum):
    return os.path.join(ROOT, anum[:4], anum + ".seq")


def get(anum):
    txt = open(path(anum)).read()
    # A long formula is written across several %F lines, each continuing the previous one:
    #
    #   %F A184566 Empirical: a(n) = (1/121645100408832000)*n^19
    #   %F A184566 + (53/3201186852864000)*n^18
    #
    # Reading them as separate formulas hands every sweep a TRUNCATED polynomial, and the
    # closed-form sweep then reports the entry's conjecture as FALSE -- 19 of them at once,
    # every single one my bug and not a false conjecture. A line whose first character
    # continues an expression is joined to the one before it.
    CONT = re.compile(r'^\s*[-+*/)^]|^\s*(?:and|or)\b')

    def field(tag):
        out = []
        for m in re.finditer(rf'^%{tag} A\d+ ?(.*)$', txt, re.M):
            body = m.group(1)
            if out and CONT.match(body):
                out[-1] = out[-1].rstrip() + ' ' + body.strip()
            else:
                out.append(body)
        return out
    data = "".join(field('S') + field('T') + field('U')).replace(' ', '')
    name = (field('N') or [''])[0]
    off = (field('O') or ['0,1'])[0]
    m = re.search(r'^%I .*?#(\d+) (.+)$', txt, re.M)
    return {"number": anum, "name": name, "data": data, "offset": off,
            "formula": field('F'), "comment": field('C'),
            "revision": m.group(1) if m else "?",
            "modified": m.group(2).strip() if m else "?",
            "keyword": (field('K') or [''])[0],
            "author": (field('A') or [''])[0]}


def lines(anum):
    """All %C and %F bodies, in file order."""
    e = get(anum)
    return e["comment"] + e["formula"]
