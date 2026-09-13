#!/usr/bin/env python3
"""One paper per entry settled by the reciprocal-link engine."""
import conjquote
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer24

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def dirtex(D):
    return texbits.offsets_tex(D)


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off, sh = h['offset'], h['shift']
    e = LE.get(a)
    p = transfer24.parse_name(e['name'])
    W, deg = p['W'], p['deg']
    D = [tuple(t) for t in p['dirs']]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    trans = ('' if re.search(r'n\s*X', e['name']) else
             " The entry writes the array with $n$ as the number of COLUMNS; transposing it "
             "exchanges the two coordinates of every neighbour offset, which is done once, "
             "before anything else, so that the walk always runs down the rows.")
    obj = ('a matching' if deg == 1 else
           'a disjoint union of cycles, since every vertex of the link graph has degree $0$ '
           'or $2$')
    extra = ''
    if p['nocoll']:
        extra = (r"""
The entry adds \emph{that no two consecutive links be collinear}: at a vertex carrying two
links their offsets may not be opposite. This is a condition on one vertex and its two links,
so it is decided at the moment that vertex's degree is settled, and costs the construction
nothing.""")
    if p['noloop3']:
        extra = (r"""
The entry adds \emph{without $3$-loops}: no three mutually linked vertices. Any three cells
that are pairwise neighbours under one of these sets lie in two consecutive rows --- three
cells of one row cannot be pairwise adjacent, the outer two being two columns apart --- so a
triangle is visible to a boundary that carries, besides the crossing edges, the horizontal
edges of the row above. The state is enlarged by those, and every triangle is caught as the
lower of its two rows is placed.""")
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{2 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the ways of linking the cells of a grid ${W}$ cells wide, each cell either to
itself or to exactly ${deg}$ of its neighbours, the links being reciprocal, and carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. A reciprocal link is an undirected edge and a self-link is
no edge, so what is counted is the spanning subgraphs of a grid graph in which every vertex
has degree $0$ or ${deg}$; the edges crossing the boundary between two consecutive rows are a
state, the count is a walk count on $S={S}$ of them, and the conjectured recurrence is then
settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05C30, 05C70.\normalsize

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

\section{{What is being counted}}

A link is \emph{{reciprocal}}: if $u$ is linked to $v$ then $v$ is linked to $u$. So the links
of a configuration are the edges of an undirected graph on the cells, and a cell ``linked to
itself'' is a cell lying in no edge. The neighbour relation the entry names is the offset set
\[
{dirtex(D)},
\]
and the condition ``either to themselves or to exactly ${deg}$ neighbours'' says that in that
graph every cell has degree $0$ or ${deg}$. Hence $a(n)$ counts the spanning subgraphs of the
grid graph on the offset set above, of $n$ rows and ${W}$ columns,
whose every degree is $0$ or ${deg}$: {obj}.{trans}

One point of the English has to be fixed rather than guessed: whether a cell may spend both of
its links on the same neighbour. It may not. For the king-move neighbourhood the $1\times2$
and $2\times2$ counts are the degree-$0$-or-$2$ subgraphs of $K_2$ and of $K_4$, which are $1$
and $1+4+3=8$ with simple edges and larger if a doubled edge were allowed; the entries of that
family publish $1$ and $8$. The reading is in any case pinned entry by entry, because the
model below is required to reproduce every term the entry publishes.
{extra}

\section{{The count is a walk count}}

Every offset above changes the row index by at most one, so an edge either lies inside a row
or crosses the boundary between two consecutive rows. Take as state the set of edges crossing
one boundary. Placing a row means choosing the horizontal edges inside it and the edges it
sends down to the next row; at that moment each of its cells knows all of its links --- those
arriving from the row above, those inside the row, those going down --- so its degree, and any
condition on the pair of links at a cell, is settled there and never revisited.

Reading a configuration from the top therefore gives a walk that begins at the empty boundary,
takes one step per row, and ends at the empty boundary, and every such walk comes from exactly
one configuration. With $M$ the adjacency matrix of the digraph on the $S={S}$ reachable
states and $\iota,\tau$ the indicator vectors of the empty boundary,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau ,
\]
so $a$ is $C$-finite. States are generated from the empty boundary outward, so only the
reachable ones are ever built; the alignment of the walk index with the entry's own $n$ was
checked against its published terms rather than assumed.

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
until the working vector was identically zero, which settles every larger $j$ at once.{tight}
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the model to the entry: the digraph is built by reading the
entry's English, and a misreading gives different counts.

Second, the conjectured recurrence was evaluated directly on those published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{lovasz}} L.~Lov\'asz and M.~D.~Plummer, \emph{{Matching Theory}}, AMS Chelsea,
2009.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer24' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t24{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
