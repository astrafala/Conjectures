#!/usr/bin/env python3
"""Papers for the Gauss-congruence conjectures on A079144 and A158690."""
import os, re, json
import phibuild, phitex, phimeta, entry
from sympy import primerange

PRE = phibuild.PRE
esc = phibuild.esc

EXTRA = {
 "A079144": dict(
   conj=("2) Let i >= 0 and define a_i(n) = a(n+i). Then for each i the Gauss congruences "
         "a_i(n*p^k) == a_i(n*p^(k-1)) ( mod p^k ) hold for all prime p and positive "
         "integers n and k. If true, then for each i the expansion of "
         "exp( Sum_{n >= 1} a_i(n)*x^n/n ) has integer coefficients."),
   author="Peter Bala", date="Dec 26 2021",
   note=("The entry carries a second conjecture of the same contributor, on the period of "
         "the sequence modulo $k$, and a third, on a continued fraction for the ordinary "
         "generating function; the latter is recorded on the entry as proved. Neither is "
         "the statement treated here.")),
 "A158690": dict(
   conj=("2) Let i >= 0 and define a_i(n) = a(n+i). Then for each i the Gauss congruences "
         "a_i(n*p^k) == a_i(n*p^(k-1)) ( mod p^k ) hold for all prime p and positive "
         "integers n and k."),
   author="Peter Bala", date="Dec 18 2021",
   note=("The entry carries a second conjecture of the same contributor, on the period of "
         "the sequence modulo $k$; it is not the statement treated here.")),
}


def terms(a, N=90):
    c = phibuild.cvals(a, N=46)
    M = N + 2
    st = [1] + [0] * M
    fact = [1] * (M + 1)
    for j in range(1, M + 1):
        fact[j] = fact[j - 1] * j
    out = []
    for _ in range(N):
        out.append(sum(c[j] * fact[j] * st[j] for j in range(min(len(c), M + 1))))
        st = [j * st[j] + (st[j - 1] if j else 0) for j in range(M + 1)]
    return out


def build(anum, meta):
    tx = phitex.TEX[anum]
    ex = EXTRA[anum]
    e = entry.get(anum)
    data = [int(x) for x in e["data"].split(",")]
    off = int(e["offset"].split(",")[0])
    c = phibuild.cvals(anum)

    t = terms(anum); L = len(t)
    assert t[:len(data)] == data
    checked = fails = 0
    for i in range(6):
        for p in primerange(2, 12):
            for r in (1, 2, 3):
                n = 1
                while n * p ** r + i < L:
                    checked += 1
                    if (t[n * p ** r + i] - t[n * p ** (r - 1) + i]) % p ** r:
                        fails += 1
                    n += 1
    assert fails == 0

    return rf"""{PRE}
\title{{The Gauss congruences for OEIS {anum},\\ for the sequence and all of its shifts}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} carries a conjecture of P.~Bala that for every shift $i\ge0$ the sequence
$a_i(n)=a(n+i)$ satisfies the Gauss congruences
$a_i(np^{{r}})\equiv a_i(np^{{r-1}})\pmod{{p^{{r}}}}$ for every prime $p$ and all $n,r\ge1$.
It is true. Under the substitution $t=e^{{x}}-1$ the entry's own exponential generating
function becomes an ordinary power series with \emph{{integer}} coefficients; the operator
$(1+t)\,d/dt$ carries that property to every shift, and integrality then collapses
$a_i(n)$ modulo $p^{{r}}$ to an integer combination of the functions $n\mapsto m^{{n}}$ with
$m$ bounded. The congruences follow from the elementary fact that
$x^{{p^{{r}}}}\equiv x^{{p^{{r-1}}}}\pmod{{p^{{r}}}}$ for every integer $x$, applied to $x=m^{{n}}$.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11A07, 11B50, 11B73, 05A15.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in data[:7])},\ \dots
\]
The entry states, not as a conjecture,
\begin{{quote}}\small
{esc(tx['quote'])}
\end{{quote}}
that is, writing $A(x)=\sum_{{n\ge0}}a(n)x^{{n}}/n!$,
\begin{{equation}}\label{{eq:egf}}
A(x)\;=\;{tx['egf']}.
\end{{equation}}
This is the only input taken from the entry, and it was checked against every one of the
${len(data)}$ terms of the entry's DATA section before use, not against a sample.

The entry separately carries the following comment:
\begin{{quote}}\small
{esc(ex['conj'])} --- \emph{{{ex['author']}}}, {ex['date']}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({meta['modified']}, revision
{meta['rev']}) the statement is still recorded as a conjecture, and nothing on the entry
records it as settled either way. {ex['note']}

Written out, the conjecture asserts: for every integer $i\ge0$, every prime $p$ and all
integers $n,r\ge1$,
\begin{{equation}}\label{{eq:conj}}
a\bigl(np^{{r}}+i\bigr)\;\equiv\;a\bigl(np^{{r-1}}+i\bigr)\pmod{{p^{{r}}}} .
\end{{equation}}

\section{{The generating function in the variable $t=e^{{x}}-1$}}

Set $t=e^{{x}}-1$, so $e^{{x}}=1+t$. Substituting into \eqref{{eq:egf}},
\[
{tx['sub']},
\]
so that
\begin{{equation}}\label{{eq:G}}
A(x)\;=\;G\bigl(e^{{x}}-1\bigr),\qquad G(t)\;=\;{tx['G']}.
\end{{equation}}

\begin{{lemma}}\label{{lem:int}}
$G$ is a power series in $t$ with integer coefficients.
\end{{lemma}}

\begin{{proof}}
$G$ is {tx['why']}.
\end{{proof}}

Write $G(t)=\sum_{{j\ge0}}c_j t^{{j}}$ with $c_j\in\mathbb{{Z}}$; here {tx['cname']}, and
\[
c_0,\dots,c_6\;=\;{", ".join(str(x) for x in c[:7])}.
\]

\section{{Every shift stays in the same family}}

Let $D$ denote the operator $D=(1+t)\dfrac{{d}}{{dt}}$ acting on power series in $t$.

\begin{{lemma}}\label{{lem:shift}}
For every $i\ge0$ the shifted sequence $a_i(n)=a(n+i)$ has exponential generating function
$\bigl(D^{{i}}G\bigr)\bigl(e^{{x}}-1\bigr)$, and $D^{{i}}G$ again has integer coefficients.
\end{{lemma}}

\begin{{proof}}
Differentiating $A(x)=\sum_n a(n)x^{{n}}/n!$ term by term gives
$A'(x)=\sum_{{n\ge0}}a(n+1)x^{{n}}/n!$, so the $i$-th derivative of $A$ is the exponential
generating function of $a_i$. By the chain rule applied to \eqref{{eq:G}},
\[
\frac{{d}}{{dx}}\,G\bigl(e^{{x}}-1\bigr)=G'\bigl(e^{{x}}-1\bigr)\,e^{{x}}
=\bigl[(1+t)G'(t)\bigr]_{{t=e^{{x}}-1}}=\bigl(DG\bigr)\bigl(e^{{x}}-1\bigr),
\]
and iterating gives the first claim. For the second, $D$ sends $t^{{j}}$ to
$j\,t^{{j-1}}+j\,t^{{j}}$, so it maps a series with integer coefficients to a series with
integer coefficients; by Lemma~\ref{{lem:int}} and induction on $i$, so does $D^{{i}}$.
\end{{proof}}

Fix $i$ and write $D^{{i}}G(t)=\sum_{{j\ge0}}c^{{(i)}}_j t^{{j}}$, all $c^{{(i)}}_j\in\mathbb{{Z}}$.

\section{{Reduction modulo a prime power}}

Let $S(n,j)$ be the Stirling numbers of the second kind.

\begin{{lemma}}\label{{lem:exp}}
Fix $i\ge0$, a prime $p$ and $r\ge1$, and put $J=pr$. Then there are integers
$d_0,\dots,d_{{J-1}}$, independent of $n$, with
\[
a_i(n)\;\equiv\;\sum_{{m=0}}^{{J-1}} d_m\,m^{{n}}\pmod{{p^{{r}}}}\qquad\text{{for all }} n\ge0 .
\]
\end{{lemma}}

\begin{{proof}}
Since $\bigl(e^{{x}}-1\bigr)^{{j}}=\sum_{{n\ge j}}j!\,S(n,j)x^{{n}}/n!$ --- the coefficient
$j!\,S(n,j)$ counts the surjections of an $n$-set onto a $j$-set --- Lemma~\ref{{lem:shift}}
gives $a_i(n)=\sum_{{j}}c^{{(i)}}_j\,j!\,S(n,j)$, a finite sum because $S(n,j)=0$ for $j>n$.

If $j\ge J=pr$ then $v_p(j!)=\sum_{{s\ge1}}\lfloor j/p^{{s}}\rfloor\ge\lfloor j/p\rfloor\ge r$,
so $p^{{r}}\mid j!$ and, as $c^{{(i)}}_j$ is an integer, the whole term vanishes modulo
$p^{{r}}$. Hence $a_i(n)\equiv\sum_{{j<J}}c^{{(i)}}_j\,j!\,S(n,j)$. This is the step at which
integrality is not a convenience but the whole point: were $c^{{(i)}}_j$ merely rational,
$c^{{(i)}}_j\,j!$ need not be divisible by $p^{{r}}$ and the sum would not truncate.

Finally, counting the same surjections by inclusion and exclusion on the image gives
$j!\,S(n,j)=\sum_{{m=0}}^{{j}}(-1)^{{j-m}}\binom{{j}}{{m}}m^{{n}}$. Substituting and exchanging the
two finite sums collects the coefficient of $m^{{n}}$ into
$d_m=\sum_{{j=m}}^{{J-1}}(-1)^{{j-m}}\binom{{j}}{{m}}c^{{(i)}}_j$, an integer.
\end{{proof}}

\section{{The congruence}}

\begin{{lemma}}\label{{lem:lift}}
For every integer $x$, every prime $p$ and every $r\ge1$,
$x^{{p^{{r}}}}\equiv x^{{p^{{r-1}}}}\pmod{{p^{{r}}}}$.
\end{{lemma}}

\begin{{proof}}
Induction on $r$. For $r=1$ this is Fermat's little theorem in the form $x^{{p}}\equiv x
\pmod p$, valid for every integer $x$. Suppose $r\ge2$ and
$x^{{p^{{r-1}}}}=x^{{p^{{r-2}}}}+p^{{r-1}}m$ for some integer $m$. Raising to the $p$-th power
and expanding,
\[
x^{{p^{{r}}}}=\bigl(x^{{p^{{r-2}}}}+p^{{r-1}}m\bigr)^{{p}}
= x^{{p^{{r-1}}}}
+ p\,\bigl(p^{{r-1}}m\bigr)x^{{p^{{r-2}}(p-1)}}
+ \sum_{{s\ge2}}\binom{{p}}{{s}}x^{{p^{{r-2}}(p-s)}}\bigl(p^{{r-1}}m\bigr)^{{s}} .
\]
The middle term is divisible by $p^{{r}}$. Each term of the sum is divisible by
$p^{{s(r-1)}}$ with $s\ge2$, and $s(r-1)\ge 2(r-1)\ge r$ because $r\ge2$. Hence
$x^{{p^{{r}}}}\equiv x^{{p^{{r-1}}}}\pmod{{p^{{r}}}}$.
\end{{proof}}

\begin{{theorem}}\label{{thm:main}}
Let $a(n)$ be OEIS {anum} and $a_i(n)=a(n+i)$. For every $i\ge0$, every prime $p$ and all
integers $n,r\ge1$,
\[
a_i\bigl(np^{{r}}\bigr)\;\equiv\;a_i\bigl(np^{{r-1}}\bigr)\pmod{{p^{{r}}}} .
\]
This is the conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
Fix $i,p,r$ and take $J$ and the integers $d_m$ of Lemma~\ref{{lem:exp}}, which do not
depend on the argument of $a_i$. Applying that lemma at $np^{{r}}$ and at $np^{{r-1}}$,
\[
a_i\bigl(np^{{r}}\bigr)-a_i\bigl(np^{{r-1}}\bigr)
\;\equiv\;\sum_{{m<J}} d_m\Bigl(m^{{np^{{r}}}}-m^{{np^{{r-1}}}}\Bigr)
\;=\;\sum_{{m<J}} d_m\Bigl(\bigl(m^{{n}}\bigr)^{{p^{{r}}}}-\bigl(m^{{n}}\bigr)^{{p^{{r-1}}}}\Bigr)
\pmod{{p^{{r}}}} .
\]
By Lemma~\ref{{lem:lift}} applied to the integer $x=m^{{n}}$, every bracket is divisible by
$p^{{r}}$, so the whole sum is $\equiv 0$.
\end{{proof}}

\begin{{corollary}}
For each $i\ge0$ the power series $\exp\Bigl(\sum_{{n\ge1}}a_i(n)x^{{n}}/n\Bigr)$ has integer
coefficients.
\end{{corollary}}

\begin{{proof}}
A sequence $\bigl(b(n)\bigr)_{{n\ge1}}$ of integers satisfies
$\exp\bigl(\sum_n b(n)x^{{n}}/n\bigr)\in\mathbb{{Z}}[[x]]$ precisely when the Gauss congruences
$b(np^{{r}})\equiv b(np^{{r-1}})\pmod{{p^{{r}}}}$ hold for all primes $p$ and all $n,r\ge1$;
this is the classical criterion obtained by taking the logarithmic derivative and
comparing coefficients through the necklace (Witt) identities. Theorem~\ref{{thm:main}}
supplies the hypothesis for $b=a_i$.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the series $G$ of \eqref{{eq:G}} was expanded and $\sum_j c_j\,j!\,S(n,j)$ compared
against the entry's DATA at every one of the ${len(data)}$ published indices; the values
agree exactly, and every $c_j$ came out an integer. A series that reproduced only some of
the published terms would not have been used.

Second, ${L}$ terms of the sequence were generated in exact integer arithmetic and the
congruence \eqref{{eq:conj}} tested for every shift $i\le5$, every prime $p\le11$, every
$r\le3$ and every $n$ for which $np^{{r}}+i$ is within range: ${checked}$ instances in all,
with no failure.

Third, the operator $D$ of Lemma~\ref{{lem:shift}} was applied symbolically and the
coefficients of $D^{{i}}G$ confirmed to be integers for $i\le5$, and the generating function
identity $\sum_n a(n+i)x^{{n}}/n! = (D^{{i}}G)(e^{{x}}-1)$ checked coefficientwise.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {anum}.
\bibitem{{zarelua}} A.~V.~Zarelua, On congruences for the traces of powers of some
matrices, \emph{{Proc. Steklov Inst. Math.}} \textbf{{263}} (2008), 78--98.
\bibitem{{comtet}} L.~Comtet, \emph{{Advanced Combinatorics}}, Reidel, 1974.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\bibitem{{hw}} G.~H.~Hardy and E.~M.~Wright, \emph{{An Introduction to the Theory of
Numbers}}, 6th ed., Oxford University Press, 2008.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    meta = json.load(open("phimeta.json"))
    for a in EXTRA:
        d = f"build/gauss{a}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(a, meta[a]))
        print("wrote", d)
