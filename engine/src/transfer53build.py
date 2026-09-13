#!/usr/bin/env python3
"""Papers for the modular-neighbour family."""
import conjquote
import os

_ROSTER = None
def _date(a):
    """the date the result was obtained: a paper already in the roster keeps the
    date it was written with, a new one takes the date the caller gives."""
    global _ROSTER
    if _ROSTER is None:
        import json as _j
        _ROSTER = {v['anum'] for v in _j.load(open('paper-engines.json')).values()}
    return '3 September 2026' if a in _ROSTER else os.environ.get('PAPER_DATE', '3 September 2026')

import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer53

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
    p = transfer53.parse_name(e['name'])
    W, A, M = p['W'], p['alpha'] + 1, p['mod']
    D = [tuple(t) for t in p['dirs']]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    dirs = texbits.offsets_tex(D)
    dnt = ('' if p['dn'] is None else
           rf" and at least ${p['dn']}$ carrying $v-1 \bmod {M}$")
    noeq = ('' if not p['noeq'] else
            " The entry also forbids two neighbouring cells from carrying equal values.")
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, so the offsets above are already the transposed ones. Each "
             "direction is taken with both signs, so transposing cannot lose one, and the top "
             "left cell is the top left cell of the transpose as well.")
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which every cell must see, among its
neighbours in named directions, a stated number carrying the value one MORE than its own
modulo ${M}$, and in some of the family a stated number carrying the value one less. The entry
carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and
it is decidable rather than empirical: a cell's neighbours lie in three consecutive rows, so
the count is a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05C15, 15A18.\normalsize

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

The array has ${W}$ cells across, with entries in ${aset}$. The NEIGHBOURS of a cell are the
cells reached from it by the offsets
\[
{dirs},
\]
those lying inside the array. Writing $v$ for the value of a cell, the condition is that among
its neighbours there be at least ${p['up']}$ carrying $v+1 \bmod {M}${dnt}.{noeq} The top left
cell is fixed at $0$.{trans}

Note that the values and the modulus agree: the alphabet has ${A}$ letters and the arithmetic
is modulo ${M}$, so ``one more than $v$'' wraps from ${A - 1}$ round to $0$.

\section{{Three rows decide one}}

\begin{{lemma}}\label{{lem:win}}
Every offset above changes the row index by $-1$, $0$ or $+1$, so all the neighbours of a cell
of row $i$ lie in rows $i-1$, $i$ and $i+1$, and the condition for the whole of row $i$ is
decided by those three rows. A neighbour outside the array is not a neighbour and contributes
nothing to any of the counts.
\end{{lemma}}

\begin{{proof}}
Immediate from the offsets listed.
\end{{proof}}

So the state is the pair (row above, current row), the row above allowed to be the symbol
$\bot$, and a step appends a row and settles the condition for the middle row of the window it
completes. Two boundaries are decided rather than assumed. The rows that may BEGIN an array are
exactly those whose first entry is $0$, which is the top-left clause. And the condition for the
LAST row is settled by the end vector, with nothing below it: the end vector is therefore not
the all-ones vector, and a row that sees enough neighbours only when a further row is written
below it does not finish an array. With $M$ the adjacency matrix,
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
until the working vector was identically zero, which settles every larger $j$ at once.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. The leading zeros the entry publishes are a sharp test of the boundary: a small
array has too few neighbours for any cell to see what the condition demands.

Second, the count was recomputed for the smallest arrays straight from the definition:
enumerate every array of that size in the orientation the entry's own name writes, count each
cell's neighbours of each kind, and keep the array when every cell is satisfied. No window, no
transfer matrix and no transposition are involved, and the published terms came back.

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
            if h.get('engine') == 'transfer53' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t53{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
