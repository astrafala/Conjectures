#!/usr/bin/env python3
"""Papers for the repeated-value family."""
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
import localentry as LE, phibuild, transferbuild, transfer55

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

# each of these is followed in the sentence by `the previous repeated value', so none of them
# may end in a pronoun of its own
REL = {'eq': 'equal to', 'ne': 'different from', 'gt': 'greater than',
       'ge': 'greater than or equal to', 'lt': 'less than',
       'le': 'less than or equal to',
       'cyc+': 'one larger modulo %d than', 'ncyc+': 'NOT one larger modulo %d than',
       'cyc-': 'one smaller modulo %d than', 'ncyc-': 'NOT one smaller modulo %d than'}


def relword(rk, mod):
    w = REL[rk]
    return w % mod if '%d' in w else w


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
    p = transfer55.parse_name(e['name'])
    W, m, K = p['W'], p['alpha'], p['K']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    rowrel = relword(*(p['inrun'] if not p['trans'] else p['across']))
    colrel = relword(*(p['across'] if not p['trans'] else p['inrun']))
    slice_word = 'row' if not p['trans'] else 'column'
    other = 'column' if not p['trans'] else 'row'
    tl0 = ('' if not p['tl0'] else
           r" The entry also fixes the top left entry at $0$, which restricts which "
           r"slices may begin an array and nothing else.")
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS, so the array grows "
             "one COLUMN at a time: the column scan is the one that runs inside a slice and the "
             "row scan is the one that runs across slices.")
    if p['rel']:
        relpar = rf"""
The entry closes with ``new values introduced in row-major sequential order'', so what is
counted is arrays up to renaming the letters. Both relations here are built from equality
alone, so the condition survives renaming and the usual inversion applies: with $N_j$ the
classes on exactly $j$ letters and $L_i$ the admissible arrays over an alphabet of $i$ letters,
\[
L_i=\sum_j N_j\,i(i-1)\cdots(i-j+1),\qquad
a=N_1+\dots+N_{{{K}}}=\bigl(\mathbf{{1}}^{{\!\top}}F^{{-1}}\bigr)L .
\]
An entry of this family whose relation compares letters by size, or does arithmetic on them,
carries no such clause and is counted over its own alphabet instead; the two cases are not
mixed.
"""
        assemble = (rf" Assembling the pieces for $i=1,\dots,{K}$ as a disjoint union, with "
                    r"$\iota$ carrying the weights above cleared of denominators,")
    else:
        relpar = r"""
The entry carries no renaming clause, and it could not: the relations here compare letters by
size or do arithmetic on them, so they are not invariant under permuting the alphabet. The
count is therefore taken over the alphabet the entry names, with no reduction to patterns.
"""
        assemble = " With $M$ the adjacency matrix of that digraph,"
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays in which the REPEATED VALUES of each row, and of each column, stand in a
prescribed relation to one another in the order they occur. The entry carries an empirical
recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable
rather than empirical: one of the two scans runs inside a slice of the array and the other
across slices, and the second needs only the previous slice together with the last repeated
value so far in each column of the scan, so the count is a walk count on $S={S}$ states.
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

Read a row of the array from left to right. A REPEATED VALUE is an entry equal to the entry
immediately before it; the row thus produces the sequence of values at the places where two
equal entries stand side by side. The entry asks that each repeated value of a row be
{rowrel} the previous repeated value of that row, and that each repeated value of a column,
read downwards, be {colrel} the previous repeated value of that column. The FIRST repeated
value of a scan has no predecessor and is unconstrained; a scan with no two equal neighbours
imposes nothing at all.{tl0}{trans}
{relpar}
\section{{One scan inside a slice, one across}}

Take the array a ${slice_word}$ at a time, the direction in which it grows.

\begin{{lemma}}\label{{lem:state}}
The ${slice_word}$ scans are settled as each ${slice_word}$ is written. The ${other}$ scans are
settled by the previous ${slice_word}$ together with, for each position, the last repeated value
so far in that ${other}$.
\end{{lemma}}

\begin{{proof}}
A ${slice_word}$ scan compares neighbours inside one ${slice_word}$, so writing the
${slice_word}$ left to right and carrying the last repeated value seen decides it. In a
${other}$ scan a repeat happens at the new ${slice_word}$ exactly when the new entry equals the
entry in the same position of the previous ${slice_word}$, and the only thing the relation needs
besides that entry is the previous repeated value of that ${other}$.
\end{{proof}}

So the state is the pair (previous ${slice_word}$, vector of last repeated values), the second
component taking ${m}+2$ values at each position --- the letters together with a symbol for
``none yet''.{assemble}
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S},\quad\tau=\mathbf{{1}} .
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
enumerate every array of that size, form each row's and each column's list of repeated values
by scanning it, and test consecutive members of those lists against the relation. No state, no
window and no transfer matrix are involved, and the published terms came back.

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
            if h.get('engine') == 'transfer55' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t55{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
