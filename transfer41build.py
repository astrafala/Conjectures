#!/usr/bin/env python3
"""Papers for the cell-condition families, plain and up to relabelling."""
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer41, transfer42

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def cond_text(p):
    k, m = p['kind'], p['alpha']
    if k == 'plusminus':
        t = (rf"every cell $v$ has, among its neighbours, one equal to $v+1$ and one equal to "
             rf"$v-1$ --- each required only when that value lies in $\{{0,\dots,{m}\}}$, which "
             rf"is what ``within the range $0..{m}$'' says")
        if p['noadj']:
            t += ", and no cell equals a neighbour"
        return t
    if k == 'complement':
        return rf"no cell $v$ has a neighbour equal to ${m}-v$"
    if k == 'somematch':
        return r"every cell equals at least one of its neighbours"
    if k == 'countself':
        return (r"every cell equals the NUMBER of its neighbours that equal it --- so its "
                r"value is bounded by the size of the neighbour set, which is what makes an "
                r"``integer array'' a finite alphabet here")
    if k == 'summod':
        return rf"no cell equals the sum of its neighbours modulo ${p['mod']}$"
    if k == 'exactly':
        w = ' or '.join(str(x) for x in p['ks'])
        return rf"no cell equals exactly ${w}$ of its neighbours"
    return (r"no cell equals all of its horizontal neighbours, and none differs from all of "
            r"its vertical ones")


import json as _json
_ROSTER_AT_BUILD = {v['anum'] for v in _json.load(open('paper-engines.json')).values()}


def datefor(a):
    """A paper carries the date its result was obtained, not the date of the batch it is
    rebuilt with."""
    return '3 September 2026' if a in _ROSTER_AT_BUILD else '6 September 2026'


def build(h, rel):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    q = (transfer42 if rel else transfer41).parse_name(e['name'])
    transnote = ("" if not q.get('trans') else
                 r""" The entry writes the array with the width fixed and $n$ counting
COLUMNS; transposing it exchanges rows with columns, which exchanges the words ``horizontal''
and ``vertical'' and fixes both diagonals, and everything below is stated in that transposed
frame, where $n$ counts rows.""")
    p = q['p'] if rel else q
    W, al = p['W'], p['alpha']
    D = [tuple(t) for t in p['dirs']]
    dirs = texbits.offsets_tex(D)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    cond = cond_text(p)
    tl = ('' if not p['topleft'] else
          " The entry also fixes the top left cell to zero, which restricts the states an "
          "array may begin in and nothing else.")
    fr = ('' if p['frac'] == 1 else
          rf" The entry counts $1/{p['frac']}$ of that number, and the model divides by "
          rf"${p['frac']}$ before anything is compared.")
    relsec = '' if not rel else rf"""
\section{{Counting patterns rather than arrays}}

The clause ``new values $0..{al}$ introduced in row major order'' says the array is the
canonical representative of its EQUALITY PATTERN. Writing $N_j$ for the patterns using exactly
$j$ letters and $L_i$ for the admissible arrays over an alphabet of $i$ letters,
\[
L_i\;=\;\sum_j N_j\,i(i-1)\cdots(i-j+1),
\]
a triangular system with unit diagonal, so the entry's count $N_1+\dots+N_{{{al + 1}}}$ is a
fixed rational combination of the $L_i$.

That step needs the condition to be invariant under permuting the alphabet, and in this family
most conditions are not: ``next to itself plus and minus one'', ``adjacent to the value
${al}-v$'' and ``equal to the sum modulo $k$'' all compare or combine letters arithmetically.
The condition here is about AGREEMENT alone, so it is invariant and the reduction applies.
"""
    tot = (al + 1) ** W
    note = (rf"""

At $n=1$ the array has {'one row' if off == 1 else 'the smallest shape the entry counts'}, and
the condition is tested there with nothing above or below it; the entry's first term is
${d[0]}$, which the model reproduces along with every later term. That is the cheapest check
that the neighbour set and the boundary have been read the same way the entry reads them: a
condition tested as though the missing rows were present, rather than absent, gives a different
first term. There are ${al + 1}^{{{W}}}={tot}$ possible rows over the entry's own alphabet.""" +
            ('' if rel else rf""" The state count $S={S}$ is exactly ${tot}\cdot{tot + 1}$,
one state for each ordered pair of a row and its possible predecessor, the absent predecessor
included."""))
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{datefor(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over $\{{0,\dots,{al}\}}$ under a condition on each cell
and its neighbours, and carries an empirical recurrence of order ${order}$ contributed by
R.~H.~Hardin. It is true, and it is decidable rather than empirical. Every neighbour named lies
in the three rows $i-1,i,i+1$, so an ordered pair of consecutive rows is a state, the count is
a walk count on $S={S}$ of them, and the conjectured recurrence is then settled by a finite
exact computation.{transnote}
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 68Q45.\normalsize

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

The neighbours of a cell are the cells at the offsets
\[
{dirs},
\]
those falling outside the array being absent. The entry requires that {cond}.{tl}{fr}
{relsec}
\section{{The count is a walk count}}

Every offset above moves the row index by at most one, so whether a cell of row $i$ passes
depends on rows $i-1$, $i$ and $i+1$ and nothing else. Take as vertices the ordered PAIRS
$(p,c)$ of consecutive rows, allowing $p$ to be ABSENT --- that is what lets a walk of no steps
describe a one-row array --- and put an edge $(p,c)\to(c,x)$ exactly when every cell of the
middle row $c$ passes with $p$ above it and $x$ below it. A state with $p$ absent may begin an
array; a state $(p,c)$ accepts when every cell of $c$ passes with nothing below it. An array of
$L$ rows is then a walk of $L-1$ steps, each step settling one row, and every array arises from
exactly one walk. Hence
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau
\]
with $\iota$ the indicator of the beginning states, $\tau$ of the accepting ones, and $j$ the
walk index, which differs from the entry's own $n$ by a constant read off from its published
terms. There are $S={S}$ states, and $a$ is $C$-finite.{note}

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
\bibitem{{comtet}} L.~Comtet, \emph{{Advanced Combinatorics}}, Reidel, 1974.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('uniall_hits.json')):
        en = h.get('engine')
        if h.get('FAILS') or en not in ('transfer41', 'transfer42'):
            continue
        dd = f"build/{en[-2:]}{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h, en == 'transfer42'))
        n += 1
    print('wrote', n, 'papers')
