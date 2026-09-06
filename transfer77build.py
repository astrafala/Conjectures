#!/usr/bin/env python3
"""Papers for the row-major clause on an array walked across its columns."""
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h['anum']
    R, alpha, S = h['R'], h['alpha'], h['S']
    order, nterms, nthr = h['order'], h['nterms'], h['nthr']
    off = h['offset']
    prec = [tuple(t) for t in h['prec']]
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    D = [tuple(t) for t in h['dirs']]
    dirs = texbits.offsets_tex(D)
    named = sorted({v for pr in prec for v in pr})
    prectex = ', '.join(rf"${lo}$ before ${hi}$" for lo, hi in prec)
    nametex = ', '.join(f"${v}$" for v in named)
    tight = ''
    kk = nthr - off
    if off <= nthr - order and 0 <= kk < len(d):
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by carrying a row major clause across
columns}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts ${R}\times n$ arrays over $\{{0,\dots,{alpha}\}}$ with a forbidden-pair
condition and a clause on the order in which values first appear, read in ROW MAJOR order, and
it carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true.
The obstacle is that the array grows in $n$, so the walk runs across COLUMNS and does not visit
the cells in row major order; the running set of ``values seen so far'' that settles the clause
for a column-fixed entry is simply the wrong set here. What the walk can carry instead is, for
each value the clause names, the least ROW in which it has yet been seen, together with the
order in which those least rows were attained. That is enough, and it is bounded, so the count
is a walk count and the recurrence is settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 68Q45.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:6])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{What is being counted}}

The array has ${R}$ rows and $n$ columns. Two cells are adjacent when they differ by one of the
offsets
\[
{dirs},
\]
and the entry forbids any adjacent pair $u,v$ with $u+v={alpha}$. It fixes the top left cell to
zero. Finally it asks that, reading the cells in ROW MAJOR order --- along the first row, then
along the second, and so on --- the first occurrences of the values {nametex} come in a
prescribed order: {prectex}. A precedence involving a value that never occurs is satisfied
vacuously; one whose later value occurs while its earlier value does not is broken.

\section{{Why the obvious state does not work}}

Since $n$ grows, the walk must run across the columns: a state is one column, and the
forbidden-pair condition is settled between two consecutive columns, because every offset above
moves the column index by at most one.

The clause is the difficulty. For an entry whose WIDTH is fixed the walk runs down the rows and
therefore visits the cells in row major order, so it is enough to carry the set of named values
already written and to refuse a column that introduces a value out of turn. Here the walk
visits the cells in COLUMN major order, and that set is the wrong one: a value first written
low down in an early column may be written again higher up in a later column, and it is the
later, higher cell that comes first in row major order.

\section{{What the walk can carry}}

\begin{{lemma}}\label{{lem:key}}
For a value $v$ occurring in the array, let $r_v$ be the least row in which $v$ occurs and
$c_v$ the least column with $x_{{r_v,c_v}}=v$. Then the first occurrence of $v$ in row major
order is the cell $(r_v,c_v)$, and $u$ precedes $v$ in row major order exactly when
$(r_u,c_u)<(r_v,c_v)$ lexicographically.
\end{{lemma}}

\begin{{proof}}
Row major order is the lexicographic order on $(\text{{row}},\text{{column}})$, and the least
element of the set of cells carrying $v$ under a lexicographic order is obtained by minimising
the first coordinate and then the second.
\end{{proof}}

\begin{{lemma}}\label{{lem:tie}}
Two distinct values with the same least row attain it in different columns.
\end{{lemma}}

\begin{{proof}}
If $r_u=r_v=r$ and $c_u=c_v=c$ then the cell $(r,c)$ carries both $u$ and $v$.
\end{{proof}}

So the walk carries, for each named value, the least row in which it has been seen so far ---
or the fact that it has not been seen --- and, for values sharing a least row, which of them
attained it first. By Lemma~\ref{{lem:tie}} those attainments happen in different columns, and
the walk meets the columns in order, so ``which attained it first'' is decided as the walk
goes. Nothing else about the past matters: a later column can only LOWER a value's least row,
and Lemma~\ref{{lem:key}} says the comparison depends on nothing else.

One thing must not be done, and is not done here. The clause cannot be enforced along the way,
because a least row can still drop and reorder the first occurrences retroactively. It is a
property of the finished array, so it is tested in the ACCEPTING states and nowhere else.

The state is therefore a column together with an ordered partition of the named values by least
row, and there are $S={S}$ of them after states with identical futures are merged. Hence
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-{off}}}\tau,
\]
and $a$ is $C$-finite.

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

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic, with no shift fitted.

Second --- and this is the check the whole paper turns on --- the arrays were enumerated
directly for the smallest shapes the entry counts, in the orientation the name writes, with the
cells listed in true row major order and each precedence tested on that list. No transposing
and no walk. The counts agree. Reading the clause in the walk's own order instead gives
different numbers for several entries of this family, so this check is what separates the two
readings.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{hopcroft}} J.~E.~Hopcroft, R.~Motwani and J.~D.~Ullman, \emph{{Introduction to
Automata Theory, Languages, and Computation}}, 3rd ed., Addison--Wesley, 2006.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('transfer77_hits.json')):
        if h.get('FAILS'):
            continue
        dd = f"build/t77{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
        n += 1
    print('wrote', n, 'papers')
