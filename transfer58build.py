#!/usr/bin/env python3
"""Papers for the adjacency/precedence family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer58

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
    off = h['offset']
    e = LE.get(a)
    p = transfer58.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    items = []
    for r in p['adj']:
        if r[0] == 'all':
            items.append(r'\item every cell carrying $%d$ has exactly $%d$ of its four '
                         r'neighbours carrying $%d$;' % (r[1], r[2], r[3]))
        else:
            items.append(r'\item every cell carrying $%d$ has exactly $%d$ of its two VERTICAL '
                         r'neighbours carrying $%d$ and exactly $%d$ of its two HORIZONTAL '
                         r'neighbours carrying $%d$;' % (r[1], r[2], r[3], r[4], r[5]))
    for kind, v, arg in p['pre']:
        if kind == 'none':
            items.append(r'\item no cell carrying $%d$ has a predecessor carrying $%d$;'
                         % (v, arg[0]))
        elif kind == 'both':
            items.append(r'\item every cell carrying $%d$ has one predecessor carrying $%d$ '
                         r'and the other carrying $%d$;' % (v, arg[0], arg[1]))
        elif len(arg) == 1:
            items.append(r'\item every cell carrying $%d$ has at least one predecessor '
                         r'carrying $%d$;' % (v, arg[0]))
        else:
            items.append(r'\item every cell carrying $%d$ has the two cells to its left, or '
                         r'the two above it, reading $%d$ then $%d$ in that order;'
                         % (v, arg[0], arg[1]))
    body = '\n'.join(items)
    hasadj = bool(p['adj'])
    haspre = bool(p['pre'])
    predef = ('' if not haspre else
              r""" The PREDECESSORS of a cell are the cell immediately to its left and the cell
immediately above it, those that lie inside the array. A cell in the top left corner has none
at all, so a clause demanding a predecessor of a given value forbids that value there --- which
is what makes the first published term what it is.""")
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, and the neighbour set of a cell is carried to itself by that, "
             "so the condition is unchanged.")
    endpar = (r"""An adjacency clause for a row is settled only when the row BELOW it has been
written, so the condition for the LAST row of an array belongs to the end vector, which asks
whether that row is satisfied with nothing below it. The end vector is therefore not the
all-ones vector: a row satisfied only because a further row is written below it does not
finish an array."""
              if hasadj else
              r"""Every clause here reaches backwards only --- to the left and upwards --- so a
row is settled as it is written and every state may end an array; the end vector is the
all-ones vector.""")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ under local conditions relating each cell
to its neighbours or to the cells preceding it. The entry carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical: every condition is settled inside three consecutive array rows, so the count is a
walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05C30, 15A18.\normalsize

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
cells immediately to its left, to its right, above it and below it, those that lie inside the
array.{predef} The entry asks that
\begin{{itemize}}
{body}
\end{{itemize}}
and nothing else.{trans}

\section{{Three rows decide everything}}

\begin{{lemma}}\label{{lem:win}}
Every clause above is decided by three consecutive array rows. An adjacency clause for a cell
of row $i$ reads rows $i-1$, $i$ and $i+1$; a precedence clause for a cell of row $i$ reads
rows $i-2$, $i-1$ and $i$, and columns at most two to the left.
\end{{lemma}}

\begin{{proof}}
The neighbours of a cell lie one step away in each of the four directions, and the predecessors
one step to the left or one step up; a clause naming two cells in a row or column reaches two
steps, never more.
\end{{proof}}

So the state is the pair (row above, current row), with a row not yet written carried as
$\bot$. A step appends a row: the precedence clauses for the NEW row are settled at once,
because everything they read is already written, and the adjacency clauses for the MIDDLE row
of the window are settled because the row below it has just arrived. {endpar} With $M$ the
adjacency matrix of the digraph on those states,
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
enumerate every array of that size in the orientation the entry's own name writes and test each
clause on each cell directly. No window, no state and no transfer matrix are involved, and the
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
            if h.get('engine') == 'transfer58' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t58{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
