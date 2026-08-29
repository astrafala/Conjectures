#!/usr/bin/env python3
"""Paper template for a conjecture settled by deriving the recurrence from the summand.

House style. The mathematics is creative telescoping followed by a division of operators,
so the middle sections are its own.
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
\title{A proof of the conjectured recurrence for OEIS %(ANUM)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{26 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured linear recurrence with polynomial coefficients, of
order %(ORDERC)d. The entry gives no generating function, but it does give the sequence as
a single hypergeometric sum. We prove the conjecture without assuming any generating
function: creative telescoping produces, from the summand alone, an operator of order
%(ORDERD)d that annihilates the sequence, together with a rational certificate that is
checked as an exact identity rather than trusted. The conjectured operator is then shown
to be a left multiple of it by division in the Ore algebra $\mathbb{Q}(n)[N]$. That last
step is what the conjecture needs: %(WHYDIV)s
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 33F10, 11B37, 68W30.\normalsize

\section{The sequence and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry states, not as a conjecture,
\begin{quote}\small
%(FORMULA)s
\end{quote}
so that, writing $F(n,k)$ for the summand,
\begin{equation}\label{eq:sum}
a(n)\;=\;\sum_{k=%(LO)s}^{%(HI)s}F(n,k),
\qquad F(n,k)=%(FLATEX)s .
\end{equation}
This is the only input the proof takes from the entry, and it was checked against the
entry's own DATA before use.

The entry separately carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

\section{Telescoping the summand}

Let $N$ denote the shift in $n$, $(Nf)(n)=f(n+1)$, and $\Delta_{k}$ the forward difference
in $k$, $(\Delta_{k}g)(k)=g(k+1)-g(k)$.

\begin{lemma}\label{lem:tel}
Suppose there are rational functions $\sigma_{0},\dots,\sigma_{r}$ of $n$, not all zero,
and a rational function $R(n,k)$ such that
\begin{equation}\label{eq:cert}
\sum_{i=0}^{r}\sigma_{i}(n)\,F(n+i,k)\;=\;\Delta_{k}\bigl[R(n,k)F(n,k)\bigr].
\end{equation}
Suppose further that $F(n,k)=0$ for every $k$ outside the range of summation in
\eqref{eq:sum}. Then $\sum_{i}\sigma_{i}(n)a(n+i)=0$.
\end{lemma}

\begin{proof}
Because $F(n,k)$ vanishes off the stated range, the sum in \eqref{eq:sum} may be taken
over all $k\in\mathbb{Z}$ without changing it, and the same holds for each $F(n+i,k)$.
Summing \eqref{eq:cert} over all $k$, the left side becomes
$\sum_{i}\sigma_{i}(n)a(n+i)$ and the right side telescopes: the partial sums of a forward
difference collapse to the boundary values, which are $0$ because $R(n,k)F(n,k)$ vanishes
for $|k|$ large. Hence the left side is $0$.
\end{proof}

The point of Lemma~\ref{lem:tel} is that \eqref{eq:cert} is an identity between rational
functions once both sides are divided by $F(n,k)$: the quotients $F(n+i,k)/F(n,k)$ and
$F(n,k+1)/F(n,k)$ are rational because $F$ is hypergeometric in both variables. So a
proposed $(\sigma,R)$ can be \emph{checked}, exactly, whatever produced it.

For %(ANUM)s such a pair exists with $r=%(ORDERD)d$:
\[
%(SIGMALATEX)s
\]
and certificate
\[
R(n,k)\;=\;%(CERTLATEX)s .
\]
Dividing \eqref{eq:cert} by $F(n,k)$ and cancelling gives $0$ identically, so
Lemma~\ref{lem:tel} applies and
\begin{equation}\label{eq:L}
L\;=\;\sum_{i=0}^{%(ORDERD)d}\sigma_{i}(n)N^{i}
\end{equation}
annihilates $a$.

\section{From the derived recurrence to the conjectured one}

The operator \eqref{eq:L} is not the conjectured one. %(WHYDIV2)s The two are connected by
division in the Ore algebra $\mathcal{A}=\mathbb{Q}(n)[N]$, where multiplication obeys
$N\,q(n)=q(n+1)\,N$.

\begin{lemma}\label{lem:factor}
If $C=QL$ in $\mathcal{A}$ and $L(a)=0$, then $C(a)=0$ at every $n$ where the coefficients
of $Q$ are defined.
\end{lemma}

\begin{proof}
$C(a)=(QL)(a)=Q\bigl(L(a)\bigr)=Q(0)=0$. The coefficients of $Q$ are rational functions of
$n$, so the step is valid away from their poles.
\end{proof}

Writing the conjectured recurrence as an operator $C$ and dividing by $L$ leaves remainder
$0$, with quotient
\[
Q\;=\;%(QLATEX)s .
\]
%(EXCTEXT)s

\begin{theorem}
The conjectured recurrence
\[
%(RECLATEX)s \;=\;0
\]
holds for every $n\ge%(FIRSTN)d$.
\end{theorem}

\begin{proof}
By Lemma~\ref{lem:tel} the operator \eqref{eq:L} annihilates $a$, and by
Lemma~\ref{lem:factor} applied to $C=QL$ so does the conjectured operator. %(EXCPROOF)s
\end{proof}

\section{Verification}

Every number above is an output of a script written separately from this note, and four
independent checks were run.

First, the certificate was verified, not trusted: \eqref{eq:cert} was divided by $F(n,k)$
and the difference of the two sides cancelled to $0$ as a rational function of $n$ and
$k$.

Second, the vanishing of $F(n,k)$ off the range of summation --- the hypothesis
Lemma~\ref{lem:tel} needs, and the one that is easy to assume without looking --- was
checked directly, on concrete integers on both sides of the range.

Third, the factorisation was confirmed by multiplying back: $QL$ was expanded in
$\mathcal{A}$ and its coefficients cancelled against those of $C$ to zero.

Fourth, the conjecture itself was evaluated on the published terms, in exact integer
arithmetic and without reference to any operator: for each $n$ in range the sum
$\sum_{i}p_{i}(n)a(n-i)$ was formed from the entry's own values and found to vanish, for
all %(NVER)d values of $n$ from $n=%(FIRSTN)d$ upward. The formula \eqref{eq:sum} was
likewise checked term by term against the DATA section before being used.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s.
\bibitem{aeqb} M.~Petkov\v{s}ek, H.~S.~Wilf and D.~Zeilberger, \emph{A=B}, A K Peters,
1996.
\bibitem{zeil} D.~Zeilberger, \emph{The method of creative telescoping}, J. Symbolic
Comput. 11 (1991), 195--204.
\bibitem{ore} O.~Ore, \emph{Theory of non-commutative polynomials}, Ann. of Math. 34
(1933), 480--508.
\end{thebibliography}
\end{document}
"""
