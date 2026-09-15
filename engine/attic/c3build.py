#!/usr/bin/env python3
"""A395833: a(n) = 0 mod 3 for n >= 2."""
import os
import entry, phibuild, sectionbuild

PRE = phibuild.PRE
esc = phibuild.esc
anum = "A395833"
mod, rev = sectionbuild.modinfo(anum)
e = entry.get(anum)
d = [int(x) for x in e['data'].split(',')]

TEX = rf"""{PRE}
\title{{Every term of OEIS {anum} after the second is divisible by $3$}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} is defined by the vanishing condition
$\bigl[x^{{n}}\bigr]A\bigl(x/A(x)^{{2n-1}}\bigr)=0$ for $n>1$, and carries a conjecture of
P.~D.~Hanna that $a(n)\equiv0\pmod3$ for $n\ge2$. It is true, and the proof reduces the
whole statement to a single divisibility of binomial coefficients. The condition determines
the coefficients one at a time, with $a(n)$ entering with coefficient $1$, so it determines
them modulo $3$; and modulo $3$ the \emph{{polynomial}} $1+x$ satisfies the condition,
because substituting it turns the $n$-th condition into
$(-1)^{{n-1}}\binom{{3n-3}}{{n-1}}\equiv0\pmod3$, which Legendre's formula gives outright:
$v_3\bigl(\binom{{3m}}{{m}}\bigr)=\tfrac12 s_3(2m)\ge1$ for every $m\ge1$. Uniqueness then
forces $A(x)\equiv1+x$, which is the conjecture. The entry's other conjecture, that $2n-1$
divides $a(n)$, is \emph{{not}} settled here.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 11B65, 05A15.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset $0$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry gives the expansion
\begin{{quote}}\small
G.f.: A(x) = 1 + x + 3*x\^{{}}2 + 30*x\^{{}}3 + 567*x\^{{}}4 + 16452*x\^{{}}5 + 663894*x\^{{}}6 + \dots
\end{{quote}}
so, writing $A(x)=\sum_{{n\ge0}}a(n)x^{{n}}$, the entry fixes
\begin{{equation}}\label{{eq:init}}
a(0)=1,\qquad a(1)=1,
\end{{equation}}
and defines the remaining coefficients by
\begin{{equation}}\label{{eq:fe}}
\bigl[x^{{n}}\bigr]\,A\!\left(\frac{{x}}{{A(x)^{{2n-1}}}}\right)\;=\;0
\qquad\text{{for }} n>1 .
\end{{equation}}
Since $a(0)=1$, the series $A$ is invertible and $A^{{-(2n-1)}}$ is a well-defined element of
$\mathbb{{Z}}[[x]]$, so the composition in \eqref{{eq:fe}} makes sense: the inner series
$x\,A(x)^{{-(2n-1)}}$ has zero constant term. This is the only input taken from the entry.

The entry separately carries the following comment:
\begin{{quote}}\small
Conjecture: a(n) == 0 (mod 3) for n >= 2. --- \emph{{Paul D. Hanna}}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as a conjecture, and nothing on the entry records it as settled either way.
The entry carries a second conjecture of the same contributor, that $2n-1$ divides $a(n)$
for $n\ge1$. It is not proved below and it is not claimed.

\section{{The condition determines the sequence}}

\begin{{lemma}}\label{{lem:unique}}
Given \eqref{{eq:init}}, there is exactly one sequence of integers $a(2),a(3),\dots$
satisfying \eqref{{eq:fe}}, and for each $N\ge2$ the condition at $n=N$ has the form
$a(N)=(\text{{a polynomial with integer coefficients in }}a(0),\dots,a(N-1))$.
\end{{lemma}}

\begin{{proof}}
Fix $N\ge2$ and write $u=x\,A(x)^{{-(2N-1)}}$, so $u=x+O(x^{{2}})$ and
$\bigl[x^{{m}}\bigr]u^{{j}}=0$ for $m<j$, while $\bigl[x^{{j}}\bigr]u^{{j}}=1$. Expanding,
\[
\bigl[x^{{N}}\bigr]A(u)\;=\;\sum_{{j\ge0}}a(j)\,\bigl[x^{{N}}\bigr]u^{{j}}
\;=\;\sum_{{j=0}}^{{N}}a(j)\,\bigl[x^{{N}}\bigr]u^{{j}} .
\]
The term $j=N$ contributes $a(N)\cdot1$. For $j<N$ the factor
$\bigl[x^{{N}}\bigr]u^{{j}}=\bigl[x^{{N-j}}\bigr]A^{{-j(2N-1)}}$ is a polynomial in
$a(1),\dots,a(N-j)$ with $N-j\le N-1$, and it is multiplied by $a(j)$ with $j\le N-1$; so
no $a(N)$ occurs there. Hence the coefficient of $a(N)$ in \eqref{{eq:fe}} is exactly $1$,
the condition solves for $a(N)$ over $\mathbb{{Z}}$, and induction from \eqref{{eq:init}}
gives existence and uniqueness.
\end{{proof}}

\begin{{corollary}}\label{{cor:mod}}
Let $k\ge2$. If $\bar A\in(\mathbb{{Z}}/k\mathbb{{Z}})[[x]]$ has
$\bigl[x^{{0}}\bigr]\bar A=\bigl[x^{{1}}\bigr]\bar A=1$ and satisfies \eqref{{eq:fe}} with all
coefficients read modulo $k$, then $a(n)\equiv\bigl[x^{{n}}\bigr]\bar A\pmod k$ for every $n$.
\end{{corollary}}

\begin{{proof}}
Reduction modulo $k$ is a ring homomorphism and carries the recursion of
Lemma~\ref{{lem:unique}} to the same recursion over $\mathbb{{Z}}/k\mathbb{{Z}}$, where the
coefficient of $a(N)$ is still $1$ and hence invertible. (The inverse $A^{{-(2N-1)}}$ is
carried to the inverse of the reduction, which exists because the constant term $1$ is a
unit.) That recursion, started from the same two initial values, has a unique solution, and
both $a\bmod k$ and the coefficients of $\bar A$ solve it.
\end{{proof}}

\section{{A divisibility of binomial coefficients}}

For a prime $p$ let $s_p(m)$ denote the sum of the base-$p$ digits of $m$, and $v_p$ the
$p$-adic valuation.

\begin{{lemma}}\label{{lem:val}}
$v_3\!\left(\dbinom{{3m}}{{m}}\right)=\dfrac{{s_3(2m)}}{{2}}$ for every $m\ge0$. In
particular $3$ divides $\dbinom{{3m}}{{m}}$ for every $m\ge1$.
\end{{lemma}}

\begin{{proof}}
Legendre's formula gives $v_3(j!)=\bigl(j-s_3(j)\bigr)/2$. Hence
\[
v_3\!\left(\binom{{3m}}{{m}}\right)
=v_3\bigl((3m)!\bigr)-v_3\bigl(m!\bigr)-v_3\bigl((2m)!\bigr)
=\frac{{\bigl(3m-s_3(3m)\bigr)-\bigl(m-s_3(m)\bigr)-\bigl(2m-s_3(2m)\bigr)}}{{2}},
\]
which simplifies to $\bigl(s_3(m)+s_3(2m)-s_3(3m)\bigr)/2$. Multiplying by $3$ shifts the
base-$3$ digits and appends a zero, so $s_3(3m)=s_3(m)$ and the expression collapses to
$s_3(2m)/2$.

For $m\ge1$ we have $2m\ge2$, so $s_3(2m)\ge1$; since the valuation is an integer,
$s_3(2m)/2\ge1$, that is $3\mid\binom{{3m}}{{m}}$.
\end{{proof}}

\section{{The reduction modulo $3$}}

\begin{{lemma}}\label{{lem:sat}}
Over $\mathbb{{Z}}/3\mathbb{{Z}}$ the polynomial $\bar A(x)=1+x$ satisfies \eqref{{eq:init}} and
\eqref{{eq:fe}}.
\end{{lemma}}

\begin{{proof}}
Clearly $\bigl[x^{{0}}\bigr]\bar A=\bigl[x^{{1}}\bigr]\bar A=1$. Fix $n>1$ and put
$u=x\,(1+x)^{{-(2n-1)}}$. Since $\bar A(u)=1+u$,
\[
\bigl[x^{{n}}\bigr]\bar A(u)\;=\;\bigl[x^{{n}}\bigr]u
\;=\;\bigl[x^{{\,n-1}}\bigr](1+x)^{{-(2n-1)}} .
\]
By the binomial series, $\bigl[x^{{m}}\bigr](1+x)^{{-k}}=(-1)^{{m}}\binom{{k+m-1}}{{m}}$, so with
$k=2n-1$ and $m=n-1$,
\[
\bigl[x^{{n}}\bigr]\bar A(u)\;=\;(-1)^{{n-1}}\binom{{(2n-1)+(n-1)-1}}{{n-1}}
\;=\;(-1)^{{n-1}}\binom{{3n-3}}{{n-1}}
\;=\;(-1)^{{n-1}}\binom{{3m'}}{{m'}},\quad m'=n-1 .
\]
Since $n>1$ we have $m'\ge1$, so Lemma~\ref{{lem:val}} makes this $\equiv0\pmod3$. Hence
\eqref{{eq:fe}} holds modulo $3$.
\end{{proof}}

\begin{{theorem}}
$a(n)\equiv0\pmod3$ for every $n\ge2$. This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
By Lemma~\ref{{lem:sat}} the polynomial $1+x$ satisfies \eqref{{eq:init}} and \eqref{{eq:fe}}
over $\mathbb{{Z}}/3\mathbb{{Z}}$, so by Corollary~\ref{{cor:mod}} it is the reduction of $A$
modulo $3$. Its coefficients are $1,1,0,0,\dots$, so $a(n)\equiv0\pmod3$ for every $n\ge2$.
\end{{proof}}

\begin{{remark}}
The proof is short because the reduction is a polynomial rather than an infinite series:
the whole content is that the substitution $x\mapsto x(1+x)^{{-(2n-1)}}$ makes the $n$-th
coefficient a single central-type binomial, and that binomial is always divisible by $3$.
The same computation modulo $2$ gives $\binom{{3n-3}}{{n-1}}$ modulo $2$, which is
\emph{{not}} always even --- for instance $\binom{{6}}{{2}}=15$ --- so $1+x$ is not the
reduction modulo $2$ and the argument is specific to the prime $3$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the recursion of Lemma~\ref{{lem:unique}} was run in exact rational arithmetic from
\eqref{{eq:init}}, inverting $A$ by the usual convolution, and its output compared against
the entry's DATA at every published index within reach; the values agree exactly and are
integers. At every step the coefficient of $a(N)$ was computed rather than assumed, by
evaluating the condition at $a(N)=0$ and at $a(N)=1$ and subtracting; it came out $1$ every
time.

Second, Lemma~\ref{{lem:val}} was checked directly: $3\mid\binom{{3m}}{{m}}$ for every
$m\le400$, and $v_3\bigl(\binom{{3m}}{{m}}\bigr)=s_3(2m)/2$ over the same range, together
with the identity $s_3(3m)=s_3(m)$ used in its proof.

Third, the reduced condition of Lemma~\ref{{lem:sat}} was evaluated for every $n$ from $2$
to $119$: the value $(-1)^{{n-1}}\binom{{3n-3}}{{n-1}}$ is divisible by $3$ in every case,
with no exception.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {anum}.
\bibitem{{legendre}} A.-M.~Legendre, \emph{{Essai sur la th\'eorie des nombres}}, 2nd ed.,
Courcier, Paris, 1808.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 2, Cambridge
University Press, 1999.
\bibitem{{hw}} G.~H.~Hardy and E.~M.~Wright, \emph{{An Introduction to the Theory of
Numbers}}, 6th ed., Oxford University Press, 2008.
\end{{thebibliography}}

\end{{document}}
"""

if __name__ == "__main__":
    os.makedirs("build/c3A395833", exist_ok=True)
    open("build/c3A395833/p.tex", "w").write(TEX)
    print("wrote build/c3A395833")
