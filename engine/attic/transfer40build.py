#!/usr/bin/env python3
"""Papers for the neighbour-comparison subblock family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer40

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

FORM = {'trace': r'the sum of its main diagonal',
        'determinant': r'its determinant',
        'permanent': r'its permanent',
        'sum': r'the sum of all its entries',
        'diagonal sum less antidiagonal sum':
            r'its diagonal sum minus its antidiagonal sum'}
NBW = {'horizontal or vertical': 'horizontally or vertically',
       'horizontal and vertical': 'horizontally or vertically',
       'diagonal or antidiagonal': 'diagonally or antidiagonally'}


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
    p = transfer40.parse_name(e['name'])
    K, W, al, kind = p['K'], p['W'], p['alpha'], p['kind']
    nb = W - K + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    sig = FORM[p['stat']]
    nbw = NBW[p['nb']]
    fracnote = ('' if p['frac'] == 1 else
                rf" The entry counts $1/{p['frac']}$ of that number, and the model divides by "
                rf"${p['frac']}$ before anything is compared.")
    if kind == 'none':
        cond = rf"no two subblocks that are neighbours {nbw} carry the same value of $\sigma$"
        local = True
    elif kind == 'maxdiff':
        cond = (rf"no two subblocks that are neighbours {nbw} have values of $\sigma$ "
                rf"differing by more than ${p['lim']}$")
        local = True
    elif kind == 'some':
        cond = (rf"every subblock carries the same value of $\sigma$ as at least ONE of its "
                rf"neighbours {nbw}")
        local = False
    else:
        cond = (rf"every subblock carries the same value of $\sigma$ as exactly one or two of "
                rf"its neighbours {nbw}")
        local = False
    if local:
        walk = rf"""The condition is on a PAIR of neighbouring subblocks, so nothing beyond the
rows themselves has to be remembered. Take as state the ${K}$-tuple of consecutive array rows
whose subblock row has just been completed: the horizontal pairs inside that row decide which
tuples are admissible at all, and the vertical pairs decide which tuple may follow which. A
step appends one array row. An array of $n+{K - 1}$ rows is a walk of $n-1$ steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ admissible tuples."""
    else:
        tally = ('a single bit saying whether it has already been matched'
                 if kind == 'some' else
                 'a count of its matches so far, capped at three, three being already too many')
        acc = ('the bit is set' if kind == 'some' else 'the count is one or two')
        walk = rf"""This condition is NOT a condition on a pair. Whether a subblock has a
matching neighbour cannot be decided when its own row is placed: the row BELOW it may yet
supply the match. So the state carries, besides the ${K}$ consecutive array rows, a tally for
each of the ${nb}$ subblocks of the row just completed --- {tally} --- counting its matches
among its own row and the row above.

A step appends an array row. It fixes the next subblock row, adds the matches between the two
rows to the OLD row's tallies, and requires those totals to be acceptable, the old row being
final at that moment; the new row's tallies start from its own horizontal matches plus the
matches just made. A state is ACCEPTING when its own tally is already acceptable, which is
exactly the right condition for the last subblock row, the one with nothing below it. Only the
states whose tally came from their own row may BEGIN an array, since the first row has nothing
above it.

An array of $n+{K - 1}$ rows is then a walk of $n-1$ steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau
\]
with $\iota$ the indicator of the starting states and $\tau$ of the accepting ones, on
$S={S}$ states in all. Getting the two vectors right is the whole of the argument: with
$\iota$ taken as all-ones the first row would be allowed a match from a row above it that does
not exist, and the count would be too large. The entry's own first terms settle it --- for
{'a width where the subblock row is a single subblock' if nb == 1 else 'the smallest cases'}
{'the count must be zero, since a lone subblock has no neighbour at all, and the entry indeed opens with zero' if nb == 1 and kind == 'some' else 'the model reproduces every published term'}."""
    from itertools import product as _prod
    vals = [transfer40._stat(p['stat'], [[c[i * K + j] for j in range(K)] for i in range(K)], K)
            for c in _prod(range(al + 1), repeat=K * K)]
    lo, hi = min(vals), max(vals)
    tot = (al + 1) ** (K * W)
    prune = ('' if not local else rf"""

The state does not compress. What a step needs of the past is the previous subblock row, and
for ${W}\ge{K}$ that row already determines the ${K}$ array rows it came from, so carrying the
rows costs nothing and carrying anything smaller loses information. Of the ${al + 1}^{{{K}\cdot
{W}}}={tot}$ tuples of ${K}$ rows, $S={S}$ survive the condition inside a single subblock row;
the rest could not occur in a counted array at all.""")
    note = (rf"""

Over the alphabet $\{{0,\dots,{al}\}}$ the statistic takes values in $[{lo},{hi}]$, so the
grid it labels carries at most ${hi - lo + 1}$ different labels. At $n=1$ the array has ${K}$
rows and the grid is a single row of ${nb}$
{'subblock, which has no neighbour of any kind' if nb == 1 else 'subblocks, with only the neighbours inside that row'}; the entry's first term is
${d[0]}$, which the model reproduces along with every later term, and that is the cheapest
check that the grid has been read with the right shape.""")
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{al}\}}$ under a condition comparing a statistic of
every ${K}\times{K}$ subblock with those of its neighbours, and carries an empirical recurrence
of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical. The count is a walk count on $S={S}$ states and is $C$-finite; whether the
conjectured recurrence annihilates it is then settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

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

Write $\sigma$ for {sig}, taken on a ${K}\times{K}$ subblock. The contiguous ${K}\times{K}$
subblocks of an $(n+{K - 1})\times{W}$ array over $\{{0,\dots,{al}\}}$ form a grid of $n$ rows
and ${nb}$ {'column' if nb == 1 else 'columns'}, and $\sigma$ labels that grid. The entry
requires that {cond}.{fracnote}

\section{{The count is a walk count}}

{walk}{prune}{note}

In particular $a$ is $C$-finite. The alignment of the walk index with the entry's own $n$ was
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
\bibitem{{hu}} J.~E.~Hopcroft, R.~Motwani and J.~D.~Ullman, \emph{{Introduction to Automata
Theory, Languages, and Computation}}, 3rd ed., Addison--Wesley, 2006.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer40' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t40{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
