#!/usr/bin/env python3
"""Papers for the 2 X 3 / 3 X 2 perimeter-cycle family."""
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
import localentry as LE, phibuild, transferbuild, transfer37

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

CYC = {'clockwise edge increases': r'p\to q\to s\to r\to p',
       'counterclockwise edge increases': r'p\to r\to s\to q\to p',
       'rightwards and downwards edge increases':
           r'p\to q,\ r\to s,\ p\to r,\ q\to s',
       'equal edges': r'\{p,q\},\ \{q,s\},\ \{s,r\},\ \{r,p\}'}


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
    p = transfer37.parse_name(e['name'])
    W, al, kind = p['W'], p['alpha'], p['kind']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    if kind == 'one':
        cond = rf"its number of {p['which']} edge increases is exactly ${p['value']}$"
    elif kind == 'both':
        cond = (rf"it has exactly ${p['ccw']}$ counterclockwise and ${p['cw']}$ clockwise "
                rf"edge increases")
    elif kind == 'cmp':
        cond = ("its clockwise and counterclockwise edge increases are equal in number"
                if p['equal'] else
                "its clockwise and counterclockwise edge increases are unequal in number")
    else:
        cond = (rf"it has {'at most' if p['atmost'] else 'exactly'} ${p['value']}$ equal edges")
    stat = 'clockwise edge increases'
    what = rf"""Both a $3\times2$ and a $2\times3$ window have all six of their cells on the
perimeter, so each carries a $6$-cycle. For
$\begin{{pmatrix}}p&q\\r&s\\t&u\end{{pmatrix}}$ the clockwise cycle is
$p\to q\to s\to u\to t\to r\to p$; for
$\begin{{pmatrix}}p&q&t\\r&s&u\end{{pmatrix}}$ it is
$p\to q\to t\to u\to s\to r\to p$. An edge increase is a step of the cycle that goes up in
value, and counterclockwise counts the same cycle traversed the other way. The entry requires
of every window of either shape that {cond}.

The readings were pinned by direct enumeration before anything was built: over
$\{{0,1,2\}}$ the $3\times2$ arrays of clockwise count $2$ number $423$ and those of count
$3$ number $150$; over $\{{0,\dots,3\}}$ the $3\times2$ arrays of count $1$ number $480$;
and the $2\times3$ arrays over $\{{0,1,2\}}$ of clockwise count $2$ also number $423$. Those
are the first terms the corresponding entries publish."""
    walk = rf"""A $3\times2$ window spans three consecutive array rows and a $2\times3$
window two, so take as state the PAIR of consecutive rows. The $2\times3$ windows lie inside a
single pair, so they decide which pairs are admissible at all; the $3\times2$ windows straddle
three rows, so they decide which pair may follow which. A step appends one array row, turning
$(r,s)$ into $(s,t)$ and testing every $3\times2$ window of $r,s,t$ at once. An $(n+1)$-row
array is a walk of $n-1$ steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ admissible pairs."""
    first = d[0]
    note = (rf"""

At $n=1$ the array has two rows, so no $3\times2$ window fits and only the
{'' if W >= 3 else 'nonexistent '}$2\times3$ windows apply; the entry's first term is
${first}$, which the model reproduces along with every later term.""")
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
OEIS {a} counts arrays over $\{{0,\dots,{al}\}}$ under a condition on the perimeter cycle of
every $2\times3$ and $3\times2$ subblock, and carries an empirical recurrence of order ${order}$ contributed by
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
            if h.get('engine') == 'transfer37' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t37{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
