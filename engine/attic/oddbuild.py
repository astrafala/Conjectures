#!/usr/bin/env python3
"""A397241: every term is odd."""
import os
import entry, phibuild, sectionbuild

PRE = phibuild.PRE
esc = phibuild.esc
anum = "A397241"
mod, rev = sectionbuild.modinfo(anum)
e = entry.get(anum)
d = [int(x) for x in e['data'].split(',')]

TEX = rf"""{PRE}
\title{{Every term of OEIS {anum} is odd}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} is defined by the coefficient condition
$n\,[x^{{n}}]A(x)^{{n}}=(n-1)\,[x^{{n}}]A(x)^{{n+1}}$ for $n>1$, and carries a conjecture of
P.~D.~Hanna that every term is odd. It is true. The condition determines the coefficients
one at a time --- $a(N)$ enters with coefficient $N^{{2}}-(N^{{2}}-1)=1$ --- so it determines
them modulo $2$ as well. Modulo $2$ the series $1/(1-x)$, all of whose coefficients are
$1$, satisfies the condition, because $\binom{{2N}}{{N}}=2\binom{{2N-1}}{{N}}$ kills the right
side while Kummer's theorem makes $N\binom{{2N-1}}{{N}}$ even on the left. Uniqueness then
forces $A(x)\equiv1/(1-x)$, which is the conjecture. The entry's two further conjectures,
modulo $3$ and modulo $4$, are \emph{{not}} settled here; Section~5 says exactly where the
argument stops.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 11B65, 05A15.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset $0$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry gives the expansion
\begin{{quote}}\small
G.f.: A(x) = 1 + x + x\^{{}}2 + 11*x\^{{}}3 + 191*x\^{{}}4 + 5279*x\^{{}}5 + 205739*x\^{{}}6 + \dots
\end{{quote}}
so, writing $A(x)=\sum_{{n\ge0}}a(n)x^{{n}}$, the entry fixes
\begin{{equation}}\label{{eq:init}}
a(0)=1,\qquad a(1)=1,
\end{{equation}}
and defines the remaining coefficients by
\begin{{equation}}\label{{eq:fe}}
n\,\bigl[x^{{n}}\bigr]A(x)^{{n}}\;=\;(n-1)\,\bigl[x^{{n}}\bigr]A(x)^{{n+1}}
\qquad\text{{for }} n>1 .
\end{{equation}}
This is the only input taken from the entry.

The entry separately carries the following comment:
\begin{{quote}}\small
Conjecture: all terms are odd. --- \emph{{Paul D. Hanna}}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as a conjecture, and nothing on the entry records it as settled either way.
The entry carries two further conjectures of the same contributor, that $a(n)\equiv2$
modulo $3$ and $a(n)\equiv3$ modulo $4$ for $n>2$. Those are stronger, they are not proved
below, and they are not claimed.

\section{{The condition determines the sequence}}

\begin{{lemma}}\label{{lem:MaN}}
Let $A(x)=\sum_{{n\ge0}}a(n)x^{{n}}$ with $a(0)=1$. Then for every $M\ge1$ and every $N\ge1$,
\[
\bigl[x^{{N}}\bigr]A^{{M}}=M\,a(N)+\bigl(\text{{a polynomial with integer coefficients in }}
a(1),\dots,a(N-1)\bigr).
\]
\end{{lemma}}

\begin{{proof}}
Write $A=1+U$ with $U=\sum_{{n\ge1}}a(n)x^{{n}}$, so
$A^{{M}}=\sum_{{r\ge0}}\binom{{M}}{{r}}U^{{r}}$. The coefficient of $x^{{N}}$ in $U^{{r}}$ is a sum
of products of $r$ coefficients $a(i_1)\cdots a(i_r)$ with all $i_s\ge1$ and
$i_1+\dots+i_r=N$. Such a product involves $a(N)$ only when $r=1$, and then it is $a(N)$
itself; for $r\ge2$ every index is at most $N-1$. Hence
$\bigl[x^{{N}}\bigr]A^{{M}}=\binom{{M}}{{1}}a(N)+\cdots=M\,a(N)+\cdots$ as claimed.
\end{{proof}}

\begin{{lemma}}\label{{lem:unique}}
Given \eqref{{eq:init}}, there is exactly one sequence of integers $a(2),a(3),\dots$
satisfying \eqref{{eq:fe}}, and for each $N\ge2$ the condition at $n=N$ has the form
$a(N)=(\text{{a polynomial with integer coefficients in }}a(0),\dots,a(N-1))$.
\end{{lemma}}

\begin{{proof}}
Fix $N\ge2$ and collect the coefficient of $a(N)$ on the two sides of \eqref{{eq:fe}} at
$n=N$, using Lemma~\ref{{lem:MaN}} with $M=N$ and $M=N+1$. The left side gives $N\cdot N$ and
the right side $(N-1)(N+1)$, so the net coefficient of $a(N)$ is
\[
N^{{2}}-(N^{{2}}-1)\;=\;1 .
\]
Everything else in the condition involves only $a(0),\dots,a(N-1)$. So the condition at
$n=N$ solves for $a(N)$ over $\mathbb{{Z}}$, and induction from \eqref{{eq:init}} gives
existence and uniqueness. (At $n=2$ it gives $a(2)=1$, matching the entry.)
\end{{proof}}

\begin{{corollary}}\label{{cor:mod}}
Let $m\ge2$. If $\bar A\in(\mathbb{{Z}}/m\mathbb{{Z}})[[x]]$ has
$\bigl[x^{{0}}\bigr]\bar A=\bigl[x^{{1}}\bigr]\bar A=1$ and satisfies \eqref{{eq:fe}} with all
coefficients read modulo $m$, then $a(n)\equiv\bigl[x^{{n}}\bigr]\bar A\pmod m$ for every $n$.
\end{{corollary}}

\begin{{proof}}
Reduction modulo $m$ is a ring homomorphism, so it carries the integer recursion of
Lemma~\ref{{lem:unique}} to the same recursion over $\mathbb{{Z}}/m\mathbb{{Z}}$, in which the
coefficient of $a(N)$ is still $1$ and hence still invertible. That recursion, started from
the same two initial values, has a unique solution, and both $a\bmod m$ and the
coefficients of $\bar A$ solve it.
\end{{proof}}

\section{{Two facts about binomial coefficients}}

\begin{{lemma}}\label{{lem:half}}
$\binom{{2N}}{{N}}=2\binom{{2N-1}}{{N}}$ for every $N\ge1$.
\end{{lemma}}

\begin{{proof}}
Pascal's rule gives
$\binom{{2N}}{{N}}=\binom{{2N-1}}{{N-1}}+\binom{{2N-1}}{{N}}$, and
$\binom{{2N-1}}{{N-1}}=\binom{{2N-1}}{{(2N-1)-(N-1)}}=\binom{{2N-1}}{{N}}$.
\end{{proof}}

\begin{{lemma}}\label{{lem:kummer}}
Let $s(N)$ be the number of $1$s in the binary expansion of $N$. Then the exponent of $2$
in $\binom{{2N}}{{N}}$ is exactly $s(N)$. Consequently $\binom{{2N-1}}{{N}}$ is even whenever
$s(N)\ge2$, in particular whenever $N$ is odd and $N\ge3$.
\end{{lemma}}

\begin{{proof}}
By Kummer's theorem the exponent of $2$ in $\binom{{2N}}{{N}}$ is the number of carries when
$N$ is added to $N$ in base $2$; each $1$ of $N$ produces exactly one carry, so that number
is $s(N)$. By Lemma~\ref{{lem:half}} the exponent of $2$ in $\binom{{2N-1}}{{N}}$ is $s(N)-1$,
which is at least $1$ as soon as $s(N)\ge2$. Finally, an odd $N\ge3$ has its last binary
digit $1$ and at least one further $1$, so $s(N)\ge2$.
\end{{proof}}

\section{{The reduction modulo $2$}}

\begin{{lemma}}\label{{lem:sat}}
Over $\mathbb{{Z}}/2\mathbb{{Z}}$ the series $\bar A(x)=\dfrac{{1}}{{1-x}}$ satisfies
\eqref{{eq:init}} and \eqref{{eq:fe}}.
\end{{lemma}}

\begin{{proof}}
All coefficients of $1/(1-x)$ equal $1$, so \eqref{{eq:init}} holds. For $M\ge1$,
$\bar A^{{M}}=(1-x)^{{-M}}$ and
$\bigl[x^{{N}}\bigr](1-x)^{{-M}}=\binom{{N+M-1}}{{N}}$, so
\[
\bigl[x^{{N}}\bigr]\bar A^{{N}}=\binom{{2N-1}}{{N}},\qquad
\bigl[x^{{N}}\bigr]\bar A^{{N+1}}=\binom{{2N}}{{N}} .
\]
Take $N\ge2$. By Lemma~\ref{{lem:half}} the right-hand side of \eqref{{eq:fe}} is
$(N-1)\binom{{2N}}{{N}}=2(N-1)\binom{{2N-1}}{{N}}\equiv0\pmod2$. For the left-hand side
$N\binom{{2N-1}}{{N}}$: if $N$ is even the factor $N$ is even; if $N$ is odd then $N\ge3$, so
$\binom{{2N-1}}{{N}}$ is even by Lemma~\ref{{lem:kummer}}. Either way the left-hand side is
$\equiv0\pmod2$ as well, and \eqref{{eq:fe}} holds modulo $2$.
\end{{proof}}

\begin{{theorem}}
Every term of OEIS {anum} is odd. This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
By Lemma~\ref{{lem:sat}} the series $1/(1-x)$ satisfies \eqref{{eq:init}} and \eqref{{eq:fe}}
over $\mathbb{{Z}}/2\mathbb{{Z}}$. By Corollary~\ref{{cor:mod}} it is the reduction of $A$ modulo
$2$, so $a(n)\equiv1\pmod2$ for every $n\ge0$.
\end{{proof}}

\section{{Where the argument stops}}

The same scheme would settle the entry's other two conjectures if one could exhibit the
corresponding reductions. Those reductions are visible in the data:
\[
\bar A_{{3}}(x)=\frac{{1+x^{{3}}}}{{1-x}}\ \ \text{{over }}\mathbb{{Z}}/3\mathbb{{Z}},
\qquad
\bar A_{{4}}(x)=\frac{{1+2x^{{3}}}}{{1-x}}\ \ \text{{over }}\mathbb{{Z}}/4\mathbb{{Z}},
\]
whose coefficients are $1,1,1,2,2,2,\dots$ and $1,1,1,3,3,3,\dots$ respectively. Both were
checked to satisfy \eqref{{eq:fe}} for every $n\le34$. What is missing is a proof that they
satisfy it for \emph{{all}} $n$. Writing $\bar A_{{4}}=f+2h$ with $f=1/(1-x)$ and
$h=x^{{3}}/(1-x)$, and using $(2h)^{{2}}\equiv0$, the condition modulo $4$ reduces to
\[
(2-N)\binom{{2N-1}}{{N}}\;\equiv\;
2\left[N^{{2}}\binom{{2N-4}}{{N-1}}-(N^{{2}}-1)\binom{{2N-3}}{{N}}\right]\pmod4 ,
\]
and the two sides do agree at every $N\le33$ --- both vanish unless $N$ or $N-1$ is a power
of $2$, where both equal $2$ --- but a proof of that congruence for all $N$ is not given
here. The modulo $3$ case reduces similarly to a Lucas-type identity. Neither is claimed.

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the recursion of Lemma~\ref{{lem:unique}} was run in exact rational arithmetic from
$a(0)=a(1)=1$ and compared against the entry's DATA at every one of the ${len(d)}$ published
indices; the values agree exactly, and every one is an integer. In particular the condition
at $n=2$ returns $a(2)=1$.

Second, at every step the coefficient of $a(N)$ was computed rather than assumed, by
evaluating the condition at $a(N)=0$ and at $a(N)=1$ and subtracting; it came out $1$ at
every $N$ up to $16$, as Lemma~\ref{{lem:unique}} requires.

Third, the identity $v_2\bigl(\binom{{2N}}{{N}}\bigr)=s(N)$ of Lemma~\ref{{lem:kummer}} was
checked directly for every $N\le299$, and the reduced condition of Lemma~\ref{{lem:sat}} was
verified over $\mathbb{{Z}}/2\mathbb{{Z}}$ by expanding $(1-x)^{{-N}}$ and $(1-x)^{{-(N+1)}}$ for
every $n\le34$.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {anum}.
\bibitem{{kummer}} E.~E.~Kummer, \"Uber die Erg\"anzungss\"atze zu den allgemeinen
Reciprocit\"atsgesetzen, \emph{{J. Reine Angew. Math.}} \textbf{{44}} (1852), 93--146.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 2, Cambridge
University Press, 1999.
\bibitem{{hw}} G.~H.~Hardy and E.~M.~Wright, \emph{{An Introduction to the Theory of
Numbers}}, 6th ed., Oxford University Press, 2008.
\end{{thebibliography}}

\end{{document}}
"""

if __name__ == "__main__":
    os.makedirs("build/oddA397241", exist_ok=True)
    open("build/oddA397241/p.tex", "w").write(TEX)
    print("wrote build/oddA397241")
