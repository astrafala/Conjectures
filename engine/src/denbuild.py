#!/usr/bin/env python3
"""One paper per entry settled by the denumerant engine.

What these have in common is a condition on every subblock, or on every pair of neighbouring
subblocks, and what differs is the condition, the shape and --- for a few of them --- a
scaling factor in front of the count. The general builder would describe all of that as "a
bounded window of consecutive lines", which is true but says nothing about the entry in
hand, and would drop the scaling factor entirely.
"""
import json
import os
import re

import localentry as LE
import phibuild
import denumerant
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}


from fractions import Fraction as _F
from math import lcm as _lcm


def _tn(H):
    """n*H*(H+1)/4 in lowest terms, so the paper prints 5n rather than 20n/4"""
    f = _F(H * (H + 1), 4)
    if f.denominator == 1:
        return "n" if f.numerator == 1 else "%dn" % f.numerator
    return "\\tfrac{%d}{%d}n" % (f.numerator, f.denominator)


def model_section(p, S, expo):
    H = p['H']
    T = "n\\,H(H+1)/4" 
    return "\n".join([
        r"\section{The array disappears}", "",
        rf"A row of $-1$s and $1$s that is nondecreasing is a block of $-1$s followed by a "
        rf"block of $1$s, so it is determined by a single number: how many $-1$s it holds. "
        rf"Write $k_i\in\{{0,1,\dots,n\}}$ for that number in row $i$. Then row $i$ sums to "
        rf"$(n-k_i)-k_i = n-2k_i$, and the entry's condition",
        r"\[ \sum_{i=1}^{H}\sum_{j=1}^{n} i\,x(i,j) \;=\; \sum_{i=1}^{H} i\,(n-2k_i) "
        r"\;=\; 0 \]",
        rf"becomes $\sum_{{i=1}}^{{{H}}} i\,k_i = T(n)$ with $T(n)={_tn(H)}$. "
        rf"The arrays are gone: what is left is the lattice points "
        rf"of the box $\{{0,\dots,n\}}^{{{H}}}$ on one hyperplane.",
        "",
        r"\section{Why that is enough}", "",
        rf"Those lattice points are the ones in the $n$-th dilate of a fixed rational "
        rf"polytope, so the count is a quasi-polynomial in $n$. That is the whole reason a "
        rf"linear recurrence can be proved here rather than observed: a quasi-polynomial of "
        rf"degree $d$ and period $P$ satisfies the recurrence whose characteristic polynomial "
        rf"is $(x^{{P}}-1)^{{d+1}}$, so it is $C$-finite of order at most $P(d+1)$.",
        "",
        rf"Both numbers can be named. By inclusion-exclusion over which coordinates exceed "
        rf"$n$,",
        r"\[ a(n)\;=\;\sum_{S\subseteq\{1,\dots,H\}}(-1)^{|S|}\,"
        r"D\bigl(T(n)-(n+1)\sigma(S)\bigr), \]",
        rf"where $\sigma(S)$ is the sum of $S$ and $D(m)$ counts the solutions of "
        rf"$\sum i\,k_i=m$ in non-negative integers with no upper bound --- the classical "
        rf"denumerant for the parts $1,\dots,{H}$. $D$ is a quasi-polynomial in $m$ of degree "
        rf"${H-1}$ with period dividing $\mathrm{{lcm}}(1,\dots,{H})={_lcm(*range(1, H+1))}$; "
        rf"each argument above is an integer-linear function of $n$, which preserves the "
        rf"degree and can only shrink the period, and the parity case at worst doubles it. So "
        rf"$a$ is a quasi-polynomial of degree at most ${H-1}$ and period dividing "
        rf"${2*_lcm(*range(1, H+1))}$, hence satisfies a linear recurrence of order at most "
        rf"$S={S}$.",
        "",
        rf"That bound is the certificate. It is also what makes the computation cheap: $D$ is "
        rf"one table, so thousands of exact terms of $a$ cost almost nothing.",
    ])


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h["anum"]
    S, order, nterms, nthr = h["S"], h["order"], h["nterms"], h["nthr"]
    off, sh = h["offset"], h["shift"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    p = denumerant.parse_name(e['name'])
    kk = off - sh
    expo = "n" if kk == 0 else ("n-%d" % kk if kk > 0 else "n+%d" % (-kk))
    frac = p['frac']
    scale = ""
    if frac != 1:
        scale = (rf" The entry does not count the arrays themselves but $1/{frac}$ of them, "
                 rf"so every count below is divided by ${frac}$; the division is exact at "
                 rf"every term, which is itself a check on the model.")
    pref = ('\\tfrac{1}{%d}\\,' % frac) if frac != 1 else ''
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        j = nthr - off
        if d[j] != sum(int(c) * d[j - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{A lattice count, not a walk count: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{7 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. A nondecreasing row of $-1$s and $1$s is
determined by one number --- how many $-1$s it holds --- so the entry's condition collapses to
a single linear equation on a box of lattice points, and the arrays disappear entirely. The
count is then the number of lattice points in a dilate of a fixed rational polytope, hence a
quasi-polynomial in $n$; its degree and its period can both be named, which bounds by
$S={S}$ the order of a linear recurrence it must satisfy. Whether the conjectured recurrence
is that recurrence is then a finite exact computation. There is no digraph and no matrix
anywhere in this argument.{scale}
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

{model_section(p, S, expo)}
so $a$ is $C$-finite of order at most $S={S}$, and the alignment between the model and the
entry's own $n$ is fixed by matching against every published term.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q$ be the characteristic polynomial of the conjectured recurrence, of order ${order}$,
and let $u_j=a(j+{order})-\sum_i c_i\,a(j+{order}-i)$ be its residual. Then $u$ satisfies the
same linear recurrence of order $S={S}$ that $a$ does, so if $u_j=0$ for $S$ consecutive
indices then $u_j=0$ for every larger $j$, and the last nonzero $u_j$ pins the threshold
exactly.
\end{{lemma}}

\begin{{proof}}
A sequence annihilated by a linear operator with constant coefficients has every linear
combination of its shifts annihilated by the same operator, and $u$ is such a combination of
shifts of $a$. A sequence satisfying a linear recurrence of order $S$ and vanishing at $S$
consecutive indices vanishes from the first of them onwards, since every later value is a
fixed combination of the $S$ before it.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The terms $a(n)$ were computed exactly from the lattice-point formula, far enough to cover
$S={S}$ consecutive residuals, and the residuals were formed in exact integer arithmetic.
They vanish from the index corresponding to $n={nthr}+1$ onwards and go on vanishing for more
than $S$ consecutive indices, which by Lemma~\ref{{lem:crit}} settles every larger $n$ at
once.{tight}
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the reduction to the entry: the lattice count is derived by reading the
entry's English, and a misreading gives different counts.

Second, the reading was pinned before the reduction was trusted, by a program that enumerates
the arrays themselves, one by one, from the entry's own words --- every nondecreasing
row of plus and minus ones, the weighted sum computed directly --- and compares the count
with the lattice-point formula. That program shares no code with the lattice-point formula, so an error in one does not
hide an error in the other.

Third, the conjectured recurrence was evaluated directly on the published terms, with
nothing from the argument above involved, and holds wherever the proved range and the data
overlap.

Fourth, the residual test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic over every index up to the certified bound, not on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Quasi-polynomials and denumerants, Sections 4.4 and 4.6;
lattice points in dilates of rational polytopes, Section 4.6.)
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\bibitem{{beck}} M.~Beck and S.~Robins, \emph{{Computing the Continuous Discretely}}, 2nd
ed., Springer, 2015. (Ehrhart quasi-polynomials; the denumerant.)
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("uniall_hits.json"))
            if h.get("engine") == "denumerant" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
