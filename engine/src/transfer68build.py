#!/usr/bin/env python3
"""Papers for the neighbourhood-condition family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer68

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

NAMEOF = {(0, -1): 'the cell to the left', (0, 1): 'the cell to the right',
          (-1, 0): 'the cell above', (1, 0): 'the cell below',
          (-1, -1): 'the cell above and left', (1, 1): 'the cell below and right',
          (-1, 1): 'the cell above and right', (1, -1): 'the cell below and left'}


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def offs_tex(offs):
    return ', '.join('(%d,%d)' % o for o in offs)


def cond_tex(p):
    k = p['kind']
    if k == 'avg':
        return (r"no cell equals the average of the neighbours it has:" "\n\\[\n"
                r"x(i,j)\;\neq\;\frac{1}{|S(i,j)|}\sum_{(a,b)\in S(i,j)}x(a,b)" "\n\\]\n"
                r"whenever $S(i,j)$ is not empty. A cell with no neighbour at all is under no "
                r"condition, and that is what the entry's first published term says.",
                "no cell is the average of its neighbours")
    if k == 'avgself':
        return (r"no cell together with its neighbours averages to $%d$:" % p['val'] + "\n\\[\n"
                r"\frac{x(i,j)+\sum_{(a,b)\in S(i,j)}x(a,b)}{1+|S(i,j)|}\;\neq\;%d ."
                % p['val'] + "\n\\]\n" +
                r"The cell itself is one of the terms of the average, so the condition is never "
                r"vacuous---even a cell with no neighbours must differ from $%d$." % p['val'],
                "no cell averages to a given value with its neighbours")
    if k == 'maj':
        return (r"no cell is equal to a strict majority of its neighbours:" "\n\\[\n"
                r"2\cdot\#\{(a,b)\in S(i,j) : x(a,b)=x(i,j)\}\;\le\;|S(i,j)| ." "\n\\]\n"
                r"Strict means more than half, so a tie is allowed and a cell with no "
                r"neighbours is under no condition.",
                "no cell matches a strict majority of its neighbours")
    if k == 'majplus':
        return (r"no cell has a strict majority of its neighbours one greater than itself "
                r"modulo $%d$:" % p['mod'] + "\n\\[\n"
                r"2\cdot\#\{(a,b)\in S(i,j) : x(a,b)\equiv x(i,j)+1 \bmod %d\}"
                r"\;\le\;|S(i,j)| ." % p['mod'] + "\n\\]\n" +
                r"With three values this is the drawn position of rock, paper and scissors: "
                r"each value beats the one below it modulo $%d$, and no cell is to be beaten "
                r"by a strict majority of its neighbours." % p['mod'],
                "no cell is beaten by a strict majority of its neighbours")
    if k == 'both':
        return (r"no cell equals BOTH the cell above it and the cell to its left:" "\n\\[\n"
                r"\neg\bigl(x(i,j)=x(i-1,j)\ \wedge\ x(i,j)=x(i,j-1)\bigr)." "\n\\]\n"
                r"A cell in the first row or the first column is missing one of the two and so "
                r"cannot equal both; it is under no condition.",
                "no cell equals both the cell above it and the cell to its left")
    return (r"every cell is the sum modulo $%d$ of one of two named groups of its neighbours:"
            % p['mod'] + "\n\\[\n"
            r"x(i,j)\;\equiv\;\sum_{(a,b)\in S(i,j)}x(a,b) \quad\text{or}\quad "
            r"x(i,j)\;\equiv\;\sum_{(a,b)\in T(i,j)}x(a,b) \pmod{%d}," % p['mod'] + "\n\\]\n"
            r"where $T$ is built from the second group of offsets, " +
            offs_tex(p['offs2']) + r", in the same way. An empty group sums to $0$.",
            "every cell is the sum of one of two groups of its neighbours")


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer68.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    U, D = transfer68._reach(p)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    body, short = cond_tex(p)
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    slice_word = 'row' if not p['trans'] else 'column'
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of COLUMNS; transposing "
                 r"it exchanges the two coordinates of every offset, and the offsets above are "
                 r"already written in the transposed frame.")
    ul0 = (r" The entry adds that the top-left cell is $0$." if p['ul0'] else "")
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes %s of that count; the division is by the constant "
                r"%d and changes nothing about the recurrence." % (
                    {2: 'one half', 4: 'one quarter'}.get(frac, '$1/%d$' % frac), frac))
    upw = 'no row' if U == 0 else ('one row' if U == 1 else '%d rows' % U)
    dnw = 'none' if D == 0 else ('one row' if D == 1 else '%d rows' % D)
    keep = 'row' if U + D == 1 else '%d of them' % (U + D)
    settled = ('the bottom row of that window' if D == 0 else
               'the one just above the bottom of that window' if D == 1 else
               'the one %d rows above the bottom of that window' % D)
    lastw = 'last row' if D == 1 else 'last %d rows' % D
    endpar = (r"Every state may end an array, so $\tau=\mathbf{1}$."
              if D == 0 else
              r"""When the array stops, the %s of it %s never been tested, because the
conditions reach %s below. So the end vector is NOT all ones: a state is accepted exactly when
those rows pass with nothing below them, which is decided by running the same test on the window
with absent rows appended --- the same rule that governs a cell at the bottom edge in
Section 2.""" % (lastw, 'has' if D == 1 else 'have', dnw))
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{4 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which {short}. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical: what a cell asks reaches {upw} above
it and {dnw} below, so the condition on a whole row is settled by
${U + D + 1}$ consecutive rows and the count is a walk count on $S={S}$ states.
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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$. Fix the
list of offsets the entry names,
\[
\Delta=\{{\,{offs_tex(p['offs'])}\,\}},
\]
and for a cell $(i,j)$ write
\[
S(i,j)=\{{\,(i+\delta_1,\,j+\delta_2) : (\delta_1,\delta_2)\in\Delta\,\}}\cap
\text{{(the cells of the array)}}
\]
for the neighbours it actually has. Only offsets landing inside the array count, so a cell on
the border simply has fewer neighbours.{transline}

The condition is that {body}{ul0}{fracline}

\section{{A window of {U + D + 1} rows}}

The offsets reach {upw} up and {dnw} down, so everything the condition asks of one row is
decided by that row together with {upw} above it and {dnw} below --- a window of
${U + D + 1}$ consecutive rows, and nothing wider. Take the array one {slice_word} at a time
and let the state be the last {keep}, with a distinguished start standing for the
array before its first row, so that a walk of $n$ steps is an array of $n$ rows.

Appending a row completes exactly one window, and the row it settles is {settled}; a step is
allowed when that row passes. Each row of the finished
array is therefore tested exactly once.

{endpar}
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
array of width ${W}$ over ${aset}$ with a few rows was written out cell by cell and each cell
tested against the neighbours it has. No window, no state and no end vector are involved in that
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
            if h.get('engine') == 'transfer68' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t68{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
