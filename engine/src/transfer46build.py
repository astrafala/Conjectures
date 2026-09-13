#!/usr/bin/env python3
"""Papers for the monotone-statistic family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer46


def _rows(n):
    """`$1$ row` and `$2$ rows` --- 15 papers said "the strip of the last $1$ rows", because
    the count was interpolated into a fixed plural."""
    return r'$%d$ row%s' % (n, '' if n == 1 else 's')


PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

PTEX = {'sum': 'a+b', 'difference': 'a-b', 'absolute difference': r'\lvert a-b\rvert',
        'min': r'\min(a,b)', 'max': r'\max(a,b)'}
PWORD = {'sum': 'the sum', 'difference': 'the difference',
         'absolute difference': 'the absolute difference', 'min': 'the smaller',
         'max': 'the larger'}
RWORD = {'sum': 'the sum', 'maximum': 'the maximum', 'minimum': 'the minimum',
         'median': 'the median', 'range': 'the maximum minus the minimum'}
RTEX = {'sum': r'\sum_{t} v_t', 'maximum': r'\max_t v_t', 'minimum': r'\min_t v_t',
        'median': r'\operatorname{med}(v)', 'range': r'\max_t v_t-\min_t v_t'}
KW = {2: 'two', 3: 'three', 4: 'four'}


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
    p = transfer46.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    # an alphabet of two or three letters is shorter written out than elided
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS. The walk is run "
             "down the transpose, which exchanges the roles of the two directions once and "
             "for all; the arguments of each statistic keep their order under that exchange, "
             "the later cell staying the first argument.")
    if p['kind'] == 'A':
        hh, vv = PTEX[p['h']], PTEX[p['v']]
        counted = rf"""
Two derived arrays are formed. The first reads the horizontal statistic across each
neighbouring pair of a row,
\[
b(i,j)\;=\;\bigl[\,{hh}\,\bigr]_{{a=x(i,j),\,b=x(i,j-1)}}\qquad (j\ge1),
\]
and must not decrease DOWN a column: $b(i,j)\le b(i{{+}}1,j)$. The second reads the vertical
statistic down each neighbouring pair of a column,
\[
c(i,j)\;=\;\bigl[\,{vv}\,\bigr]_{{a=x(i,j),\,b=x(i{{-}}1,j)}}\qquad (i\ge1),
\]
and must not decrease ALONG a row: $c(i,j)\le c(i,j{{+}}1)$. In words, the horizontal statistic
is {PWORD[p['h']]} of a cell and its left neighbour, and the vertical one is
{PWORD[p['v']]} of a cell and the cell above it.{trans}
"""
        state = rf"""
\begin{{lemma}}\label{{lem:win}}
Both conditions are conditions on TWO consecutive array rows and nothing more.
\end{{lemma}}

\begin{{proof}}
$b(i,j)\le b(i{{+}}1,j)$ names four cells, all in rows $i$ and $i+1$. $c(i,j)\le c(i,j{{+}}1)$
names four cells, all in rows $i-1$ and $i$. No comparison reaches further.
\end{{proof}}

So a single row is a state. Let $M$ be the matrix on the ${A}^{{{W}}}={A ** W}$ rows with
$M[r,s]=1$ when the pair $(r,s)$ passes both tests and $0$ otherwise. An array of $R$ rows is a
walk of $R-1$ steps and every row may begin or end one, so with $\iota=\tau=\mathbf{{1}}$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S}.
\]
"""
    else:
        k = p['k']
        st = RTEX[p['stat']]
        counted = rf"""
Fix the statistic $\sigma(v)={st}$ of a run $v$ of ${k}$ consecutive cells --- in words,
{RWORD[p['stat']]} of the ${k}$ values. Two derived arrays are formed and both must be
nondecreasing in their own direction: reading along a row,
\[
\sigma\bigl(x(i,j),\dots,x(i,j{{+}}{k - 1})\bigr)\ \le\
\sigma\bigl(x(i,j{{+}}1),\dots,x(i,j{{+}}{k})\bigr),
\]
and reading down a column,
\[
\sigma\bigl(x(i,j),\dots,x(i{{+}}{k - 1},j)\bigr)\ \le\
\sigma\bigl(x(i{{+}}1,j),\dots,x(i{{+}}{k},j)\bigr).
\]
The same statistic and the same run length serve both directions, so the condition is
unchanged by transposing the array.{trans}
"""
        state = rf"""
\begin{{lemma}}\label{{lem:win}}
The row comparisons involve one array row each. A column comparison involves the
${k}+1={k + 1}$ consecutive rows $i,\dots,i{{+}}{k}$ and no others.
\end{{lemma}}

\begin{{proof}}
The two runs compared start at rows $i$ and $i+1$ and have length ${k}$, so together they
occupy rows $i$ through $i+{k}$.
\end{{proof}}

So the window of the last {_rows(k)} is a state, each row of it already satisfying its own row
comparisons, and one step appends a row and settles the column comparisons that the new row
completes. With $M$ the adjacency matrix of that digraph and $\iota=\tau=\mathbf{{1}}$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S},
\]
a walk of no steps being an array of exactly ${k}$ rows.
"""
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over ${aset}$ in which a statistic taken over short runs
of cells produces a derived array that is monotone in a named direction. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical: every comparison the condition makes lies inside a bounded
window of consecutive rows, so the count is a walk count on $S={S}$ states, and the
conjectured recurrence is then settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 15A18.\normalsize

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

The array has ${W}$ cells across and entries $x(i,j)\in{aset}$.
{counted}
Nothing in the condition is invariant under renaming the letters --- each statistic either does
arithmetic on them or compares them by size --- so no reduction to equality patterns is
available, and the walk is run over the alphabet the entry names.

\section{{A bounded window}}
{state}
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
cells in row major order and test each comparison the moment both of its runs are complete,
in the orientation the entry's own name writes. No transfer matrix and no transposition are
involved, and the published terms came back.

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
            if h.get('engine') == 'transfer46' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t46{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
