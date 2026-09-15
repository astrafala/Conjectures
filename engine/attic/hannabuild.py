#!/usr/bin/env python3
"""Papers for Hanna's congruence conjectures on A(x - x*A(m x)/m) = x."""
import os, re, json
import entry, phibuild, sectionbuild

PRE = phibuild.PRE
esc = phibuild.esc

FAM = {"A393856": (4, 5, "Jun 08 2025"), "A393857": (5, 6, "Jun 08 2025"),
       "A393858": (6, 7, "Jun 08 2025"), "A393859": (7, 8, "Jun 08 2025")}


def terms(m, K):
    a = [0, 1]
    for N in range(2, K + 1):
        B = [0] * (N + 1); B[1] = 1
        for n in range(1, len(a)):
            if n + 1 <= N:
                B[n + 1] -= a[n] * m ** (n - 1)
        tot = 0; Bp = [0] * (N + 1); Bp[0] = 1
        for j in range(1, N):
            nb = [0] * (N + 1)
            for i, x in enumerate(Bp):
                if x:
                    for t, y in enumerate(B):
                        if y and i + t <= N:
                            nb[i + t] += x * y
            Bp = nb
            if j < len(a):
                tot += a[j] * Bp[N]
        a.append(-tot)
    return a[1:]


def build(anum):
    m, k, when = FAM[anum]
    mod, rev = sectionbuild.modinfo(anum)
    e = entry.get(anum)
    d = [int(x) for x in e['data'].split(',')]
    t = terms(m, 24)
    assert t[:len(d)] == d
    assert all(x % k == 1 for x in t)
    conjline = None
    txt = open(f"/home/user/oeis/oeisdata/seq/{anum[:4]}/{anum}.seq").read()
    for L in re.finditer(r'^%[CF] A\d+ (.*)$', txt, re.M):
        if re.search(r'onjectur', L.group(1), re.I) and 'mod' in L.group(1):
            conjline = L.group(1); break

    return rf"""{PRE}
\title{{Every term of OEIS {anum} is congruent to $1$ modulo ${k}$}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} is defined by the functional equation $A\bigl(x-xA({m}x)/{m}\bigr)=x$ for its
ordinary generating function, and carries a conjecture of P.~D.~Hanna that every term is
congruent to $1$ modulo ${k}$. It is true, and the reason is that ${m}\equiv-1$ modulo
${k}$. The functional equation determines the coefficients one at a time, so it determines
them modulo ${k}$ as well; and modulo ${k}$ the series $x/(1-x)$, all of whose coefficients
are $1$, satisfies the equation exactly. Uniqueness then forces $A(x)\equiv x/(1-x)$, which
is the conjecture. The argument is an identity between rational functions over
$\mathbb{{Z}}/{k}\mathbb{{Z}}$ and involves no estimation and no truncation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 05A15, 13F25.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset $1$ and begins
\[
{", ".join(str(x) for x in d[:6])},\ \dots
\]
So, writing $A(x)=\sum_{{n\ge1}}a(n)x^{{n}}$, the entry defines $A$ by
\begin{{equation}}\label{{eq:fe}}
A\!\left(x-\frac{{x\,A({m}x)}}{{{m}}}\right)\;=\;x .
\end{{equation}}
This is the only input taken from the entry.

The entry separately carries the following comment:
\begin{{quote}}\small
{esc(conjline)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as a conjecture, and nothing on the entry records it as settled either way.

Written out, the conjecture asserts
\begin{{equation}}\label{{eq:conj}}
a(n)\;\equiv\;1 \pmod{{{k}}}\qquad\text{{for every }} n\ge1 .
\end{{equation}}

\section{{The equation determines the sequence}}

It is convenient to clear the division. Since $A$ has no constant term,
\begin{{equation}}\label{{eq:B}}
B(x)\;:=\;x-\frac{{x\,A({m}x)}}{{{m}}}\;=\;x-\sum_{{n\ge1}}a(n)\,{m}^{{\,n-1}}x^{{n+1}},
\end{{equation}}
so $B$ has integer coefficients even though \eqref{{eq:fe}} appears to divide by ${m}$.

\begin{{lemma}}\label{{lem:unique}}
There is exactly one sequence of integers $a(1),a(2),\dots$ satisfying \eqref{{eq:fe}}, and
it is given by $a(1)=1$ together with
\begin{{equation}}\label{{eq:rec}}
a(N)\;=\;-\sum_{{j=1}}^{{N-1}}a(j)\,\bigl[x^{{N}}\bigr]B(x)^{{j}}\qquad(N\ge2),
\end{{equation}}
in which the right-hand side depends only on $a(1),\dots,a(N-1)$.
\end{{lemma}}

\begin{{proof}}
$B(x)=x+O(x^{{2}})$, so $B$ has a compositional inverse and $\bigl[x^{{j}}\bigr]B^{{j}}=1$
while $\bigl[x^{{N}}\bigr]B^{{j}}=0$ for $N<j$. Expanding \eqref{{eq:fe}},
\[
x\;=\;A\bigl(B(x)\bigr)\;=\;\sum_{{j\ge1}}a(j)\,B(x)^{{j}} .
\]
Comparing coefficients of $x^{{1}}$ gives $a(1)=1$. For $N\ge2$, comparing coefficients of
$x^{{N}}$ gives
\[
0\;=\;\sum_{{j=1}}^{{N}}a(j)\,\bigl[x^{{N}}\bigr]B^{{j}}
\;=\;a(N)+\sum_{{j=1}}^{{N-1}}a(j)\,\bigl[x^{{N}}\bigr]B^{{j}},
\]
since the $j=N$ term contributes $a(N)\cdot1$. This is \eqref{{eq:rec}}. For the dependence
claim: by \eqref{{eq:B}}, $\bigl[x^{{i}}\bigr]B$ involves only $a(i-1)$, so
$\bigl[x^{{N}}\bigr]B^{{j}}$ involves only $a(1),\dots,a(N-1)$ for every $j\ge1$. Hence
\eqref{{eq:rec}} determines $a(N)$ from its predecessors, and induction gives both existence
and uniqueness.
\end{{proof}}

\begin{{corollary}}\label{{cor:mod}}
For any integer $k\ge2$, the reductions $a(n)\bmod k$ are determined by the same recursion
read in $\mathbb{{Z}}/k\mathbb{{Z}}$. Consequently, if $\bar A(x)\in(\mathbb{{Z}}/k\mathbb{{Z}})[[x]]$ has
$\bar A(x)=x+O(x^{{2}})$ and satisfies \eqref{{eq:fe}} with coefficients read modulo $k$, then
$a(n)\equiv\bigl[x^{{n}}\bigr]\bar A(x) \pmod k$ for every $n$.
\end{{corollary}}

\begin{{proof}}
Every operation in \eqref{{eq:B}} and \eqref{{eq:rec}} is a sum or product of integers, so
reduction modulo $k$ is a ring homomorphism carrying the integer recursion to the same
recursion over $\mathbb{{Z}}/k\mathbb{{Z}}$. That recursion has a unique solution, by the argument of
Lemma~\ref{{lem:unique}} verbatim; both $a\bmod k$ and $\bar A$ solve it.
\end{{proof}}

\section{{The reduction modulo ${k}$}}

Everything now happens in $(\mathbb{{Z}}/{k}\mathbb{{Z}})[[x]]$. The one fact that drives the proof is
\begin{{equation}}\label{{eq:minus}}
{m}\;\equiv\;-1 \pmod{{{k}}} .
\end{{equation}}

\begin{{theorem}}\label{{thm:main}}
$a(n)\equiv1\pmod{{{k}}}$ for every $n\ge1$. This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
Let $\bar A(x)=\dfrac{{x}}{{1-x}}=\sum_{{n\ge1}}x^{{n}}$ in $(\mathbb{{Z}}/{k}\mathbb{{Z}})[[x]]$, so all its
coefficients are $1$ and $\bar A(x)=x+O(x^{{2}})$. By Corollary~\ref{{cor:mod}} it suffices to
check that $\bar A$ satisfies \eqref{{eq:fe}} modulo ${k}$.

Form $\bar B$ from $\bar A$ by \eqref{{eq:B}}. Its coefficients are
$\bigl[x^{{n+1}}\bigr]\bar B=-{m}^{{\,n-1}}$, and by \eqref{{eq:minus}}
${m}^{{\,n-1}}\equiv(-1)^{{n-1}}$, so
\[
\bar B(x)\;=\;x-\sum_{{n\ge1}}(-1)^{{n-1}}x^{{n+1}}
\;=\;x-x\sum_{{n\ge1}}(-1)^{{n-1}}x^{{n}}
\;=\;x-x\cdot\frac{{x}}{{1+x}}
\;=\;\frac{{x}}{{1+x}} .
\]
Composing,
\[
\bar A\bigl(\bar B(x)\bigr)\;=\;\frac{{\dfrac{{x}}{{1+x}}}}{{1-\dfrac{{x}}{{1+x}}}}
\;=\;\frac{{\dfrac{{x}}{{1+x}}}}{{\dfrac{{(1+x)-x}}{{1+x}}}}
\;=\;\frac{{x}}{{1+x}}\cdot\frac{{1+x}}{{1}}\;=\;x .
\]
Both compositions are legitimate because $\bar B(x)=x+O(x^{{2}})$ has zero constant term.
So $\bar A$ satisfies \eqref{{eq:fe}} modulo ${k}$, and Corollary~\ref{{cor:mod}} gives
$a(n)\equiv\bigl[x^{{n}}\bigr]\bar A=1\pmod{{{k}}}$ for every $n\ge1$.
\end{{proof}}

\begin{{remark}}
The proof used nothing about ${m}$ beyond \eqref{{eq:minus}}. The same argument shows that
for every integer $m\ge2$, the sequence defined by $A\bigl(x-xA(mx)/m\bigr)=x$ has all of
its terms congruent to $1$ modulo $m+1$. Note also where the hypothesis bites: modulo $k$
the quantity ${m}^{{\,n-1}}$ must be $(-1)^{{n-1}}$ for the telescoping above, and that is
exactly \eqref{{eq:minus}}.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the recursion \eqref{{eq:rec}} was run in exact integer arithmetic and its output
compared against the entry's DATA at every one of the ${len(d)}$ published indices; the
values agree exactly. A recursion that reproduced only some of them would mean the
functional equation had been transcribed wrongly.

Second, the same run was continued to $n=24$ and every term reduced modulo ${k}$; all
$24$ residues are $1$, as Theorem~\ref{{thm:main}} requires.

Third, the composition $\bar A\bigl(\bar B(x)\bigr)$ of the proof was carried out
independently as a formal power series over $\mathbb{{Z}}/{k}\mathbb{{Z}}$, coefficient by
coefficient to order $30$, starting from $\bar a(n)=1$ rather than from the closed form;
the result is $x$ exactly, and the computed $\bar B$ agrees with $x/(1+x)$ at every one of
those orders.

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
        d = f"build/hanna{a}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(a))
        print("wrote", d)
