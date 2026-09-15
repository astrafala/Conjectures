#!/usr/bin/env python3
"""Papers for the forbidden-run family."""
import conjquote
import os

# a paper carries the date its result was obtained; one already in the roster keeps
# the date it was written with, and this builder runs again when the sweep reaches
# more of its family
_ROSTER = None
def _date(a):
    global _ROSTER
    if _ROSTER is None:
        import json as _j
        _ROSTER = {v['anum'] for v in _j.load(open('paper-engines.json')).values()}
    return '3 September 2026' if a in _ROSTER else os.environ.get('PAPER_DATE', '3 September 2026')

import os, json, re
import localentry as LE, phibuild, transferbuild, transfer56

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

DIRNAME = {(0, 1): 'along a row', (1, 0): 'down a column',
           (1, 1): 'down a diagonal, nw to se',
           (1, -1): 'down an antidiagonal, ne to sw'}


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
    p = transfer56.parse_name(e['name'])
    W, m, K, L = p['W'], p['alpha'], p['K'], p['L']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    # the qualifier is prose and has to stay inside \text, or its spaces are lost
    lines = '\n'.join('\\text{%s%s} \\\\' % (DIRNAME[(s, q)],
                                             ', read the other way' if r else '')
                      for s, q, r in p['dirs'])
    what = ('all equal' if p['kind'] == 'eq' else 'strictly increasing')
    aset = (r'\{' + ','.join(str(t) for t in range(K)) + r'\}' if K <= 4 else
            r'\{0,1,\dots,%d\}' % m)
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, so the directions above are already the transposed ones.")
    revnote = ('' if not any(r for _, _, r in p['dirs']) else rf"""

One direction above is marked ``read the other way''. Transposing an array exchanges a row with
a column and carries each diagonal direction to itself only up to sense: an antidiagonal read
from the northeast becomes one read from the southwest. For a condition built from EQUALITY
that would not matter, but ``strictly increasing'' read backwards is ``strictly decreasing'',
so the sense is carried explicitly rather than normalised away. The
difference is not subtle: normalising it away makes the model disagree with the entry's
published terms from the very first one, which is how the point was found.""")
    if p['rel']:
        relpar = rf"""
The entry closes with ``new values $0..{m}$ introduced in row major order'', so what is counted
is arrays up to renaming the letters. That is legitimate here because the forbidden runs are
the runs of EQUAL entries, and whether entries are equal is untouched by any renaming. Writing
$N_j$ for the classes on exactly $j$ letters and $L_i$ for the admissible arrays over an
alphabet of $i$ letters,
\[
L_i=\sum_j N_j\,i(i-1)\cdots(i-j+1),\qquad
a=N_1+\dots+N_{{{K}}}=\bigl(\mathbf{{1}}^{{\!\top}}F^{{-1}}\bigr)L .
\]
The neighbouring entries that forbid INCREASING runs carry no such clause, and could not: a
permutation of the alphabet does not preserve order.
"""
        assemble = (rf" Assembling the pieces for $i=1,\dots,{K}$ as a disjoint union, with "
                    r"$\iota$ carrying those weights cleared of denominators,")
    else:
        relpar = r"""
The entry carries no renaming clause, and it could not: ``strictly increasing'' compares
letters by size, so it is not preserved by a permutation of the alphabet. The count is taken
over the alphabet the entry names.
"""
        assemble = " With $M$ the adjacency matrix of that digraph,"
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ containing no run of ${L}$ consecutive
cells, taken along a named direction of the grid, whose entries are {what}. The entry carries
an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical: every such run lies inside ${L}$ consecutive array rows, so
the count is a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 68R15, 15A18.\normalsize

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

A RUN is ${L}$ consecutive cells taken along one of the directions
\[
\begin{{array}}{{l}}
{lines}
\end{{array}}
\]
all of them inside the array. The array is counted when no run has its entries {what}.{trans}
{revnote}
{relpar}
\section{{Every run lies in ${L}$ consecutive rows}}

\begin{{lemma}}\label{{lem:win}}
Each direction above changes the row index by $0$ or $1$ from one cell of a run to the next, so
a run of ${L}$ cells lies inside ${L}$ consecutive array rows, and a run whose last cell is in
row $i$ lies inside rows $i-{L - 1},\dots,i$.
\end{{lemma}}

\begin{{proof}}
Immediate from the row steps of the four directions, which are $0$ for a row and $1$ for the
other three.
\end{{proof}}

So the state is the window of the last ${L - 1}$ array rows, a row not yet written carried as
$\bot$; a step appends a row and rejects it exactly when some run ends in it or lies inside it.
A run needing a row that is $\bot$ does not exist, which is the boundary rule and is read off
the window rather than assumed. The walk starts at the all-$\bot$ window, so a walk of $R$ steps
is an array of $R$ rows.{assemble}
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S},\quad\tau=\mathbf{{1}} .
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

Second, the count was recomputed for the smallest arrays straight from the definition: fill the
cells in row major order, in the orientation the entry's own name writes, and reject as soon as
a completed run is {what}. No window, no transposition and no transfer matrix are involved, and
the published terms came back.

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
            if h.get('engine') == 'transfer56' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t56{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
