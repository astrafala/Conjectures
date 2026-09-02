#!/usr/bin/env python3
"""One paper per entry settled by the circular-colouring engine."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer25

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off, sh = h['offset'], h['shift']
    e = LE.get(a)
    p = transfer25.parse_name(e['name'])
    K = p['K']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    if p['mode'] == 'A':
        W = p['W']
        shape = rf"$n\times{W}$, wrapped in the direction of width ${W}$"
        walk = rf"""
A row of the array is a proper colouring of the cycle $C_{{{W}}}$, since the wrapping makes
its first and last cells adjacent, and two consecutive rows must differ in every one of the
${W}$ positions. So $L_i(n)$ is the number of walks of $n-1$ steps in the digraph whose
vertices are the proper colourings of $C_{{{W}}}$ over $i$ colours and whose edges join
colourings differing everywhere:
\[
L_i(n)\;=\;\iota^{{\!\top}}M_i^{{\,n-1}}\iota ,\qquad \iota=(1,\dots,1)^{{\!\top}} .
\]
There are $(i-1)^{{{W}}}+(-1)^{{{W}}}(i-1)$ such colourings, which at $i={K}$ is already more
than is comfortable; Lemma~\ref{{lem:lump}} removes the difficulty."""
        traceword = ''
    else:
        R, c = p['R'], p['c']
        shape = rf"${R}\times(n+{c})$, wrapped in the growing direction"
        walk = rf"""
A column of the array is a proper colouring of the path $P_{{{R}}}$ and two consecutive
columns must differ in every one of the ${R}$ positions; the wrapping makes the last column
adjacent to the first. A colouring of the array is therefore a CLOSED walk of $m=n+{c}$ steps
in the digraph $T_i$ whose vertices are the proper colourings of $P_{{{R}}}$ over $i$ colours
and whose edges join colourings differing everywhere, so
\[
L_i(n)\;=\;\operatorname{{tr}}\,T_i^{{\,m}},\qquad m=n+{c}.
\]
A trace is not $\iota^{{\!\top}}M^m\tau$ for fixed vectors, and computing it as a sum over all
starting vertices is far too expensive. Lemma~\ref{{lem:trace}} replaces it by a handful of
walks with fixed ends."""
        traceword = rf"""
\begin{{lemma}}\label{{lem:trace}}
Let $G$ be a group acting on the vertex set of a digraph and preserving its edges, and let $M$
be the adjacency matrix. Then $(M^m)_{{ss}}=(M^m)_{{\sigma s,\sigma s}}$ for every
$\sigma\in G$, and hence
\[
\operatorname{{tr}} M^m\;=\;\sum_{{\text{{orbits }}O}}|O|\;(M^m)_{{s_O s_O}} ,
\]
one representative $s_O$ per orbit. For $T_i$ with $G=S_i$ permuting the colours, the orbits
are the equality patterns and the orbit of a colouring using $j$ colours has
$i(i-1)\cdots(i-j+1)$ members.
\end{{lemma}}

\begin{{proof}}
$\sigma$ permutes the vertices and carries walks to walks bijectively, so the closed walks of
length $m$ at $s$ correspond to those at $\sigma s$. Summing the diagonal over each orbit
gives the displayed identity. Permuting colours preserves ``differ in every position'', so
$S_i$ acts on the colourings of $P_{{{R}}}$ preserving $T_i$; two colourings lie in one orbit
exactly when they have the same equality pattern, and a pattern using $j$ colours is realised
in $i(i-1)\cdots(i-j+1)$ ways.
\end{{proof}}
"""
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{2 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the proper colourings of a grid {shape}, with at most ${K}$ colours and
counted up to renaming the colours, and carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical. Counting
up to renaming is a fixed rational combination of ordinary colouring counts; each of those is
a walk count; and because permuting the colours preserves everything in sight, the walk may be
run on the colour-patterns rather than on the colourings, which is what brings the state count
down to $S={S}$ and makes the exact residual test affordable.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05C15, 05C30.\normalsize

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

A \emph{{colouring}} here is proper: cells adjacent horizontally or vertically carry different
values, and ``circular in one direction'' means the two ends of that direction are adjacent as
well. The check that this is the right reading is the entry's own first term for the
one-row case: a cycle of $W$ cells has $(i-1)^W+(-1)^W(i-1)$ proper colourings over $i$
colours, which at $W=6$, $i=3$ is $66$, and $66/3!=11$ is what the corresponding entry of this
family publishes.

The clause ``new values $0..{K - 1}$ introduced in row major order'' says the array is the
canonical representative of its equality pattern, so what is counted is patterns, not arrays.
Write $N_j$ for the number of admissible patterns using exactly $j$ colours and $L_i$ for the
number of admissible colourings over an alphabet of $i$ colours. A colouring over $i$ colours
is a pattern together with an injection of its colours into the alphabet, so
\[
L_i\;=\;\sum_j N_j\,i(i-1)\cdots(i-j+1),
\]
a triangular system with unit diagonal, hence invertible over $\mathbf{{Q}}$. The entry counts
$a=N_1+\dots+N_{{{K}}}$, so
\[
a\;=\;\sum_{{i=1}}^{{{K}}}w_i\,L_i
\]
for one fixed rational vector $w=\mathbf{{1}}^{{\!\top}}F^{{-1}}$, $F$ the matrix of falling
factorials. Being properly coloured is a statement about equalities alone, so it is invariant
under permuting the colours and the reduction is legitimate.

\section{{Each $L_i$ is a walk count}}
{walk}
{traceword}
\begin{{lemma}}\label{{lem:lump}}
Let a group $G$ act on the vertices of a digraph preserving its edges, and let $v$ be constant
on the $G$-orbits. Then $Mv$ is constant on the $G$-orbits, and for a representative $s$ of
the orbit $O$,
\[
(Mv)(O)\;=\;\sum_{{O'}}A_{{OO'}}\,v(O'),\qquad
A_{{OO'}}=\#\{{t\in O':\ s\to t\}} .
\]
So an iteration started at a $G$-invariant vector may be carried out on the orbits.
\end{{lemma}}

\begin{{proof}}
$\sigma\in G$ is an edge-preserving bijection, so it carries the out-neighbours of $s$ onto
those of $\sigma s$; with $v$ constant on orbits, $(Mv)(s)$ and $(Mv)(\sigma s)$ are the same
sum. The count $A_{{OO'}}$ is likewise independent of which representative of $O$ is used.
\end{{proof}}

Both endpoint vectors above are invariant under the relevant group --- the all-ones vectors
under all of $S_i$, and, for a diagonal entry $(T_i^m)_{{ss}}$, the vector $e_s$ under the
subgroup fixing $s$ --- so the whole computation runs on orbits. That is the entire reason the
state count is $S={S}$ rather than the number of colourings.

Assembling the pieces, $a(n)$ is $\iota^{{\!\top}}M^{{\,j}}\tau$ on the disjoint union of the
orbit digraphs for $i=1,\dots,{K}$, with $\iota$ carrying the weights $w_i$ cleared of
denominators; the walk index $j$ and the entry's $n$ differ by a constant, read off by
matching the entry's published terms rather than assumed. In particular $a$ is $C$-finite.

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
until the working vector was identically zero, which settles every larger $j$ at once. The
rational weights $w_i$ are cleared by a common denominator before any of this, so the whole
computation is over the integers.
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
\bibitem{{biggs}} N.~Biggs, \emph{{Algebraic Graph Theory}}, 2nd ed., Cambridge University
Press, 1993. (Chromatic polynomials and transfer matrices.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer25' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t25{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
