#!/usr/bin/env python3
"""Prove a CONJECTURED closed form, from a recurrence or g.f. the entry states as fact.

The mirror of every other sweep here. Let L be a recurrence the entry states as fact, so
a(n) satisfies L, and -- provided L's leading coefficient has no integer root past the
initial segment -- L together with the first r terms determines a(n). Let c(n) be the
conjectured closed form. If c satisfies L and agrees with the published terms on the
initial segment, then c(n) = a(n) for every n, which is the conjecture.

That c satisfies L is decided, not sampled: c is a sum of hypergeometric terms and
hyperterm.py reduces sum_i p_i(n) c(n-i) = 0 to one rational-function identity per
similarity class. Where the entry states a generating function instead of a recurrence, the
recurrence is read off it first by the residual criterion.
"""
import json, re, sys
sys.path.insert(0, ".")
import sympy as sp
import cfparse, gfclean, fsplit, blocks, hyperterm, holo
from makeslots import coeffs_of
from regf import entry

n = sp.Symbol('n')
MARKSTRIP = re.compile(r"^\s*(Conjectur\w*|Empirical)\s*\d*\s*[:.,]?\s*"
                       r"(?:(?:to be\s+)?D-finite\s+with\s+recurrence\s*[:.,]?\s*)?", re.I)


def _from_gf(A, egf):
    """A recurrence in BACKWARD form from a generating function.

    holo.annihilator returns the forward relation sum_j q_j(n) c(n+j) = 0 for the Taylor
    coefficients c_n. Two conversions are needed. For an EXPONENTIAL g.f. those coefficients
    are a(n)/n!, so multiplying through by (n+r)! turns the relation into one for a(n), the
    factor (n+r)!/(n+j)! being a rising factorial and hence a polynomial. Then n -> n - r
    re-indexes forward into backward form, which is what the rest of this project speaks.
    """
    r = holo.annihilator(A)
    if r is None:
        return None
    qs, start = r
    m = len(qs) - 1
    if egf:
        qs = [sp.expand(qs[j] * sp.rf(n + j + 1, m - j)) for j in range(m + 1)]
    back = [sp.expand(sp.simplify(qs[m - i].subs(n, n - m))) for i in range(m + 1)]
    while len(back) > 1 and sp.expand(back[0]) == 0:
        return None                       # leading coefficient vanished: not usable
    return back


def determines(ps, off, r):
    lead = ps[0]
    if lead == 0:
        return False
    if not lead.free_symbols:
        return True
    try:
        roots = sp.Poly(lead, n).all_roots()
    except Exception:
        return False
    return not any(t.is_Integer and int(t) >= off + r for t in roots)


def attack(item):
    a = item["anum"]
    F, data, off, nm = entry(a)
    recs = []
    for q in item.get("rec", []):
        try:
            ps = coeffs_of(q)
        except Exception:
            continue
        if ps and len(ps) > 1 and determines(ps, off, len(ps) - 1):
            recs.append((q, ps))
    # a stated generating function determines the sequence just as well: read a recurrence
    # off it. Without this the sweep skipped every entry whose fact side is an e.g.f.
    if not recs:
        for q in item.get("gf", []):
            egf = bool(re.match(r"^\s*e\.g\.f\.", q, re.I))
            for cand in gfclean.candidates(q):
                cand = cand[0] if isinstance(cand, (tuple, list)) else cand
                try:
                    A = sp.sympify(str(cand).replace("^", "**"))
                except Exception:
                    continue
                if not isinstance(A, sp.Expr) or (A.free_symbols - {sp.Symbol('x')}):
                    continue
                ps = _from_gf(A, egf)
                if ps and len(ps) > 1 and determines(ps, off, len(ps) - 1):
                    recs.append((q, ps)); break
            if recs:
                break
    if not recs:
        return ("no", "no fact side that determines the sequence")
    out = []
    for cl in item["conj"]:
        e = cfparse.parse(MARKSTRIP.sub("", cl))
        if e is None:
            continue
        al, sh = cfparse.align(e, data, off)
        if al is None:
            # a conjecture qualified "for n > k" is not expected to hold below k
            m = re.search(r"for\s+n\s*>=?\s*(\d+)", cl)
            if m:
                start = int(m.group(1))
                if all(sp.nsimplify(e.subs(n, i), rational=True) == data[i - off]
                       for i in range(start + 1, min(start + 7, off + len(data)))):
                    al = e
            if al is None:
                out.append(("the closed form does not match the terms", cl, None)); continue
        got = None
        for q, ps in recs:
            ok, ev = hyperterm.is_zero_sum(
                sp.expand(sum(p * al.subs(n, n - j) for j, p in enumerate(ps) if p != 0)), n)
            if ok:
                got = {"rec": q, "order": len(ps) - 1, "classes": len(ev)}
                break
        if not got:
            out.append(("the closed form does not satisfy the stated recurrence", cl, None))
            continue
        r = got["order"]
        bad = [i for i in range(min(len(data), r + 4))
               if sp.nsimplify(al.subs(n, i + off), rational=True) != data[i]]
        if bad:
            out.append(("initial terms disagree", cl, bad[:3])); continue
        got["nver"] = min(len(data), r + 4)
        out.append(("PROVED", cl, got))
    return ("ok", out)


if __name__ == "__main__":
    import timeoutrun
    hits = []
    for it in json.load(open("cftarget_todo.json")):
        st, r = timeoutrun.call(attack, (it,), timeout=180)
        if st != "ok":
            print(f"{it['anum']}  {st}", flush=True); continue
        if r[0] != "ok":
            print(f"{it['anum']}  skip: {r[1]}", flush=True); continue
        for v, cl, extra in r[1]:
            print(f"{it['anum']}  {v}  {cl[:56]}", flush=True)
            if v == "PROVED":
                hits.append({"anum": it["anum"], "conj": cl, **extra})
    json.dump(hits, open("cftarget_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} proved")
