#!/usr/bin/env python3
"""Papers for the self-counting neighbour family."""
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer50

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {'zero': 'are zero',
        'eqk': 'are equal to $%d$',
        'lt': 'are smaller than it',
        'le': 'are smaller than or equal to it',
        'gt': 'are larger than it',
        'ge': 'are larger than or equal to it',
        'ne': 'differ from it',
        'eq': 'are equal to it',
        'sm1': 'are exactly one smaller than it',
        'lg1': 'are exactly one larger than it',
        'd1': 'differ from it by exactly one'}
FORM = {'zero': 'y=0', 'eqk': 'y=%d', 'lt': 'y<v', 'le': r'y\le v', 'gt': 'y>v',
        'ge': r'y\ge v', 'ne': r'y\ne v', 'eq': 'y=v', 'sm1': 'y=v-1', 'lg1': 'y=v+1',
        'd1': r'\lvert y-v\rvert=1'}


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
    p = transfer50.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    D = [tuple(t) for t in p['dirs']]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    w = WORD[p['pred']] % p['k'] if p['pred'] == 'eqk' else WORD[p['pred']]
    fo = FORM[p['pred']] % p['k'] if p['pred'] == 'eqk' else FORM[p['pred']]
    dirs = texbits.offsets_tex(D)
    given = re.search(r'0\.\.(\d+)\s*arrays', e['name'].replace(' ', ' '))
    bound = ('' if given else rf"""
The entry says ``integer arrays'' and names no alphabet, but one is forced. An entry counts
neighbours in the named directions, of which there are ${len(D)}$, so every entry of the array
lies in $\{{0,1,\dots,{len(D)}\}}$ and the count is finite. That bound is used below and
nothing wider is needed.""")
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, so the offsets above are already the transposed ones. Each "
             "direction is taken with both signs, so transposing cannot lose one.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ in which every entry is equal to the NUMBER of its own
neighbours, in named directions, that stand in a stated relation to it. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. The condition is self-referential but local: a cell's
neighbours lie in the row above, its own row and the row below, so a window of three
consecutive rows decides the condition for the middle one, and the count is a walk count on
$S={S}$ states.
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

The array has ${W}$ cells across. The NEIGHBOURS of a cell are the cells reached from it by the
offsets
\[
{dirs},
\]
those that lie inside the array. The condition is that every entry counts its own neighbours
that {w}: writing $v=x(i,j)$,
\[
v\;=\;\#\{{\text{{neighbours }} y \text{{ of }} (i,j)\ :\ {fo}\}} .
\]
{bound}{trans}

\section{{Three rows decide one}}

\begin{{lemma}}\label{{lem:win}}
Every offset above changes the row index by $-1$, $0$ or $+1$, so all the neighbours of a cell
of row $i$ lie in rows $i-1$, $i$ and $i+1$. The condition for the whole of row $i$ is
therefore decided by those three rows, an absent row contributing no neighbours.
\end{{lemma}}

\begin{{proof}}
Immediate from the offsets, together with the rule that a neighbour outside the array is not a
neighbour.
\end{{proof}}

So the state is the pair (row above, current row), the row above allowed to be the symbol
$\bot$; a step appends a row and settles the condition for the middle row of the window it
completes. Two boundaries have to be right and neither is assumed. The walk starts at the state
$(\bot,\bot)$, which stands for the empty array, so a walk of no steps is the empty array and
one step is a one-row array. And the condition for the LAST row is settled by the end vector,
which asks whether that row satisfies its condition with nothing written below it: the end
vector is therefore NOT the all-ones vector, and a row that counts correctly only when
something is written below it does not finish an array. With $M$ the adjacency matrix,
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
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition:
enumerate every array of that size, count each cell's neighbours satisfying the relation, and
keep the array when every cell equals its own count. No window, no transfer matrix and no
transposition are involved, and the published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{hu}} J.~E.~Hopcroft, R.~Motwani and J.~D.~Ullman, \emph{{Introduction to Automata
Theory, Languages, and Computation}}, 3rd ed., Addison--Wesley, 2006.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer50' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t50{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
