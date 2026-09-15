#!/usr/bin/env python3
"""Papers for the triangular arrays whose alphabet grows."""
import conjquote
import os, json, re
from fractions import Fraction
import localentry as LE, phibuild, transferbuild, transfer78

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def branch_lines(anum):
    e = LE.get(anum)
    return [L for L in e['comment'] + e['formula']
            if re.search(r'n mod 2', L, re.I)]


def poly_tex(coef, var='n'):
    """coef low degree first, exact Fractions."""
    out = []
    for k in range(len(coef) - 1, -1, -1):
        c = coef[k]
        if c == 0:
            continue
        s = ''
        if c.denominator == 1:
            num = abs(c.numerator)
            body = '' if (num == 1 and k > 0) else str(num)
        else:
            body = rf"\tfrac{{{abs(c.numerator)}}}{{{c.denominator}}}"
        if k == 0:
            s = body or '1'
        elif k == 1:
            s = body + var
        else:
            s = body + var + f"^{{{k}}}"
        out.append(('-' if c < 0 else '+') + ' ' + s)
    if not out:
        return '0'
    t = ' '.join(out)
    return t[2:] if t.startswith('+ ') else t


def build(h):
    a = h['anum']
    K, T, shift = h['K'], h['T'], h['shift']
    order, nterms, nthr, off = h['order'], h['nterms'], h['nthr'], h['offset']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    A = [Fraction(x) for x in h['A']]
    C = [Fraction(x) for x in h['C']]
    tgt = 'n' if shift == 0 else (f'n+{shift}' if shift > 0 else f'n{shift}')
    Btex = ('n+1' if shift == 0 else ('n' if shift == 1 else 'n+1-|s|'))
    Fcond = ('$n$ is even' if shift == 0 else '$n$ is odd')
    brs = branch_lines(a)
    brtex = ''
    if brs:
        # A and C have different degrees, so zip alone silently drops the leading terms of
        # the longer one: pad first.
        m = max(len(A), len(C))
        Ap = A + [Fraction(0)] * (m - len(A))
        Cp = C + [Fraction(0)] * (m - len(C))
        even = poly_tex([x + y for x, y in zip(Ap, Cp)])
        odd = poly_tex([x - y for x, y in zip(Ap, Cp)])
        quoted = '\n\n'.join(esc(L) for L in brs[:2])
        brtex = rf"""
\section{{The two branch formulas}}

The entry also records, as separate empirical observations:
\begin{{quote}}
{quoted}
\end{{quote}}
These follow at once, and are exact: putting $n$ even and $n$ odd into
Theorem~\ref{{thm:quasi}},
\[
a(n)=\begin{{cases}}
{even}, & n\ \text{{even}},\\[2pt]
{odd}, & n\ \text{{odd}},
\end{{cases}}
\]
which is what the entry states.
"""
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by an exact quasi-polynomial}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts triangular arrays of a FIXED shape over the alphabet $0..n$, and carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true. The array
family usually met in this part of the OEIS fixes the alphabet and lets the shape grow, so the
count is a walk count in a finite digraph; here it is the alphabet that grows and there is no
digraph to walk. Inclusion--exclusion over the adjacent pairs, together with the observation
that a set of pairs forces the values along each of its connected components to alternate,
gives $a(n)$ in closed form as a quasi-polynomial of period $2$, exactly and for every $n$.
The recurrence, and the entry's two branch formulas with it, then follow by polynomial
division.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A19, 11B37.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:6])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{What is being counted}}

The array is the triangle with ${K}$ rows: cells $(i,j)$ for $0\le i<{K}$ and $0\le j\le i$,
so $T={T}$ of them. Two cells are adjacent when they are neighbours in that triangle --- side
by side in a row, or one directly below the other on either side --- and there are
$3\binom{{{K}}}{{2}}={h['nedges']}$ adjacent pairs. Each cell carries a value in
$\{{0,1,\dots,n\}}$, and the entry counts those arrays in which EXACTLY ONE adjacent pair
$\{{u,v\}}$ has $x_u+x_v={tgt}$.

Note which parameter grows. The shape is fixed; the alphabet is what $n$ counts. So this is not
a walk in a finite digraph, and nothing about transfer matrices applies.

\section{{A set of pairs forces the values along its components}}

Write $E$ for the set of adjacent pairs, $t={tgt}$ for the target, and for $S\subseteq E$ let
$N(S)$ be the number of arrays satisfying $x_u+x_v=t$ for every pair in $S$ --- and possibly
others.

\begin{{lemma}}\label{{lem:comp}}
Let $S\subseteq E$ and let the graph $(V,S)$ have $c_b$ bipartite and $c_o$ non-bipartite
components among the cells it touches, $v(S)$ cells being touched. Then
\[
N(S)\;=\;(n+1)^{{\,T-v(S)}}\;B^{{\,c_b}}\;F^{{\,c_o}},
\]
where $B=\#\{{c: 0\le c\le n,\ 0\le t-c\le n\}}$ and $F=1$ if $t$ is even with $0\le t/2\le n$,
and $F=0$ otherwise.
\end{{lemma}}

\begin{{proof}}
A pair in $S$ forces $x_v=t-x_u$, so within one connected component of $(V,S)$ the value of any
one cell determines every other: cells at even distance from a chosen root carry the root's
value $c$, cells at odd distance carry $t-c$. That assignment is consistent exactly when no
cycle of the component has odd length; if some cycle does, following it around forces $c=t-c$,
so $2c=t$, and the component admits one value when $t$ is even and $t/2$ lies in the alphabet,
and none otherwise. A bipartite component is therefore free to choose $c$ subject only to
$c$ and $t-c$ both lying in $\{{0,\dots,n\}}$, which is $B$ choices. Cells touched by no pair
of $S$ are unconstrained, giving $(n+1)$ choices each.
\end{{proof}}

Here $B={Btex}$ and $F=1$ precisely when {Fcond}.

\section{{The count}}

\begin{{theorem}}\label{{thm:quasi}}
For every $n\ge0$,
\[
a(n)\;=\;A(n)+(-1)^n\,C(n),\qquad
A(n)={poly_tex(A)},
\]
\[
C(n)={poly_tex(C)}.
\]
\end{{theorem}}

\begin{{proof}}
For an array $x$ let $\sigma(x)$ be its number of satisfied pairs. Then
\[
\sum_{{S\subseteq E}}w^{{|S|}}\,\#\{{x:\ S\subseteq\text{{satisfied pairs of }}x\}}
=\sum_x (1+w)^{{\sigma(x)}},
\]
and differentiating in $w$ at $w=-1$ picks out exactly the arrays with $\sigma(x)=1$:
\[
a(n)\;=\;\sum_{{\emptyset\neq S\subseteq E}}(-1)^{{|S|-1}}\,|S|\;N(S).
\]
Each $N(S)$ is given by Lemma~\ref{{lem:comp}}. The exponents $T-v(S)$, $c_b$ and $c_o$ do not
involve $n$, so the sum was formed once by running over all $2^{{{h['nedges']}}}$ subsets and
recording those three numbers. Every term is a polynomial in $n$ multiplied by $F^{{c_o}}$, and
$F$ depends only on the parity of $n$; collecting the two parities gives a polynomial identity
in $n$ on each, and the displayed $A$ and $C$ are their half-sum and half-difference. The
identity holds for every $n\ge0$, with no threshold: Lemma~\ref{{lem:comp}} is exact at every
$n$.
\end{{proof}}

The degree of $A$ is ${h['degA']}$ and that of $C$ is ${h['degC']}$. Both are at most $T-1$,
because a set $S$ with a single pair leaves $T-2$ cells free and contributes one bipartite
component.
{brtex}
\section{{The recurrence}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
Write $E$ for the shift operator, $(Ea)(n)=a(n+1)$. A polynomial of degree $d$ is annihilated
by $(E-1)^{{d+1}}$ and by nothing smaller, and $(-1)^n$ times a polynomial of degree $d$ is
annihilated by $(E+1)^{{d+1}}$ and by nothing smaller. By Theorem~\ref{{thm:quasi}} the
sequence is therefore annihilated by
\[
(E-1)^{{{h['degA'] + 1}}}(E+1)^{{{h['degC'] + 1}}},
\]
a monic operator of order ${h['minimal']}$, and by no proper divisor of it, since the two
factors act on the two parts independently and neither part is annihilated by less. The
characteristic polynomial of the conjectured recurrence is
$t^{{{order}}}-\sum_i c_it^{{{order}-i}}$; dividing it by the operator above in
$\mathbb{{Z}}[t]$ leaves no remainder, so the conjectured recurrence is a consequence of
Theorem~\ref{{thm:quasi}} and holds wherever every index it names is at least the offset.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the closed form reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the arrays themselves were enumerated for the smallest alphabets --- every assignment
of $0..n$ to the ${T}$ cells written out and its satisfied pairs counted, with no
inclusion--exclusion and no closed form --- and the counts agree. A wrong reading of the cell
set, of the adjacency, or of the target would show here and nowhere else.

Third, the conjectured recurrence was applied directly to the closed form's own values over a
long range, in exact integer arithmetic, and holds throughout; this is independent of the
divisibility argument, which is what actually proves it.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Quasi-polynomials, Section 4.4.)
\bibitem{{beck}} M.~Beck and S.~Robins, \emph{{Computing the Continuous Discretely}}, 2nd ed.,
Springer, 2015.
\bibitem{{comtet}} L.~Comtet, \emph{{Advanced Combinatorics}}, Reidel, 1974.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('transfer78_hits.json')):
        if h.get('FAILS'):
            continue
        dd = f"build/t78{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
        n += 1
    print('wrote', n, 'papers')
