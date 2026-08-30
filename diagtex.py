#!/usr/bin/env python3
"""Paper template for a conjecture on an entry defined by coefficient extraction."""

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
\date{30 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured linear recurrence with polynomial coefficients, of
order %(ORDER)d. The entry posts no generating function; it defines the sequence by an
extraction, $a(n)=[x^{n}]\,f(x)g(x)^{n}$. We derive a generating function from that
definition and prove the conjecture from it. Reading the extraction as a contour integral
and summing the geometric series turns $\sum_{n}a(n)t^{n}$ into a single integral whose
only pole inside a small circle is the branch of $x=t\,g(x)$ through the origin; the
residue there gives $A(t)=f(x(t))/\bigl(1-t\,g'(x(t))\bigr)$. So $A$ is algebraic, with
minimal polynomial obtained by eliminating $x$, and the recurrence follows from the
residual test in the field that polynomial generates. Here the residual is
$%(BLATEX)s$, of degree $%(DEG)d$, which proves the recurrence for every $n>%(DEG)d$.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 30B10, 33F10.\normalsize

\section{The sequence and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry states, not as a conjecture,
\begin{quote}\small
%(DEFN)s
\end{quote}
that is,
\begin{equation}\label{eq:def}
a(n)\;=\;[x^{n}]\,f(x)\,g(x)^{n},
\qquad f(x)=%(FLATEX)s,\qquad g(x)=%(GLATEX)s .
\end{equation}
This is the only input taken from the entry, and it was checked against the entry's own
DATA before use. In particular \emph{no generating function is assumed}: the entry posts
none, and the one used below is derived.

The entry separately carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

\section{A generating function from the extraction}

\begin{lemma}\label{lem:diag}
Let $f,g$ be rational functions regular at $0$ with $g(0)\neq0$, and let
$a(n)=[x^{n}]f(x)g(x)^{n}$. Then $A(t)=\sum_{n\ge0}a(n)t^{n}$ satisfies
\[
A(t)\;=\;\frac{f\bigl(x(t)\bigr)}{1-t\,g'\bigl(x(t)\bigr)},
\]
where $x(t)$ is the unique power series with $x(0)=0$ solving $x=t\,g(x)$. In particular
$A$ is algebraic over $\mathbb{Q}(t)$.
\end{lemma}

\begin{proof}
Write the extraction as a contour integral on a circle $|x|=\rho$ small enough that $f$
and $g$ are regular on and inside it:
\[
a(n)=\frac{1}{2\pi i}\oint \frac{f(x)g(x)^{n}}{x^{n+1}}\,dx .
\]
For $|t|$ small, $|t\,g(x)/x|<1$ on the circle, so the geometric series may be summed
under the integral:
\[
A(t)=\frac{1}{2\pi i}\oint\frac{f(x)}{x}\sum_{n\ge0}\Bigl(\frac{t\,g(x)}{x}\Bigr)^{n}dx
     =\frac{1}{2\pi i}\oint\frac{f(x)}{x-t\,g(x)}\,dx .
\]
Since $g(0)\neq0$, the equation $x=t\,g(x)$ has, for small $t$, exactly one root in the
disc, namely the branch $x(t)$ with $x(0)=0$ furnished by Lagrange inversion; it is a
simple zero of $x-t\,g(x)$ because the derivative $1-t\,g'(x)$ is $1$ at $t=0$. The
residue theorem gives the stated value. Both $x(t)$ and hence $A(t)$ are algebraic,
being defined by polynomial equations over $\mathbb{Q}(t)$.
\end{proof}

\begin{corollary}\label{cor:minpoly}
$A$ satisfies the polynomial obtained by eliminating $x$ between
$x-t\,g(x)=0$ and $y\bigl(1-t\,g'(x)\bigr)-f(x)=0$.
\end{corollary}

\begin{proof}
Both equations hold at $x=x(t)$, $y=A(t)$ by Lemma~\ref{lem:diag}. Eliminating $x$ by a
resultant produces a polynomial in $t$ and $y$ vanishing there.
\end{proof}

For %(ANUM)s this yields
\[
%(MINPOLY)s \;=\;0 ,
\]
and $A$ is the branch of this polynomial whose expansion is the entry's own sequence.
The branch is identified by that expansion, not by solving for it in radicals --- the
polynomial can have degree beyond four, where no such expression exists.

\section{The recurrence}

Let $\theta=x\,\dfrac{d}{dx}$, acting on $x^{m}$ as multiplication by $m$.

\begin{lemma}\label{lem:transfer}
Let $p_{0},\dots,p_{r}$ be polynomials and put $b(n)=\sum_{i}p_{i}(n)a(n-i)$, with
$a(m)=0$ for $m<0$. Then $B(x)=\sum_{n}b(n)x^{n}=\sum_{i}x^{i}(p_{i}(\theta+i)A)(x)$, so
the recurrence $\sum_{i}p_{i}(n)a(n-i)=0$ holds for every $n>d$ if and only if $B$ is a
polynomial of degree at most $d$.
\end{lemma}

\begin{proof}
Substituting $m=n-i$ gives $\sum_{n}p_{i}(n)a(n-i)x^{n}=x^{i}(p_{i}(\theta+i)A)(x)$, and
$b(n)$ is the coefficient of $x^{n}$ in $B$.
\end{proof}

Since $A$ lies in the algebraic function field generated by the polynomial of
Corollary~\ref{cor:minpoly}, and such a field is closed under $\theta$ --- differentiating
its defining relation expresses the derivative of the generator inside the field ---
every $p_{i}(\theta+i)A$ lies there too, and so does $B$. Computing it exactly gives
\[
B(x)\;=\;%(BLATEX)s ,
\]
a polynomial of degree $%(DEG)d$.

\begin{theorem}
The conjectured recurrence
\[
%(RECLATEX)s \;=\;0
\]
holds for every $n>%(DEG)d$.
\end{theorem}

\begin{proof}
Immediate from Lemma~\ref{lem:transfer} and the displayed value of $B$.
\end{proof}

\section{Verification}

Every number above is an output of a script written separately from this note, and three
independent checks were run.

First, the derived generating function was not assumed to be right. Its series was
computed from \eqref{eq:def} in two independent ways --- once through the residue formula
of Lemma~\ref{lem:diag}, by solving $x=t\,g(x)$ as a truncated series, and once directly,
by expanding $f\,g^{n}$ and reading off the coefficient of $x^{n}$ --- and the two agree.
The result was then compared term by term with the DATA section of %(ANUM)s, agreeing on
all %(NCHECK)d terms compared.

Second, the recurrence was evaluated directly on the published terms, in exact integer
arithmetic and without reference to any generating function: for each $n$ in range the sum
$\sum_{i}p_{i}(n)a(n-i)$ was formed from the entry's own values and found to vanish, for
all %(NVER)d values of $n$ from $n=%(FIRSTN)d$ upward.

Third, the symbolic step is exact throughout. The residual is obtained by
rational-function arithmetic in the algebraic function field, not by series truncation, so
the identity $B=%(BLATEX)s$ is an identity of functions and the theorem holds for all
$n>%(DEG)d$ simultaneously.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s.
\bibitem{stanley} R.~P.~Stanley, \emph{Enumerative Combinatorics}, Volume 2, Cambridge
University Press, 1999, Section 6.3 (Lagrange inversion) and Chapter 6 (algebraic and
D-finite generating functions).
\bibitem{flajolet} P.~Flajolet and R.~Sedgewick, \emph{Analytic Combinatorics}, Cambridge
University Press, 2009, Chapter VII.
\bibitem{kp} M.~Kauers and P.~Paule, \emph{The Concrete Tetrahedron}, Springer, 2011,
Chapter 7.
\end{thebibliography}
\end{document}
"""
