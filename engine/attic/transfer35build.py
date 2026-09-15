#!/usr/bin/env python3
"""Papers for the commuting-subblock family."""
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
import localentry as LE, phibuild, transferbuild, transfer35

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


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
    p = transfer35.parse_name(e['name'])
    K, W, al, every, det = p['K'], p['W'], p['alpha'], p['every'], p['det']
    nb = W - K + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    word = 'commute' if every else 'do not commute'
    # The abstract said only that neighbouring subblocks commute. Fifteen of these entries
    # also require every subblock to have nonzero determinant, which the body explained and
    # the abstract did not -- so the abstract stated a weaker condition than the one proved.
    detabs = ', each of nonzero determinant,' if det else ''
    detclause = ('' if not det else
                 r" The entry adds that every subblock have nonzero determinant; that is a "
                 r"condition on one subblock alone and is checked where the subblock is "
                 r"formed.")
    first = d[0]
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the $(n+{K - 1})\times{W}$ arrays over $\{{0,\dots,{al}\}}$ in which
neighbouring ${K}\times{K}$ subblocks{detabs} {word} as matrices, and carries an empirical
recurrence
of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical. The condition ties together ${K}+1$ consecutive rows, so ${K}$ consecutive rows are
a state, the count is a walk count on $S={S}$ of them, and the conjectured recurrence is then
settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 15A27, 15B36.\normalsize

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

The contiguous ${K}\times{K}$ subblocks of an $(n+{K - 1})\times{W}$ array form a grid of $n$
rows and ${nb}$ {'column' if nb == 1 else 'columns'}. Two subblocks that are neighbours in that
grid OVERLAP: horizontally they share ${K}\times{K - 1}$ entries, vertically
${K - 1}\times{K}$. Nevertheless each is a ${K}\times{K}$ integer matrix in its own right, and
the entry requires that every neighbouring pair, horizontal or vertical, {word} --- that is,
$AB=BA$ as matrices over $\mathbf{{Z}}$.{detclause}

At $n=1$ the array has ${K}$ rows and the grid is a single row of ${nb}$
{'subblock, with no neighbouring pair at all' if nb == 1 else 'subblocks, with only the horizontal pairs to test'}; the entry's first term is
${first}$, which the model reproduces along with every later term.

\section{{The count is a walk count}}

A subblock row is fixed by ${K}$ consecutive array rows, and the vertical condition compares
two consecutive subblock rows, hence ${K}+1$ consecutive array rows. So take as state the
${K}$-tuple of consecutive rows whose subblock row has just been completed. A step appends one
array row: that fixes the next subblock row, and the horizontal pairs inside it and the
vertical pairs against the previous one are all settled there. An array of $n+{K - 1}$ rows is
a walk of $n-1$ steps and every walk comes from exactly one array, so
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
on the $S={S}$ admissible ${K}$-tuples. In particular $a$ is $C$-finite.

This state does not compress. What a step needs of the past is the previous subblock row, and
for ${W}\ge{K}$ that row already determines the ${K}$ array rows it was built from, so nothing
is lost by carrying the rows and nothing would be gained by carrying the matrices instead. The
size of the construction is therefore ${al + 1}^{{{K}\cdot{W}}}$ before the condition prunes
it, which is what puts the wider members of this family out of reach rather than settling them.

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
\bibitem{{suprunenko}} D.~A.~Suprunenko and R.~I.~Tyshkevich, \emph{{Commutative Matrices}},
Academic Press, 1968.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer35' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t35{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
