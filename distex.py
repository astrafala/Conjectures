#!/usr/bin/env python3
"""Paper template for a conjectured recurrence shown to be FALSE, with the correct one.

House style. A disproof needs more than a proof does: the reader cannot check it by
following an argument they already believe, so the note gives an explicit smallest
counterexample, an exact reason the failure repeats forever, and the recurrence that
does hold.
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
\newtheorem{remark}[theorem]{Remark}
\title{A disproof of the conjectured recurrence for OEIS %(ANUM)s,\\ and the recurrence
that holds instead}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{30 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured linear recurrence with polynomial coefficients, of
order %(ORDERC)d. It is false. The entry's own generating function gives, exactly, the
quantity the recurrence claims to annihilate, and that quantity is not eventually zero:
the smallest failure is at $n=%(FAILN)d$, where the left-hand side equals $%(FAILVAL)s$
rather than $0$, and the failure recurs for infinitely many $n$. We then give a recurrence
of order %(ORDERT)d that does hold, derived from the same generating function and proved by
the same criterion that refutes the conjectured one.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 33F10.\normalsize

\section{The sequence and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry states, not as a conjecture,
\begin{quote}\small
%(GFLINE)s
\end{quote}
that is,
\begin{equation}\label{eq:gf}
A(x)\;=\;\sum_{n\ge %(OFFSET)d}a(n)x^{n}\;=\;%(GFLATEX)s .
\end{equation}
This is the only input taken from the entry, and it was checked against every term of the
entry's DATA section before use --- all $%(NDATA)d$ of them --- not against a sample.

The entry separately carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and nothing on the entry records it as
settled either way.

Written out, the conjecture asserts
\begin{equation}\label{eq:conj}
%(RECLATEX)s\;=\;0 .
\end{equation}

\section{The residual, and what it decides}

Write $\theta=x\,\frac{d}{dx}$, so that $\theta x^{n}=n\,x^{n}$, and set
\begin{equation}\label{eq:B}
B(x)\;=\;\sum_{i=0}^{%(ORDERC)d}x^{i}\,\bigl(p_{i}(\theta+i)A\bigr)(x).
\end{equation}

\begin{lemma}\label{lem:transfer}
$[x^{n}]B(x)=\sum_{i}p_{i}(n)\,a(n-i)$ for every $n$. Consequently the recurrence
\eqref{eq:conj} holds for all $n>d$ if and only if $B$ is a polynomial of degree at most
$d$; and if $B$ is not a polynomial at all, \eqref{eq:conj} fails for infinitely many $n$.
\end{lemma}

\begin{proof}
$\theta$ acts diagonally on powers, so $\bigl(p_{i}(\theta+i)A\bigr)(x)
=\sum_{m}p_{i}(m+i)a(m)x^{m}$, and multiplying by $x^{i}$ shifts the exponent, giving
$\sum_{m}p_{i}(m+i)a(m)x^{m+i}=\sum_{n}p_{i}(n)a(n-i)x^{n}$. Summing over $i$ gives the
first claim. The rest is immediate: a power series is a polynomial of degree at most $d$
exactly when all its coefficients beyond $x^{d}$ vanish, and a series with infinitely many
nonzero coefficients is not a polynomial.
\end{proof}

Lemma~\ref{lem:transfer} is the same criterion used to \emph{prove} such conjectures. Its
force here is that it is an equivalence, so a negative answer is a disproof rather than a
failure to find a proof --- and the answer is computed exactly, in the field
$%(FIELD)s$ where $A$ lives, with no series truncated.

\section{The conjecture is false}

Carrying out \eqref{eq:B} for %(ANUM)s and reducing in $%(FIELD)s$, the residual $B$ is
\emph{not} a polynomial. By Lemma~\ref{lem:transfer} the conjectured recurrence therefore
fails for infinitely many $n$.

The failure is not confined to small indices, and it is not an artefact of the first few
terms: expanding \eqref{eq:gf} and evaluating the left side of \eqref{eq:conj} directly
gives

\begin{center}
\begin{tabular}{r@{\qquad}l}
$n$ & $\sum_{i}p_{i}(n)a(n-i)$ \\ \hline
%(TABLE)s
\end{tabular}
\end{center}

\begin{theorem}
The recurrence \eqref{eq:conj} conjectured on OEIS %(ANUM)s is false. Its smallest failure
is at $n=%(FAILN)d$, where the left-hand side equals $%(FAILVAL)s$, and it fails for
infinitely many $n$.
\end{theorem}

\begin{proof}
The tabulated values are computed from \eqref{eq:gf}, whose coefficients agree with the
entry's DATA at every published index, so each is a value of $\sum_{i}p_{i}(n)a(n-i)$ for
the sequence %(ANUM)s itself; the entry at $n=%(FAILN)d$ is nonzero. That $B$ is not a
polynomial, established exactly above, gives infinitely many such $n$ by
Lemma~\ref{lem:transfer}.
\end{proof}

%(INDEXNOTE)s

\section{A recurrence that does hold}

The generating function \eqref{eq:gf} is %(NATURE)s, so the sequence is $P$-recursive and
a correct recurrence exists; it is obtained from \eqref{eq:gf} rather than guessed.
%(DERIVATION)s

\begin{theorem}
For all $n\ge%(TRUEFROM)d$,
\[
%(TRUEREC)s\;=\;0 .
\]
\end{theorem}

\begin{proof}
The residual \eqref{eq:B} formed with these coefficients %(TRUEPROOF)s
\end{proof}

\section{Verification}

Three checks, each independent of the algebra above.

First, the generating function \eqref{eq:gf} was expanded and compared against the entry's
DATA at every one of the $%(NDATA)d$ published indices; the values agree exactly. A
generating function that reproduced only some of them would not have been used.

Second, the conjectured recurrence was evaluated on those published terms in exact integer
arithmetic, with no generating function involved: %(INDEPNOTE)s

Third, the recurrence of the previous section was evaluated the same way, on the published
terms, and vanishes at all $%(TRUEVER)d$ indices where it applies.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s.
\bibitem{fs} P.~Flajolet and R.~Sedgewick, \emph{Analytic Combinatorics}, Cambridge
University Press, 2009.
\bibitem{stanley} R.~P.~Stanley, \emph{Enumerative Combinatorics}, Volume 2, Cambridge
University Press, 1999.
\bibitem{aeqb} M.~Petkov\v{s}ek, H.~S.~Wilf and D.~Zeilberger, \emph{A=B}, A K Peters,
1996.
\end{thebibliography}

\end{document}
"""
