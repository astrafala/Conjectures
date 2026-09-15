#!/usr/bin/env python3
"""Papers for the bounded-difference lower triangles."""
import os, json, re
import localentry as LE, phibuild, transfer80

PRE = phibuild.PRE
esc = phibuild.esc

WORD = {(0, 1): 'horizontal', (1, 0): 'vertical', (1, 1): 'diagonal',
        (1, -1): 'antidiagonal'}


def build(h):
    a = h['anum']
    K, d, kind = h['K'], h['d'], h['kind']
    N, C, thr, off = h['slope'], h['intercept'], h['thr'], h['offset']
    D, bound = h['D'], h['bound']
    dirs = [tuple(t) for t in h['dirs']]
    T = len(transfer80.cells(K))
    nE = len(transfer80.edges(K, dirs))
    e = LE.get(a)
    dat = [int(x) for x in e['data'].split(',') if x.strip()]
    modf, rev = e['modified'], e['revision']
    words = ', '.join(WORD[t] for t in dirs)
    cond = (rf"|x_u-x_v|\le {d}" if kind == 'atmost' else rf"|x_u-x_v|={d}")
    condw = (f"differ by at most ${d}$" if kind == 'atmost' else f"differ by exactly ${d}$")
    quoted = '\n\n'.join(esc(t) for _, t in h['settled'])
    kinds = sorted({k for k, _ in h['settled']})
    kindtxt = ', '.join(kinds[:-1]) + (' and ' + kinds[-1] if len(kinds) > 1 else kinds[0])
    gfsec = ''
    if any(k == 'generating function' for k, _ in h['settled']):
        gfsec = r"""
Since $a$ agrees with a linear polynomial from a known point on, its generating function is a
polynomial divided by $(1-x)^2$: multiplying the series by $(1-x)^2$ annihilates the linear
tail term by term, leaving only finitely many nonzero coefficients, and those coefficients are
the second differences of the values below the threshold. The conjectured generating function
is that one, which was checked coefficient by coefficient in exact rational arithmetic.
"""
    recsec = ''
    if any(k == 'recurrence' for k, _ in h['settled']):
        recsec = rf"""
The conjectured recurrence $a(n)=2a(n-1)-a(n-2)$ is the statement that the second difference
vanishes, which for a linear function it does; it therefore holds for every $n\ge{thr}+2$.
"""
    return rf"""{PRE}
\title{{The empirical {kindtxt} for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the lower triangles of a ${K}\times{K}$ array over $\{{0,\dots,n\}}$ in which
adjacent entries {condw}, and carries {kindtxt} recorded as empirical. The shape here is FIXED
and it is the alphabet that grows, so there is no digraph to walk. What settles it is that the
condition constrains DIFFERENCES only: translating an admissible array by a constant leaves it
admissible, so the arrays split into translation classes, and a class with spread $s$ contains
exactly $\max(0,n+1-s)$ arrays with entries in $\{{0,\dots,n\}}$. Since no spread can exceed
${d}$ times the diameter of the neighbour graph, $a(n)$ is exactly linear from a point that is
known in advance, and two evaluations pin it. Nothing is fitted.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A19, 11B37.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in dat[:6])},\ \dots
\]
The entry states, as conjectures contributed by its author and by later readers and never
marked settled:
\begin{{quote}}
{quoted}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) these are still
recorded as empirical, and nothing on the entry records them as proved.

\section{{What is being counted}}

The lower triangle of a ${K}\times{K}$ array is the set of cells $(i,j)$ with $0\le j\le
i<{K}$, so there are $T={T}$ of them. Two cells are adjacent when they differ by one of the
{words} offsets, which here gives ${nE}$ adjacent pairs. Each cell carries a value in
$\{{0,\dots,n\}}$, and the entry requires
\[
{cond}\qquad\text{{for every adjacent pair }}u,v .
\]

The shape is fixed and $n$ is the size of the ALPHABET. So this is not a walk count and
nothing about transfer matrices applies.

\section{{Translation}}

\begin{{lemma}}\label{{lem:trans}}
Let $\mathcal P$ be the set of integer arrays $y$ on these cells satisfying the same condition
and having least entry $0$, and for $y\in\mathcal P$ write $\mathrm{{sp}}(y)$ for its largest
entry. Then $\mathcal P$ is finite and
\[
a(n)\;=\;\sum_{{y\in\mathcal P}}\max\bigl(0,\;n+1-\mathrm{{sp}}(y)\bigr).
\]
\end{{lemma}}

\begin{{proof}}
The condition depends only on the differences $x_u-x_v$, so if $x$ is admissible so is $x+m$
for any integer $m$, and every admissible $x$ is $y+m$ for exactly one $y\in\mathcal P$ and one
integer $m$, namely $m=\min x$. Given $y$, the array $y+m$ has all entries in
$\{{0,\dots,n\}}$ precisely when $m\ge0$ and $m+\mathrm{{sp}}(y)\le n$, which is
$\max(0,n+1-\mathrm{{sp}}(y))$ values of $m$. Finiteness follows from
Lemma~\ref{{lem:bound}}.
\end{{proof}}

\begin{{lemma}}\label{{lem:bound}}
Every $y\in\mathcal P$ has $\mathrm{{sp}}(y)\le {d}\cdot{D}={bound}$, where ${D}$ is the
diameter of the neighbour graph.
\end{{lemma}}

\begin{{proof}}
The neighbour graph is connected, so any two cells are joined by a path of at most ${D}$
edges, and each edge changes the value by at most ${d}$. Hence the largest and the smallest
entry differ by at most ${d}\cdot{D}$.
\end{{proof}}

\section{{The count}}

\begin{{theorem}}\label{{thm:line}}
\[
a(n)\;=\;{N}\,n{C:+d}\qquad\text{{for every }}n\ge{thr},
\]
and $\mathcal P$ has exactly ${N}$ elements.
\end{{theorem}}

\begin{{proof}}
For $n\ge{bound}$ every term of Lemma~\ref{{lem:trans}} is positive by
Lemma~\ref{{lem:bound}}, so
\[
a(n)=\sum_{{y\in\mathcal P}}\bigl(n+1-\mathrm{{sp}}(y)\bigr)
=|\mathcal P|\,(n+1)-\sum_{{y}}\mathrm{{sp}}(y),
\]
which is a linear function of $n$. Two values determine it, and $a({bound})$ and
$a({bound}+1)$ were computed exactly, giving slope ${N}$ and the stated intercept; the slope
is $|\mathcal P|$. That the identity already holds from $n={thr}$ was then read off by
comparing it with the exact values of $a(n)$ below ${bound}$, each computed the same way.
\end{{proof}}

The counts $a(n)$ themselves are obtained by walking over the cells in row major order and
carrying only the entries a later cell can still see --- for this shape at most ${K}+1$ of
them --- so no array is ever written down.
{gfsec}{recsec}
Each statement quoted in Section 1 is a consequence of Theorem~\ref{{thm:line}}, and each was
also checked directly against it.

\section{{Verification}}

Three checks, each independent of the argument above.

First, the count reproduces all ${h['nterms']}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the arrays themselves were enumerated for the smallest alphabets --- every assignment
of $0..n$ to the ${T}$ cells written out and every adjacent pair tested --- with no
translation argument and no frontier walk. Where the shape is too large for that, the first
term is settled by an exact argument instead: at $n=1$ every entry is $0$ or $1$, so an ``at
most'' condition is no condition and the count is $2^{{{T}}}$, while ``differing by exactly
one'' asks for a proper $2$-colouring of the neighbour graph. Both test the cell set and the
adjacency, which is what this check is for.

Third, the linear form was compared against the entry's own published terms over their whole
range, and the conjectured statements were each evaluated against it in exact arithmetic
rather than sampled.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\bibitem{{comtet}} L.~Comtet, \emph{{Advanced Combinatorics}}, Reidel, 1974.
\bibitem{{kauers}} M.~Kauers and P.~Paule, \emph{{The Concrete Tetrahedron}}, Springer, 2011.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('transfer80_hits.json')):
        if h.get('FAILS'):
            continue
        dd = f"build/t80{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
        n += 1
    print('wrote', n, 'papers')
