#!/usr/bin/env python3
"""Papers for the lumped graph-colouring family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer66, transfer67
from transfer66build import conj_line, wordlist, graph_tex, OFF

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer67.parse_name(e['name'])
    W, N, nG = p['W'], p['N'], p['aut']
    rows, pedges = transfer66.plain_bounds(p)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    gdesc, gshort, vtrans = graph_tex(p)
    dirs = wordlist(p['orig'])
    offs = ', '.join(OFF[w] for w in p['orig'])
    slice_word = 'row' if not p['trans'] else 'column'
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of COLUMNS, so the slice "
                 r"added at each step is a column; transposing exchanges the horizontal and "
                 r"vertical directions and carries each diagonal direction to itself.")
    startsec = (r"""
\section{The cell the entry fixes}

The entry asks for $x(0,0)=0$. That condition is removed here, and paid for once at the end.

\begin{lemma}\label{lem:fibre}
$\Gamma$ is transitive on the vertices of $G$. Consequently the valid arrays with $x(0,0)=v$
are equinumerous for every vertex $v$, and the number with $x(0,0)=0$ is the number of valid
arrays with no condition on any cell, divided by $%d$.
\end{lemma}

\begin{proof}
Transitivity was checked directly on the group computed above: the orbit of one vertex is the
whole vertex set. Given vertices $v,w$ pick $\sigma\in\Gamma$ with $\sigma v=w$; then
$x\mapsto\sigma\circ x$ is a bijection from the valid arrays with $x(0,0)=v$ onto the valid
arrays with $x(0,0)=w$, with inverse given by $\sigma^{-1}$. The $%d$ fibres of
$x\mapsto x(0,0)$ therefore all have the same size and partition the unrestricted count.
\end{proof}
""" % (N, N) if p['start0'] else "")
    fracnote = (r"and the count the entry publishes is that divided by $%d$, by "
                r"Lemma~\ref{lem:fibre}" % N if p['start0'] else
                r"which is what the entry publishes")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{4 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the ways of writing the vertices of a fixed graph $G$ into an array of width
${W}$ so that any two cells adjacent in one of the named directions carry vertices joined by an
edge of $G$; here $G$ is {gshort}. The entry carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical. A slice of
the array would be a state, but there are ${rows}$ legal slices here and that is too many to
carry one by one. The condition names only the edge relation, so the automorphism group of $G$
--- of order ${nG}$ --- acts on the arrays and commutes with the transfer matrix; the walk may
then be run on the ORBITS of slices instead of on the slices, and $S={S}$ of those suffice.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05C15, 05A15, 05C25, 15A18.\normalsize

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

Let $G$ be the graph on the label set $\{{0,1,\dots,{N-1}\}}$ whose vertices are {gdesc}.

An array $x$ is a map from the cells of a rectangle to the vertices of $G$. The entry names the
directions {dirs}, that is the cell offsets
\[
{offs},
\]
and asks that whenever two cells of the array differ by one of those offsets, the two vertices
they carry are joined by an edge of $G$.

Write $\Gamma=\operatorname{{Aut}}(G)$ for the group of adjacency-preserving bijections of the
vertex set. It was computed by backtracking over the vertices in breadth-first order, assigning
each an image consistent with every vertex already placed, and has order $|\Gamma|={nG}$.

\begin{{lemma}}\label{{lem:act}}
For $\sigma\in\Gamma$ the array $\sigma\circ x$ is valid whenever $x$ is, and this is an action
of $\Gamma$ on the set of valid arrays. In particular the count does not depend on how the
vertices of $G$ are labelled.
\end{{lemma}}

\begin{{proof}}
The condition mentions the vertices only through the relation ``joined by an edge'', which
$\sigma$ preserves in both directions. The same argument with an isomorphism between two
labelled copies of $G$ gives the second statement.
\end{{proof}}
{startsec}
\section{{Orbits of slices}}

Take the array one ${slice_word}$ at a time, in the direction in which it grows.{transline}
Every offset the entry names has its two cells either in the same ${slice_word}$ or in two
consecutive ones, so a ${slice_word}$ is a state: let $M$ be the $0/1$ matrix indexed by the
legal ${slice_word}$s with $M_{{uv}}=1$ when $v$ may follow $u$, and let $\tau=\mathbf{{1}}$.
The number of valid arrays of $m$ ${slice_word}$s is $\mathbf{{1}}^{{\!\top}}M^{{m-1}}\tau$.

There are ${rows}$ legal ${slice_word}$s, which is more than can be carried one at a time. They
need not be.

\begin{{lemma}}\label{{lem:lump}}
$\Gamma$ acts on the ${slice_word}$s coordinatewise; $M_{{uv}}=M_{{\sigma u\,\sigma v}}$ for
every $\sigma\in\Gamma$, and $\tau$ is fixed by $\Gamma$. Consequently $M^{{m}}\tau$ is constant
on each $\Gamma$-orbit of ${slice_word}$s, for every $m\ge0$.
\end{{lemma}}

\begin{{proof}}
That $v$ may follow $u$ is again a conjunction of statements ``these two vertices are joined by
an edge'', so $\sigma$ preserves it; and $\tau$ is the all-ones vector. Induct on $m$: if
$w=M^{{m}}\tau$ satisfies $w_{{\sigma u}}=w_u$ then
$(Mw)_{{\sigma u}}=\sum_v M_{{\sigma u\,v}}w_v=\sum_v M_{{u\,\sigma^{{-1}}v}}w_v
=\sum_{{v'}}M_{{uv'}}w_{{\sigma v'}}=(Mw)_u$.
\end{{proof}}

Let $\mathcal{{O}}$ be the set of orbits, $r_O$ a representative of $O$, and
\[
\widehat{{M}}_{{O,O'}}=\#\{{\,v\in O' : M_{{r_O v}}=1\,\}} .
\]
By Lemma~\ref{{lem:lump}} the value $(M^{{m}}\tau)_{{r_O}}$ is what $M^m\tau$ takes on all of
$O$, and one step reads
\[
(M w)_{{r_O}}=\sum_{{O'}}\widehat{{M}}_{{O,O'}}\,w_{{r_{{O'}}}} ,
\]
so the whole walk may be run on $\mathcal{{O}}$. Summing over ${slice_word}$s and grouping,
\[
\mathbf{{1}}^{{\!\top}}M^{{m}}\tau=\sum_{{O\in\mathcal{{O}}}}|O|\,(M^{{m}}\tau)_{{r_O}}
=\iota^{{\!\top}}\widehat{{M}}^{{\,m}}\mathbf{{1}},\qquad \iota_O=|O| ,
\]
{fracnote}. Here $S=|\mathcal{{O}}|={S}$, down from ${rows}$.

The orbit representatives are generated directly rather than by listing the ${slice_word}$s and
grouping them. A ${slice_word}$ is built one cell at a time, carrying the set of $\sigma$ that
have so far written exactly the same prefix; a choice is abandoned as soon as one of them would
write a smaller letter. What reaches the last cell is the lexicographically least member of its
orbit, one per orbit, and the set still tied there is its stabiliser, so
$|O|=|\Gamma|/|\Gamma_{{r_O}}|$ falls out of the same walk.

The walk index and the entry's own $n$ differ by a constant, read off by matching the published
terms rather than assumed. In particular $a$ is $C$-finite.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. The residual $a(n)-\sum_ic_ia(n-i)$ equals
$\iota^{{\!\top}}\widehat{{M}}^{{\,j}}q(\widehat{{M}})\mathbf{{1}}$ for the corresponding walk
index $j$, so the recurrence holds from some point on if and only if that vanishes for all large
$j$, and it is enough to examine $j<S$.
\end{{lemma}}

\begin{{proof}}
Factor $\widehat{{M}}^{{j}}$ out of
$\widehat{{M}}^{{j+{order}}}-\sum_ic_i\widehat{{M}}^{{j+{order}-i}}$. For the bound,
$\widehat{{M}}^{{S}}$ is an integer combination of
$I,\widehat{{M}},\dots,\widehat{{M}}^{{S-1}}$ by Cayley--Hamilton, so the numbers
$u_j=\iota^{{\!\top}}\widehat{{M}}^{{j}}q(\widehat{{M}})\mathbf{{1}}$ obey the monic recurrence
given by its characteristic polynomial; $S$ consecutive zeros force every later one, and the
last nonzero $u_j$ pins the threshold exactly.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(\widehat{{M}})\mathbf{{1}}$ was formed by ${order}$ matrix--vector products in
exact integer arithmetic and $\iota^{{\!\top}}\widehat{{M}}^{{j}}w$ evaluated for
$j=0,1,\dots$, again exactly; those integers vanish from the index corresponding to
$n={nthr}+1$ onwards and the run continued until the working vector was identically zero, which
settles every larger $j$ at once.
\end{{proof}}

\section{{Verification}}

Five checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition, with the
graph rebuilt by a different route---the cube from its corner points and face normals in space,
the icosahedron as a pentagonal antiprism capped at both poles---and the arrays written out cell
by cell, each cell tested against the cells it must be joined to. That recount applies the
entry's own condition on the top-left cell directly, so it tests Lemma~\ref{{lem:fibre}} as well:
no orbit, no lumping and no division is involved in it, and the published terms came back.

Third, the automorphism group was checked to be a group---closed under composition and
inverses---and every one of its ${nG}$ elements verified to preserve the edge set.

Fourth, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fifth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{kemeny}} J.~G.~Kemeny and J.~L.~Snell, \emph{{Finite Markov Chains}}, Springer, 1976.
(Lumping, Section 6.3.)
\bibitem{{cox}} H.~S.~M.~Coxeter, \emph{{Regular Polytopes}}, 3rd ed., Dover, 1973.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer67' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t67{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
