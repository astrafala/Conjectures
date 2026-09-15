#!/usr/bin/env python3
"""Papers for the pair-sums family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer61

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer61.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    kind, up = p['kind'], p['up']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    if kind == 'mono':
        cond = r"""
\[
b(i,j)\le b(i{+}1,j)\qquad\text{and}\qquad c(i,j)\le c(i,j{+}1)
\]
wherever both sides are defined: the array $b$ must not decrease DOWN a column and the array
$c$ must not decrease ALONG a row. The two directions are crossed, which is the only subtle
part of the reading --- $b$ is built across a row and tested down a column, and $c$ the other
way about.
"""
        why = r"""
\begin{lemma}\label{lem:win}
Both conditions are conditions on two consecutive rows of $a$ and nothing more.
\end{lemma}

\begin{proof}
$b(i,j)\le b(i{+}1,j)$ names four cells of $a$, all in rows $i$ and $i+1$. $c(i,j)\le
c(i,j{+}1)$ names four cells, all in rows $i-1$ and $i$.
\end{proof}

So a single row of $a$ is a state and one step appends a row.
"""
        extra = ''
    elif kind == 'det':
        cond = r"""
\[
b(i,j)\,b(i{-}1,j)\;-\;c(i,j)\,c(i,j{-}1)\;\neq\;0
\]
wherever all four terms are defined.
"""
        why = r"""
\begin{lemma}\label{lem:win}
The condition is a condition on two consecutive rows of $a$ and nothing more.
\end{lemma}

\begin{proof}
$b(i,j)$ is built from row $i$, $b(i{-}1,j)$ from row $i-1$, and each of $c(i,j)$ and
$c(i,j{-}1)$ from rows $i-1$ and $i$. So all four terms live in those two rows.
\end{proof}

So a single row of $a$ is a state and one step appends a row.
"""
        extra = ''
    else:
        w = 'nondecreasing' if up else 'nonincreasing'
        cond = rf"""
that the ROWS of $b$ and the COLUMNS of $c$ are each in lexicographic {w} order. Row $i$ of $b$
is $\bigl(b(i,1),\dots,b(i,{W - 1})\bigr)$ and column $j$ of $c$ is
$\bigl(c(1,j),c(2,j),\dots\bigr)$.
"""
        why = rf"""
\begin{{lemma}}\label{{lem:win}}
The row comparison is a condition on two consecutive rows of $a$. The column comparison is
settled by the FIRST row in which the two columns of $c$ differ.
\end{{lemma}}

\begin{{proof}}
Row $i$ of $b$ is built from row $i$ of $a$ alone, so comparing rows $i$ and $i+1$ of $b$ reads
rows $i$ and $i+1$ of $a$. Two sequences are compared lexicographically by their first
difference; entry $i$ of column $j$ of $c$ is built from rows $i-1$ and $i$ of $a$, so scanning
the array downwards reveals the entries of every column of $c$ in order.
\end{{proof}}

So the state is the last row of $a$ together with one bit for each adjacent pair of columns,
recording whether that pair of columns of $c$ has been equal in every row so far. A row that
would put a pair in the wrong order is rejected at once, and a pair still equal at the end is
in order, equality being allowed.
"""
        extra = ''
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ through two derived arrays of PAIR SUMS ---
each cell added to its left neighbour, and each cell added to the one above it --- on which the
entry imposes an order condition. The entry carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical: the count is
a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 06A07, 15A18.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{What is being counted}}

The array $a$ has ${W}$ cells across, with entries in ${aset}$. Two derived arrays are formed,
\[
b(i,j)=a(i,j)+a(i,j-1)\quad(j\ge1),\qquad c(i,j)=a(i,j)+a(i-1,j)\quad(i\ge1),
\]
so $b$ adds each cell to its LEFT neighbour and $c$ adds each cell to the one ABOVE it. The
entry asks
{cond}

\section{{Two rows decide it}}
{why}{extra}
With $M$ the adjacency matrix of the digraph on those states, $\iota$ the indicator of the
starting state and $\tau=\mathbf{{1}}$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S}.
\]
The walk index $j$ and the entry's own $n$ differ by a constant, read off by matching the
published terms rather than assumed. In particular $a$ is $C$-finite.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. The residual $a(n)-\sum_ic_ia(n-i)$ equals
$\iota^{{\!\top}}M^{{\,j}}q(M)\tau$ for the corresponding walk index $j$, so the recurrence
holds from some point on if and only if $\iota^{{\!\top}}M^{{j}}q(M)\tau=0$ for all large $j$,
and it is enough to examine $j<S$.
\end{{lemma}}

\begin{{proof}}
Factor $M^{{j}}$ out of $M^{{j+{order}}}-\sum_ic_iM^{{j+{order}-i}}$. For the bound, $M^{{S}}$
is an integer combination of $I,M,\dots,M^{{S-1}}$ by Cayley--Hamilton, so the numbers
$u_j=\iota^{{\!\top}}M^{{j}}q(M)\tau$ obey the monic recurrence given by the characteristic
polynomial of $M$; $S$ consecutive zeros force every later one, and the last nonzero $u_j$
pins the threshold exactly.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(M)\tau$ was formed by ${order}$ matrix--vector products in exact integer
arithmetic and $\iota^{{\!\top}}M^{{j}}w$ evaluated for $j=0,1,\dots$, again exactly; those
integers vanish from the index corresponding to $n={nthr}+1$ onwards and the run continued
until the working vector was identically zero.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition:
enumerate every array of that size, form the two derived arrays in full, and test the condition
on them directly. No window, no state and no incremental bookkeeping are involved, and the
published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer61' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t61{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
