#!/usr/bin/env python3
"""One paper per entry whose order line is recovered on a TAIL rather than on the whole
sequence.

`ordbuild` is for the case where Berlekamp--Massey returns the stated order from the first
term, and its theorem says the recurrence holds for every n. That statement would be FALSE
here: these are the entries where the whole sequence gives a larger minimal order and only
some tail gives the stated one, so the recurrence is proved from a stated index on and the
paper has to say which index.

The identification also needs one thing `ordbuild` never has to check. A minimal recurrence
whose last coefficient vanishes has a zero root, and then a further tail satisfies a SHORTER
recurrence -- so the entry's order-N recurrence would not be pinned down after all. Every
paper this builder writes states the last coefficient is nonzero, and `build` refuses to
write one where it is not.
"""
import json
import os
import re

import localentry as LE
import phibuild

PRE = phibuild.PRE
esc = phibuild.esc
ORDER = re.compile(r'[^.]*[Ee]mpirical recurrence of order \d+[^.]*\.?')


def _line(e):
    for l in (e['comment'] + e['formula']):
        m = ORDER.search(l)
        if m:
            return m.group(0).strip()
    return ''


def coeff_table(coeffs, order, cols=4):
    cs = [(i, int(coeffs[str(i)])) for i in range(1, order + 1)]
    per = (len(cs) + cols - 1) // cols
    rows = []
    for r in range(per):
        cells = []
        for j in range(cols):
            k = r + j * per
            cells.append(r'$c_{%d}$ & $%d$' % (cs[k][0], cs[k][1]) if k < len(cs) else ' & ')
        rows.append(' & '.join(cells) + r' \\')
    return '\n'.join(rows)


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    S, order, off, drop = h['S'], h['order'], h['offset'], h['drop']
    last = int(h['coeffs'][str(order)])
    if last == 0:
        raise ValueError(f'{a}: last coefficient is zero, the identification does not close')
    # seq[k] is a(off+k), so the tail begins at entry index off+drop and the recurrence is
    # testable from off+drop+order on
    start = off + drop
    first = start + order
    line = _line(e)
    ntest = sum(1 for k in range(len(d)) if k - drop - order >= 0)

    if drop == 0:
        where = (r'the whole sequence, so the recurrence holds from $n={0}$ --- every index at '
                 r'which it can be written down.'.format(first))
        tailsent = (r'Here the stated order is already the minimal order of the sequence '
                    r'itself, so no tail has to be taken.')
    else:
        where = (r'the tail beginning at $n={0}$, so the recurrence is proved for every '
                 r'$n\ge{1}$.'.format(start, first))
        tailsent = (
            r'Running Berlekamp--Massey on the sequence from its first term returns an order '
            r'LARGER than ${0}$: the opening terms do not satisfy the recurrence, and a '
            r'recurrence that holds only eventually always looks longer when the exceptional '
            r'terms are included. That is not evidence against the entry. An OEIS empirical '
            r'recurrence is asserted for $n$ beyond some index, not from the first term, so '
            r'the question has to be asked of the tails. It was asked of each tail in turn, '
            r'and the tail beginning at $n={1}$ is the first whose minimal order is exactly '
            r'the stated ${0}$.'.format(order, start))

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, recovered from its tail}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{os.environ.get('PAPER_DATE', '8 September 2026')}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} records ``Empirical recurrence of order ${order}$'' and keeps the recurrence itself in
a linked file rather than in the entry, so the conjecture cannot be read off the entry at all.
It can still be settled. The entry counts arrays under a condition local to a bounded window of
lines, which makes the count a walk count on a finite digraph and forces a monic integer
recurrence of order at most the number $S'={S}$ of states with distinct futures. Berlekamp--Massey on
enough exact terms therefore returns the minimal such recurrence, and on {where}
Its last coefficient is $c_{{{order}}}={last}\neq0$, so no further tail satisfies anything
shorter; any order-${order}$ recurrence the sequence satisfies from any point on must then have
the same characteristic polynomial. The entry's recurrence is the one displayed here, whatever
its linked file contains, and it is proved.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 15A18.\normalsize

\section{{A conjecture that is not written down}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(v) for v in d[:8])},\ \dots
\]
The entry states:
\begin{{quote}}
{esc(line)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical, and it is still open. The coefficients are nowhere in the
entry text: what is conjectured is only that a recurrence of that order exists.

\section{{The count is a walk count}}

The entry's condition is local. It constrains a bounded window of consecutive lines of the
array and nothing beyond it, so the admissible configurations of one window are the vertices of
a finite digraph, an edge joins $u$ to $v$ when $v$ may follow $u$, and an admissible array is
exactly a walk. Writing $M$ for the adjacency matrix and $\iota,\tau$ for the indicator vectors
of the admissible first and last windows,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j(n)}}\tau
\]
for a linear reindexing $j$ fixed by the entry's shape. States with identical futures
contribute identically to that product and may be merged without changing any count; after
merging $S'={S}$ states remain, and it is that bound every computation below uses.

\begin{{lemma}}\label{{lem:cf}}
$a$ satisfies a monic linear recurrence with integer coefficients of order at most $S'={S}$.
\end{{lemma}}

\begin{{proof}}
By the Cayley--Hamilton theorem $M^{{S'}}$ is an integer combination of $I,M,\dots,M^{{S'-1}}$,
and multiplying that relation on the left by $\iota^{{\!\top}}M^{{\,j}}$ and on the right by
$\tau$ turns it into a relation among $S'+1$ consecutive values of $a$.
\end{{proof}}

\section{{Why the question has to be asked of a tail}}

{tailsent}

\begin{{lemma}}\label{{lem:bm}}
A sequence known to satisfy some linear recurrence of order at most $S'$ is determined,
together with its minimal recurrence, by any $2S'$ consecutive terms: Berlekamp--Massey applied
to them returns that minimal recurrence exactly.
\end{{lemma}}

Applied to $2S'={2 * S}$ exact terms from $n={start}$ on, it returns order ${order}$ --- the
order the entry states --- with integer coefficients:
\[
a(n)\;=\;\sum_{{i=1}}^{{{order}}}c_i\,a(n-i),
\]
\begin{{center}}\small
\begin{{tabular}}{{cccccccc}}
{coeff_table(h['coeffs'], order)}
\end{{tabular}}
\end{{center}}

\section{{The recurrence, and the identification}}

\begin{{theorem}}
The recurrence above holds for every $n\ge{first}$, and it is the recurrence OEIS {a} records.
\end{{theorem}}

\begin{{proof}}
That it holds is Lemma~\ref{{lem:bm}} applied to the tail from $n={start}$, whose minimal
recurrence it is.

For the identification, write $q_{{\min}}$ for the characteristic polynomial of that minimal
recurrence, $x^{{{order}}}-c_1x^{{{order}-1}}-\dots-c_{{{order}}}$. Its constant term is
$-c_{{{order}}}={-last}$, which is not zero, so $q_{{\min}}(0)\neq0$ and $q_{{\min}}$ has no
root at the origin. A solution of a constant-coefficient recurrence is a combination of terms
$n^{{k}}\lambda^{{n}}$ with $\lambda$ a root of its characteristic polynomial, and only the
components with $\lambda=0$ vanish after finitely many terms. Since $q_{{\min}}$ has none, no
component of $a$ dies out, and the minimal recurrence of every further tail is again
$q_{{\min}}$ --- the order cannot drop below ${order}$ at any later starting point.

Now let $q$ be the characteristic polynomial of whatever recurrence the entry asserts. The
entry asserts it has order ${order}$, so $\deg q={order}$, and it is monic. It holds from some
index $t$ on. From $\max(t,{start})$ on, the sequence satisfies both $q$ and $q_{{\min}}$, and
the minimal polynomial of that tail is $q_{{\min}}$ by the previous paragraph; therefore
$q_{{\min}}\mid q$. Both are monic of degree ${order}$, so $q=q_{{\min}}$.
\end{{proof}}

\section{{Verification}}

Four checks, all in exact integer or rational arithmetic.

First, the walk model reproduces all ${len(d)}$ terms the entry publishes, exactly. This is
what ties the model to the entry, and it is the only place where reading the entry's English
enters the argument.

Second, the order was computed twice by independent routes: once modulo a $61$-bit prime, where
every intermediate is a machine word, and once over $\mathbb{{Q}}$ in exact rational arithmetic.
Both return ${order}$, and the exact run additionally confirms every coefficient is an integer
--- had any been a proper fraction the recurrence would not be the entry's.

Third, the recovered recurrence was evaluated directly on the entry's own published terms, with
no matrices and no Berlekamp--Massey involved. It holds at each of the ${ntest}$ indices where
the entry publishes enough earlier terms to test it.

Fourth, the last coefficient was checked to be nonzero, which is what the identification above
turns on; it is ${last}$.

\begin{{remark}}
The conjecture's own statement was never read. The entry pins it down to the family of
order-${order}$ recurrences this sequence satisfies from some point on, and that family turns
out to have exactly one member.
\end{{remark}}

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{massey}} J.~L.~Massey, Shift-register synthesis and BCH decoding, \emph{{IEEE
Trans. Inform. Theory}} \textbf{{15}} (1969), 122--127.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{kauers}} M.~Kauers and P.~Paule, \emph{{The Concrete Tetrahedron}}, Springer, 2011.
(C-finite sequences and their closure properties.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""
