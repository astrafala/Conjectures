#!/usr/bin/env python3
"""Positive controls for every selector.

Four times now a sweep has reported a pool far from the truth because the function that
CHOOSES the candidates silently accepted nothing, or accepted everything, and the number it
printed looked plausible enough to act on:

    equate_cands   1214 reported, 50 real   ("a(n) =" is a prefix of "a(n) ==")
    emp_cands         1 reported, 1457 real (matched against an unstripped prefix)
    conjlines/xref    0 reported, 376 real  (marker stripped before a test that needs it)

A count has no error bar. The only defence is a hand-written example that each selector
MUST accept and one it MUST refuse, checked every time. That is this file.
"""
import sys
sys.path.insert(0, ".")
FAIL = []


def check(name, fn, yes, no):
    for s in yes:
        try:
            r = fn(s)
        except Exception as e:
            FAIL.append(f"{name}: raised on {s!r}: {e}"); continue
        if not r:
            FAIL.append(f"{name}: REFUSED a positive control: {s!r}")
    for s in no:
        try:
            r = fn(s)
        except Exception:
            continue
        if r:
            FAIL.append(f"{name}: ACCEPTED a negative control: {s!r}")


import conjlines
check("conjlines.is_recurrence", conjlines.is_recurrence,
      ["Conjecture: a(n) = 3*a(n-1) - a(n-2).",
       "Empirical: a(n) = 2*a(n-1) + a(n-3).",
       "Conjecture: n*a(n) -3*a(n-1) = 0.",
       "Conjecture D-finite with recurrence (n-8)*a(n) -a(n-1)=0."],
      ["Empirical g.f.: x/(1-x).",
       "a(n) = 3*a(n-1) - a(n-2).",           # stated as fact, not conjectured
       "Conjecture: a(n) is always prime."])

import gfclean
check("gfclean.candidates", lambda s: bool(gfclean.candidates(s)),
      ["Empirical g.f.: x*(1+x)/(1-x)^3.",
       "G.f.: (1-x)/(1-3*x+x^2). - _Colin Barker_, Jan 01 2015"],
      [])

import cfparse
check("cfparse.parse", lambda s: cfparse.parse(s) is not None,
      ["a(n) = binomial(2*n,n)/(n+1).",
       "a(n) = n*(n+1)/2."],
      ["a(n) = number of divisors of n.",
       "a(n) = denominator(n/2)."])

import sumparse
check("sumparse.parse", lambda s: sumparse.parse(s) is not None,
      ["a(n) = Sum_{k=0..n} binomial(n,k)^2.",
       "a(n) = Sum_{k>=0} binomial(n,2*k)."],
      ["a(n) = Sum of the digits of n."])

import blocks
def _blk(s):
    # statements() reads lines with the "%F A000001 " prefix already stripped
    return blocks.conjectured_lines(s.split("\n"))
check("blocks.conjectured_lines picks up the (End) line", 
      lambda s: any("x/(1-x)" in l for l in _blk(s)),
      ["Conjecture: (Start)\nsomething.\ng.f. = x/(1-x). (End)"], [])

import xref
check("xref.resolve", lambda s: xref.resolve(s) is not None,
      ["a(n) = A000079(n-1)*A000027(n)."],
      ["a(n) = 3*n+1."])

import hyperterm
import sympy as sp
n = sp.Symbol('n')
check("hyperterm.is_zero_sum", lambda e: hyperterm.is_zero_sum(e, n)[0],
      [sp.binomial(n, 1) - n], [])
check("hyperterm.is_zero_sum refuses a nonzero identity",
      lambda e: not hyperterm.is_zero_sum(e, n)[0], [sp.binomial(n, 1) - n - 1], [])

if FAIL:
    print(f"{len(FAIL)} SELECTOR(S) WRONG\n")
    for f in FAIL:
        print("  " + f)
else:
    print("all selectors accept their positive controls and refuse their negative ones")
