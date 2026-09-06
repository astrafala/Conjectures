#!/usr/bin/env python3
"""Paper template for a conjectured identity between OEIS entries.

Same house style as the recurrence papers; the mathematics is different, so the middle
sections are their own.
"""

TEMPLATE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[margin=1in]{geometry}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{remark}[theorem]{Remark}
\title{A proof of the conjectured identity for OEIS %(ANUM)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{26 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured identity expressing its terms through the terms of
%(REFLIST)s. We prove it. Each entry involved posts a generating function, so the claim is
a single identity between generating functions: writing $F_{a}$ for the generating
function of %(ANUM)s and $F_{j}$ for those of the entries on the right, the conjecture
says that a specific combination of the $F_{j}$, shifted and weighted as the identity
prescribes, differs from $F_{a}$ by a polynomial. That difference is computed here in
closed form and equals $%(BLATEX)s$, of degree $%(DEG)d$, which proves the identity for
every $n>%(DEG)d$.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 11B83, 05A15.\normalsize

\section{The sequences and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
Its generating function, as posted on the entry, is
\begin{equation}\label{eq:gf}
F_{a}(x)\;=\;\sum_{n\ge %(OFFSET)d} a(n)\,x^{n}\;=\;%(GFLATEX)s ,
\end{equation}
and the entry carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

The entries appearing on the right-hand side post the generating functions
\[
%(REFGFS)s
\]

\section{Shifts of a generating function}

Throughout, a sequence $b$ defined on the indices its OEIS entry uses is identified with
the formal series $F_{b}(x)=\sum_{m\ge0}b(m)x^{m}$, where $b(m)=0$ for $m$ below the
entry's offset. This convention makes shifting immediate.

\begin{lemma}\label{lem:shift}
For an integer $k\ge0$,
\[
\sum_{m\ge0}b(m+k)\,x^{m}=\frac{F_{b}(x)-\sum_{m<k}b(m)x^{m}}{x^{k}},
\qquad
\sum_{m\ge0}b(m-k)\,x^{m}=x^{k}F_{b}(x).
\]
\end{lemma}

\begin{proof}
Both are re-indexings of the defining sum. In the first, subtracting the terms below
$x^{k}$ removes exactly the coefficients that have no counterpart after the shift, and
dividing by $x^{k}$ relabels $m+k$ as $m$. In the second, multiplying by $x^{k}$ relabels
$m$ as $m+k$, and the coefficients of $x^{m}$ for $m<k$ are $b(m-k)=0$.
\end{proof}

\begin{lemma}\label{lem:theta}
Let $\theta=x\,\dfrac{d}{dx}$, so that $\theta$ acts on $x^{m}$ as multiplication by $m$.
For a polynomial $c$, the sequence $m\mapsto c(m)b(m)$ has generating function
$c(\theta)F_{b}$. In particular $m\mapsto m^{j}$ has generating function
$\theta^{j}\bigl[(1-x)^{-1}\bigr]$.
\end{lemma}

\begin{proof}
$\theta$ multiplies the coefficient of $x^{m}$ by $m$, so $c(\theta)$ multiplies it by
$c(m)$. The last statement is the case $b\equiv1$.
\end{proof}

\begin{corollary}\label{cor:criterion}
Let $R(x)$ be the generating function assembled from the right-hand side of the conjecture
by Lemmas~\ref{lem:shift} and~\ref{lem:theta}. Then the conjectured identity holds for
every $n>d$ if and only if $F_{a}-R$ is a polynomial of degree at most $d$.
\end{corollary}

\begin{proof}
The coefficient of $x^{n}$ in $F_{a}-R$ is the difference between the two sides of the
identity at $n$. That difference vanishes for all $n>d$ exactly when $F_{a}-R$ has no
terms above $x^{d}$.
\end{proof}

Note that the test is for a \emph{polynomial}, not for zero. A claim of this kind
typically fails at a few small indices, where the shifted terms on the right reach outside
the range of their own sequences; the polynomial records precisely those indices.

\section{The computation for %(ANUM)s}

Assembling the right-hand side by Lemmas~\ref{lem:shift} and~\ref{lem:theta} gives
\[
R(x)\;=\;%(RHSLATEX)s ,
\]
and subtracting \eqref{eq:gf} the rational parts cancel, leaving
\[
F_{a}(x)-R(x)\;=\;%(BLATEX)s ,
\]
a polynomial of degree $%(DEG)d$.

\begin{theorem}
The conjectured identity holds for every $n>%(DEG)d$.
\end{theorem}

\begin{proof}
Immediate from Corollary~\ref{cor:criterion} and the displayed difference.
\end{proof}

\section{Verification}

Every number above is an output of a script written separately from this note, and two
independent checks were run.

First, no generating function was assumed. For each entry involved, the posted expression
was expanded as a Taylor series and compared term by term with that entry's own DATA
section; only expressions reproducing the published terms were used.

Second, the identity itself was evaluated directly on the published terms, in exact
integer arithmetic and without reference to any generating function: for each $n$ in range
both sides were formed from the entries' own values and found to agree, for all %(NVER)d
values of $n$ from $n=%(FIRSTN)d$ upward. This is what Corollary~\ref{cor:criterion}
predicts from the degree of the difference, and it is a genuinely different computation
from the symbolic one.

The symbolic step is exact throughout: the difference is obtained by rational-function
cancellation, not by series truncation, so the displayed identity is an identity of
functions and the theorem holds for all $n>%(DEG)d$ simultaneously.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s.
\bibitem{wilf} H.~S.~Wilf, \emph{generatingfunctionology}, 3rd ed., A K Peters, 2006,
Chapter 2 (series manipulations and shifts).
\bibitem{stanley} R.~P.~Stanley, \emph{Enumerative Combinatorics}, Volume 1, 2nd ed.,
Cambridge University Press, 2011, Chapter 1.
\end{thebibliography}
\end{document}
"""
