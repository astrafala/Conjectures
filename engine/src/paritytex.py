#!/usr/bin/env python3
"""Paper template for a conjecture settled by splitting the closed form on the
parity of n. House style; the middle sections are its own.
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
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{remark}[theorem]{Remark}
\title{A proof of the conjectured recurrence for OEIS %(ANUM)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{30 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured linear recurrence with polynomial coefficients, of
order %(ORDER)d. The entry posts no generating function, and the closed form it does post
is not a hypergeometric term in $n$: it contains a floor, so its shift quotients are not
rational and the usual argument does not start. Splitting on the parity of $n$ repairs
this. Writing $a(2m)=e_{0}(m)$ and $a(2m+1)=e_{1}(m)$, both halves are ordinary
hypergeometric expressions in $m$, and the recurrence becomes two identities in $m$, since
each shifted term $a(n-i)$ lands in whichever half the parity of $n-i$ selects. Both are
then decided exactly, by grouping into similarity classes and cancelling. The procedure
returns a proof or a refutation; both halves must hold, and here both do.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 33F10, 11B37, 05A10.\normalsize

\section{The sequence and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry states, not as a conjecture,
\begin{quote}\small
%(FORMULA)s
\end{quote}
that is,
\begin{equation}\label{eq:cf}
a(n)\;=\;%(CFLATEX)s .
\end{equation}
This is the only input the proof takes from the entry. It was checked against the entry's
own DATA before use, and the index alignment was determined from that check rather than
assumed: %(SHIFTNOTE)s

The entry separately carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

Written out, the conjecture is
\begin{equation}\label{eq:conj}
%(RECLATEX)s
\end{equation}

\section{Hypergeometric terms, and why the closed form is not one}

\begin{definition}
A nonzero expression $c(m)$ is a \emph{hypergeometric term} in $m$ if $c(m+1)/c(m)$ is a
rational function of $m$. Two such terms $c,d$ are \emph{similar}, $c\sim d$, if $c/d$ is a
rational function of $m$.
\end{definition}

Products of factorials, binomial coefficients with arguments linear in the variable,
exponentials and polynomials are hypergeometric. A floor is not: $\lfloor n/2\rfloor$ takes
the same value at $n$ and $n+1$ for even $n$ and jumps at odd $n$, so the quotient
$c(n+1)/c(n)$ is not a rational function of $n$, and \eqref{eq:cf} is therefore outside the
reach of the direct argument.

Parity removes the floor. For integer $m$,
$\lfloor 2m/2\rfloor=m$ and $\lfloor (2m+1)/2\rfloor=m$, and similarly for the ceiling, so
substituting $n=2m$ and $n=2m+1$ into \eqref{eq:cf} and simplifying gives two expressions
free of rounding:
\begin{equation}\label{eq:halves}
a(2m)\;=\;e_{0}(m)\;=\;%(EVENLATEX)s,
\qquad
a(2m+1)\;=\;e_{1}(m)\;=\;%(ODDLATEX)s,
\end{equation}
and each of $e_{0},e_{1}$ is a sum of finitely many hypergeometric terms in $m$.

\begin{lemma}\label{lem:indep}
Hypergeometric terms that are pairwise dissimilar are linearly independent over the field
of rational functions: if $\sum_{j}u_{j}(m)c_{j}(m)=0$ for rational $u_{j}$ and all large
$m$, then every $u_{j}$ is zero. See Petkov\v{s}ek, Wilf and Zeilberger \cite{AB},
Chapter~5.
\end{lemma}

\section{The recurrence, one residue class at a time}

Fix the conjectured coefficients $p_{0},\dots,p_{r}$ and consider
$T(n)=\sum_{i=0}^{r}p_{i}(n)a(n-i)$. Each term reaches a half of \eqref{eq:halves} chosen
by the parity of $n-i$:

\begin{proposition}\label{prop:split}
With $a(2j)=e_{0}(j)$ and $a(2j+1)=e_{1}(j)$,
\[
T(2m)=\sum_{i \text{ even}}p_{i}(2m)\,e_{0}\!\left(m-\tfrac{i}{2}\right)
      +\sum_{i \text{ odd}}p_{i}(2m)\,e_{1}\!\left(m-\tfrac{i+1}{2}\right),
\]
\[
T(2m+1)=\sum_{i \text{ even}}p_{i}(2m+1)\,e_{1}\!\left(m-\tfrac{i}{2}\right)
      +\sum_{i \text{ odd}}p_{i}(2m+1)\,e_{0}\!\left(m-\tfrac{i-1}{2}\right).
\]
Both right-hand sides are finite sums of hypergeometric terms in $m$. The recurrence
$T(n)=0$ holds for all large $n$ if and only if both vanish identically, and by
Lemma~\ref{lem:indep} each vanishes identically if and only if, after grouping its
summands into similarity classes, every class contributes the zero rational function.
\end{proposition}

\begin{proof}
The two displays are the definition of $T$ with $n-i$ written in the form $2j$ or $2j+1$:
for $n=2m$ the index $n-i$ is even exactly when $i$ is, and for $n=2m+1$ exactly when $i$
is odd. Every $e_{\epsilon}(m-s)$ is a sum of hypergeometric terms in $m$, and
$p_{i}(2m)$, $p_{i}(2m+1)$ are polynomials in $m$, so each display is a finite sum of
hypergeometric terms. Within a similarity class every summand is the class representative
times a rational function, so the class contributes the representative times the sum of
those rational functions; the classes are pairwise dissimilar by construction, and
Lemma~\ref{lem:indep} applies. Finally $n$ ranges over both parities, so $T(n)=0$ for all
large $n$ is exactly the conjunction of the two.
\end{proof}

\section{The computation for %(ANUM)s}

Carrying out Proposition~\ref{prop:split} with the coefficients of \eqref{eq:conj} and the
two halves \eqref{eq:halves}, every similarity class of $T(2m)$ contributes zero, and so
does every similarity class of $T(2m+1)$. The even half splits into %(NEVEN)s class%(EES)s
and the odd half into %(NODD)s class%(OES)s.

\begin{theorem}
For all $n%(EXCLTEX)s$,
\[
%(RECLATEX)s
\]
\end{theorem}

\begin{proof}
Both residue classes vanish identically by the computation above, and every integer $n$
lies in one of them. The excluded values are those at which a class residual has a pole or
a term of \eqref{eq:cf} is undefined.
\end{proof}

\section{Verification}

Two checks were made, and both are independent of the algebra above.

First, the closed form \eqref{eq:cf} was evaluated at the first $%(NCHECK)d$ indices and
compared term by term with the entry's DATA; the values agree exactly, on both parities. A
formula that did not reproduce the entry's own terms would not have been used, and the
alignment was fixed by that comparison rather than assumed.

Second, the conjectured recurrence \eqref{eq:conj} was evaluated on the published terms in
exact integer arithmetic at every index where it applies: $%(NVER)d$ instances beginning at
$n=%(FIRSTN)d$, all of them zero. This is not part of the proof, which is symbolic, but it
would have caught a transcription error in the coefficients.

\begin{thebibliography}{9}
\bibitem{AB} M.~Petkov\v{s}ek, H.~S.~Wilf and D.~Zeilberger, \emph{A=B}, A K Peters,
Wellesley MA, 1996.
\bibitem{OEIS} OEIS Foundation Inc., \emph{The On-Line Encyclopedia of Integer Sequences},
entry \href{https://oeis.org/%(ANUM)s}{%(ANUM)s}, %(TIME)s.
\bibitem{GKP} R.~L.~Graham, D.~E.~Knuth and O.~Patashnik, \emph{Concrete Mathematics},
2nd ed., Addison-Wesley, 1994.
\end{thebibliography}

\end{document}
"""
