#!/usr/bin/env python3
"""The paper for an image count of a sliding-window MAXIMUM over a growing alphabet.

The theorem proved is not a recurrence and not a transfer-matrix count, so neither `unibuild`
nor `degbuild` states it correctly. What the entry says is that the number of distinct arrays
obtainable as the windowed maxima of a length-k array over {0..n} agrees with a given
polynomial in n; what is proved here is an exact closed form for that number, from which the
entry's polynomial follows by expanding binomial coefficients.
"""
import sympy as sp

import localentry as LE
import phibuild
import unibuild
import window

PRE, esc = phibuild.PRE, phibuild.esc


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    k, w, L = h['k'], h['w'], h['k'] - h['w'] + 1
    A = h['A']
    n = window.n
    P = sp.expand(sp.sympify(h['poly']))
    head = ', '.join(str(x) for x in d[:8])
    terms = ' + '.join(rf'{c}\binom{{n+1}}{{{m}}}'
                       for m, c in enumerate(A, start=1) if c)
    claim = esc(' '.join(h['line'].split()))
    census = ', '.join(rf'A_{{{m}}}={c}' for m, c in enumerate(A, start=1))
    return rf"""{PRE}
\title{{An exact count for OEIS {a}: windowed maxima over a growing alphabet}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the arrays obtainable as the maxima of ${w}$ adjacent elements of a length
${k}$ array with entries in $\{{0,\dots,n\}}$, and carries an empirical polynomial for that
count. The count is not a transfer-matrix count: the length is fixed and it is the ALPHABET
that grows with $n$. It is nevertheless exactly computable, because membership in the image
depends only on the relative order of the entries of the candidate array and not on their
values, so the count is a fixed non-negative combination of binomial coefficients
$\binom{{n+1}}{{m}}$. Computing that combination settles the empirical claim as an identity in
$\mathbb{{Q}}[n]$.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A05, 06A07.\normalsize

\section{{The conjecture}}

The entry's first terms are ${head},\dots$ and it states

\begin{{quote}}\raggedright {claim}\end{{quote}}

\section{{The object}}

Fix $k={k}$ and $w={w}$, and put $L=k-w+1={L}$. For $a=(a_1,\dots,a_k)\in\{{0,\dots,n\}}^k$
let
\[
  \Phi(a)=\bigl(\max(a_1,\dots,a_w),\ \max(a_2,\dots,a_{{w+1}}),\ \dots,\
  \max(a_{{k-w+1}},\dots,a_k)\bigr)\in\{{0,\dots,n\}}^{{L}} .
\]
The entry counts $\lvert\Phi(\{{0,\dots,n\}}^k)\rvert$.

\section{{Membership in the image is decided by the order type}}

Write $W_j=\{{j,j+1,\dots,j+w-1\}}$ for the $j$-th window, $1\le j\le L$.

\begin{{lemma}}\label{{lem:greedy}}
Let $b\in\{{0,\dots,n\}}^{{L}}$ and define $\hat a\in\{{0,\dots,n\}}^k$ by
$\hat a_i=\min\{{\,b_j : i\in W_j\,\}}$. Then $b\in\Phi(\{{0,\dots,n\}}^k)$ if and only if
$\Phi(\hat a)=b$.
\end{{lemma}}

\begin{{proof}}
Each $\hat a_i$ is one of the $b_j$, so $\hat a$ does lie in $\{{0,\dots,n\}}^k$ and the
condition is meaningful. If $\Phi(\hat a)=b$ there is nothing to prove. Conversely suppose
$\Phi(a)=b$ for some $a$. For every $i\in W_j$ we have $a_i\le\max_{{l\in W_j}}a_l=b_j$, so
$a_i\le\min\{{b_j : i\in W_j\}}=\hat a_i$: the array $\hat a$ dominates every witness
componentwise. Hence
$\max_{{i\in W_j}}\hat a_i\ge\max_{{i\in W_j}}a_i=b_j$. The reverse inequality is immediate
from the definition, since $\hat a_i\le b_j$ for each $i\in W_j$. So $\Phi(\hat a)=b$.
\end{{proof}}

Both the construction of $\hat a$ and the test $\Phi(\hat a)=b$ use only comparisons between
entries of $b$. Consequently:

\begin{{corollary}}\label{{cor:ordertype}}
Whether $b$ lies in the image depends only on the \emph{{order type}} of $b$ -- the weak
ordering of its $L$ coordinates -- and not on $n$ or on the values themselves.
\end{{corollary}}

\begin{{proof}}
Let $\sigma$ be any strictly increasing map defined on the values of $b$. Applying $\sigma$
entrywise commutes with $\min$ and $\max$, so it carries $\hat a$ for $b$ to $\hat a$ for
$\sigma(b)$ and preserves the equalities tested in Lemma~\ref{{lem:greedy}}. Any two arrays with
the same order type differ by such a $\sigma$.
\end{{proof}}

\section{{The count}}

For $1\le m\le L$ let $A_m$ be the number of order types of $L$ coordinates that use exactly
$m$ distinct values and are achievable. An array $b\in\{{0,\dots,n\}}^{{L}}$ using exactly $m$
distinct values is determined by the $m$-element subset of $\{{0,\dots,n\}}$ it uses together
with its order type, and every pair occurs exactly once; so by Corollary~\ref{{cor:ordertype}},
\[
  \lvert\Phi(\{{0,\dots,n\}}^k)\rvert=\sum_{{m=1}}^{{{L}}}A_m\binom{{n+1}}{{m}}
  \qquad\text{{for every }} n\ge 0 .
\]
Enumerating the weak orderings of ${L}$ elements and applying Lemma~\ref{{lem:greedy}} to each
gives ${census}$, so
\[
  \lvert\Phi(\{{0,\dots,n\}}^k)\rvert={terms}={sp.latex(P)} .
\]

\section{{Conclusion}}

The right-hand side is the polynomial the entry states, so the empirical claim of OEIS {a} is
true for every $n\ge 0$. The argument is finite and exact: it enumerates the weak orderings of
${L}$ elements, of which there are {sum(A)} achievable, and performs no fitting to the
published terms. Those terms are reproduced by the formula as a check, not as evidence.

\end{{document}}
"""
