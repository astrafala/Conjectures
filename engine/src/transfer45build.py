#!/usr/bin/env python3
"""Papers for the consecutive-triple family."""
import conjquote
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
import localentry as LE, phibuild, transferbuild, transfer45

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

STEP = {'row': '(i,j),\\ (i,j+1),\\ (i,j+2)',
        'column': '(i,j),\\ (i+1,j),\\ (i+2,j)',
        'diagonal': '(i,j),\\ (i+1,j+1),\\ (i+2,j+2)',
        'antidiagonal': '(i,j),\\ (i+1,j-1),\\ (i+2,j-2)'}
NAMED = {'row': 'a row', 'column': 'a column', 'diagonal': 'a diagonal (nw--se)',
         'antidiagonal': 'an antidiagonal (ne--sw)'}
# the first column of the array is prose, so it has to leave math mode: without \text the
# spaces collapse and the en-dash turns into two minus signs

ORDER = ('row', 'column', 'diagonal', 'antidiagonal')


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
    p = transfer45.parse_name(e['name'])
    W, K, cond = p['W'], p['K'], p['cond']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    rows = []
    for k in ORDER:
        if k in cond:
            vals = ', '.join(str(x) for x in cond[k])
            rows.append(rf"\text{{{NAMED[k]}}} & ${STEP[k]}$ & ${vals}$ \\")
    free = [k for k in ORDER if k not in cond]
    freetxt = ('' if not free else
               ' The entry places no condition on triples along '
               + ' or '.join(NAMED[k].split(' (')[0] for k in free) + '.')
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS. The walk is run "
             "down the transpose, which exchanges rows with columns and carries each diagonal "
             "direction to itself, so the two conditions are exchanged once and the diagonal "
             "ones left alone.")
    tbl = '\n'.join(rows)
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over an alphabet of ${K}$ letters in which every three
consecutive entries taken along any of the directions the entry names hold a prescribed number of
DISTINCT values, the arrays being counted up to renaming of the letters. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. Nothing in the condition compares letters by size, so the
count up to renaming is recovered from counts over fixed alphabets by inverting a triangular
system of falling factorials; each of those is a walk count on pairs of consecutive rows, and
the same symmetry is used a second time to run the walk on ORBITS of pairs, which is what
brings the state count down to $S={S}$.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A18, 15A18.\normalsize

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

The array has width ${W}$ and entries in $\{{0,1,\dots,{K - 1}\}}$. Four families of triples
run through it, and each carries its own condition on how many distinct values the three
entries may hold:
\[
\begin{{array}}{{lll}}
\text{{along}} & \text{{the triple}} & \text{{admissible numbers of distinct values}} \\[2pt]
{tbl}
\end{{array}}
\]
A triple counts only when all three of its cells lie inside the array.{freetxt}{trans}

The clause ``new values $0$ upwards introduced in row major order'' says the array is the
canonical representative of its EQUALITY PATTERN: reading the cells in row major order, a
letter may appear for the first time only if every smaller letter already has. So what the
entry counts is patterns, not arrays.

\section{{From patterns to fixed alphabets}}

Write $N_j$ for the number of admissible patterns using exactly $j$ letters and $L_i$ for the
number of admissible arrays over an alphabet of $i$ letters. An array over $i$ letters is a
pattern together with an injection of its letters into the alphabet, so
\[
L_i\;=\;\sum_j N_j\,i(i-1)\cdots(i-j+1),
\]
a triangular system with unit diagonal, hence invertible over $\mathbf{{Q}}$. The entry counts
$a=N_1+\dots+N_{{{K}}}$, so
\[
a\;=\;\sum_{{i=1}}^{{{K}}}w_i\,L_i ,\qquad w=\mathbf{{1}}^{{\!\top}}F^{{-1}},
\]
$F$ being the matrix of falling factorials.

This step is legitimate only if the condition is invariant under permuting the alphabet, and
here it is: every clause counts how many DISTINCT values a triple holds, and whether two cells
agree is untouched by any renaming. No clause compares letters by size and none does arithmetic
on them, so the reduction applies with nothing left over.

\section{{Each $L_i$ is a walk count, on orbits}}

Every triple lies inside three consecutive rows, so with $c_1,\dots,c_R$ the rows of the array
the condition is a conjunction of tests on the windows $(c_{{t}},c_{{t+1}},c_{{t+2}})$ together
with the row test on each $c_t$ separately. A pair of consecutive admissible rows is therefore
a state, and $L_i$ counts walks in the digraph on those pairs, one edge $(c_t,c_{{t+1}})\to
(c_{{t+1}},c_{{t+2}})$ for each admissible window.

That digraph has up to $i^{{2\cdot{W}}}$ vertices, which is more than can be written down for
the wider arrays. The symmetry is used again to cut it. Let $G=S_i$ act on states by renaming
letters. Every test is invariant, so the adjacency matrix $M$ commutes with the action, and the
all-ones vector $\tau$ is invariant; hence $M^{{t}}\tau$ is invariant, that is, constant on
orbits. Writing $\bar M[O,O']$ for the number of edges from one fixed representative of $O$ to
states of $O'$ --- a number independent of the representative, again by invariance --- gives
$\overline{{M^{{t}}\tau}}=\bar M^{{t}}\bar\tau$, and therefore
\[
L_i(R)\;=\;\sum_{{s}}(M^{{R-2}}\tau)(s)\;=\;\sum_{{O}}|O|\,(\bar M^{{R-2}}\bar\tau)(O),
\]
the sum being over the orbits of admissible pairs. An orbit is exactly the PATTERN of the pair,
and if that pattern uses $p$ letters its orbit has $i(i-1)\cdots(i-p+1)$ members, since a state
is fixed only by permutations fixing every letter it shows. So the start vector is the falling
factorial and the end vector is all ones.

Assembling the $i=1,\dots,{K}$ pieces as a disjoint union, with $\iota$ carrying the weights
$w_i$ cleared of denominators,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,
\]
with $S={S}$ states in all. The walk index $j$ and the entry's own $n$ differ by a constant,
read off by matching the published terms rather than assumed. In particular $a$ is $C$-finite.

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
until the working vector was identically zero, which settles every larger $j$ at once. The
rational weights $w_i$ are carried as one common denominator throughout, so no division is
performed until the final term.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition: fill the
cells in row major order, allow a cell to introduce a new letter only when every smaller letter
is already present, and reject a partial array as soon as a triple all of whose cells are
placed violates its condition. This uses neither the transfer matrix, nor the orbit reduction,
nor the falling-factorial inversion, and it returns the published terms.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7; Stirling numbers and
falling factorials, Section 1.9.)
\bibitem{{kemeny}} J.~G.~Kemeny and J.~L.~Snell, \emph{{Finite Markov Chains}}, Springer,
1976. (Lumping a chain along a partition preserved by the transition rule, Section 6.3.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer45' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t45{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
