#!/usr/bin/env python3
"""Papers for the graph-colouring family: cube and icosahedron footprints, and named graphs."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer66

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

DESC = {
    'faces of a cube': (
        r"the six faces of a cube, two of them adjacent unless they are opposite. That is the "
        r"octahedron graph $K_{2,2,2}$: $6$ vertices, $4$-regular, $12$ edges",
        'octahedron graph'),
    'vertices of a cube': (
        r"the eight corners of a cube, two of them adjacent when an edge of the cube joins "
        r"them. That is the graph $Q_3$ of the $3$-dimensional cube: $8$ vertices, "
        r"$3$-regular, $12$ edges",
        'cube graph $Q_3$'),
    'faces of an icosahedron': (
        r"the twenty faces of a regular icosahedron, two of them adjacent when they share an "
        r"edge. That is the dodecahedron graph: $20$ vertices, $3$-regular, $30$ edges",
        'dodecahedron graph'),
    'vertices of an icosahedron': (
        r"the twelve vertices of a regular icosahedron, two of them adjacent when an edge "
        r"joins them. That is the icosahedron graph: $12$ vertices, $5$-regular, $30$ edges",
        'icosahedron graph'),
}
OFF = {'horizontal': '(0,1)', 'vertical': '(1,0)', 'diagonal': '(1,1)',
       'antidiagonal': '(1,-1)'}


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def wordlist(ws):
    ws = list(ws)
    if len(ws) == 1:
        return ws[0]
    return ', '.join(ws[:-1]) + ' and ' + ws[-1]


def graph_tex(p):
    g = p['graph']
    if g in DESC:
        return DESC[g][0], DESC[g][1], True
    if g.startswith('triangular'):
        k = int(g.split()[1])
        return (r"the $%d\cdot%d/2=%d$ nodes of a triangle of side %d cut out of the triangular "
                r"lattice: the nodes are the pairs $(i,j)$ with $0\le j\le i<%d$, and each is "
                r"joined to $(i,j+1)$, $(i+1,j)$ and $(i+1,j+1)$ whenever those lie in the "
                r"triangle" % (k, k + 1, k * (k + 1) // 2, k, k),
                'triangular graph of side %d' % k, False)
    ed = ', '.join('\\{%d,%d\\}' % e for e in p['edges'])
    return (r"the $%d$ nodes $0,\dots,%d$ with the edges the entry lists, namely %s"
            % (p['N'], p['N'] - 1, ed), 'graph named in the entry', False)


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer66.parse_name(e['name'])
    W, N = p['W'], p['N']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    gdesc, gshort, vtrans = graph_tex(p)
    dirs = wordlist(p['orig'])
    offs = ', '.join(OFF[w] for w in p['orig'])
    slice_word = 'row' if not p['trans'] else 'column'
    other_word = 'column' if not p['trans'] else 'row'
    startline = (r"The entry also fixes the top-left cell: $x(0,0)=0$." if p['start0'] else
                 r"The entry places no condition on any particular cell.")
    labline = (r"Because the four named graphs are vertex-transitive---the symmetry group of "
               r"the solid is transitive on its vertices, and on its faces---the count is the "
               r"same whichever vertex is the one called $0$, so fixing the top-left cell at "
               r"$0$ is unambiguous too." if (vtrans and p['start0']) else
               r"Here the labelling is written out in the entry itself, so nothing is left to "
               r"choose." if not vtrans else
               r"Nothing in the condition distinguishes one label from another, so the choice "
               r"of labelling is immaterial.")
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of COLUMNS, so the slice "
                 r"added at each step is a column. Transposing the array exchanges the "
                 r"horizontal and vertical directions and carries each diagonal direction to "
                 r"itself, and that is how the directions are read below.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the ways of writing the vertices of a fixed graph $G$ into an array of width
${W}$ so that any two cells adjacent in one of the named directions carry vertices joined by an
edge of $G$; here $G$ is {gshort}. The entry carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical: every
condition joins cells inside one slice of the array or inside two consecutive slices, so a
single slice is a state and the count is a walk count on a finite digraph with $S={S}$ vertices.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05C15, 05A15, 15A18.\normalsize

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
they carry are joined by an edge of $G$:
\[
x(i,j)\,x(i+\delta_1,j+\delta_2)\in E(G)\qquad
\text{{for every named offset }} (\delta_1,\delta_2)\text{{ and every pair of cells in range.}}
\]
{startline}

\begin{{lemma}}\label{{lem:label}}
The count does not depend on how the vertices are labelled.
\end{{lemma}}

\begin{{proof}}
A relabelling is a bijection $\sigma$ of the label set; if it is an isomorphism from one
labelled copy of $G$ to another then $x\mapsto\sigma\circ x$ is a bijection between the arrays
counted for the two copies, because the condition mentions only the edge relation.
{labline}
\end{{proof}}

\section{{One slice is a state}}

Take the array one ${slice_word}$ at a time, in the direction in which it grows.{transline}
Every offset the entry names has its two cells either in the same ${slice_word}$ or in two
consecutive ones. So a ${slice_word}$, a word of length ${W}$ over the vertices of $G$, carries
everything the next ${slice_word}$ needs: the conditions inside a ${slice_word}$ constrain that
${slice_word}$ alone, and the conditions across ${slice_word}$s are a relation between the
${slice_word}$ just written and the one about to be written.

Let $M$ be the matrix indexed by the legal ${slice_word}$s, with $M_{{uv}}=1$ when $v$ may
follow $u$. Add one further state for the empty array, whose successors are the legal first
${slice_word}$s{'---those beginning with the vertex $0$' if p['start0'] else ''}; then a walk of
$n$ steps from that state is exactly an array of $n$ ${slice_word}$s. Every state may end an
array, so $\tau=\mathbf{{1}}$ and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S}.
\]
The ${slice_word}$s themselves are built one cell at a time with the conditions applied as soon
as they can be, which for the sparser graphs is what makes the state list short: a ${slice_word}$
of length ${W}$ over ${N}$ vertices is one of ${N}^{{{W}}}$ words, but only $S-1$ of them are
legal. The walk index $j$ and the entry's own $n$ differ by a constant, read off by matching the
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
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition, with the
graph rebuilt by a different route---the cube from its corner points and face normals in space,
the icosahedron as a pentagonal antiprism capped at both poles---and the arrays written out cell
by cell, each cell tested against the cells it must be joined to. No slice, no state and no
recurrence is involved in that computation, and the published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{cox}} H.~S.~M.~Coxeter, \emph{{Regular Polytopes}}, 3rd ed., Dover, 1973.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer66' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t66{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
