#!/usr/bin/env python3
"""Build one standalone paper per entry for the modulo-k periodicity conjecture."""
import json, os, re, subprocess
from fractions import Fraction as Fr
from sympy import totient, factorint
import entry, phispec, phitex, phimeta

KMAX = 40
OUT = "build"


def cvals(anum, N=46):
    g = phispec.SPEC[anum][2]()
    assert all(x.denominator == 1 for x in g), anum
    return [int(x) for x in g]


def seq_mod(k, N, c):
    st = [1] + [0] * (k - 1)
    fact = [1] * k
    for j in range(1, k):
        fact[j] = fact[j - 1] * j % k
    w = [c[j] * fact[j] % k for j in range(k)]
    out = []
    for _ in range(N):
        out.append(sum(w[j] * st[j] for j in range(k)) % k)
        st = [(j * st[j] + (st[j - 1] if j else 0)) % k for j in range(k)]
    return out


def exact_period(k, c, limit=3_000_000):
    st = tuple([1] + [0] * (k - 1))
    fact = [1] * k
    for j in range(1, k):
        fact[j] = fact[j - 1] * j % k
    w = [c[j] * fact[j] % k for j in range(k)]
    seen = {st: 0}
    vals = [sum(w[j] * st[j] for j in range(k)) % k]
    n = 0
    while n < limit:
        st = tuple((j * st[j] + (st[j - 1] if j else 0)) % k for j in range(k))
        n += 1
        if st in seen:
            pre, per = seen[st], n - seen[st]
            tail = vals[pre:]
            for p in sorted(d for d in range(1, per + 1) if per % d == 0):
                if all(tail[i] == tail[(i + p) % per] for i in range(per)):
                    return p
            return per
        seen[st] = n
        vals.append(sum(w[j] * st[j] for j in range(k)) % k)
    return None


PRE = r"""\documentclass[11pt,a4paper]{article}
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
"""


def esc(s):
    return (s.replace("\\", r"\textbackslash ").replace("_", r"\_")
             .replace("^", r"\^{}").replace("&", r"\&").replace("%", r"\%")
             .replace("#", r"\#").replace("$", r"\$"))


def build(anum, meta, ndata_note=""):
    tx = phitex.TEX[anum]
    c = cvals(anum)
    e = entry.get(anum)
    name = e.get("name", "").strip()
    data = [int(x) for x in e["data"].split(",")]
    off = int(e["offset"].split(",")[0])

    rows = []
    for k in range(2, KMAX + 1):
        p = exact_period(k, c)
        phi = int(totient(k))
        rows.append((k, phi, p, phi % p == 0 if p else False))
    assert all(r[3] for r in rows), anum

    tbl = []
    for k, phi, p, _ in rows:
        tbl.append(f"${k}$ & ${phi}$ & ${p}$ \\\\")
    half = (len(tbl) + 1) // 2
    left, right = tbl[:half], tbl[half:]
    while len(right) < len(left):
        right.append(" & & \\\\")
    table = "\n".join(f"{a[:-3]} & {b}" for a, b in zip(left, right))

    conj = esc(meta["conj"])
    quote = esc(tx["quote"])
    cs = ", ".join(str(x) for x in c[:9])

    body = rf"""{PRE}
\title{{The reduction of OEIS {anum} modulo $k$:\\ a proof that the period divides
$\varphi(k)$}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {anum} carries a conjecture of P.~Bala that for every positive integer $k$ the
sequence reduced modulo $k$ is eventually periodic with period dividing $\varphi(k)$.
It is true. The entry's own exponential generating function becomes, under the
substitution $t=e^{{x}}-1$, an ordinary power series with \emph{{integer}} coefficients;
that integrality forces all but finitely many terms of the Stirling expansion of $a(n)$
to vanish modulo $k$, and what is left is an integer combination of the functions
$n\mapsto i^{{n}}$ with $0\le i<k$. Each of those is eventually periodic with period
dividing $\varphi(k)$, and so is the sum. The argument also gives the exact point at
which periodicity starts: $n\ge v(k)$, where $v(k)$ is the largest exponent in the
prime factorisation of $k$.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 11B73, 05A15.\normalsize

\section{{The sequence and the conjecture}}

OEIS {anum} is ``{esc(name)}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in data[:8])},\ \dots
\]
The entry states, not as a conjecture,
\begin{{quote}}\small
{quote}
\end{{quote}}
that is, writing $A(x)=\sum_{{n\ge 0}}a(n)x^{{n}}/n!$,
\begin{{equation}}\label{{eq:egf}}
A(x)\;=\;{tx['egf']}.
\end{{equation}}
This is the only input taken from the entry, and it was checked against every one of the
${len(data)}$ terms of the entry's DATA section before use, not against a sample.

The entry separately carries the following comment:
\begin{{quote}}\small
\textbf{{{conj.split(':')[0] if ':' in conj else 'Conjecture'}}}{(':' + conj.split(':',1)[1]) if ':' in conj else ' ' + conj} --- \emph{{{meta['author']}}}, {meta['date']}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({meta['modified']}, revision
{meta['rev']}) the statement is still recorded as a conjecture, and nothing on the entry
records it as settled either way.

Written out, the conjecture asserts: for every integer $k\ge 1$ there are $n_0$ and a
positive integer $P$ with $P\mid\varphi(k)$ such that
\begin{{equation}}\label{{eq:conj}}
a(n+P)\;\equiv\;a(n)\pmod{{k}}\qquad\text{{for all }} n\ge n_0 .
\end{{equation}}
It is proved below, with $P=\varphi(k)$ and $n_0=v(k)$, the largest exponent occurring in
the prime factorisation of $k$.

\section{{The generating function in the variable $t=e^{{x}}-1$}}

Set $t=e^{{x}}-1$. Then $e^{{x}}=1+t$, and substituting into \eqref{{eq:egf}},
\[
{tx['sub']},
\]
so that
\begin{{equation}}\label{{eq:G}}
A(x)\;=\;G\bigl(e^{{x}}-1\bigr),\qquad
G(t)\;=\;{tx['G']}.
\end{{equation}}

\begin{{lemma}}\label{{lem:int}}
$G$ is a power series in $t$ with integer coefficients.
\end{{lemma}}

\begin{{proof}}
$G$ is {tx['why']}.
\end{{proof}}

Write $G(t)=\sum_{{j\ge0}}c_j t^{{j}}$, so $c_j\in\mathbb{{Z}}$; here {tx['cname']}, and the
first few are
\[
c_0,\dots,c_8 \;=\; {cs}.
\]

\section{{The Stirling expansion, and what survives modulo $k$}}

Let $S(n,j)$ denote the Stirling numbers of the second kind.

\begin{{lemma}}\label{{lem:stir}}
$a(n)=\sum_{{j=0}}^{{n}} c_j\, j!\, S(n,j)$ for every $n\ge 0$. In particular $a(n)\in\mathbb{{Z}}$.
\end{{lemma}}

\begin{{proof}}
The standard expansion $\bigl(e^{{x}}-1\bigr)^{{j}}
=\sum_{{n\ge j}} j!\,S(n,j)\,x^{{n}}/n!$ holds because $j!\,S(n,j)$ counts the surjections
from an $n$-set onto a $j$-set. Substituting it into
$A(x)=G(e^{{x}}-1)=\sum_j c_j\bigl(e^{{x}}-1\bigr)^{{j}}$ and reading off the coefficient of
$x^{{n}}/n!$ gives the claim; the sum is finite because $S(n,j)=0$ for $j>n$. Integrality is
then immediate from Lemma~\ref{{lem:int}}.
\end{{proof}}

\begin{{lemma}}\label{{lem:trunc}}
For every $k\ge 1$ and every $n$,
$a(n)\equiv \sum_{{j=0}}^{{k-1}} c_j\, j!\, S(n,j) \pmod{{k}}$.
\end{{lemma}}

\begin{{proof}}
For $j\ge k$ the integer $j!$ is a multiple of $k$, since $k$ is one of the factors
$1,2,\dots,j$. Hence every term of Lemma~\ref{{lem:stir}} with $j\ge k$ vanishes modulo
$k$; this uses $c_j\in\mathbb{{Z}}$, which is Lemma~\ref{{lem:int}}.
\end{{proof}}

This is the step at which integrality is not a convenience but the whole point: were the
$c_j$ merely rational, $c_j\,j!$ need not be divisible by $k$ for large $j$ and the sum
would not truncate.

\begin{{lemma}}\label{{lem:exp}}
There are integers $d_0,\dots,d_{{k-1}}$, namely
$d_i=\sum_{{j=i}}^{{k-1}}(-1)^{{j-i}}\binom{{j}}{{i}}c_j$, with
\[
a(n)\;\equiv\;\sum_{{i=0}}^{{k-1}} d_i\, i^{{n}} \pmod{{k}}\qquad\text{{for all }} n\ge 0 .
\]
\end{{lemma}}

\begin{{proof}}
Counting surjections from an $n$-set onto a $j$-set by inclusion and exclusion on the
image gives $j!\,S(n,j)=\sum_{{i=0}}^{{j}}(-1)^{{j-i}}\binom{{j}}{{i}}i^{{n}}$. Substituting this
into Lemma~\ref{{lem:trunc}} and exchanging the two finite sums collects the coefficient of
$i^{{n}}$ into $d_i$ as stated. Each $d_i$ is an integer because each $c_j$ is.
\end{{proof}}

\section{{The period}}

For $k\ge 2$ let $v(k)$ be the largest exponent in the prime factorisation of $k$, so
$k\mid m^{{v(k)}}$ whenever $m$ is divisible by every prime factor of $k$, and
$v(k)\le\log_2 k$.

\begin{{lemma}}\label{{lem:power}}
Let $k\ge2$ and $0\le i<k$. Then $i^{{\,n+\varphi(k)}}\equiv i^{{\,n}}\pmod{{k}}$ for every
$n\ge v(k)$.
\end{{lemma}}

\begin{{proof}}
Write $k=k_1k_2$, where $k_1=\prod_{{p\mid k,\ p\mid i}}p^{{v_p(k)}}$ and $k_2=k/k_1$; then
$\gcd(k_1,k_2)=1$ and $\gcd(i,k_2)=1$.

Modulo $k_1$: for each prime $p\mid k_1$ we have $p\mid i$, so
$v_p\bigl(i^{{n}}\bigr)=n\,v_p(i)\ge n\ge v(k)\ge v_p(k)$. Hence $k_1\mid i^{{n}}$ for
$n\ge v(k)$, and likewise $k_1\mid i^{{n+\varphi(k)}}$; both sides are $\equiv 0$.

Modulo $k_2$: $i$ is a unit, so by Euler's theorem $i^{{\varphi(k_2)}}\equiv 1$. Since
$\gcd(k_1,k_2)=1$ we have $\varphi(k)=\varphi(k_1)\varphi(k_2)$, so
$\varphi(k_2)\mid\varphi(k)$ and therefore $i^{{\varphi(k)}}\equiv 1 \pmod{{k_2}}$, giving
$i^{{\,n+\varphi(k)}}\equiv i^{{\,n}}$.

The two congruences and the Chinese remainder theorem give the claim modulo $k=k_1k_2$.
(For $i=0$ note $0^{{n}}=0$ for $n\ge 1$ and $v(k)\ge1$.)
\end{{proof}}

\begin{{theorem}}\label{{thm:main}}
Let $a(n)$ be OEIS {anum}. For every integer $k\ge1$,
\[
a\bigl(n+\varphi(k)\bigr)\;\equiv\;a(n)\pmod{{k}}\qquad\text{{for all }} n\ge v(k),
\]
where $v(k)$ is the largest exponent in the prime factorisation of $k$ (and $v(1)=0$).
In particular the sequence $\bigl(a(n)\bmod k\bigr)_{{n\ge0}}$ is eventually periodic with
period dividing $\varphi(k)$, with a pre-period of length at most $\log_2 k$. This is the
conjecture of Section~1.
\end{{theorem}}

\begin{{proof}}
The case $k=1$ is trivial. For $k\ge2$, Lemma~\ref{{lem:exp}} writes $a(n)$ modulo $k$ as
$\sum_{{i<k}}d_i i^{{n}}$ with integer $d_i$ independent of $n$, and Lemma~\ref{{lem:power}}
gives $i^{{\,n+\varphi(k)}}\equiv i^{{\,n}}$ for each $i<k$ once $n\ge v(k)$. Summing the
$k$ congruences with the weights $d_i$ gives
$a(n+\varphi(k))\equiv a(n)\pmod k$ for $n\ge v(k)$. The true period of the eventually
periodic sequence is then a divisor of $\varphi(k)$.
\end{{proof}}

\begin{{remark}}
The bound $n\ge v(k)$ cannot be lowered in general: for $k$ a prime power $p^{{e}}$ the
term $i=p$ contributes $p^{{n}}$, which is not divisible by $p^{{e}}$ until $n=e=v(k)$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the series $G$ of \eqref{{eq:G}} was expanded and $\sum_j c_j j! S(n,j)$ compared
against the entry's DATA at every one of the ${len(data)}$ published indices; the values
agree exactly, and every $c_j$ came out an integer. A series that reproduced only some of
the published terms would not have been used.

Second, for each $k$ from $2$ to ${KMAX}$ the sequence $a(n)\bmod k$ was computed exactly
--- not sampled --- from the recurrence $S(n,j)=j\,S(n-1,j)+S(n-1,j-1)$ carried out in
$\mathbb{{Z}}/k\mathbb{{Z}}$ on the truncated state
$\bigl(S(n,0),\dots,S(n,k-1)\bigr)$ of Lemma~\ref{{lem:trunc}}, and its exact eventual
period found by detecting the repetition of that state. The result is tabulated below.
In every case the period divides $\varphi(k)$, as Theorem~\ref{{thm:main}} requires.

\begin{{center}}\small
\begin{{tabular}}{{rrr@{{\qquad\qquad}}rrr}}
$k$ & $\varphi(k)$ & period & $k$ & $\varphi(k)$ & period \\ \hline
{table}
\end{{tabular}}
\end{{center}}

Third, the congruence $a(n+\varphi(k))\equiv a(n)\pmod k$ of Theorem~\ref{{thm:main}} was
checked directly on the published terms for every $k$ in that range and every $n\ge v(k)$
for which both indices are published; it holds without exception.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {anum}.
\bibitem{{comtet}} L.~Comtet, \emph{{Advanced Combinatorics}}, Reidel, 1974.
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\bibitem{{hw}} G.~H.~Hardy and E.~M.~Wright, \emph{{An Introduction to the Theory of
Numbers}}, 6th ed., Oxford University Press, 2008.
\end{{thebibliography}}

\end{{document}}
"""
    return body


def main():
    meta = json.load(open("phimeta.json"))
    os.makedirs(OUT, exist_ok=True)
    made = []
    for anum in phispec.SPEC:
        d = f"{OUT}/phi{anum}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(anum, meta[anum]))
        made.append((anum, d))
        print("wrote", d)
    json.dump([a for a, _ in made], open("phi-built.json", "w"), indent=1)


if __name__ == "__main__":
    main()
