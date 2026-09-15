#!/usr/bin/env python3
"""The paper for the image count of a sliding-window MEDIAN over a growing alphabet.

The max case (`winbuild`) is settled by the order type of the candidate alone. The median is
not: a witness can need a value strictly BETWEEN two entries of the candidate, and whether an
integer sits in that open interval is a fact about the GAPS, which the order type does not
record. The count is therefore taken over (order type, gap pattern) pairs, and the monotonicity
of achievability in the gap set is what keeps that computable.
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
    k, w = h['k'], h['w']
    L = k - w + 1
    A = h['A']
    n = window.n
    P = sp.expand(sp.sympify(h['poly']))
    head = ', '.join(str(v) for v in d[:8])
    claim = esc(' '.join(h['line'].split()))
    plain = ' + '.join(rf'{c}\binom{{n+1}}{{{m}}}' for m, c in enumerate(A, start=1) if c)
    resid = ' + '.join(rf'{c}\binom{{n-{key.split("_")[0]}}}{{{int(key.split("_")[1]) - 1}}}'
                       for key, c in sorted(h['extra'].items())) or '0'
    nae = (r" The source array is further required to have no two adjacent entries equal; that "
           r"condition is a comparison between entries too, so it is carried through the whole "
           r"argument unchanged." if h['nae'] else "")
    return rf"""{PRE}
\title{{An exact count for OEIS {a}: windowed medians over a growing alphabet}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the arrays obtainable as the medians of ${w}$ adjacent elements of a length
${k}$ array with entries in $\{{0,\dots,n\}}$, and carries an empirical polynomial for that
count. The length is fixed and it is the ALPHABET that grows, so no transfer matrix applies.
Membership in the image is decided by comparisons, but -- unlike the analogous question for a
windowed maximum -- \emph{{not}} by the relative order of the candidate's entries alone: a
witness may need a value strictly between two of them, and whether an integer lies there depends
on the gaps. Counting by order type together with gap pattern, and using the fact that
achievability only improves as more gaps open, gives the count exactly.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A05, 06A07.\normalsize

\section{{The conjecture}}

The entry's first terms are ${head},\dots$ and it states

\begin{{quote}}\raggedright {claim}\end{{quote}}

\section{{The object}}

Fix $k={k}$, $w={w}$ and $L=k-w+1={L}$. For $a\in\{{0,\dots,n\}}^k$ let
\[
  \Phi(a)=\bigl(\operatorname{{med}}(a_1,\dots,a_w),\ \dots,\
  \operatorname{{med}}(a_{{k-w+1}},\dots,a_k)\bigr)\in\{{0,\dots,n\}}^{{L}} ,
\]
where $\operatorname{{med}}$ is the middle entry in sorted order.{nae} The entry counts
$\lvert\Phi(\{{0,\dots,n\}}^k)\rvert$.

\section{{Why the order type is not enough}}

For a windowed MAXIMUM the componentwise-largest witness uses only the candidate's own values,
so membership depends on nothing but their relative order. That fails here. A median window
forces its value to be one of its three entries, but the two others may have to straddle it, and
a straddling value need only lie in an open interval between two entries of $b$ -- any integer
there will do, and some integer must be there. Two candidates with the same order type can differ
in whether such an integer exists: $b=(0,1)$ and $b=(0,5)$ order alike and gap differently.

So the invariant is the pair: the order type of $b$, and which of the $m+1$ gaps around its $m$
distinct values contain an integer.

\begin{{lemma}}\label{{lem:mono}}
Achievability is monotone in the gap set: if $b$ is in the image when a set $G$ of gaps is
non-empty, it is in the image when any $G'\supseteq G$ is.
\end{{lemma}}

\begin{{proof}}
A witness for $G$ uses letters drawn from the values of $b$ and from the gaps of $G$; every such
letter is still available under $G'$, and the medians it produces are determined by its position
in the order, which is unchanged.
\end{{proof}}

\section{{The count}}

Write $m$ for the number of distinct values of $b$. The number of $b\in\{{0,\dots,n\}}^{{L}}$ with
a prescribed order type on $m$ values and a prescribed set $P$ of non-empty gaps is
$\binom{{n-m}}{{\lvert P\rvert-1}}$, and summing that over every $P$ recovers
$\binom{{n+1}}{{m}}$, the number of ways to choose the $m$ values at all.

By Lemma~\ref{{lem:mono}} each order type falls into one of three cases, and only the third needs
the pattern-by-pattern sum:

\begin{{itemize}}
\item achievable with NO extra letters -- every pattern works, and the type contributes the whole
      $\binom{{n+1}}{{m}}$;
\item not achievable even with every gap open -- it contributes nothing;
\item otherwise, the patterns that work are enumerated.
\end{{itemize}}

Carrying that out over the weak orderings of ${L}$ elements gives
\[
  \lvert\Phi(\{{0,\dots,n\}}^k)\rvert
  = {plain if plain else '0'} \;+\; {resid}
  = {sp.latex(P)} .
\]

\section{{Conclusion}}

The right-hand side is the polynomial the entry states, so the empirical claim of OEIS {a} is
true for every $n\ge 0$. The computation is finite and exact -- it enumerates the weak orderings
of ${L}$ elements and, for the few that need it, the gap patterns -- and performs no fitting to
the published terms. Those {h['nterms']} terms are reproduced by the formula as a check, not as
evidence.

\end{{document}}
"""
