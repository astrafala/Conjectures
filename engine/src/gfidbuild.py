#!/usr/bin/env python3
"""The paper for a conjectured generating function proved against one the entry ASSERTS."""
import sympy as sp

import algf
import localentry as LE
import phibuild
import unibuild

PRE, esc = phibuild.PRE, phibuild.esc
x = algf.x


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    F = sp.sympify(h['fact'], locals={'x': x})
    G = sp.sympify(h['conj'], locals={'x': x})
    head = ', '.join(str(v) for v in d[:8])
    claim = esc(' '.join(h['line'].split()))
    Fc, Gc = sp.cancel(sp.together(F)), sp.cancel(sp.together(G))
    return rf"""{PRE}
\title{{The conjectured generating function of OEIS {a}\\ \large is the one the entry already
states}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} states one generating function as a fact and carries a second as an empirical
conjecture. The conjecture is true, and no model of the sequence is needed to see it: the two
expressions are the same rational function, so the conjectured form holds wherever the stated
one does. The identity is exact, not a comparison of finitely many coefficients.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 30B10.\normalsize

\section{{The two statements}}

The entry's first terms are ${head},\dots$. It states, as a fact and not as a conjecture,
\[
  F(x)={sp.latex(F)} ,
\]
and separately records the conjecture

\begin{{quote}}\raggedright {claim}\end{{quote}}

\noindent which is
\[
  G(x)={sp.latex(G)} .
\]

\section{{They are the same function}}

Both $F$ and $G$ are rational. Writing each over a common denominator and cancelling,
\[
  F(x)={sp.latex(Fc)}=G(x) ,
\]
so $F-G$ is identically zero as a rational function, and $F$ and $G$ have the same Taylor
expansion at the origin wherever either converges.

\begin{{theorem}}
The conjectured generating function of OEIS {a} is correct.
\end{{theorem}}

\begin{{proof}}
The entry asserts that $F$ is the generating function of the sequence. By the identity above
$G=F$, so $G$ is that generating function as well.
\end{{proof}}

\section{{What this rests on}}

It rests on the entry's own asserted generating function and on nothing else. That assertion is
not taken on trust: $F$ was expanded and its first {h['nterms']} coefficients agree with every
term the entry publishes, from offset ${h['offset']}$ onward. The asserted line was read from
the entry's factual formulas only -- a generating function written inside a conjectural block
would be the same conjecture stated twice and is not a premise.

\end{{document}}
"""
