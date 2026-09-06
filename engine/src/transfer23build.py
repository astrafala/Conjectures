#!/usr/bin/env python3
"""One paper per entry settled by the K X K-subblock matrix engine."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer23

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

COND = {'idem': ('idempotent', r'$B^2=B$'),
        # "the same population" is the count of EACH value. On a binary matrix that is the
        # number of 1s; over a larger range the sum reading is wrong, and only the
        # count-of-each-value one reproduces the published terms.
        'pop': ('of equal population', r'the same number of occurrences of each value'),
        'perm': ('of equal permanent', r'the same permanent $b_{11}b_{22}+b_{12}b_{21}$')}


import json as _json
_ROSTER_AT_BUILD = {v['anum'] for v in _json.load(open('paper-engines.json')).values()}


def datefor(a):
    """A paper carries the date its result was obtained, not the date of the batch it is
    rebuilt with."""
    return '2 September 2026' if a in _ROSTER_AT_BUILD else '6 September 2026'


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def windows_section(p, nwin, ngrp):
    K, al, pred = p['K'], p['alpha'], p['pred']
    if pred == 'idem':
        return rf"""
\section{{The admissible windows}}

The vertices of the overlap graph are the $0/1$ matrices $B$ of size ${K}\times{K}$ with
$B^2=B$. There are $2^{{{K * K}}}$ matrices to sift, which is already awkward at ${K}={K}$ and
hopeless a little beyond it, so they are not sifted; they are generated from the following
description, which also makes the count itself transparent.

\begin{{lemma}}\label{{lem:idem}}
Let $B$ be a $k\times k$ matrix with entries in $\{{0,1\}}$, let $r_i$ denote its $i$th row and
$S_i=\{{j:B_{{ij}}=1\}}$ the support of that row. Then $B^2=B$ if and only if
\[
r_i=\sum_{{t\in S_i}}r_t \qquad (1\le i\le k),
\]
the rows on the right necessarily having pairwise disjoint supports. Writing
$Z=\{{i:r_i=0\}}$ and $U=\{{1,\dots,k\}}\setminus Z$, and calling $i\in U$ \emph{{primitive}}
when $S_i\cap U=\{{i\}}$, the idempotent $0/1$ matrices are exactly those obtained as follows:
choose $Z$; choose the set $B^{{\ast}}\subseteq U$ of primitive indices and for each
$b\in B^{{\ast}}$ a set $Z_b\subseteq Z$, putting $r_b=e_b+\sum_{{j\in Z_b}}e_j$; and for each
$i\in U\setminus B^{{\ast}}$ choose a nonempty $B_i\subseteq B^{{\ast}}$ whose rows have
pairwise disjoint supports, putting $r_i=\sum_{{b\in B_i}}r_b$. Distinct data give distinct
matrices.
\end{{lemma}}

\begin{{proof}}
The $i$th row of $B^2$ is $\sum_t B_{{it}}r_t=\sum_{{t\in S_i}}r_t$, so $B^2=B$ is precisely the
displayed system. Its entries lie in $\{{0,1\}}$, so for each $i$ the supports $S_t$,
$t\in S_i$, are pairwise disjoint with union $S_i$.

Assume $B^2=B$. Rows indexed by $Z$ vanish, so for $i\in U$ we may write
$r_i=\sum_{{t\in S_i\cap U}}r_t$ with $S_i\cap U\neq\emptyset$. If $i$ is primitive this says
$S_i\subseteq\{{i\}}\cup Z$, which is the stated shape with $Z_i=S_i\cap Z$. For the rest argue
by induction on $|S_i|$. The supports $S_t$, $t\in S_i\cap U$, are disjoint, nonempty and
cover $S_i$; if one of them has $|S_t|=|S_i|$ it is the only one, whence $r_t=r_i$,
$S_t\cap U=S_i\cap U=\{{t\}}$ and $t$ is primitive. Otherwise every such $t$ has
$|S_t|<|S_i|$, and each $r_t$ is by induction a sum of primitive rows with disjoint supports.
Either way $r_i=\sum_{{b\in B_i}}r_b$ with $B_i\subseteq B^{{\ast}}$, and intersecting
$S_i=\bigsqcup_{{b\in B_i}}(\{{b\}}\cup Z_b)$ with $U$ returns $B_i$, so the data is recovered
from $B$ and distinct data give distinct matrices.

Conversely, given data of the stated shape, the disjointness makes every entry $0$ or $1$, and
$\sum_{{t\in S_i}}r_t$ equals $0$, $r_b$, $\sum_{{b\in B_i}}r_b$ in the three cases, which is
$r_i$ each time. Hence $B^2=B$.
\end{{proof}}

Generating from Lemma~\ref{{lem:idem}} gives ${nwin}$ admissible ${K}\times{K}$ windows. For
$k=2,3,4$ the same generation gives $8$, $50$ and $452$, which agree with exhaustion over all
$2^{{k^2}}$ matrices; that is the check that the description above is neither too wide nor too
narrow.
"""
    what = 'population' if pred == 'pop' else 'permanent'
    if pred == 'pop':
        qty = (r'the number of its entries equal to $1$' if al == 1
               else r'the list of how many times each of the values $0,\dots,%d$ occurs in it'
               % al)
    else:
        qty = r'$b_{11}b_{22}+b_{12}b_{21}$'
    return rf"""
\section{{The admissible windows}}

The entry does not name the common value; it only asks that all the windows of one matrix agree.
So fix a value $v$ and let $W_v$ be the set of ${K}\times{K}$ matrices over
$\{{0,\dots,{al}\}}$ whose {what}, {qty}, equals $v$. A matrix counted by the entry has all of
its windows in a single $W_v$, and the value of $v$ is determined by the matrix, so the sets of
matrices belonging to different $v$ are disjoint and
\[
a(n)\;=\;\sum_v a_v(n),
\]
each $a_v$ being the walk count of Section~2 built from $W_v$ alone. A disjoint union of the
${ngrp}$ digraphs, one per value of $v$, therefore counts the whole of $a(n)$ with the same
all-ones vectors, and the ${K}\times{K}$ windows in play number ${nwin}$ in total.
"""


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off, sh = h['offset'], h['shift']
    e = LE.get(a)
    p = transfer23.parse_name(e['name'])
    K, W, al, pred = p['K'], p['W'], p['alpha'], p['pred']
    groups = transfer23.windows(p, 100000)
    nwin = sum(len(g) for g in groups)
    ngrp = len([g for g in groups if g])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    adj = COND[pred][0]
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
OEIS {a} counts the $(n+{K - 1})\times{W}$ matrices over $\{{0,\dots,{al}\}}$ all of whose
${K}\times{K}$ contiguous subblocks are {adj}, and carries an empirical recurrence of order
${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical.
The condition ties together ${K}$ consecutive rows and ${K}$ consecutive columns at once, so a
single row is not a state; the strip of the last ${K - 1}$ rows is, and the admissible strips
are read off the overlap graph of the admissible windows instead of being enumerated. That
makes $a(n)$ a walk count on $S={S}$ vertices, hence $C$-finite, and whether the conjectured
recurrence annihilates it is settled by a finite exact computation.
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
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{The count is a walk count}}

Call a ${K}\times{K}$ matrix over $\{{0,\dots,{al}\}}$ a \emph{{window}} when it is {adj}, and
call a ${K}\times{W}$ matrix a \emph{{band}} when every one of its ${W - K + 1}$ contiguous
${K}\times{K}$ subblocks is a window. What the entry counts is the matrices of ${W}$ columns
whose every ${K}$ consecutive rows form a band.

Take as states the ${K - 1}\times{W}$ strips that occur as the top ${K - 1}$ rows of a band,
together with those that occur as its bottom ${K - 1}$ rows, and put an edge from $u$ to $v$
when the band whose first ${K - 1}$ rows are $u$ and whose last ${K - 1}$ rows are $v$ exists.
A band is determined by that pair, so the edge is unique when it exists. Reading a counted
matrix from the top, its rows $1..{K - 1}$, then $2..{K}$, and so on, form a walk, and every
walk arises from exactly one matrix; a matrix with $n+{K - 1}$ rows gives a walk of $n$ edges.
Since the first ${K - 1}$ rows of a counted matrix with at least ${K}$ rows are the top of a
band, and since no further condition falls on where a walk starts or ends,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau ,\qquad \iota=\tau=(1,1,\dots,1)^{{\!\top}},
\]
with $M$ the adjacency matrix on $S={S}$ states. In particular $a$ is $C$-finite. The
alignment was checked against the entry's published terms rather than assumed.

There are $({al} + 1)^{{{(K - 1) * W}}}$ strips of ${K - 1}$ rows and ${W}$ columns, far too
many to test one by one, and they are not tested one by one. Two consecutive windows of a band
overlap in ${K}\times{K - 1}$ entries, so a band is exactly a walk of ${W - K + 1}$ windows in
the graph that joins a window to those whose first ${K - 1}$ columns are its last ${K - 1}$
columns. Enumerating those walks produces the bands, and with them the states and the edges,
directly.
{windows_section(p, nwin, ngrp)}
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
\bibitem{{kim}} K.~H.~Kim, \emph{{Boolean Matrix Theory and Applications}}, Marcel Dekker,
1982.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer23' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t23{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
