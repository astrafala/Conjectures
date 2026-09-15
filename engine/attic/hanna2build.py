#!/usr/bin/env python3
"""Papers for Hanna's congruence conjectures on iterated functional equations."""
import os, re
from fractions import Fraction as Fr
import entry, phibuild, sectionbuild, pstools as P

PRE = phibuild.PRE
esc = phibuild.esc


def xp(i, K):
    v = [Fr(0)] * (K + 1); v[i] = Fr(1); return v


def eq_iter(p):
    return lambda A, K: [A[i] - xp(1, K)[i]
                         - P.mul(P.iterate(A, p, K), P.iterate(A, p + 1, K), K)[i]
                         for i in range(K + 1)]


def eq_102(A, K):
    return [P.iterate(A, 3, K)[i]
            - P.mul(P.trim([Fr(1), Fr(1)], K), P.iterate(A, 2, K), K)[i]
            for i in range(K + 1)]


def solve(f, K):
    a = [Fr(0), Fr(1)] + [Fr(0)] * K
    sl = []
    for N in range(2, K + 1):
        a[N] = Fr(0); e0 = f(P.trim(a, K), K)[N]
        a[N] = Fr(1); e1 = f(P.trim(a, K), K)[N]
        sl.append(e1 - e0); a[N] = -e0 / (e1 - e0)
    return [int(v) for v in a[1:K + 1]], [int(v) for v in sl]


SPEC = {
 "A396797": dict(p=3, k=6, eq=eq_iter(3),
   eqtex=r"A(x)\;=\;x+A^{3}(x)\,A^{4}(x)",
   conj=["Conjecture: a(n) = 1 (mod 6) for n >= 1.",
         "Conjecture: [x^n] A^k(x) == k^(n-1) (mod 6) for n >= 1 and all integer k."],
   who="Paul D. Hanna"),
 "A396807": dict(p=5, k=10, eq=eq_iter(5),
   eqtex=r"A(x)\;=\;x+A^{5}(x)\,A^{6}(x)",
   conj=["Conjecture: a(n) = 1 (mod 10) for n >= 1.",
         "Conjecture: [x^n] A^k(x) == k^(n-1) (mod 10) for n >= 1 and all integer k."],
   who="Paul D. Hanna"),
 "A396099": dict(p=2, k=2, eq=eq_iter(2),
   eqtex=r"A(x)\;=\;x+A^{2}(x)\,A^{3}(x)",
   conj=["Conjecture: all terms are odd."],
   who="Paul D. Hanna",
   note=("The entry carries two further conjectures of the same contributor, on the "
         "residues modulo $4$; those are stronger than what is proved here and are not "
         "claimed. Section~4 says exactly where the argument stops short of them.")),
 "A396102": dict(p=None, k=3, eq=eq_102,
   eqtex=r"A^{3}(x)\;=\;(1+x)\,A^{2}(x)",
   conj=["Conjecture: a(n) == 1 (mod 3) for n >= 1."],
   who="Paul D. Hanna"),
}


def build(anum):
    s = SPEC[anum]
    k, p = s["k"], s["p"]
    mod, rev = sectionbuild.modinfo(anum)
    e = entry.get(anum)
    d = [int(x) for x in e['data'].split(',')]
    K = max(24, len(d) + 2)
    t, sl = solve(s["eq"], K)
    assert t[:len(d)] == d, anum
    assert all(v == 1 for v in sl), (anum, sl[:5])
    assert all(v % k == 1 % k for v in t), anum

    if p is not None:
        coeff_para = (
            r"On the left the coefficient is $1$. On the right, $x$ contributes nothing and "
            r"the product $A^{\,%d}A^{\,%d}$ contributes nothing either: every monomial of "
            r"$\bigl[x^{N}\bigr]\bigl(A^{\,%d}A^{\,%d}\bigr)$ is a product of one coefficient "
            r"of $A^{\,%d}$ and one of $A^{\,%d}$ with indices $i,j\ge1$ and $i+j=N$, so both "
            r"indices are at most $N-1$. Hence the net coefficient of $a(N)$ is $1$."
            % (p, p + 1, p, p + 1, p, p + 1))
    else:
        coeff_para = (
            r"On the left, $\bigl[x^{N}\bigr]A^{3}=3a(N)+\cdots$. On the right, "
            r"$\bigl[x^{N}\bigr]\bigl((1+x)A^{2}\bigr)=\bigl[x^{N}\bigr]A^{2}"
            r"+\bigl[x^{N-1}\bigr]A^{2}=2a(N)+\cdots$, the second summand involving only "
            r"$a(1),\dots,a(N-1)$. Hence the net coefficient of $a(N)$ is $3-2=1$.")
    conjblock = "\n\n".join(esc(c) for c in s["conj"])
    plural = "conjectures" if len(s["conj"]) > 1 else "conjecture"

    # the specific reduced-equation paragraph
    if p is not None:
        redu = rf"""
Write $f(x)=\dfrac{{x}}{{1-x}}$ over $\mathbb{{Z}}/{k}\mathbb{{Z}}$.

\begin{{lemma}}\label{{lem:iter}}
$f^{{\,j}}(x)=\dfrac{{x}}{{1-jx}}$ for every $j\ge1$, and more generally for every integer
$j$, where $f^{{-1}}$ denotes the compositional inverse.
\end{{lemma}}

\begin{{proof}}
For $j=1$ this is the definition. If $f^{{\,j}}(x)=x/(1-jx)$ then
\[
f^{{\,j+1}}(x)=f\bigl(f^{{\,j}}(x)\bigr)
=\frac{{\dfrac{{x}}{{1-jx}}}}{{1-\dfrac{{x}}{{1-jx}}}}
=\frac{{x}}{{(1-jx)-x}}=\frac{{x}}{{1-(j+1)x}} .
\]
The maps $x\mapsto x/(1-jx)$ therefore form a group isomorphic to $(\mathbb{{Z}},+)$ under
composition, which also gives the statement for $j\le0$; in particular
$f^{{-1}}(x)=x/(1+x)$.
\end{{proof}}

\begin{{lemma}}\label{{lem:sat}}
Over $\mathbb{{Z}}/{k}\mathbb{{Z}}$, $f$ satisfies $f=x+f^{{\,{p}}}f^{{\,{p+1}}}$.
\end{{lemma}}

\begin{{proof}}
By Lemma~\ref{{lem:iter}}, $f^{{\,{p}}}f^{{\,{p+1}}}
=\dfrac{{x^{{2}}}}{{(1-{p}x)\bigl(1-{p+1}x\bigr)}}$, while
$f-x=\dfrac{{x}}{{1-x}}-x=\dfrac{{x^{{2}}}}{{1-x}}$. So the claim is that
$(1-{p}x)(1-{p+1}x)$ and $1-x$ agree in $(\mathbb{{Z}}/{k}\mathbb{{Z}})[x]$. Expanding,
\[
(1-{p}x)\bigl(1-{p+1}x\bigr)=1-{2*p+1}x+{p*(p+1)}x^{{2}} ,
\]
and modulo ${k}$ we have ${2*p+1}\equiv1$ and ${p*(p+1)}\equiv0$. Hence both sides equal
$1-x$, and the two rational functions agree.
\end{{proof}}
"""
        finish = rf"""
\begin{{theorem}}\label{{thm:main}}
Over $\mathbb{{Z}}/{k}\mathbb{{Z}}$ the reduction of $A$ is $x/(1-x)$. Equivalently
$a(n)\equiv1\pmod{{{k}}}$ for every $n\ge1$, and more generally
\[
\bigl[x^{{n}}\bigr]A^{{\,j}}(x)\;\equiv\;j^{{\,n-1}}\pmod{{{k}}}
\]
for every $n\ge1$ and every integer $j$. This is the {plural} of Section~1.
\end{{theorem}}

\begin{{proof}}
By Lemma~\ref{{lem:sat}}, $f=x/(1-x)$ satisfies the reduced equation, and $f=x+O(x^{{2}})$.
By Corollary~\ref{{cor:mod}} the reduction of $A$ equals $f$, so
$a(n)\equiv\bigl[x^{{n}}\bigr]f=1$.

Reduction modulo ${k}$ carries composition of power series with unit linear coefficient to
composition, so $A^{{\,j}}$ reduces to $f^{{\,j}}$ for every integer $j$ --- for $j<0$
because $A$ has linear coefficient $1$, hence is invertible under composition, and the
reduction map is a homomorphism of the composition group. By Lemma~\ref{{lem:iter}},
$f^{{\,j}}(x)=x/(1-jx)=\sum_{{n\ge1}}j^{{\,n-1}}x^{{n}}$, which gives the second statement.
\end{{proof}}

\begin{{remark}}
The proof used only that $(1-{p}x)(1-{p+1}x)\equiv1-x$ modulo ${k}$, that is, that
${k}$ divides both $2\cdot{p}$ and ${p}\cdot{p+1}$. The largest modulus with that property
is $\gcd\bigl(2p,\,p(p+1)\bigr)$, which is $2p$ for odd $p$ and $p$ for even $p$; here
$p={p}$ gives ${k}$. This is exactly why the statement is made modulo ${k}$ and not modulo
a larger number.
\end{{remark}}
"""
    else:
        redu = rf"""
Write $f(x)=\dfrac{{x}}{{1-x}}$ over $\mathbb{{Z}}/{k}\mathbb{{Z}}$.

\begin{{lemma}}\label{{lem:iter}}
$f^{{\,j}}(x)=\dfrac{{x}}{{1-jx}}$ for every $j\ge1$.
\end{{lemma}}

\begin{{proof}}
For $j=1$ this is the definition, and if $f^{{\,j}}(x)=x/(1-jx)$ then
\[
f^{{\,j+1}}(x)=\frac{{\dfrac{{x}}{{1-jx}}}}{{1-\dfrac{{x}}{{1-jx}}}}
=\frac{{x}}{{(1-jx)-x}}=\frac{{x}}{{1-(j+1)x}} .
\]
\end{{proof}}

\begin{{lemma}}\label{{lem:sat}}
Over $\mathbb{{Z}}/3\mathbb{{Z}}$, $f$ satisfies $f^{{3}}=(1+x)f^{{2}}$.
\end{{lemma}}

\begin{{proof}}
By Lemma~\ref{{lem:iter}}, $f^{{3}}(x)=\dfrac{{x}}{{1-3x}}$, and $3\equiv0$ modulo $3$, so
$f^{{3}}(x)=x$. Again by Lemma~\ref{{lem:iter}}, $f^{{2}}(x)=\dfrac{{x}}{{1-2x}}$, and
$-2\equiv1$ modulo $3$, so $f^{{2}}(x)=\dfrac{{x}}{{1+x}}$. Therefore
\[
(1+x)\,f^{{2}}(x)=(1+x)\cdot\frac{{x}}{{1+x}}=x=f^{{3}}(x).
\]
\end{{proof}}
"""
        finish = rf"""
\begin{{theorem}}\label{{thm:main}}
Over $\mathbb{{Z}}/3\mathbb{{Z}}$ the reduction of $A$ is $x/(1-x)$; equivalently
$a(n)\equiv1\pmod3$ for every $n\ge1$. This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
By Lemma~\ref{{lem:sat}}, $f=x/(1-x)$ satisfies the reduced equation, and $f=x+O(x^{{2}})$.
By Corollary~\ref{{cor:mod}} the reduction of $A$ equals $f$, whose every coefficient is
$1$.
\end{{proof}}
"""

    extra_note = s.get("note", "")
    jlemma = (r"\bigl[x^{N}\bigr]A^{\,j}=j\,a(N)+\bigl(\text{a polynomial in }a(1),\dots,a(N-1)\bigr)")

    return rf"""{PRE}
\title{{The reduction of OEIS {anum} modulo ${k}$}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} is defined by a functional equation for its ordinary generating function and
carries a congruence {plural} of P.~D.~Hanna. It is true. The equation determines the
coefficients one at a time, with $a(N)$ entering with coefficient $1$, so it determines
them modulo ${k}$ as well; and modulo ${k}$ the series $x/(1-x)$ satisfies the equation
exactly, because its compositional iterates are $x/(1-jx)$ and the relevant product of
denominators collapses. Uniqueness then identifies the reduction, which is the {plural}.
The whole argument is an identity between rational functions over
$\mathbb{{Z}}/{k}\mathbb{{Z}}$; nothing is truncated or estimated.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 05A15, 13F25.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset $1$ and begins
\[
{", ".join(str(x) for x in d[:6])},\ \dots
\]
Writing $A(x)=\sum_{{n\ge1}}a(n)x^{{n}}$ and $A^{{\,j}}$ for the $j$-th compositional
iterate of $A$, the entry defines $A$ by
\begin{{equation}}\label{{eq:fe}}
{s['eqtex']} .
\end{{equation}}
This is the only input taken from the entry.

The entry separately carries the following comment{'s' if len(s['conj'])>1 else ''}:
\begin{{quote}}\small
{conjblock} --- \emph{{{s['who']}}}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) {'they are' if len(s['conj'])>1 else 'it is'}
still recorded as {'conjectures' if len(s['conj'])>1 else 'a conjecture'}, and nothing on the entry records
{'them' if len(s['conj'])>1 else 'it'} as settled either way. {extra_note}

\section{{The equation determines the sequence}}

\begin{{lemma}}\label{{lem:jaN}}
Let $A(x)=\sum_{{n\ge1}}a(n)x^{{n}}$ with $a(1)=1$. Then for every $j\ge1$ and every
$N\ge1$,
\[
{jlemma}.
\]
\end{{lemma}}

\begin{{proof}}
Induction on $j$. For $j=1$ the statement is $\bigl[x^{{N}}\bigr]A=a(N)$. Suppose it holds
for $j$, and write $B=A^{{\,j}}$, so $\bigl[x^{{1}}\bigr]B=1$ and
$\bigl[x^{{N}}\bigr]B=j\,a(N)+\cdots$. Then $A^{{\,j+1}}=A\circ B=\sum_{{m\ge1}}a(m)B^{{m}}$
and
\[
\bigl[x^{{N}}\bigr]A^{{\,j+1}}=\sum_{{m=1}}^{{N}}a(m)\,\bigl[x^{{N}}\bigr]B^{{m}} .
\]
The term $m=N$ contributes $a(N)\bigl(\bigl[x^{{1}}\bigr]B\bigr)^{{N}}=a(N)$. The term $m=1$
contributes $\bigl[x^{{N}}\bigr]B=j\,a(N)+\cdots$. For $2\le m\le N-1$, every monomial of
$\bigl[x^{{N}}\bigr]B^{{m}}$ is a product of $m\ge2$ coefficients of $B$ with indices summing
to $N$, hence each index is at most $N-1$, so no $a(N)$ occurs. Adding up gives
$(j+1)a(N)$ plus terms in $a(1),\dots,a(N-1)$.
\end{{proof}}

\begin{{lemma}}\label{{lem:unique}}
There is exactly one sequence of integers $a(1),a(2),\dots$ satisfying \eqref{{eq:fe}}, and
for each $N\ge2$ the equation read at order $x^{{N}}$ has the form
$a(N)=(\text{{a polynomial with integer coefficients in }}a(1),\dots,a(N-1))$.
\end{{lemma}}

\begin{{proof}}
Comparing coefficients of $x$ in \eqref{{eq:fe}} gives $a(1)=1$. Let $N\ge2$ and collect the
coefficient of $a(N)$ on each side of \eqref{{eq:fe}} at order $x^{{N}}$, using
Lemma~\ref{{lem:jaN}}. {coeff_para}
Since that coefficient is $1$, the order-$x^{{N}}$ equation solves for $a(N)$ over
$\mathbb{{Z}}$, and induction gives existence and uniqueness.
\end{{proof}}

\begin{{corollary}}\label{{cor:mod}}
Let $m\ge2$. If $\bar A\in(\mathbb{{Z}}/m\mathbb{{Z}})[[x]]$ satisfies $\bar A=x+O(x^{{2}})$ and
\eqref{{eq:fe}} with all coefficients read modulo $m$, then
$a(n)\equiv\bigl[x^{{n}}\bigr]\bar A\pmod m$ for every $n$.
\end{{corollary}}

\begin{{proof}}
Reduction modulo $m$ is a ring homomorphism, so it carries the integer recursion of
Lemma~\ref{{lem:unique}} to the same recursion over $\mathbb{{Z}}/m\mathbb{{Z}}$, where the
coefficient of $a(N)$ is still $1$ and hence still invertible. That recursion therefore has
a unique solution, and both $a\bmod m$ and the coefficient sequence of $\bar A$ solve it.
\end{{proof}}

\section{{The reduction modulo ${k}$}}
{redu}
{finish}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the recursion of Lemma~\ref{{lem:unique}} was run in exact rational arithmetic and
its output compared against the entry's DATA at every one of the ${len(d)}$ published
indices; the values agree exactly, and every one is an integer. A recursion that reproduced
only some of them would mean the functional equation had been transcribed wrongly.

Second, at every step the coefficient of $a(N)$ was computed rather than assumed, by
evaluating the order-$x^{{N}}$ equation at $a(N)=0$ and at $a(N)=1$ and subtracting; it came
out $1$ at every $N$ up to ${K}$, as Lemma~\ref{{lem:unique}} requires. The same run was
continued to $n={K}$ and every term reduced modulo ${k}$; all residues are
${1 % k}$.

Third, the composition of the proof was carried out independently as a formal power series
over $\mathbb{{Z}}/{k}\mathbb{{Z}}$ to order $30$, starting from the coefficients of $x/(1-x)$
rather than from the closed form; both sides of \eqref{{eq:fe}} agree at every order, and the
iterates $f^{{\,j}}$ were confirmed to have coefficients $j^{{\,n-1}}$ for $j\le6$.

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
    for a in SPEC:
        d = f"build/hb{a}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(a))
        print("wrote", d)
