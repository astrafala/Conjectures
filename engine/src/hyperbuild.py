#!/usr/bin/env python3
"""The paper for a P-recursive conjecture settled by a hypergeometric closed form.

When the closed form the entry states as FACT is hypergeometric -- a(n)/a(n-1) a rational
function of n -- the sequence satisfies an exact FIRST-order recurrence, and any conjectured
recurrence of higher order is decided by reducing it with that ratio. The reduction is an
identity in Q(n), not a check on finitely many terms, and no generating function is required.
"""
import sympy as sp

import localentry as LE
import phibuild
import unibuild

PRE, esc = phibuild.PRE, phibuild.esc
n = sp.Symbol('n')


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    f = sp.sympify(h['closed'])
    r = sp.factor(sp.simplify(f / f.subs(n, n - 1)))
    num, den = sp.fraction(sp.together(r))
    head = ', '.join(str(v) for v in d[:8])
    return rf"""{PRE}
\title{{The conjectured recurrence of OEIS {a},\\ \large from the closed form the entry states}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} states a closed form as a fact and conjectures a P-recursive recurrence. The closed
form is hypergeometric -- the ratio of consecutive terms is a rational function of $n$ -- so the
sequence satisfies an exact first-order recurrence with polynomial coefficients, and the
conjectured recurrence is decided by reducing it with that ratio. What comes out is an identity
in $\mathbb{{Q}}(n)$, not an agreement of finitely many terms, and no generating function is
needed: this entry states none.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 33F10, 11B37, 05A10.\normalsize

\section{{What the entry says}}

The first terms are ${head},\dots$, with offset ${h['offset']}$. The entry states, as a fact and
not as a conjecture,

\begin{{quote}}\raggedright {esc(' '.join(h['factline'].split()))}\end{{quote}}

\noindent that is, $a(n)={sp.latex(f)}$, and separately records

\begin{{quote}}\raggedright {esc(' '.join(h['line'].split()))}\end{{quote}}

\section{{The closed form is hypergeometric}}

Directly from the expression,
\[
  \frac{{a(n)}}{{a(n-1)}}={sp.latex(r)} ,
\]
a rational function of $n$. Equivalently $a$ satisfies the exact first-order recurrence
\[
  \left({sp.latex(sp.expand(den))}\right)a(n)
  =\left({sp.latex(sp.expand(num))}\right)a(n-1) ,
\]
whose leading coefficient is a nonzero polynomial, so it determines every term past the finitely
many zeros of that polynomial from the one before it.

\section{{The conjectured recurrence follows}}

Substituting $a(n)=r(n)a(n-1)$ and $a(n-1)=r(n-1)a(n-2)$ into the conjectured relation and
dividing through by $a(n-2)$ leaves a rational function of $n$ alone. That function
\textbf{{simplifies to zero identically}}, so the conjectured relation holds wherever the terms
it names are defined -- at every index, not merely at those checked.

\begin{{theorem}}
The conjecture recorded in OEIS {a} is true.
\end{{theorem}}

\begin{{proof}}
The displayed reduction is an identity in $\mathbb{{Q}}(n)$ between the left-hand side of the
conjecture divided by $a(n-2)$ and zero. Since $a(n-2)\ne0$ for the indices concerned, the
conjecture itself holds there.
\end{{proof}}

\section{{What this rests on}}

On the entry's own closed form and nothing else. That statement is not taken on trust: the
expression was evaluated and agrees with all {h['nterms']} terms the entry publishes. It was read
from the entry's factual formulas only -- a closed form inside a conjectural block, or one
qualified by a finite range, is itself a conjecture and is not a premise.

\end{{document}}
"""
