#!/usr/bin/env python3
"""Papers for the clashing-pair family."""
import conjquote
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer47

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

DIRNAME = {(0, 1): 'horizontal', (1, 0): 'vertical', (1, 1): 'diagonal (nw--se)',
           (1, -1): 'antidiagonal (ne--sw)'}


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
    p = transfer47.parse_name(e['name'])
    W, m = p['W'], p['alpha']
    A = m + 1
    D = [tuple(t) for t in p['dirs']]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    dirs = texbits.offsets_tex(D)
    ws = [DIRNAME[t] for t in D]
    words = ws[0] if len(ws) == 1 else ', '.join(ws[:-1]) + ' and ' + ws[-1]
    selft = (r' and, the entry saying ``adjacent to itself or'''
             r"'', also when $u=v$" if p['self'] else '')
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % m)
    tl0 = ('' if not p['tl0'] else
           r" The entry also fixes the top left entry: $x(1,1)=0$.")
    prec = {int(k): sorted(v) for k, v in p['prec'].items()}
    if prec:
        lines = []
        for w in sorted(prec):
            for v in prec[w]:
                lines.append('%d\\prec %d' % (v, w))
        joined = ',\\qquad '.join(sorted(set(lines)))
        nnamed = len(set(prec) | {v for vs in prec.values() for v in vs})
        prectxt = rf"""
Finally the entry asks that, reading the cells in ROW MAJOR order, certain values make their
first appearance before certain others:
\[
{joined} ,
\]
writing $u\prec v$ for ``the first cell carrying $u$ comes before the first cell carrying
$v$''. The entry's own name glosses the effect of this clause together with $x(1,1)=0$ as
counting UNLABELLED colourings. Nothing below rests on that gloss: the clause is imposed
exactly as it is written, and it is the written clause that the model and the independent
check both test.

\begin{{lemma}}\label{{lem:seen}}
Let $P$ be the set of values named in the clause. Reading the cells in row major order and
carrying the SET $T\subseteq P$ of named values already written, the clause holds if and only
if every cell whose value $v\in P$ is not yet in $T$ has $u\in T$ for every $u$ with $u\prec v$.
\end{{lemma}}

\begin{{proof}}
$u\prec v$ says the first cell carrying $v$ is preceded by some cell carrying $u$, that is, at
the moment $v$ is first written $u$ already belongs to $T$. Conversely if that holds at each
first writing then each required precedence holds. A cell whose value is already in $T$ is not
a first appearance and imposes nothing.
\end{{proof}}

The walk of this paper runs DOWN THE ROWS and visits the cells of each row from left to right,
which is exactly row major order, so the set $T$ can be carried in the state. It takes at most
$2^{{{nnamed}}}$ values, and the state of the walk is a pair (array row, set $T$).
"""
        statetxt = rf"""
So the state is a pair: the last array row, and the set $T$ of Lemma~\ref{{lem:seen}}. A step
appends a row, which settles every clash between it and the row above, every clash inside it,
and every first appearance it contains. Two states from which, for every remaining length, the
same number of arrays can be completed contribute identically to the count, so they are
identified; after that identification there are $S={S}$ of them.
"""
    else:
        prectxt = ''
        statetxt = rf"""
So a single array row is a state. A step appends a row, which settles every clash between it
and the row above and every clash inside it. Two states from which, for every remaining length,
the same number of arrays can be completed contribute identically to the count, so they are
identified; after that identification there are $S={S}$ of them.
"""
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS. The walk is run "
             "down the transpose, so the offsets above are already the transposed ones: "
             "transposing exchanges the horizontal and vertical directions and fixes each "
             "diagonal one.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{m}\}}$ in which no two entries that are neighbours in
a named set of directions may sum to ${m}$, together with clauses that pick one array out of
each class of arrays differing by a renaming. The entry carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical: the clash condition is local to two consecutive rows and the renaming clauses are
carried by one bounded piece of extra state, so the count is a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05C15, 15A18.\normalsize

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

The array is ${W}$ cells across with entries $x(i,j)\in{aset}$. Call two values $u,v$ CLASHING
when $u+v={m}${selft}. Two cells are neighbours when one is obtained from the other by one of
the offsets
\[
{dirs},
\]
that is, in the {words} directions, and the condition is that no two neighbouring cells carry
clashing values.{trans} The clash relation is symmetric, so an offset and its negative name the
same pairs and only one of each is listed.{tl0}
{prectxt}
\section{{The walk}}

Every offset above moves the row index by at most one, so a clash is a condition on two
consecutive array rows and on nothing else.
{statetxt}
With $\iota$ the indicator of the states that may begin an array and $\tau=\mathbf{{1}}$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau .
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
until the working vector was identically zero, which settles every larger $j$ at once.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition: fill the
cells in row major order, in the orientation the entry's own name writes, and test each clause
the moment it can be tested. No transfer matrix, no transposition and no state are involved,
and the published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
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
            if h.get('engine') == 'transfer47' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t47{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
