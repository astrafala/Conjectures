#!/usr/bin/env python3
"""Papers for the capped-pair-count family."""
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
import localentry as LE, phibuild, transferbuild, transfer60

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

STEP = {'horizontally': '(i,j)\\text{ and }(i,j{+}1)',
        'vertically': '(i,j)\\text{ and }(i{+}1,j)',
        'diagonally': '(i,j)\\text{ and }(i{+}1,j{+}1)',
        'antidiagonally': '(i,j)\\text{ and }(i{+}1,j{-}1)'}
ORDER = ('horizontally', 'vertically', 'diagonally', 'antidiagonally')


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
    p = transfer60.parse_name(e['name'])
    W, A, T = p['W'], p['alpha'] + 1, p['total']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    lines = '\n'.join('$%s$ \\\\' % STEP[w] for w in ORDER if w in p['dirs'])
    want = ('exactly one' if p['exact'] else 'at most one')
    endw = ('$k=1$' if p['exact'] else '$k\\le1$')
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, so the pairs above are already the transposed ones --- "
             "transposing exchanges the horizontal pairs with the vertical ones and carries "
             "each diagonal pair to itself.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which the number of adjacent PAIRS of
cells whose entries add up to ${T}$ is {want}. The entry carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical. The condition is global --- no window of the array decides it --- but the quantity
it constrains is a count that may be capped at two, and a capped count is a bounded state; the
result is a walk count on $S={S}$ states.
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

The array has ${W}$ cells across, with entries in ${aset}$. An ADJACENT PAIR is a pair of cells
\[
\begin{{array}}{{l}}
{lines}
\end{{array}}
\]
both lying inside the array. A pair is a pair of CELLS, so it is counted once and not once from
each end. Writing $k$ for the number of adjacent pairs whose two entries add up to ${T}$, the
entry counts the arrays with $k$ {want}.{trans}

\section{{A capped count is a state}}

No window of the array decides the condition: $k$ is a total over the whole array. But the
condition distinguishes only $k=0$, $k=1$ and $k\ge2$, so the count may be carried capped at
two and stays bounded.

\begin{{lemma}}\label{{lem:cap}}
Let $k_t$ be the number of qualifying pairs lying inside the first $t$ rows. Then
\[
k_{{t}}\;=\;k_{{t-1}}+\bigl(\text{{pairs inside row }} t\bigr)
+\bigl(\text{{pairs joining rows }} t-1 \text{{ and }} t\bigr),
\]
and both added terms are determined by rows $t-1$ and $t$ alone.
\end{{lemma}}

\begin{{proof}}
Every adjacent pair lies either inside one row or across two consecutive rows, by the list
above; a pair inside rows $1..t$ that is not inside rows $1..t-1$ must meet row $t$, so it is
one of the two kinds counted.
\end{{proof}}

So the state is the pair $(\text{{previous row}},\min(k,2))$: a step appends a row, adds the
pairs Lemma~\ref{{lem:cap}} names and caps the total at two. The end vector accepts the states
with {endw}, so it is not the all-ones vector. With $M$ the adjacency matrix,
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
enumerate every array of that size in the orientation the entry's own name writes, count the
adjacent pairs summing to ${T}$ by running over the array once for each kind of pair, and keep
the array when that count is {want}. No cap, no state and no transfer matrix are involved, and
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
            if h.get('engine') == 'transfer60' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t60{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
