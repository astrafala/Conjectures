#!/usr/bin/env python3
"""Papers for the matrix-statistic subblock families."""
import conjquote
import os

# a paper carries the date its result was obtained; a paper already in the roster
# keeps the date it was written with, and this builder runs again when the sweep
# reaches more of its family
_ROSTER = None
def _date(a):
    global _ROSTER
    if _ROSTER is None:
        import json as _j
        _ROSTER = {v['anum'] for v in _j.load(open('paper-engines.json')).values()}
    return '2 September 2026' if a in _ROSTER else os.environ.get('PAPER_DATE', '2 September 2026')

import os, json, re
import localentry as LE, phibuild, transferbuild, transfer34

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

FORM = {'determinant': r'ps-qr', 'permanent': r'ps+qr', 'trace': r'p+s',
        'sum': r'p+q+r+s'}


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
    p = transfer34.parse_name(e['name'])
    W, al, kind, stat = p['W'], p['alpha'], p['kind'], p['stat']
    K = W - 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    sig = FORM[stat]
    common = rf"""Write $\sigma$ for the {stat} of a $2\times2$ subblock
$\begin{{pmatrix}}p&q\\r&s\end{{pmatrix}}$, that is $\sigma={sig}$. The subblocks of an
$(n+1)\times{W}$ array over $\{{0,\dots,{al}\}}$ form a grid of $n$ rows and ${K}$
{'column' if K == 1 else 'columns'}, and $\sigma$ colours that grid."""
    if kind == 'single':
        cond = ('vanish' if p['want'] == 'zero' else 'not vanish')
        what = common + rf"""

The condition is on each subblock separately: every $\sigma$ must {cond}, which is what
``{'singular' if p['want'] == 'zero' else 'nonsingular'}'' says of a $2\times2$ matrix. Nothing
relates one subblock to another."""
        walk = rf"""Because the condition looks at one subblock at a time and a subblock is
built from two consecutive array rows, a single row is a state: rows $r$ and $s$ may follow one
another exactly when all ${K}$ of the subblocks they form pass. An $(n+1)$-row array is then a
walk of $n$ steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ rows."""
    elif kind == 'same':
        nz = ' and the value $0$ is excluded by the entry' if p['nonzero'] else ''
        what = common + rf"""

The condition is that all the subblocks of one array share a single value of $\sigma$. That
value is not named, so the count splits by it{nz}: for a fixed $v$ let $a_v(n)$ count the
arrays all of whose subblocks give $\sigma=v$. An array determines its own common value, so
the sets belonging to different $v$ are disjoint and $a(n)=\sum_v a_v(n)$, a finite sum."""
        walk = rf"""For a fixed $v$ the condition again looks at one subblock at a time, so a
row is a state and rows $r,s$ may follow one another when all ${K}$ of their subblocks give
$v$. Taking the disjoint union over $v$ and with $M$ its adjacency matrix,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ states that survive. Rows carrying no edge at all are dropped: such a row could
only be the whole of a one-row array, which is not among the objects counted."""
    else:
        rel = ('differ' if kind == 'differ' else 'not decrease')
        what = common + rf"""

The condition relates NEIGHBOURING subblocks: the values of two subblocks adjacent in the grid,
horizontally or vertically, must {rel}. {'The entry writes this as ``no subblock value equal to any horizontal or vertical neighbour''s'', which is the same thing.' if kind == 'differ' else 'Rightwards and downwards are the two directions named.'}"""
        walk = rf"""A subblock's value needs two consecutive array rows, and the vertical
comparison needs the two subblock rows that three consecutive array rows produce. So the state
is the PAIR of consecutive array rows: the horizontal comparisons decide which pairs are
admissible at all, and the vertical ones decide which pair may follow which. A step appends one
array row, turning $(r,s)$ into $(s,t)$ and settling every comparison between the two subblock
rows at once. An $(n+1)$-row array is a walk of $n-1$ steps, so
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ admissible pairs."""
    first = d[0]
    lo = min(transfer34.STAT[stat](*t) for t in __import__('itertools').product(
        range(al + 1), repeat=4))
    hi = max(transfer34.STAT[stat](*t) for t in __import__('itertools').product(
        range(al + 1), repeat=4))
    rng = (rf"""

Over the alphabet $\{{0,\dots,{al}\}}$ the {stat} of a $2\times2$ subblock takes values in
$[{lo},{hi}]$, so the colouring of the grid it induces has at most ${hi - lo + 1}$ values.
That bound is what keeps the construction below finite in the only place where the value of
$\sigma$, rather than a comparison between two of them, has to be carried.""")
    if kind in ('single', 'same'):
        note = (rf"""

At $n=1$ the array has two rows and the grid is a single row of ${K}$
{'subblock' if K == 1 else 'subblocks'}, each tested on its own, so $a(1)$ counts the
$2\times{W}$ arrays over $\{{0,\dots,{al}\}}$ all of whose subblocks pass. The entry's
first term is ${first}$, and the model reproduces it along with every later term; that is the
cheapest check that the grid has been read with the right shape.""")
    else:
        note = (rf"""

At $n=1$ the array has two rows, so the grid is a single row of ${K}$
{'subblock, which has no neighbour at all and so is unconstrained' if K == 1 else 'subblocks with no vertical neighbours, so only the horizontal comparisons apply'}. The
entry's first term is ${first}$, and the model reproduces it along with every later term; that
is the cheapest check that the grid has been read with the right shape.""")
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{al}\}}$ under a condition on the {stat} of every
$2\times2$ subblock, and carries an empirical recurrence of order ${order}$ contributed by
R.~H.~Hardin. It is true, and it is decidable rather than empirical. The condition is local to
a bounded window of consecutive rows, so the count is a walk count on $S={S}$ states and is
$C$-finite; whether the conjectured recurrence annihilates it is then settled by a finite exact
computation, with the Cayley--Hamilton theorem bounding the work.
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

{what}

\section{{The count is a walk count}}

{walk}{note}{rng}
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
\bibitem{{minc}} H.~Minc, \emph{{Permanents}}, Addison--Wesley, 1978.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer34' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t34{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
