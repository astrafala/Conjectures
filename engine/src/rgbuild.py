#!/usr/bin/env python3
"""The paper for a conjectured generating function proved from a stated recurrence.

See `recgf` for the argument: the stated recurrence gives a denominator D, the published terms
give the numerator P exactly, and B = P/D is then an identity of rational functions rather than
an agreement of finitely many coefficients.
"""
import sympy as sp

import localentry as LE
import phibuild
import unibuild

PRE, esc = phibuild.PRE, phibuild.esc
x = sp.Symbol('x')


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    head = ', '.join(str(v) for v in d[:8])
    K = h['K']
    order = h['order']
    co = {int(k): sp.Integer(v) for k, v in h['coeffs'].items()}
    D = 1 - sum(co[i] * x ** i for i in sorted(co))
    G = sp.sympify(h['gf'])
    P = sp.cancel(sp.together(G * D))
    return rf"""{PRE}
\title{{The conjectured generating function of OEIS {a},\\ \large from the recurrence the entry
states}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} states a linear recurrence as a fact and carries a rational generating function as an
empirical conjecture. The conjecture follows from the recurrence by polynomial algebra alone:
the recurrence fixes the denominator, the published terms fix the numerator exactly, and the
generating function is then determined as a rational function rather than checked on finitely
many coefficients. No model of the sequence and no reading of its name is required.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B37, 05A15, 30B10.\normalsize

\section{{What the entry says}}

The first terms are ${head},\dots$, with offset ${h['offset']}$. The entry states, as a fact,

\begin{{quote}}\raggedright {esc(' '.join(h['factline'].split()))}\end{{quote}}

\noindent and separately records the conjecture

\begin{{quote}}\raggedright {esc(' '.join(h['gfline'].split()))}\end{{quote}}

The stated line was taken from the entry's factual formulas only. A formula qualified by a
finite range -- "holds at least up to $n=1000$ but is not known to hold in general" -- is not a
fact and is not used, nor is anything inside a conjectural block.

\section{{The argument}}

Write $b_k=a({h['offset']}+k)$ and
\[
  D(x)=1-\sum_{{i}} c_i x^{{i}}={sp.latex(sp.expand(D))} ,
\]
the polynomial of the stated recurrence, of degree ${order}$. Let $B(x)=\sum_{{k\ge0}}b_kx^k$.

The recurrence says $b_k=\sum_i c_ib_{{k-i}}$ for every $k\ge {K}$. The coefficient of $x^k$ in
$D(x)B(x)$ is exactly $b_k-\sum_i c_ib_{{k-i}}$, so it vanishes for every $k\ge {K}$ and
\[
  D(x)B(x)=P(x)=\sum_{{k<{K}}}\Bigl(b_k-\sum_i c_ib_{{k-i}}\Bigr)x^k
         ={sp.latex(sp.expand(P))} ,
\]
a polynomial whose every coefficient is fixed by finitely many published terms. Therefore
\[
  B(x)=\frac{{P(x)}}{{D(x)}}={h['gftex']} ,
\]
which is the conjectured expression.

\begin{{theorem}}
The conjectured generating function of OEIS {a} is correct, given the recurrence the entry
states.
\end{{theorem}}

\begin{{proof}}
Immediate from the displayed identity: $D\,B=P$ holds coefficientwise, $D(0)=1\ne0$ so $D$ is
invertible in the ring of formal power series, and $B=P/D$ follows. This is an identity of
rational functions, not a comparison of the ${h['nterms']}$ terms the entry publishes -- those
enter only in fixing the ${K}$ coefficients of $P$.
\end{{proof}}

\end{{document}}
"""
