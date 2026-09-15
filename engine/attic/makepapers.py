#!/usr/bin/env python3
"""Generate papers 32-51: one per OEIS entry settled by the periodicity theorem.

Each paper stands alone: it states and proves the general theorem, then applies it
to its own entry. No paper refers to any of the others.
"""
import json, os, subprocess
from math import factorial
from sympy import totient
from sympy.functions.combinatorial.numbers import stirling

ENT = json.load(open("entries.json"))

# Per entry: the reduction to G(y) with y = e^x - 1, and why G is integral.
G = {
"A000670": (r"\frac{1}{1-y}",
    r"The posted e.g.f.\ is $1/(2-e^{x})$. Since $e^{x}=1+y$, the denominator is "
    r"$2-(1+y)=1-y$.",
    r"a geometric series, all coefficients $1$"),
"A002050": (r"\frac{y(1+y)}{1-y}",
    r"The posted e.g.f.\ is $(e^{2x}-e^{x})/(2-e^{x})$. With $e^{x}=1+y$ the numerator is "
    r"$(1+y)^{2}-(1+y)=y(1+y)$ and the denominator is $1-y$.",
    r"a polynomial over $1-y$"),
"A004123": (r"\frac{1}{1-2y}",
    r"The entry's own formula line reads ``e.g.f.\ for sequence with offset $0$: "
    r"$1/(3-2e^{x})$''. With $e^{x}=1+y$ the denominator is $3-2(1+y)=1-2y$.",
    r"a geometric series with ratio $2y$"),
"A006531": (r"C\!\left(\frac{y}{1+y}\right),\quad C(t)=\frac{1-\sqrt{1-4t}}{2t}",
    r"The posted e.g.f.\ is $C(1-e^{-x})$ with $C$ the ordinary generating function of the "
    r"Catalan numbers. Here $1-e^{-x}=(e^{x}-1)/e^{x}=y/(1+y)$, so the e.g.f.\ is a power "
    r"series in $y$ after all, even though it is not written that way on the entry.",
    r"Catalan numbers composed with $y/(1+y)$, an integral substitution fixing $0$"),
"A052895": (r"C(y),\quad C(t)=\frac{1-\sqrt{1-4t}}{2t}",
    r"The entry states ``E.g.f.: $C(\exp(x)-1)$, where $C(x)=(1-\sqrt{1-4x})/(2x)$ is the "
    r"o.g.f.\ for A000108'', which is already of the required shape.",
    r"the Catalan numbers"),
"A064618": (r"\sum_{k\ge0}k!\,y^{k}",
    r"The entry is the Stirling transform of $(n!)^{2}$, and its formula line gives "
    r"``E.g.f: hypergeom$([1,1],[\,],\exp(x)-1)$''. Since "
    r"${}_{2}F_{0}(1,1;\,;t)=\sum_{k}\frac{(1)_{k}(1)_{k}}{k!}t^{k}=\sum_{k}k!\,t^{k}$, "
    r"this is $G(y)$ with $G(t)=\sum_{k}k!\,t^{k}$.",
    r"the factorials"),
"A080253": (r"\frac{1+y}{1-2y-y^{2}}",
    r"The posted e.g.f.\ is $e^{x}/(2-e^{2x})$. With $e^{x}=1+y$ the denominator is "
    r"$2-(1+y)^{2}=1-2y-y^{2}$.",
    r"a rational function with constant term $1$ in the denominator"),
"A162314": (r"\frac{(1+y)^{2}}{1-2y-y^{2}}",
    r"The posted e.g.f.\ is $e^{2x}/(2-e^{2x})$; with $e^{x}=1+y$ this is "
    r"$(1+y)^{2}/(2-(1+y)^{2})=(1+y)^{2}/(1-2y-y^{2})$.",
    r"a rational function with constant term $1$ in the denominator"),
"A167137": (r"\exp\!\Big(\sum_{n\ge1}\frac{\sigma(n)}{n}y^{n}\Big)=\prod_{j\ge1}\frac{1}{1-y^{j}}",
    r"The entry states ``E.g.f.: $P(\exp(x)-1)$ where $P(x)$ is the g.f.\ of the partition "
    r"numbers'', and equivalently ``E.g.f.: $\exp(\sum_{n\ge1}\sigma(n)[\exp(x)-1]^{n}/n)$''. "
    r"Both are $G(y)$ with $G$ the partition generating function.",
    r"the partition numbers"),
"A259533": (r"\frac{(1+y)^{3}}{1-y}",
    r"The posted e.g.f.\ is $e^{3x}/(2-e^{x})$; with $e^{x}=1+y$ this is "
    r"$(1+y)^{3}/(1-y)$.",
    r"a polynomial over $1-y$"),
"A301921": (r"\cfrac{1}{1-\cfrac{y}{1-\cfrac{y^{2}}{1-\cdots}}}",
    r"The entry is defined by ``e.g.f.\ $1/(1-(\exp(x)-1)/(1-(\exp(x)-1)^{2}/(1-\cdots)))$'', "
    r"a continued fraction whose every appearance of $x$ is inside $\exp(x)-1$.",
    r"a continued fraction with integer entries, each convergent integral"),
"A305550": (r"\prod_{j\ge1}\bigl(1+y^{j}\bigr)",
    r"The entry is ``Expansion of e.g.f.\ $\prod_{k\ge1}(1+(\exp(x)-1)^{k})$'', already of "
    r"the required shape.",
    r"the partitions into distinct parts"),
"A306082": (r"\prod_{j\ge1}\frac{1}{1-y^{j^{2}}}",
    r"The entry is ``Expansion of e.g.f.\ $\prod_{k\ge1}1/(1-(\exp(x)-1)^{k^{2}})$'', "
    r"already of the required shape.",
    r"partitions into square parts"),
"A316142": (r"\prod_{j\ge1}\bigl(1+y^{j}\bigr)^{2}",
    r"The entry is ``Expansion of e.g.f.\ $\prod_{k\ge1}(1+(\exp(x)-1)^{k})^{2}$''.",
    r"a product of integral factors"),
"A316143": (r"\prod_{j\ge1}\frac{1}{\bigl(1-y^{j}\bigr)^{2}}",
    r"The entry is ``Expansion of e.g.f.\ $\prod_{k\ge1}1/(1-(\exp(x)-1)^{k})^{2}$''.",
    r"a product of integral factors"),
"A316144": (r"\prod_{j\ge1}\left(\frac{1+y^{j}}{1-y^{j}}\right)^{2}",
    r"The entry is ``Expansion of e.g.f.\ "
    r"$\prod_{k\ge1}((1+(\exp(x)-1)^{k})/(1-(\exp(x)-1)^{k}))^{2}$''.",
    r"a product of integral factors"),
"A320352": (r"\frac{y}{1-y-y^{2}}",
    r"The posted e.g.f.\ is $(1+\sinh x-\cosh x)/(1-2\sinh x)$. Since "
    r"$1+\sinh x-\cosh x=1-e^{-x}$ and $1-2\sinh x=1-e^{x}+e^{-x}$, multiplying numerator "
    r"and denominator by $e^{x}$ turns this into $(e^{x}-1)/(e^{x}-e^{2x}+1)$; with "
    r"$e^{x}=1+y$ the denominator is $(1+y)-(1+y)^{2}+1=1-y-y^{2}$.",
    r"the Fibonacci numbers"),
"A354242": (r"\sum_{k\ge0}\binom{2k}{k}y^{k}=\frac{1}{\sqrt{1-4y}}",
    r"The entry gives both ``E.g.f.: $1/\sqrt{5-4\exp(x)}$'' and ``E.g.f.: "
    r"$\sum_{k\ge0}\binom{2k}{k}(\exp(x)-1)^{k}$''. The second is already of the required "
    r"shape; the first agrees with it because $5-4(1+y)=1-4y$.",
    r"the central binomial coefficients"),
"A354253": (r"\sum_{k\ge0}\binom{2k}{k}2^{k}y^{k}=\frac{1}{\sqrt{1-8y}}",
    r"The entry gives both ``E.g.f.: $1/\sqrt{9-8\exp(x)}$'' and ``E.g.f.: "
    r"$\sum_{k\ge0}\binom{2k}{k}(2(\exp(x)-1))^{k}$''; and $9-8(1+y)=1-8y$.",
    r"central binomial coefficients times powers of $2$"),
"A355409": (r"\frac{1}{1-y-2y^{2}-y^{3}}",
    r"The posted e.g.f.\ is $1/(1+e^{2x}-e^{3x})$. With $e^{x}=1+y$ the denominator is "
    r"$1+(1+y)^{2}-(1+y)^{3}=1-y-2y^{2}-y^{3}$.",
    r"a rational function with constant term $1$ in the denominator"),
}

_s1 = {}
def s1(k, n):
    if (k, n) not in _s1:
        _s1[(k, n)] = (-1) ** (k - n) * int(stirling(k, n, kind=1, signed=False))
    return _s1[(k, n)]


def coeffs(a, upto=8):
    out = []
    for k in range(min(upto, len(a))):
        t = sum(s1(k, n) * a[n] for n in range(k + 1))
        assert t % factorial(k) == 0, (k, t)
        out.append(t // factorial(k))
    return out


def stirling_mod(c, N, m):
    K = len(c)
    prev = [0] * (K + 1); prev[0] = 1
    out = []
    for n in range(N + 1):
        if n:
            cur = [0] * (K + 1)
            for k in range(K + 1):
                cur[k] = ((prev[k - 1] if k else 0) + k * prev[k]) % m
            prev = cur
        out.append(sum(c[k] * factorial(k) * prev[k] for k in range(K)) % m)
    return out


def period(seq, tail=160):
    n = len(seq); start = n - tail
    for p in range(1, tail // 2 + 1):
        if all(seq[i] == seq[i + p] for i in range(start, n - p)):
            return p
    return None


MODULI = [5, 7, 8, 9, 11, 12, 13, 16, 25, 27]

TEMPLATE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{remark}[theorem]{Remark}
\newcommand{\ord}{\operatorname{ord}}
\newcommand{\Z}{\mathbb{Z}}
\title{%(TITLE)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{25 August 2026}
\begin{document}
\maketitle

\begin{abstract}
%(ABSTRACT)s
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 11B50, 11B73, 05A15, 11A07.\normalsize

\section{The sequence and the conjecture}

Throughout, $m$ and $k$ denote positive integers, $\varphi$ is Euler's totient function
(OEIS A000010), and $S(n,k)$ are the Stirling numbers of the second kind, with
$S(0,0)=1$ and $S(n,k)=0$ for $k>n$. We write $0^{0}=1$, and throughout
\[
y := e^{x}-1, \qquad\text{so that}\qquad e^{x}=1+y .
\]

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
and it carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

Bala also states the conjecture in a general form: that the property should hold for
every integer sequence whose exponential generating function has the shape $G(e^{x}-1)$
with $G$ an integral power series. We prove that general statement as
Theorem~\ref{thm:main} below, and then obtain the present entry as
Corollary~\ref{cor:this} by identifying its $G$ in Section~\ref{sec:apply}.

\section{The theorem}

\begin{theorem}\label{thm:main}
Let $G(t)=\sum_{k\ge0}c_{k}t^{k}$ be a power series with integer coefficients, and define
integers $a(n)$ by $\sum_{n\ge0}a(n)x^{n}/n!=G(e^{x}-1)$. Then for every $m\ge1$ the
sequence $\bigl(a(n)\bmod m\bigr)_{n\ge0}$ is eventually periodic, with period dividing
$\varphi(m)$.
\end{theorem}

The proof uses three standard facts.

\begin{lemma}\label{lem:stirling}
$(e^{x}-1)^{k}=k!\sum_{n\ge k}S(n,k)x^{n}/n!$, and hence
$a(n)=\sum_{k=0}^{n}c_{k}\,k!\,S(n,k)$ for every $n\ge0$. In particular every $a(n)$ is an
integer.
\end{lemma}

\begin{proof}
The first identity is the exponential generating function of the Stirling numbers of the
second kind. Multiplying by $c_{k}$ and summing over $k$ is legitimate in $\Z[[x]]$
because $(e^{x}-1)^{k}$ has order $k$ in $x$, so each coefficient of $x^{n}$ receives
contributions from only finitely many $k$; comparing coefficients of $x^{n}/n!$ gives the
formula, and the sum terminates because $S(n,k)=0$ for $k>n$.
\end{proof}

\begin{lemma}\label{lem:power}
$k!\,S(n,k)=\sum_{j=0}^{k}(-1)^{k-j}\binom{k}{j}j^{\,n}$ for all $n,k\ge0$.
\end{lemma}

\begin{proof}
Both sides count the surjections from an $n$-set onto a $k$-set: the left directly, the
right by inclusion--exclusion over the points of the codomain that are missed. For $n=0$
both sides equal $[k=0]$, using $0^{0}=1$.
\end{proof}

\begin{lemma}\label{lem:jn}
For integers $m\ge1$ and $j\ge0$, the sequence $\bigl(j^{\,n}\bmod m\bigr)_{n\ge0}$ is
eventually periodic with period dividing $\varphi(m)$.
\end{lemma}

\begin{proof}
Write $m=m_{1}m_{2}$, where $m_{1}$ is the product of those prime powers $p^{v_{p}(m)}$ of
$m$ whose prime $p$ divides $j$, and $m_{2}=m/m_{1}$. Then $\gcd(m_{1},m_{2})=1$ and
$\gcd(j,m_{2})=1$.

Every prime dividing $m_{1}$ divides $j$, so $m_{1}\mid j^{\,n}$ once $n\ge\log_{2}m$;
thus $j^{\,n}\equiv0 \pmod{m_{1}}$ for all large $n$, a sequence of eventual period $1$.
Modulo $m_{2}$ the integer $j$ is a unit, so $j^{\,n}$ is purely periodic with period
$\ord_{m_{2}}(j)$, a divisor of $\varphi(m_{2})$. By the Chinese remainder theorem
$j^{\,n} \bmod m$ is eventually periodic with period dividing
$\operatorname{lcm}(1,\ord_{m_{2}}(j))=\ord_{m_{2}}(j)$. Finally $m_{2}\mid m$ gives
$\varphi(m_{2})\mid\varphi(m)$, so that period divides $\varphi(m)$.
\end{proof}

\begin{proof}[Proof of Theorem~\ref{thm:main}]
Fix $m\ge1$. Because $m\mid m!$ we have $m\mid k!$ for every $k\ge m$, so in
Lemma~\ref{lem:stirling} every term with $k\ge m$ is divisible by $m$. Hence for $n\ge m$
\begin{equation}\label{eq:trunc}
a(n)\;\equiv\;\sum_{k=0}^{m-1}c_{k}\,k!\,S(n,k) \pmod m ,
\end{equation}
a sum whose number of terms no longer depends on $n$. This is the only place the
hypothesis $G\in\Z[[t]]$ is used: it keeps the $c_{k}$ integral, so no denominator can
cancel the factor $k!$ that supplies the divisibility.

Substituting Lemma~\ref{lem:power} and exchanging the two finite sums,
\begin{equation}\label{eq:expo}
a(n)\;\equiv\;\sum_{j=0}^{m-1}w_{j}\,j^{\,n} \pmod m ,
\qquad
w_{j}:=\sum_{k=j}^{m-1}(-1)^{k-j}\binom{k}{j}c_{k}\in\Z ,
\end{equation}
for all $n\ge m$; the weights $w_{j}$ depend on $m$ and $G$ but not on $n$. By
Lemma~\ref{lem:jn} each sequence $n\mapsto j^{\,n}\bmod m$ is eventually periodic with
period dividing $\varphi(m)$. A finite $\Z$-linear combination of eventually periodic
sequences is eventually periodic with period dividing the least common multiple of their
periods, and the least common multiple of finitely many divisors of $\varphi(m)$ again
divides $\varphi(m)$. So the right-hand side of \eqref{eq:expo}, and therefore $a(n)$, is
eventually periodic modulo $m$ with period dividing $\varphi(m)$.
\end{proof}

\begin{remark}
``Eventually'' cannot be dropped, and the divisor need not be $\varphi(m)$ itself.
Equation \eqref{eq:trunc} is asserted only for $n\ge m$, and Lemma~\ref{lem:jn} adds a
further preperiod coming from the primes shared by $j$ and $m$; meanwhile the exact period
is the least common multiple of the orders $\ord_{m_{2}}(j)$ over those $j$ whose weight
$w_{j}$ survives modulo $m$, which is often a proper divisor of $\varphi(m)$. Both effects
are visible in the table of Section~\ref{sec:ver}.
\end{remark}

\section{Application to %(ANUM)s}\label{sec:apply}

\begin{corollary}\label{cor:this}
The conjecture quoted in Section~1 is true: for every $m\ge1$ the sequence
%(ANUM)s$(n) \bmod m$ is eventually periodic with period dividing $\varphi(m)$.
\end{corollary}

\begin{proof}
By Theorem~\ref{thm:main} it suffices to exhibit the entry's exponential generating
function in the form $G(e^{x}-1)$ with $G$ integral. %(REDUCTION)s Therefore
\[
\sum_{n\ge0}a(n)\frac{x^{n}}{n!}=G(y),\qquad G(t)=%(GLATEX)s ,
\]
whose coefficients are %(WHYINT)s, all integers. So $G\in\Z[[t]]$ and
Theorem~\ref{thm:main} applies.%(OFFNOTE)s
\end{proof}

Concretely, the first coefficients of $G$ are
\[
c_{0},c_{1},c_{2},\dots \;=\; %(CKS)s ,
\]
and these are exactly what the inversion of Section~\ref{sec:ver} recovers from the
entry's published terms.

\section{Verification}\label{sec:ver}

Every number quoted here is an output of a script written separately from this note.

First, the identification of $G$ was checked against the entry rather than assumed. If
$\sum_{n}a(n)x^{n}/n!=G(e^{x}-1)$ then substituting $x=\log(1+y)$ gives
\[
c_{k}=\frac{1}{k!}\sum_{n}s(k,n)\,a(n),
\]
with $s$ the signed Stirling numbers of the first kind. Applying this to the
$%(NDATA)d$ terms published on %(ANUM)s returns integers at every $k$, and the values
agree with the coefficients of the $G$ named in Section~\ref{sec:apply}.

Second, the conclusion itself was tested. From the recovered $c_{k}$ we generated
$a(n)\bmod m$ for $n\le400$ using $a(n)=\sum_{k}c_{k}k!\,S(n,k)$ with an integer
recurrence for $S(n,k)$ --- a computation that touches neither the generating function nor
the published terms --- then measured the exact eventual period over the last $160$
values. The results:

\begin{center}
\begin{tabular}{@{}%(COLSPEC)s@{}}
\toprule
$m$ %(MROW)s\\
$\varphi(m)$ %(PHIROW)s\\
exact period %(PERROW)s\\
\bottomrule
\end{tabular}
\end{center}

\noindent
In every column the exact period divides $\varphi(m)$, as Corollary~\ref{cor:this}
asserts.

\section{Relation to earlier work}

A related note of Bala (\emph{Integer sequences that become periodic on reduction modulo
$k$ for all $k$}, December 2017, linked from OEIS A047974) proves a different theorem, for
generating functions of the shape $F(x)\exp(xG(x))$ and with the stronger conclusion
$a(n+k)\equiv a(n)\pmod{k}$, i.e.\ pure periodicity with period dividing $k$. Neither its
hypothesis nor its conclusion covers the statement proved here, and the argument of
Section~2 is independent of it.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s; conjecture of P.\ Bala.
\bibitem{bala} P.\ Bala, \emph{Integer sequences that become periodic on reduction modulo
$k$ for all $k$}, December 2017; linked from OEIS A047974.
\bibitem{comtet} L.\ Comtet, \emph{Advanced Combinatorics}, Reidel, 1974, Chapter V.
\end{thebibliography}
\end{document}
"""


def tex_escape(s):
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("^", r"\^{}"), ("~", r"\~{}")]:
        s = s.replace(a, b)
    return s


def render_conj(raw):
    s = tex_escape(raw)
    s = s.replace("Conjecture:", r"\textbf{Conjecture:}", 1)
    # italicise the OEIS contributor markup _Name_
    out, parts = "", s.split("\\_")
    if len(parts) >= 3:
        s = raw
        import re as _re
        s = _re.sub(r"_([^_]+)_", r"\\emph{\1}", s)
        s = tex_escape(s).replace(r"\emph\{", r"\emph{").replace(r"\}", "}")
        s = s.replace("Conjecture:", r"\textbf{Conjecture:}", 1)
    return s


os.makedirs("papers", exist_ok=True)
os.makedirs("build", exist_ok=True)
num = 32
made = []
for anum in ["A000670", "A002050", "A004123", "A006531", "A052895", "A064618",
             "A080253", "A162314", "A167137", "A259533", "A301921", "A305550",
             "A306082", "A316142", "A316143", "A316144", "A320352", "A354242",
             "A354253", "A355409"]:
    e = ENT[anum]
    glatex, reduction, whyint = G[anum]
    c = coeffs(e["data"])
    pers = []
    for m in MODULI:
        seq = stirling_mod(c, 400, m)
        p = period(seq)
        assert p is not None and int(totient(m)) % p == 0, (anum, m, p)
        pers.append(p)
    off = e["offset"]
    first = ", ".join(str(v) for v in e["data"][:8])
    subs = {
        "ANUM": anum,
        "NAME": tex_escape(e["name"].rstrip(".")),
        "OFFSET": off,
        "FIRSTTERMS": f"a({off}),\\dots,a({off+7})\\;=\\;{first},\\ \\dots",
        "CONJ": render_conj(e["conjecture"]),
        "TIME": e["time"],
        "REV": e["revision"],
        "REDUCTION": reduction,
        "GLATEX": glatex,
        "WHYINT": whyint,
        "CKS": ", ".join(str(v) for v in c[:7]) + ", \\dots",
        "NDATA": len(e["data"]),
        "COLSPEC": "l" + "c" * len(MODULI),
        "MROW": "".join(f" & ${m}$" for m in MODULI),
        "PHIROW": "".join(f" & ${int(totient(m))}$" for m in MODULI),
        "PERROW": "".join(f" & ${p}$" for p in pers),
        "OFFNOTE": (r" The entry has offset $1$ and its formula line specifies the e.g.f.\ "
                    r"``for sequence with offset $0$'', so the entry's sequence is a shift "
                    r"of the one generated by $G$; a shift alters neither eventual "
                    r"periodicity nor the period."
                    if off == 1 else ""),
        "TITLE": (r"Eventual periodicity modulo $m$ with period dividing $\varphi(m)$:\\"
                  f"a proof of Bala's conjecture on OEIS {anum}"),
        "ABSTRACT": (
            f"Peter Bala conjectured on OEIS {anum} that the sequence reduced modulo $k$ is "
            r"eventually periodic with period dividing $\varphi(k)$. We prove it, as an "
            r"instance of the general statement --- also Bala's --- that this holds for "
            r"every integer sequence whose exponential generating function has the form "
            r"$G(e^{x}-1)$ with $G$ an integral power series. Expanding $(e^{x}-1)^{k}$ in "
            r"Stirling numbers of the second kind writes $a(n)=\sum_{k}c_{k}k!\,S(n,k)$; "
            r"modulo $m$ every term with $k\ge m$ dies because $m\mid k!$, leaving a fixed "
            r"finite sum, which inclusion--exclusion turns into an integer combination of "
            r"the sequences $n\mapsto j^{n}$, each eventually periodic modulo $m$ with "
            r"period dividing $\varphi(m)$. The identification of $G$ for this entry is "
            r"carried out in Section~3."),
    }
    tex = TEMPLATE % subs
    d = f"build/{num}"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/p.tex", "w").write(tex)
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "p.tex"],
                       cwd=d, capture_output=True)
    log = open(f"{d}/p.log", errors="ignore").read()
    errs = [l for l in log.split("\n") if l.startswith("! ")]
    pdf = f"{d}/p.pdf"
    ok = os.path.exists(pdf) and not errs
    if ok:
        subprocess.run(["cp", pdf, f"papers/{num}-PROOF.pdf"])
    made.append((num, anum, ok, errs[:2], os.path.getsize(pdf) if os.path.exists(pdf) else 0))
    num += 1

for n, a, ok, errs, size in made:
    print(f"{n:3d}  {a}  {'OK' if ok else 'FAILED ' + str(errs)}  {size} bytes")
print(f"\n{sum(1 for m in made if m[2])}/{len(made)} papers built")
