#!/usr/bin/env python3
"""Prove a CONJECTURED generating function, from a recurrence the entry states as fact.

Every sweep so far used a generating function as the KNOWN side and proved a recurrence.
The corpus holds 6,420 open conjectures that are themselves generating functions, and they
had never been treated as targets. The logic reverses cleanly.

Let L be a recurrence the entry states as fact, so a(n) satisfies L and -- provided L's
leading coefficient has no integer root past the initial segment -- L together with the
first r terms DETERMINES a(n). Let G be the conjectured generating function. If

  (i) the coefficients of G satisfy L for all n past some d, and
  (ii) G's coefficients agree with the published terms up to and including d + r,

then the two sequences agree everywhere, so G is the generating function. Condition (i) is
the residual-polynomial criterion -- B a polynomial of degree d -- which decide.decide_one
computes exactly, and (ii) is what strict_gf checks before it accepts a candidate at all.

The caveat is real and is enforced: a recurrence whose leading coefficient vanishes at some
integer past the start does not determine the sequence there, and such an entry is refused.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import decide, gfclean, fsplit, blocks, cfparse
from makeslots import coeffs_of
from regf import entry

x, n = sp.symbols('x n')
GUESS = re.compile(r"\b(guess|apparently|probabl|seems|presumabl|empirical|conjectur)", re.I)
FINITE = re.compile(r"holds at least|for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b"
                    r"|\bverified for\b|\bup to\b\s+n|up to n\s*=", re.I)
ATTRIB = re.compile(r"\s+-\s*_[^_]+_,?\s*[A-Z][a-z]{2}\s+\d.*$")
STATEDREC = re.compile(r"^\s*a\(n\)\s*=.*a\(n\s*-\s*\d", re.I)
GFC = re.compile(r"^\s*(o\.|e\.)?g\.f\.", re.I)
MARKSTRIP = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*"
                       r"(?:(?:to be\s+)?D-finite\s+with\s+recurrence\s*[:.,]?\s*)?", re.I)


def determines(ps, off, ndata):
    """Does the recurrence determine the sequence from its initial terms?"""
    lead = ps[0]
    if lead == 0:
        return False
    if not lead.free_symbols:
        return True
    try:
        roots = sp.Poly(lead, n).all_roots()
    except Exception:
        return False
    return not any(r.is_Integer and int(r) >= off + len(ps) - 1 for r in roots)


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    cj = blocks.conjectured_lines(F)
    known = [ATTRIB.sub("", l) for l in F
             if l.strip() not in cj and not GUESS.search(l) and not FINITE.search(l)]
    parts = [q for l in known for q in [l] + fsplit.split(l)]
    recs = []
    for q in parts:
        if not STATEDREC.match(q):
            continue
        try:
            ps = coeffs_of(q)
        except Exception:
            continue
        if ps and len(ps) > 1 and determines(ps, off, len(data)):
            recs.append((q, ps))
    if not recs:
        return ("no", "no recurrence stated as fact that determines the sequence")
    out = []
    for cl in item["conj"]:
        body = MARKSTRIP.sub("", cl)
        if not GFC.match(body):
            continue
        egf = bool(re.match(r"^\s*e\.g\.f\.", body, re.I))
        cands = [c[0] if isinstance(c, (tuple, list)) else c for c in gfclean.candidates(body)]
        if not cands:
            continue
        got = None
        for q, ps in recs:
            r = decide.decide_one(q, data, off, egf, cands)
            if r.get("status") == "PROVED":
                got = dict(r, rec=q, order=len(ps) - 1); break
        out.append(("PROVED" if got else "not settled", cl, got))
    return ("ok", out)


if __name__ == "__main__":
    import timeoutrun
    hits = []
    for it in json.load(open("gftarget_todo.json")):
        st, r = timeoutrun.call(attack, (it,), timeout=200)
        if st != "ok" or r[0] != "ok":
            continue
        for verdict, cl, extra in r[1]:
            if verdict == "PROVED":
                hits.append({"anum": it["anum"], "conj": cl, **extra})
                print(f"  PROVED {it['anum']}  {cl[:60]}", flush=True)
    json.dump(hits, open("gftarget_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
