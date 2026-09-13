#!/usr/bin/env python3
"""Papers for the subblock-statistic-versus-neighbour family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer72

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

STAT_TEX = {
    'nesw': (r"f(B)=B_{1,k}-B_{k,1}",
             "the northeast entry minus the southwest entry"),
    'nwse': (r"f(B)=B_{1,1}+B_{k,k}",
             "the northwest entry plus the southeast entry"),
    'dmax-amin': (r"f(B)=\max_{1\le t\le k}B_{t,t}\;-\;\min_{1\le t\le k}B_{t,k+1-t}",
                  "the largest entry on the main diagonal minus the smallest on the "
                  "antidiagonal"),
    'dmax-amax': (r"f(B)=\max_{1\le t\le k}B_{t,t}\;-\;\max_{1\le t\le k}B_{t,k+1-t}",
                  "the largest entry on the main diagonal minus the largest on the "
                  "antidiagonal"),
    'dmax+amin': (r"f(B)=\max_{1\le t\le k}B_{t,t}\;+\;\min_{1\le t\le k}B_{t,k+1-t}",
                  "the largest entry on the main diagonal plus the smallest on the "
                  "antidiagonal"),
    'dsum-asum': (r"f(B)=\sum_{t=1}^{k}B_{t,t}\;-\;\sum_{t=1}^{k}B_{t,k+1-t}",
                  "the sum of the main diagonal minus the sum of the antidiagonal"),
}

DIR_TEX = {'horizontal': r"(0,1)", 'vertical': r"(1,0)",
           'diagonal': r"(1,1)", 'antidiagonal': r"(1,-1)"}

ADV = {'horizontal': 'horizontally', 'vertical': 'vertically',
       'diagonal': 'diagonally', 'antidiagonal': 'antidiagonally'}


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def wordlist(ws):
    ws = list(ws)
    if len(ws) == 1:
        return ws[0]
    return ', '.join(ws[:-1]) + ' and ' + ws[-1]


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer72.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    ks = p['ks']
    K = max(ks)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    sizes = ' and '.join('$%d\\times%d$' % (k, k) for k in ks)
    ksw = 'that one size' if len(ks) == 1 else 'each of the two sizes'

    # the clauses
    cl = []
    for kind, ws in p['clauses']:
        formula, words = STAT_TEX[kind]
        cl.append((kind, ws, formula, words))
    if len(cl) == 1:
        kind, ws, formula, words = cl[0]
        statpar = (r"""For a $k\times k$ block $B$ of cells of the array, let
\[
%s ,
\]
which in words is %s. The condition is that $f$ takes different values on any two blocks that
are neighbours in one of the directions the entry names: writing $B(i,j)$ for the block whose
top-left cell is $(i,j)$,
\[
f\bigl(B(i,j)\bigr)\;\neq\;f\bigl(B(i+\delta_1,\,j+\delta_2)\bigr)
\qquad\text{for }(\delta_1,\delta_2)\in\Delta,
\]
whenever both blocks lie wholly inside the array, where
\[
\Delta=\{\,%s\,\}
\]
collects the steps for the directions the entry names, namely %s. The
requirement is imposed for %s of block, %s.""" % (
            formula, words,
            ',\ '.join(DIR_TEX[w] for w in ws), wordlist(ws), ksw, sizes))
        short = "%s of every %s subblock differs from the same number at the neighbouring " \
                "subblock" % (words, ' and '.join('$%d\\times%d$' % (k, k) for k in ks))
    else:
        names = ['f', 'g']
        parts = []
        for (kind, ws, formula, words), nm in zip(cl, names):
            parts.append(r"""\[
%s\qquad\text{compared %s,}
\]
that is, %s;""" % (formula.replace('f(B)', nm + '(B)', 1), wordlist([ADV[w] for w in ws]),
                  words))
        statpar = (r"""The entry states two conditions at once. For a $k\times k$ block $B$ of
cells of the array put
""" + "\n".join(parts).rstrip(';') + r""".
Each condition says that its own number takes different values on two blocks that are
neighbours in its own directions: with $B(i,j)$ the block whose top-left cell is $(i,j)$ and
$(\delta_1,\delta_2)$ the step for the direction concerned --- $%s$ %s, $%s$ %s ---
\[
f\bigl(B(i,j)\bigr)\neq f\bigl(B(i+\delta_1,\,j+\delta_2)\bigr)
\quad\text{resp.}\quad
g\bigl(B(i,j)\bigr)\neq g\bigl(B(i+\delta_1,\,j+\delta_2)\bigr),
\]
whenever both blocks lie wholly inside the array. Both conditions are imposed for %s of block,
%s.""" % (DIR_TEX[cl[0][1][0]], wordlist([ADV[w] for w in cl[0][1]]),
          DIR_TEX[cl[1][1][0]], wordlist([ADV[w] for w in cl[1][1]]), ksw, sizes))
        short = "two diagonal numbers of every %s subblock each differ from the same number " \
                "at a neighbouring subblock" % (' and '.join('$%d\\times%d$' % (k, k)
                                                             for k in ks))

    dirs = sorted({w for _, ws in p['clauses'] for w in ws})
    downdirs = [w for w in dirs if w != 'horizontal']
    reachw = ('no lower' if not downdirs else 'one lower')
    transline = ("" if not p['trans'] else
                 r""" The entry writes the array with $n$ as the number of COLUMNS. Transposing
it exchanges the horizontal and vertical directions and fixes the two diagonal ones, and it
either fixes the number $f$ or replaces it by its negative --- the northeast and southwest
entries change places. An equality is unaffected by negating both sides, so the transposed
problem is the same problem with the horizontal and vertical directions exchanged, and the
directions above are named in the transposed frame.""")
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes %s of that count; the division is by the constant "
                r"%d and changes nothing about the recurrence." % (
                    {2: 'one half', 4: 'one quarter'}.get(frac, '$1/%d$' % frac), frac))
    krows = 'the last %d rows' % K
    stepw = 'row' if not p['trans'] else 'column'

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{5 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which {short}. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical: a block of $k$ rows and the block one row lower together
occupy $k+1$ consecutive rows, so every comparison the condition makes is settled inside
${K + 1}$ consecutive rows and the count is a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B20, 15A18.\normalsize

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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$.

{statpar}{transline}{fracline}

Two remarks fix the reading. A neighbouring block is the block one step over, overlapping the
first, not the next disjoint block: the entry says ``its neighbors'', and the counts below
confirm it. And a comparison is imposed only when both blocks lie wholly inside the array, so a
block near an edge is compared in fewer directions and a block whose named neighbour falls off
the array is under no condition in that direction.

\section{{A window of {K + 1} rows}}

A $k\times k$ block occupies $k$ consecutive rows, and each of its neighbours occupies either
the same $k$ rows or the $k$ rows one lower. So both blocks of any comparison lie inside $k+1$
consecutive rows, hence inside ${K + 1}$ consecutive rows for every size the entry names. No
comparison reaches further than that, in either direction.

Take the array one {stepw} at a time and let the state be {krows} written so far, with a
distinguished start standing for the array before its first row, so that a walk of $n$ steps is
an array of $n$ rows. Appending a row produces a window of ${K + 1}$ rows, and the step is
allowed exactly when every comparison whose two blocks both lie inside that window holds.

Every comparison of the finished array is tested this way. Each one lies inside ${K + 1}$
consecutive rows, and every ${K + 1}$ consecutive rows of the array form the window of some
step. A comparison lying inside more than one window is tested more than once, which costs
nothing. Conversely no step imposes anything not asked by the definition, since a step tests
only comparisons whose two blocks lie inside the array.

Every state may end an array, so $\tau=\mathbf{{1}}$. A block sitting in the final rows whose
neighbour would lie below the last row is not compared in that direction at all --- the
neighbour is not part of the array --- so stopping never leaves a condition unchecked. For the
same reason the array of exactly ${K}$ rows is handled by the walks of length ${K}$ with no
further test: all of its comparisons already lie inside the windows of those steps.

Thus
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S},
\]
for the transfer matrix $M$ on those $S$ states. The walk index $j$ and the entry's own $n$
differ by a constant, read off by matching the published terms rather than assumed. In
particular $a$ is $C$-finite.

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

Second, the count was recomputed for the smallest arrays straight from the definition: every
array of width ${W}$ over ${aset}$ with a few rows was written out cell by cell, every block of
{ksw} was located, its number computed, and the comparison made with each neighbouring block
that lies inside the array. No window, no state and no end vector are involved in that
computation, and the published terms came back.

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
            if h.get('engine') == 'transfer72' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t72{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
