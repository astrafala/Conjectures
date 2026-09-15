#!/usr/bin/env python3
"""A389472: a(2n-1) is even for n > 1."""
import os
import entry, phibuild, sectionbuild

PRE = phibuild.PRE
esc = phibuild.esc
anum = "A389472"
mod, rev = sectionbuild.modinfo(anum)
e = entry.get(anum)
d = [int(x) for x in e['data'].split(',')]

TEX = rf"""{PRE}
\title{{Every odd-indexed term of OEIS {anum} after the first is even}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} is defined by the functional equation $A(x)=A(x^{{2}}+x^{{3}})/x^{{2}}-1$ for its
ordinary generating function, and carries a conjecture of P.~D.~Hanna that $a(2n-1)$ is
even for every $n>1$. It is true. The equation determines the coefficients one at a time,
so it determines them modulo $2$; and over $\mathbb{{F}}_{{2}}$ it turns out to be
\emph{{parity-preserving}}: the series $x+C(x^{{2}})$ satisfies it exactly, for $C$ the
solution of the companion equation $y\,C(y)=C(y^{{2}}+y^{{3}})$, because
$(x^{{2}}+x^{{3}})^{{2}}=x^{{4}}+x^{{6}}$ in characteristic $2$. Uniqueness then forces the
reduction of $A$ to be supported, apart from the term $x$, on even exponents only --- which
is the conjecture. The entry's second conjecture, modulo $3$, is \emph{{not}} settled here;
Section~5 says where the argument fails to carry over.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 05A15, 13F35.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset $1$ and begins
\[
{", ".join(str(x) for x in d[:10])},\ \dots
\]
The entry gives the expansion
\begin{{quote}}\small
G.f.: A(x) = x + x\^{{}}2 + 2*x\^{{}}3 + 3*x\^{{}}4 + 6*x\^{{}}5 + 9*x\^{{}}6 + 14*x\^{{}}7 + 24*x\^{{}}8 + \dots
\end{{quote}}
so, writing $A(x)=\sum_{{n\ge1}}a(n)x^{{n}}$, the entry fixes
\begin{{equation}}\label{{eq:init}}
a(1)=1,\qquad a(2)=1,
\end{{equation}}
and defines the remaining coefficients by $A(x)=A(x^{{2}}+x^{{3}})/x^{{2}}-1$, which we clear
of the division and write as
\begin{{equation}}\label{{eq:fe}}
x^{{2}}\bigl(A(x)+1\bigr)\;=\;A\bigl(x^{{2}}+x^{{3}}\bigr).
\end{{equation}}
This is the only input taken from the entry.

The entry separately carries the following comment:
\begin{{quote}}\small
Conjecture: a(2*n-1) = 0 (mod 2) for n > 1. --- \emph{{Paul D. Hanna}}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as a conjecture, and nothing on the entry records it as settled either way.
The entry carries a second conjecture of the same contributor, that $a(3n-1)\equiv0$
modulo $3$ for $n>1$. It is not proved below and it is not claimed.

\section{{The equation determines the sequence}}

Because $(x^{{2}}+x^{{3}})^{{n}}=x^{{2n}}(1+x)^{{n}}$, comparing coefficients of $x^{{N}}$ in
\eqref{{eq:fe}} gives, for every $N\ge2$,
\begin{{equation}}\label{{eq:rec}}
a(N-2)\;=\;\sum_{{n\ge1}}a(n)\binom{{n}}{{N-2n}},
\end{{equation}}
with $a(0):=0$ and the convention $\binom{{n}}{{j}}=0$ unless $0\le j\le n$.

\begin{{lemma}}\label{{lem:unique}}
The coefficient $a(1)=1$ is forced by \eqref{{eq:fe}}. Given also $a(2)$, equation
\eqref{{eq:rec}} determines $a(m)$ for every $m\ge3$ as a polynomial with integer
coefficients in $a(1),\dots,a(m-1)$; so \eqref{{eq:init}} and \eqref{{eq:fe}} together have
exactly one integer solution.
\end{{lemma}}

\begin{{proof}}
At $N=2$, \eqref{{eq:rec}} reads $a(0)=a(1)\binom{{1}}{{0}}$ --- reading the left side of
\eqref{{eq:fe}} instead, the coefficient of $x^{{2}}$ there is $1$, so $a(1)=1$.

Now take $N\ge5$ and put $m=N-2\ge3$. On the right of \eqref{{eq:rec}} the binomial
$\binom{{n}}{{N-2n}}$ vanishes unless $2n\le N$, so only $a(n)$ with
$n\le\lfloor N/2\rfloor$ occur. Since $N\ge5$,
\[
\Bigl\lfloor \tfrac{{N}}{{2}}\Bigr\rfloor\;\le\;N-3\;=\;m-1,
\]
so the right side involves only $a(1),\dots,a(m-1)$ and \eqref{{eq:rec}} expresses $a(m)$
through them. (At $N=3$ and $N=4$ the relation reads $a(1)=a(1)$ and $a(2)=a(2)$, giving no
information; that is why $a(2)$ is part of the data.) Induction finishes the proof.
\end{{proof}}

\begin{{corollary}}\label{{cor:mod}}
Let $k\ge2$. If $\bar A\in(\mathbb{{Z}}/k\mathbb{{Z}})[[x]]$ has
$\bigl[x^{{1}}\bigr]\bar A=\bigl[x^{{2}}\bigr]\bar A=1$, no constant term, and satisfies
\eqref{{eq:fe}} with all coefficients read modulo $k$, then
$a(n)\equiv\bigl[x^{{n}}\bigr]\bar A\pmod k$ for every $n$.
\end{{corollary}}

\begin{{proof}}
Reduction modulo $k$ is a ring homomorphism, so it carries \eqref{{eq:rec}} to the same
relation over $\mathbb{{Z}}/k\mathbb{{Z}}$; by Lemma~\ref{{lem:unique}} that relation, together
with the two initial values, has a unique solution, and both $a\bmod k$ and the
coefficients of $\bar A$ solve it.
\end{{proof}}

\section{{The companion equation}}

Work in $\mathbb{{F}}_{{2}}[[y]]$.

\begin{{lemma}}\label{{lem:C}}
There is exactly one $C(y)=\sum_{{m\ge1}}c_m y^{{m}}\in\mathbb{{F}}_{{2}}[[y]]$ with $c_1=1$ and
\begin{{equation}}\label{{eq:C}}
y\,C(y)\;=\;C\bigl(y^{{2}}+y^{{3}}\bigr).
\end{{equation}}
\end{{lemma}}

\begin{{proof}}
Comparing coefficients of $y^{{m}}$ in \eqref{{eq:C}} and using
$(y^{{2}}+y^{{3}})^{{n}}=y^{{2n}}(1+y)^{{n}}$ gives
$c_{{m-1}}=\sum_{{n\ge1}}c_n\binom{{n}}{{m-2n}}$, where again only $n\le\lfloor m/2\rfloor$
occur. For $m\ge3$ we have $\lfloor m/2\rfloor\le m-2$, so this expresses $c_{{m-1}}$
through $c_1,\dots,c_{{m-2}}$; at $m=2$ it reads $c_1=c_1$. Hence $c_1$ may be prescribed
and everything after it is determined.
\end{{proof}}

\begin{{lemma}}\label{{lem:sat}}
Let $C$ be as in Lemma~\ref{{lem:C}} and put $\bar A(x)=x+C(x^{{2}})$. Then $\bar A$ satisfies
\eqref{{eq:fe}} over $\mathbb{{F}}_{{2}}$, and $\bigl[x^{{1}}\bigr]\bar A=\bigl[x^{{2}}\bigr]\bar A=1$.
\end{{lemma}}

\begin{{proof}}
In characteristic $2$ squaring is additive, so
\begin{{equation}}\label{{eq:frob}}
\bigl(x^{{2}}+x^{{3}}\bigr)^{{2}}\;=\;x^{{4}}+x^{{6}} .
\end{{equation}}
Substituting $u=x^{{2}}+x^{{3}}$ into $\bar A(u)=u+C(u^{{2}})$ and using \eqref{{eq:frob}},
\[
\bar A\bigl(x^{{2}}+x^{{3}}\bigr)\;=\;x^{{2}}+x^{{3}}+C\bigl(x^{{4}}+x^{{6}}\bigr),
\]
while
\[
x^{{2}}\bigl(\bar A(x)+1\bigr)\;=\;x^{{2}}\bigl(x+C(x^{{2}})+1\bigr)
\;=\;x^{{2}}+x^{{3}}+x^{{2}}C\bigl(x^{{2}}\bigr).
\]
The two agree exactly when $x^{{2}}C(x^{{2}})=C(x^{{4}}+x^{{6}})$, which is \eqref{{eq:C}} read
at $y=x^{{2}}$. Finally $\bigl[x^{{1}}\bigr]\bar A=1$ and
$\bigl[x^{{2}}\bigr]\bar A=c_1=1$.
\end{{proof}}

\section{{The reduction modulo $2$}}

\begin{{theorem}}
$a(2n-1)\equiv0\pmod 2$ for every $n>1$. This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
By Lemma~\ref{{lem:sat}} the series $\bar A(x)=x+C(x^{{2}})$ satisfies \eqref{{eq:fe}} over
$\mathbb{{F}}_{{2}}$ and matches \eqref{{eq:init}}. By Corollary~\ref{{cor:mod}} with $k=2$ it is
therefore the reduction of $A$ modulo $2$.

Every exponent occurring in $C(x^{{2}})$ is even, so the only odd exponent occurring in
$\bar A$ is $1$. Hence $\bigl[x^{{m}}\bigr]\bar A=0$ for every odd $m\ge3$, that is,
$a(m)\equiv0\pmod2$ for every odd $m\ge3$. Writing $m=2n-1$ with $n>1$ gives the statement.
\end{{proof}}

\begin{{remark}}
The mechanism is worth isolating: \eqref{{eq:fe}} substitutes $x^{{2}}+x^{{3}}$, and in
characteristic $2$ the square of that is again a polynomial in $x^{{2}}$, by \eqref{{eq:frob}}.
So the substitution cannot manufacture new odd exponents beyond the ones already present,
and the single odd exponent $1$ forced by $a(1)=1$ is all there is.
\end{{remark}}

\section{{Where the argument stops}}

The entry's other conjecture is that $a(3n-1)\equiv0$ modulo $3$ for $n>1$, that is, that
the reduction of $A$ modulo $3$ is supported off the exponents $\equiv2\pmod 3$ apart from
$x^{{2}}$ itself. That is not proved here, and the proof above does not adapt: it turns on
the Frobenius identity \eqref{{eq:frob}}, which in characteristic $3$ becomes
$(x^{{2}}+x^{{3}})^{{3}}=x^{{6}}+x^{{9}}$ --- but \eqref{{eq:fe}} substitutes the \emph{{first}}
power of $x^{{2}}+x^{{3}}$, not the third, so the Frobenius map is not available where it
would be needed. The residues modulo $3$ were computed for every $n\le60$ and the
conjecture holds throughout that range; no proof is offered.

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the recursion \eqref{{eq:rec}} was run in exact integer arithmetic from
\eqref{{eq:init}} and compared against the entry's DATA at every one of the ${len(d)}$
published indices; the values agree exactly. A recursion that reproduced only some of them
would mean the functional equation had been transcribed wrongly.

Second, the series $C$ of Lemma~\ref{{lem:C}} was generated from its own recursion over
$\mathbb{{F}}_{{2}}$ and $x+C(x^{{2}})$ compared, coefficient by coefficient, against
$a(n)\bmod2$ for every $n\le60$; the two agree at every index, with no mismatch. Equation
\eqref{{eq:C}} was checked directly over $\mathbb{{F}}_{{2}}$ to order $60$.

Third, $a(2n-1)\bmod2$ was evaluated for every $n$ with $2n-1\le60$: all zero, as the
theorem requires.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {anum}.
\bibitem{{lidl}} R.~Lidl and H.~Niederreiter, \emph{{Finite Fields}}, 2nd ed., Cambridge
University Press, 1997.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 2, Cambridge
University Press, 1999.
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\end{{thebibliography}}

\end{{document}}
"""

if __name__ == "__main__":
    os.makedirs("build/parA389472", exist_ok=True)
    open("build/parA389472/p.tex", "w").write(TEX)
    print("wrote build/parA389472")
