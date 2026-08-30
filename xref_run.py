#!/usr/bin/env python3
"""Sweep: settle a conjectural recurrence whose known side names other sequences.

xref.py resolves a definition like a(n) = A000079(n-1)*A001700(n) into an ordinary
expression in n by substituting the closed forms those entries state as fact. Once that is
done the conjecture is an identity between hypergeometric terms, which hyperterm.py
decides outright.

Every ingredient is checked before use: each referenced entry's formula is aligned against
that entry's own data, and the resolved expression is checked against this entry's data.
Conjectural lines are excluded on both sides, using blocks.py so that a line ending a
(Start)...(End) block is excluded too -- that omission is what once produced 21 false
proofs.
"""
import os, re, sys, json
sys.path.insert(0, ".")
import sympy as sp
import blocks, conjlines, xref, hyperterm, cfparse
from prove_rec import parse_conj
import timeoutrun

ROOT = "/home/user/oeis/oeisdata/seq"
MARK = re.compile(r"^\s*(Conjectur\w*|Empirical)", re.I)
GUESS = re.compile(r"\b(guess|appears|apparently|probabl|seems|presumabl)", re.I)
FINITE = re.compile(r"for\s+n\s*=\s*\d+\s*\.\.\s*\d+|\bchecked\b|\bverified for\b|\bup to\b\s+n", re.I)
SETTLED = re.compile(r"\bproof\b|prove[sndg]?\b|is true|confirm\w*|verif\w*|"
                     r"follows from|establish\w*|is correct", re.I)
n = sp.Symbol('n')


def candidates():
    out = []
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            a = "A" + fn[1:7]
            F = open(os.path.join(dd, fn), errors="ignore").read()
            flines = [re.sub(r"^%.\s+A\d{6}\s*", "", l) for l in F.split("\n")
                      if len(l) > 3 and l[0] == "%" and l[1] == "F"]
            if not any(MARK.match(l) for l in flines):
                continue
            if any(SETTLED.search(l) for l in flines):
                continue
            conjraw = blocks.conjectured_lines(F)
            # is_recurrence wants the marker still on the line: it uses it to tell a
            # conjectural recurrence from a stated one. Stripping it first made this
            # sweep report zero candidates.
            conj = [l for l in flines if conjlines.is_recurrence(l)]
            if not conj:
                continue
            known = [l for l in flines
                     if not MARK.match(l) and l.strip() not in conjraw
                     and not GUESS.search(l) and not FINITE.search(l)
                     and re.search(r"\bA\d{6}\s*\(", l)]
            if known:
                out.append((a, conj, known))
    return out


def attack(item):
    a, conj, known = item
    from regf import entry
    F, data, off, name = entry(a)
    for kl in known:
        e = xref.resolve(kl)
        if e is None:
            continue
        al, _ = cfparse.align(e, data, off)
        if al is None:
            continue
        for cl in conj:
            ps = parse_conj(MARK.sub("", cl))
            if ps is None:
                continue
            expr = sum(p * al.subs(n, n - j) for j, p in enumerate(ps) if p != 0)
            # is_zero_sum returns (verdict, evidence). A non-empty tuple is truthy, so
            # testing it directly accepts everything.
            ok, _ = hyperterm.is_zero_sum(sp.expand(expr), n)
            if ok:
                return (a, cl, kl, sp.srepr(al))
    return None


if __name__ == "__main__":
    cands = candidates()
    print(f"{len(cands)} entries with a conjectural recurrence and an A-referencing fact line",
          flush=True)
    hits = []
    for i, it in enumerate(cands):
        # call returns (status, value); the tuple itself is always truthy.
        st, r = timeoutrun.call(attack, (it,), timeout=60)
        if st == "ok" and r:
            hits.append(r)
            print(f"  HIT {r[0]}", flush=True)
        if i % 200 == 0:
            print(f"  ...{i}", flush=True)
    json.dump(hits, open("xref_hits.json", "w"), indent=1)
    print(f"\n{len(hits)} settled")
