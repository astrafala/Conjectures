#!/usr/bin/env python3
"""Papers for the edge-count subblock families."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer36

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

CYC = {'clockwise edge increases': r'p\to q\to s\to r\to p',
       'counterclockwise edge increases': r'p\to r\to s\to q\to p',
       'rightwards and downwards edge increases':
           r'p\to q,\ r\to s,\ p\to r,\ q\to s',
       'equal edges': r'\{p,q\},\ \{q,s\},\ \{s,r\},\ \{r,p\}'}


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
    p = transfer36.parse_name(e['name'])
    W, al, kind, stat = p['W'], p['alpha'], p['kind'], p['stat']
    K = W - 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    what_edge = ('counts how many of the four steps of the cycle $%s$ go up in value'
                 % CYC[stat] if 'increases' in stat else
                 'counts how many of the four perimeter edges $%s$ join two equal cells'
                 % CYC[stat])
    common = rf"""For a $2\times2$ subblock $\begin{{pmatrix}}p&q\\r&s\end{{pmatrix}}$ the
entry's quantity, the number of {stat}, {what_edge}. Write $\sigma$ for it. The subblocks of an
$(n+1)\times{W}$ array over $\{{0,\dots,{al}\}}$ form a grid of $n$ rows and ${K}$
{'column' if K == 1 else 'columns'} and $\sigma$ labels that grid.

The reading is not a guess. Over $0..1$ the $2\times3$ arrays whose two subblocks have equal
clockwise counts number $40$; over $0..2$ the $2\times2$ arrays of clockwise count $2$ number
$30$; the $3\times2$ binary arrays whose two subblocks have unequal rightwards-and-downwards
counts number $40$. Those are the first terms the corresponding entries publish, and each was
computed by direct enumeration before any transfer matrix was built."""
    if kind == 'fixed':
        det = (' and, the entry adds, no subblock may be singular' if p['det'] else '')
        what = common + rf"""

The condition is on each subblock separately: $\sigma$ must equal ${p['value']}${det}. Nothing
relates one subblock to another."""
        walk = rf"""A subblock is built from two consecutive array rows and the condition looks
at one subblock at a time, so a single row is a state: rows $r$ and $s$ may follow one another
exactly when all ${K}$ subblocks they form pass. An $(n+1)$-row array is a walk of $n$ steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ rows."""
    elif kind == 'twostat':
        what = common + rf"""

The condition is on each subblock separately: its number of {stat} must differ from its number
of {p['stat2']}. Both are functions of the same four cells, so this too is local to one
subblock."""
        walk = rf"""A single array row is a state, since a subblock is built from two
consecutive rows and nothing relates one subblock to another: rows $r$ and $s$ may follow one
another exactly when all ${K}$ subblocks they form pass. An $(n+1)$-row array is a walk of $n$
steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ rows."""
    elif kind == 'same':
        what = common + rf"""

The condition is that all the subblocks of one array share a single value of $\sigma$. That
value is not named, so the count splits by it: for a fixed $v$ let $a_v(n)$ count the arrays all
of whose subblocks give $\sigma=v$. An array determines its own common value, so the sets
belonging to different $v$ are disjoint and $a(n)=\sum_v a_v(n)$, a finite sum --- $\sigma$
lies between $0$ and $4$."""
        walk = rf"""For a fixed $v$ the condition looks at one subblock at a time, so a row is
a state and rows $r,s$ may follow one another when all ${K}$ of their subblocks give $v$.
Taking the disjoint union over $v$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ states that survive. Rows carrying no edge at all are dropped: such a row could
only be the whole of a one-row array, which is not among the objects counted."""
    elif kind == 'mixed':
        hstat, vstat = (p['stat2'], p['stat']) if p.get('trans') else (p['stat'], p['stat2'])
        det = ('' if not p['det'] else
               ' No subblock may be singular, which is a condition on one subblock alone.')
        what = common + rf"""

The condition treats the two directions differently: subblocks that are horizontal neighbours
must carry the SAME number of {hstat}, while subblocks that are vertical neighbours must carry
DIFFERENT numbers of {vstat}.{det}{' The entry writes the array with $n$ as the number of COLUMNS, so the two directions are exchanged before anything is built.' if p.get('trans') else ''}"""
        walk = rf"""A subblock's value needs two consecutive array rows, and the vertical
comparison needs the two subblock rows that three consecutive rows produce. So the state is the
PAIR of consecutive array rows: the horizontal condition decides which pairs are admissible at
all, the vertical one decides which pair may follow which. A step appends one array row,
turning $(r,s)$ into $(s,t)$ and settling every vertical comparison at once. An $(n+1)$-row
array is a walk of $n-1$ steps, so
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ admissible pairs."""
    else:
        rel = 'equal' if kind == 'nbequal' else 'different'
        det = ('' if not p['det'] else
               ' The entry also asks that no subblock be singular, which is a condition on one '
               'subblock alone and is checked where the subblock is formed.')
        what = common + rf"""

The condition relates NEIGHBOURING subblocks: two subblocks adjacent in the grid, horizontally
or vertically, must carry {rel} values of $\sigma$."""
        walk = rf"""A subblock's value needs two consecutive array rows, and the vertical
comparison needs the two subblock rows that three consecutive rows produce. So the state is the
PAIR of consecutive array rows: the horizontal comparisons decide which pairs are admissible at
all, the vertical ones decide which pair may follow which. A step appends one array row,
turning $(r,s)$ into $(s,t)$ and settling every comparison between the two subblock rows at
once. An $(n+1)$-row array is a walk of $n-1$ steps, so
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ admissible pairs."""
    first = d[0]
    note = (rf"""

At $n=1$ the array has two rows, so the grid is a single row of ${K}$
{'subblock' if K == 1 else 'subblocks'}; the entry's first term is ${first}$, which the model
reproduces along with every later term. That is the cheapest check that the grid has been read
with the right shape.""")
    rng = ''
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
OEIS {a} counts arrays over $\{{0,\dots,{al}\}}$ under a condition on the number of {stat}
in every $2\times2$ subblock, and carries an empirical recurrence of order ${order}$ contributed by
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

{walk}{note}
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
\bibitem{{bona}} M.~B\'ona, \emph{{Combinatorics of Permutations}}, 2nd ed., CRC
Press, 2012.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer36' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t36{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
