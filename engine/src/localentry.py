#!/usr/bin/env python3
"""Read an OEIS entry from the local oeisdata clone -- no network, no rate limit."""
import re, os

ROOT = "/home/user/oeis/oeisdata/seq"


def path(anum):
    return os.path.join(ROOT, anum[:4], anum + ".seq")


def get(anum):
    txt = open(path(anum)).read()
    def field(tag):
        return [m.group(1) for m in
                re.finditer(rf'^%{tag} A\d+ ?(.*)$', txt, re.M)]
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
