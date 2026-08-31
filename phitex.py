#!/usr/bin/env python3
"""Per-entry LaTeX: the entry's own e.g.f., the substitution to t = exp(x)-1, and why
the resulting G has integer coefficients. One dictionary entry per sequence; each paper
is written from its own line and stands on its own."""

# egf   : the e.g.f. as the entry states it, in LaTeX
# quote : the entry's own line, quoted verbatim in the paper
# sub   : the substitution worked through, in LaTeX (displayed)
# G     : G(t) in LaTeX
# why   : why G has integer coefficients, as a sentence
# cname : what the coefficients c_j are
TEX = {
"A000670": dict(
  egf=r"\frac{1}{2-e^{x}}",
  quote="E.g.f.: 1/(2-exp(x)).",
  sub=r"2-e^{x}=2-(1+t)=1-t",
  G=r"\frac{1}{1-t}",
  why="a geometric series, all of whose coefficients equal $1$",
  cname="$c_j=1$ for every $j$"),
"A002050": dict(
  egf=r"\frac{e^{2x}-e^{x}}{2-e^{x}}",
  quote="E.g.f.: (exp(2x)-exp(x))/(2-exp(x)).",
  sub=r"e^{2x}-e^{x}=e^{x}\bigl(e^{x}-1\bigr)=(1+t)\,t,\qquad 2-e^{x}=1-t",
  G=r"\frac{t(1+t)}{1-t}",
  why="a quotient of polynomials with integer coefficients whose denominator has constant term $1$",
  cname="$c_0=0$, $c_1=1$ and $c_j=2$ for $j\\ge 2$"),
"A004123": dict(
  egf=r"\frac{1}{3-2e^{x}}",
  quote="E.g.f. for sequence with offset 0: 1/(3-2*exp(x)).",
  sub=r"3-2e^{x}=3-2(1+t)=1-2t",
  G=r"\frac{1}{1-2t}",
  why="a geometric series in $2t$",
  cname="$c_j=2^{j}$"),
"A006531": dict(
  egf=r"C\bigl(1-e^{-x}\bigr),\quad C(s)=\frac{1-\sqrt{1-4s}}{2s}",
  quote="E.g.f.: C(1-exp(-x)), where C(x) = (1 - sqrt(1 - 4*x)) / (2*x) is the ordinary g.f. for the Catalan numbers A000108.",
  sub=r"1-e^{-x}=1-\frac{1}{1+t}=\frac{t}{1+t}",
  G=r"C\!\left(\frac{t}{1+t}\right)",
  why=(r"a composition $C(s)$ with $s=t/(1+t)$: the Catalan g.f.\ $C$ has integer "
       r"coefficients, and $t/(1+t)=t-t^{2}+t^{3}-\cdots$ has integer coefficients and "
       r"zero constant term, so the composition is a well-defined integer series"),
  cname="$c_j = 1, 1, 1, 2, 4, 9, 21, 51, \\dots$"),
"A052895": dict(
  egf=r"\frac{1}{2\,(e^{x}-1)}\Bigl(1-\sqrt{5-4e^{x}}\Bigr)",
  quote="E.g.f.: (1/2)/(exp(x) - 1)*(1 - (5 - 4*exp(x))^(1/2)).",
  sub=r"5-4e^{x}=5-4(1+t)=1-4t,\qquad e^{x}-1=t",
  G=r"\frac{1-\sqrt{1-4t}}{2t}",
  why="the ordinary generating function of the Catalan numbers, whose coefficients are integers",
  cname="$c_j=\\binom{2j}{j}/(j+1)$, the Catalan numbers A000108"),
"A064618": dict(
  egf=r"{}_{2}F_{0}\bigl(1,1;\,;e^{x}-1\bigr)",
  quote="E.g.f: hypergeom([1, 1], [], exp(x)-1).",
  sub=r"e^{x}-1=t",
  G=r"\sum_{j\ge 0} j!\,t^{j}",
  why=(r"the hypergeometric series ${}_{2}F_{0}(1,1;\,;t)=\sum_j (1)_j (1)_j t^{j}/j! "
       r"=\sum_j j!\,t^{j}$, whose coefficients are factorials and so integers"),
  cname="$c_j=j!$"),
"A080253": dict(
  egf=r"\frac{e^{x}}{2-e^{2x}}",
  quote="E.g.f.: exp(x)/(2-exp(2*x)).",
  sub=r"e^{2x}=(1+t)^{2},\qquad 2-(1+t)^{2}=1-2t-t^{2}",
  G=r"\frac{1+t}{1-2t-t^{2}}",
  why="a rational function with integer coefficients whose denominator has constant term $1$",
  cname="$c_j = 1, 3, 7, 17, 41, 99, \\dots$, the half-companion Pell numbers A001333"),
"A162314": dict(
  egf=r"\frac{e^{2x}}{2-e^{2x}}",
  quote="E.g.f.: exp(2*x)/(2-exp(2*x)).",
  sub=r"e^{2x}=(1+t)^{2},\qquad 2-(1+t)^{2}=1-2t-t^{2}",
  G=r"\frac{(1+t)^{2}}{1-2t-t^{2}}",
  why="a rational function with integer coefficients whose denominator has constant term $1$",
  cname="$c_j = 1, 4, 10, 24, 58, 140, \\dots$"),
"A167137": dict(
  egf=r"P\bigl(e^{x}-1\bigr),\quad P(t)=\prod_{k\ge 1}\frac{1}{1-t^{k}}",
  quote="E.g.f.: P(exp(x)-1) where P(x) is the g.f. of the partition numbers (A000041).",
  sub=r"e^{x}-1=t",
  G=r"\prod_{k\ge 1}\frac{1}{1-t^{k}}",
  why=("the generating function of the partition numbers; each factor $1/(1-t^{k})$ is an "
       "integer series and only finitely many factors affect any one coefficient"),
  cname="$c_j=p(j)$, the partition numbers A000041"),
"A259533": dict(
  egf=r"\frac{e^{3x}}{2-e^{x}}",
  quote="E.g.f.: exp(3*x)/(2-exp(x)).",
  sub=r"e^{3x}=(1+t)^{3},\qquad 2-e^{x}=1-t",
  G=r"\frac{(1+t)^{3}}{1-t}",
  why="a rational function with integer coefficients whose denominator has constant term $1$",
  cname="$c_j = 1, 4, 7, 8, 8, 8, \\dots$"),
"A301921": dict(
  egf=r"\cfrac{1}{1-\cfrac{u}{1-\cfrac{u^{2}}{1-\cfrac{u^{3}}{1-\cdots}}}},\quad u=e^{x}-1",
  quote="Expansion of e.g.f. 1/(1 - (exp(x) - 1)/(1 - (exp(x) - 1)^2/(1 - (exp(x) - 1)^3/(1 - ...)))), a continued fraction.",
  sub=r"e^{x}-1=t",
  G=r"\cfrac{1}{1-\cfrac{t}{1-\cfrac{t^{2}}{1-\cfrac{t^{3}}{1-\cdots}}}}",
  why=("a continued fraction whose $k$-th partial numerator is $t^{k}$: truncating after "
       "level $k$ leaves the coefficients below $t^{k}$ unchanged, and each truncation is a "
       "quotient of integer polynomials with denominator of constant term $1$"),
  cname="$c_j = 1, 1, 1, 2, 3, 5, 9, 15, 26, 45, \\dots$"),
"A305550": dict(
  egf=r"\prod_{k\ge 1}\Bigl(1+(e^{x}-1)^{k}\Bigr)",
  quote="Expansion of e.g.f. Product_{k>=1} (1 + (exp(x) - 1)^k).",
  sub=r"e^{x}-1=t",
  G=r"\prod_{k\ge 1}\bigl(1+t^{k}\bigr)",
  why=("the generating function for partitions into distinct parts; each factor is a "
       "polynomial with integer coefficients and only finitely many affect any one coefficient"),
  cname="$c_j=q(j)$, partitions into distinct parts A000009"),
"A306082": dict(
  egf=r"\prod_{k\ge 1}\frac{1}{1-(e^{x}-1)^{k^{2}}}",
  quote="Expansion of e.g.f. Product_{k>=1} 1/(1 - (exp(x) - 1)^(k^2)).",
  sub=r"e^{x}-1=t",
  G=r"\prod_{k\ge 1}\frac{1}{1-t^{k^{2}}}",
  why=("the generating function for partitions into square parts; each factor is an integer "
       "series and only finitely many affect any one coefficient"),
  cname="$c_j$ counts partitions of $j$ into square parts"),
"A316142": dict(
  egf=r"\prod_{k\ge 1}\Bigl(1+(e^{x}-1)^{k}\Bigr)^{2}",
  quote="Expansion of e.g.f. Product_{k>=1} (1 + (exp(x)-1)^k)^2.",
  sub=r"e^{x}-1=t",
  G=r"\prod_{k\ge 1}\bigl(1+t^{k}\bigr)^{2}",
  why=("a product of polynomials with integer coefficients, only finitely many of which "
       "affect any one coefficient"),
  cname="$c_j = 1, 2, 3, 6, 9, 14, 22, \\dots$"),
"A316143": dict(
  egf=r"\prod_{k\ge 1}\frac{1}{\bigl(1-(e^{x}-1)^{k}\bigr)^{2}}",
  quote="Expansion of e.g.f. Product_{k>=1} 1 / (1 - (exp(x)-1)^k)^2.",
  sub=r"e^{x}-1=t",
  G=r"\prod_{k\ge 1}\frac{1}{(1-t^{k})^{2}}",
  why=("a product of integer series $1/(1-t^{k})^{2}$, only finitely many of which affect "
       "any one coefficient"),
  cname="$c_j = 1, 2, 5, 10, 20, 36, 65, \\dots$"),
"A316144": dict(
  egf=r"\prod_{k\ge 1}\left(\frac{1+(e^{x}-1)^{k}}{1-(e^{x}-1)^{k}}\right)^{2}",
  quote="Expansion of e.g.f. Product_{k>=1} ((1 + (exp(x)-1)^k) / (1 - (exp(x)-1)^k))^2.",
  sub=r"e^{x}-1=t",
  G=r"\prod_{k\ge 1}\left(\frac{1+t^{k}}{1-t^{k}}\right)^{2}",
  why=("a product of integer series, only finitely many of which affect any one coefficient"),
  cname="$c_j = 1, 4, 12, 32, 76, 168, \\dots$"),
"A320352": dict(
  egf=r"\frac{e^{x}-1}{e^{x}-e^{2x}+1}",
  quote="Expansion of e.g.f. (exp(x) - 1)/(exp(x) - exp(2*x) + 1).",
  sub=r"e^{x}-e^{2x}+1=(1+t)-(1+t)^{2}+1=1-t-t^{2}",
  G=r"\frac{t}{1-t-t^{2}}",
  why="the generating function of the Fibonacci numbers, which are integers",
  cname="$c_j=F_j$, the Fibonacci numbers A000045"),
"A354242": dict(
  egf=r"\frac{1}{\sqrt{5-4e^{x}}}",
  quote="Expansion of e.g.f. 1/sqrt(5 - 4 * exp(x)).",
  sub=r"5-4e^{x}=5-4(1+t)=1-4t",
  G=r"\frac{1}{\sqrt{1-4t}}",
  why=r"$\sum_j \binom{2j}{j}t^{j}$, whose coefficients are central binomial coefficients",
  cname=r"$c_j=\binom{2j}{j}$, the central binomial coefficients A000984"),
"A354253": dict(
  egf=r"\frac{1}{\sqrt{9-8e^{x}}}",
  quote="Expansion of e.g.f. 1/sqrt(9 - 8 * exp(x)).",
  sub=r"9-8e^{x}=9-8(1+t)=1-8t",
  G=r"\frac{1}{\sqrt{1-8t}}",
  why=r"$\sum_j \binom{2j}{j}2^{j}t^{j}$, whose coefficients are integers",
  cname=r"$c_j=\binom{2j}{j}2^{j}$"),
"A355409": dict(
  egf=r"\frac{1}{1+e^{2x}-e^{3x}}",
  quote="Expansion of e.g.f. 1/(1 + exp(2*x) - exp(3*x)).",
  sub=r"1+e^{2x}-e^{3x}=1+(1+t)^{2}-(1+t)^{3}=1-t-2t^{2}-t^{3}",
  G=r"\frac{1}{1-t-2t^{2}-t^{3}}",
  why="a rational function with integer coefficients whose denominator has constant term $1$",
  cname="$c_j = 1, 1, 3, 6, 13, 28, 60, \\dots$"),
"A079144": dict(
  egf=r"\sum_{k\ge 0} k!\,S(n,k)\,b(k),\quad b=\text{A138265}",
  quote="a(n) = Sum_{k=0..n} k!*Stirling2(n,k)*A138265(k).",
  sub=r"e^{x}-1=t",
  G=r"\sum_{k\ge 0} b(k)\,t^{k},\qquad b=\text{A138265}",
  why="a power series whose coefficients are the terms of the integer sequence A138265",
  cname="$c_k=b(k)$, the terms of A138265"),
"A158690": dict(
  egf=r"\sum_{n\ge 0}\ \prod_{k=1}^{n}\Bigl(1-e^{-(2k-1)x}\Bigr)",
  quote="Expansion of the basic hypergeometric series 1 + (1 - exp(-t)) + (1 - exp(-t))*(1 - exp(-3*t)) + ...",
  sub=r"e^{-(2k-1)x}=(1+t)^{-(2k-1)}",
  G=r"\sum_{n\ge 0}\ \prod_{k=1}^{n}\Bigl(1-(1+t)^{-(2k-1)}\Bigr)",
  why=(r"each factor $1-(1+t)^{-(2k-1)}$ is an integer series with zero constant term, so "
       r"the $n$-th product is divisible by $t^{n}$ and only finitely many terms of the sum "
       r"affect any one coefficient"),
  cname="$c_j = 1, 1, 5, 23, 137, \\dots$"),
}
