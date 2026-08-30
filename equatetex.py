#!/usr/bin/env python3
"""Paper template for a conjectured closed form or a conjectured generating function.

House style. The argument is the same in both directions and is stated once: derive a
recurrence from what the entry asserts, check the conjectured description satisfies it,
match initial values, and appeal to uniqueness.
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
\theoremstyle{definition}
\newtheorem{remark}[theorem]{Remark}
\title{A proof of the conjectured %(KINDWORD)s for OEIS %(ANUM)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{31 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured %(KINDWORD)s. We prove it. The entry states, as fact,
%(KNOWNWORD)s, and from that a linear recurrence with polynomial coefficients satisfied by
the sequence is derived exactly. The conjectured %(KINDWORD)s is then shown to satisfy the
same recurrence, and to agree with the sequence at enough consecutive indices. A recurrence
of order $%(ORDER)d$ whose leading coefficient does not vanish, together with $%(ORDER)d$
consecutive values, determines a sequence completely, so the two agree everywhere. Nothing
is checked numerically and then assumed: the recurrence is derived symbolically, the
verification is an exact identity, and the finitely many indices where the leading
coefficient vanishes are computed rather than waved at.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 33F10.\normalsize

\section{The sequence, what is known, and what is conjectured}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry states, not as a conjecture,
\begin{quote}\small
%(KNOWNLINE)s
\end{quote}
and separately carries the comment
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the second
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

\section{A recurrence from what is known}

%(DERIVSECTION)s

\begin{equation}\label{eq:rec}
%(OPLATEX)s
\end{equation}

The leading coefficient of \eqref{eq:rec} is $%(LEADLATEX)s$. %(POLETEXT)s

\section{The conjectured description satisfies it}

%(CHECKSECTION)s

\section{Uniqueness}

\begin{lemma}\label{lem:unique}
Let $\sum_{j=0}^{r}q_{j}(n)\,b(n+j)=0$ be a linear recurrence whose leading coefficient
$q_{r}$ has no zero at any integer $n\ge n_{0}$. If two sequences both satisfy it for all
$n\ge n_{0}$ and agree at the $r$ consecutive indices $n_{0},\dots,n_{0}+r-1$, they agree
at every $n\ge n_{0}$.
\end{lemma}

\begin{proof}
Induction. Suppose the two agree at $n_{0},\dots,m+r-1$ for some $m\ge n_{0}$. The
recurrence at $n=m$ determines $b(m+r)$ from the preceding $r$ values, because $q_{r}(m)$
is nonzero and may be divided by; both sequences therefore take the same value at $m+r$.
\end{proof}

\begin{theorem}
For all $n\ge %(FROMN)d$,
\[
%(CLAIMLATEX)s
\]
\end{theorem}

\begin{proof}
Both sides satisfy \eqref{eq:rec}: the sequence because the recurrence was derived from
the entry's own %(KNOWNWORD2)s, and the conjectured %(KINDWORD)s by the computation of the
previous section. They agree at the $%(ORDER)d$ consecutive indices beginning
$n=%(FROMN)d$, which was checked against the entry's DATA in exact integer arithmetic.
The leading coefficient has no zero at any integer $n\ge%(FROMN)d$, so
Lemma~\ref{lem:unique} applies.
\end{proof}

\section{Verification}

Three checks, independent of one another.

First, the description the entry states as fact was itself confirmed against the entry's
DATA before any recurrence was derived from it; a statement that did not reproduce the
entry's own terms would not have been used as the basis of anything.

Second, the derived recurrence \eqref{eq:rec} was evaluated on the published terms in
exact integer arithmetic and vanishes at every index where it applies.

Third, the conjectured %(KINDWORD)s was evaluated at the first $%(NCHECK)d$ indices and
compared term by term with the DATA; the values agree exactly. This is not part of the
proof, which is symbolic, but it would catch a transcription error in either statement.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s.
\bibitem{aeqb} M.~Petkov\v{s}ek, H.~S.~Wilf and D.~Zeilberger, \emph{A=B}, A K Peters,
1996.
\bibitem{fs} P.~Flajolet and R.~Sedgewick, \emph{Analytic Combinatorics}, Cambridge
University Press, 2009.
\bibitem{kauers} M.~Kauers and P.~Paule, \emph{The Concrete Tetrahedron}, Springer, 2011.
\end{thebibliography}

\end{document}
"""
