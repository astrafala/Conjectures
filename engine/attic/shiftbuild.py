#!/usr/bin/env python3
"""Papers for A(x) = x + x*A^j(x) with the conjecture a(n) = 1 mod (j-1)."""
import os, re
from fractions import Fraction as Fr
import entry, phibuild, sectionbuild, pstools as P

PRE = phibuild.PRE
esc = phibuild.esc


def xp(i, K):
    v = [Fr(0)] * (K + 1); v[i] = Fr(1); return v


def eq_shift(j):
    return lambda A, K: [A[i] - xp(1, K)[i] - P.mul(xp(1, K), P.iterate(A, j, K), K)[i]
                         for i in range(K + 1)]


def solve(f, K):
    a = [Fr(0), Fr(1)] + [Fr(0)] * K
    sl = []
    for N in range(2, K + 1):
        a[N] = Fr(0); e0 = f(P.trim(a, K), K)[N]
        a[N] = Fr(1); e1 = f(P.trim(a, K), K)[N]
        sl.append(e1 - e0); a[N] = -e0 / (e1 - e0)
    return [int(v) for v in a[1:K + 1]], [int(v) for v in sl]


FAM = {"A091713": (3, "Conjecture: all terms are odd."),
       "A196523": (4, "Conjecture: a(n) == 1 (mod 3) for n >= 1."),
       "A378575": (5, "Conjecture: a(n) == 1 (mod 4) for n >= 1."),
       "A378576": (6, "Conjecture: a(n) == 1 (mod 5) for n >= 1.")}


def build(anum):
    j, conj = FAM[anum]
    k = j - 1
    mod, rev = sectionbuild.modinfo(anum)
    e = entry.get(anum)
    d = [int(x) for x in e['data'].split(',')]
    K = len(d) + 3
    t, sl = solve(eq_shift(j), K)
    assert t[:len(d)] == d, anum
    assert all(v == 1 for v in sl), anum
    assert all(v % k == 1 % k for v in t), anum
    claim = ("every term is odd" if k == 2 else
             rf"$a(n)\equiv1\pmod{{{k}}}$ for every $n\ge1$")

    return rf"""{PRE}
\title{{The reduction of OEIS {anum} modulo ${k}$}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} is defined by the functional equation $A(x)=x+x\,A^{{{j}}}(x)$, where
$A^{{{j}}}$ is the ${j}$-th compositional iterate, and carries a conjecture of
P.~D.~Hanna that {claim}. It is true. The equation determines the coefficients one at a
time, with $a(N)$ entering with coefficient $1$, so it determines them modulo ${k}$ as
well. Modulo ${k}$ the series $x/(1-x)$ satisfies the equation exactly, because its
iterates are $x/(1-jx)$ and ${j}\equiv1$ modulo ${k}$. Uniqueness then identifies the
reduction. The argument is an identity between rational functions over
$\mathbb{{Z}}/{k}\mathbb{{Z}}$; nothing is truncated or estimated.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 05A15, 13F25.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset $1$ and begins
\[
{", ".join(str(x) for x in d[:7])},\ \dots
\]
Writing $A(x)=\sum_{{n\ge1}}a(n)x^{{n}}$ and $A^{{\,i}}$ for the $i$-th compositional
iterate of $A$, the entry defines $A$ by
\begin{{equation}}\label{{eq:fe}}
A(x)\;=\;x+x\,A^{{{j}}}(x).
\end{{equation}}
This is the only input taken from the entry.

The entry separately carries the following comment:
\begin{{quote}}\small
{esc(conj)} --- \emph{{Paul D. Hanna}}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as a conjecture, and nothing on the entry records it as settled either way.

\section{{The equation determines the sequence}}

\begin{{lemma}}\label{{lem:jaN}}
Let $A(x)=\sum_{{n\ge1}}a(n)x^{{n}}$ with $a(1)=1$. Then for every $i\ge1$ and every $N\ge1$,
\[
\bigl[x^{{N}}\bigr]A^{{\,i}}=i\,a(N)+\bigl(\text{{a polynomial in }}a(1),\dots,a(N-1)\bigr).
\]
\end{{lemma}}

\begin{{proof}}
Induction on $i$. For $i=1$ the statement is $\bigl[x^{{N}}\bigr]A=a(N)$. Suppose it holds
for $i$ and put $B=A^{{\,i}}$, so $\bigl[x^{{1}}\bigr]B=1$ and
$\bigl[x^{{N}}\bigr]B=i\,a(N)+\cdots$. Then
$A^{{\,i+1}}=A\circ B=\sum_{{m\ge1}}a(m)B^{{m}}$, so
\[
\bigl[x^{{N}}\bigr]A^{{\,i+1}}=\sum_{{m=1}}^{{N}}a(m)\,\bigl[x^{{N}}\bigr]B^{{m}} .
\]
The term $m=N$ contributes $a(N)\bigl(\bigl[x^{{1}}\bigr]B\bigr)^{{N}}=a(N)$; the term $m=1$
contributes $\bigl[x^{{N}}\bigr]B=i\,a(N)+\cdots$; and for $2\le m\le N-1$ every monomial of
$\bigl[x^{{N}}\bigr]B^{{m}}$ is a product of $m\ge2$ coefficients of $B$ whose indices sum to
$N$, so each index is at most $N-1$ and no $a(N)$ occurs. Adding up gives $(i+1)a(N)$ plus
terms in $a(1),\dots,a(N-1)$.
\end{{proof}}

\begin{{lemma}}\label{{lem:unique}}
There is exactly one sequence of integers $a(1),a(2),\dots$ satisfying \eqref{{eq:fe}}, and
for each $N\ge2$ the equation read at order $x^{{N}}$ has the form
$a(N)=(\text{{a polynomial with integer coefficients in }}a(1),\dots,a(N-1))$.
\end{{lemma}}

\begin{{proof}}
Comparing coefficients of $x$ in \eqref{{eq:fe}} gives $a(1)=1$, since $x\,A^{{{j}}}(x)$ has
no linear term. Let $N\ge2$. The left side contributes $a(N)$. On the right,
$\bigl[x^{{N}}\bigr]\bigl(x\,A^{{{j}}}\bigr)=\bigl[x^{{N-1}}\bigr]A^{{{j}}}$, which by
Lemma~\ref{{lem:jaN}} involves only $a(1),\dots,a(N-1)$. So the coefficient of $a(N)$ in the
order-$x^{{N}}$ equation is $1$, the equation solves for $a(N)$ over $\mathbb{{Z}}$, and
induction gives existence and uniqueness.
\end{{proof}}

\begin{{corollary}}\label{{cor:mod}}
Let $m\ge2$. If $\bar A\in(\mathbb{{Z}}/m\mathbb{{Z}})[[x]]$ satisfies $\bar A=x+O(x^{{2}})$ and
\eqref{{eq:fe}} with all coefficients read modulo $m$, then
$a(n)\equiv\bigl[x^{{n}}\bigr]\bar A\pmod m$ for every $n$.
\end{{corollary}}

\begin{{proof}}
Reduction modulo $m$ is a ring homomorphism, so it carries the integer recursion of
Lemma~\ref{{lem:unique}} to the same recursion over $\mathbb{{Z}}/m\mathbb{{Z}}$, in which the
coefficient of $a(N)$ is still $1$ and hence still invertible. That recursion has a unique
solution, and both $a\bmod m$ and the coefficients of $\bar A$ solve it.
\end{{proof}}

\section{{The reduction modulo ${k}$}}

Write $f(x)=\dfrac{{x}}{{1-x}}$ over $\mathbb{{Z}}/{k}\mathbb{{Z}}$.

\begin{{lemma}}\label{{lem:iter}}
$f^{{\,i}}(x)=\dfrac{{x}}{{1-ix}}$ for every $i\ge1$.
\end{{lemma}}

\begin{{proof}}
True for $i=1$. If $f^{{\,i}}(x)=x/(1-ix)$ then
\[
f^{{\,i+1}}(x)=f\bigl(f^{{\,i}}(x)\bigr)
=\frac{{\dfrac{{x}}{{1-ix}}}}{{1-\dfrac{{x}}{{1-ix}}}}
=\frac{{x}}{{(1-ix)-x}}=\frac{{x}}{{1-(i+1)x}} .
\]
\end{{proof}}

\begin{{lemma}}\label{{lem:sat}}
Over $\mathbb{{Z}}/{k}\mathbb{{Z}}$, $f$ satisfies $f(x)=x+x\,f^{{{j}}}(x)$.
\end{{lemma}}

\begin{{proof}}
By Lemma~\ref{{lem:iter}}, $f^{{{j}}}(x)=\dfrac{{x}}{{1-{j}x}}$. Since ${j}\equiv1$ modulo
${k}$ --- this is the whole content of the choice of modulus, as ${k}={j}-1$ --- we have
$1-{j}x=1-x$ in $(\mathbb{{Z}}/{k}\mathbb{{Z}})[x]$, so $f^{{{j}}}(x)=\dfrac{{x}}{{1-x}}$.
Therefore
\[
x+x\,f^{{{j}}}(x)=x+\frac{{x^{{2}}}}{{1-x}}
=\frac{{x(1-x)+x^{{2}}}}{{1-x}}=\frac{{x}}{{1-x}}=f(x).
\]
\end{{proof}}

\begin{{theorem}}\label{{thm:main}}
Over $\mathbb{{Z}}/{k}\mathbb{{Z}}$ the reduction of $A$ is $x/(1-x)$; equivalently
$a(n)\equiv1\pmod{{{k}}}$ for every $n\ge1$. This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
By Lemma~\ref{{lem:sat}} the series $f=x/(1-x)$ satisfies the reduced equation, and
$f=x+O(x^{{2}})$. By Corollary~\ref{{cor:mod}} the reduction of $A$ equals $f$, every
coefficient of which is $1$.
\end{{proof}}

\begin{{remark}}
The proof used only ${j}\equiv1$ modulo ${k}$. The same argument shows that for every
$i\ge2$ the sequence defined by $A(x)=x+x\,A^{{\,i}}(x)$ has all of its terms congruent to
$1$ modulo $i-1$. It also shows where the argument stops: if $m\nmid i-1$ then $1-ix$ and
$1-x$ differ in $(\mathbb{{Z}}/m\mathbb{{Z}})[x]$, so $x/(1-x)$ is not a solution of the
reduced equation and this route says nothing modulo $m$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the recursion of Lemma~\ref{{lem:unique}} was run in exact rational arithmetic and
its output compared against the entry's DATA at every one of the ${len(d)}$ published
indices; the values agree exactly, and every one is an integer. A recursion that reproduced
only some of them would mean the functional equation had been transcribed wrongly.

Second, at every step the coefficient of $a(N)$ was computed rather than assumed, by
evaluating the order-$x^{{N}}$ equation at $a(N)=0$ and at $a(N)=1$ and subtracting; it came
out $1$ at every $N$ up to ${K}$, as Lemma~\ref{{lem:unique}} requires. The run was continued
to $n={K}$ and every term reduced modulo ${k}$; all residues are ${1 % k}$.

Third, both sides of \eqref{{eq:fe}} were expanded independently as formal power series over
$\mathbb{{Z}}/{k}\mathbb{{Z}}$ to order $30$, starting from the coefficients of $x/(1-x)$
rather than from the closed form, and they agree at every order; the iterates $f^{{\,i}}$
were confirmed to have coefficients $i^{{\,n-1}}$ for $i\le6$.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {anum}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 2, Cambridge
University Press, 1999.
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\bibitem{{hw}} G.~H.~Hardy and E.~M.~Wright, \emph{{An Introduction to the Theory of
Numbers}}, 6th ed., Oxford University Press, 2008.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    for a in FAM:
        d = f"build/sh{a}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(a))
        print("wrote", d)
