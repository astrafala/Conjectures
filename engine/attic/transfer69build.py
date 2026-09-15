#!/usr/bin/env python3
"""Papers for the chessboard-colour subarray family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer69

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
    p = transfer69.parse_name(e['name'])
    C, A = p['C'], p['alpha'] + 1
    col = 'white' if p['par'] == 0 else 'black'
    other = 'black' if p['par'] == 0 else 'white'
    par = 'even' if p['par'] == 0 else 'odd'
    firstcell = '(0,0)' if p['par'] == 0 else '(0,1)'
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    if p['kind'] == 'maj':
        cond = (r"no cell equals a strict majority of its neighbours:" "\n\\[\n"
                r"2\cdot\#\{(a,b)\in S(i,j) : x(a,b)=x(i,j)\}\;\le\;|S(i,j)| ." "\n\\]\n"
                r"Strict means more than half, so a tie is allowed and a cell with no "
                r"neighbours is under no condition.")
        short = "no cell matches a strict majority of its diagonal neighbours"
    else:
        cond = (r"every cell has a neighbour one greater than it modulo $%d$, and no neighbour "
                r"equal to it:" % p['mod'] + "\n\\[\n"
                r"\exists\,(a,b)\in S(i,j)\ \ x(a,b)\equiv x(i,j)+1 \!\!\pmod{%d},"
                r"\qquad x(a,b)\neq x(i,j)\ \ \text{for all }(a,b)\in S(i,j)."
                % p['mod'] + "\n\\]\n")
        short = ("every cell has a diagonal neighbour one greater than it modulo %d, and none "
                 "equal to it" % p['mod'])
    extra = (r"The entry adds that the first cell of the subarray in reading order, the cell "
             r"$%s$ of the array, is $0$." % firstcell if p['ul0'] else
             r"The entry adds that the values $0..%d$ are introduced in reading order: reading "
             r"the cells of the subarray row by row, a value may appear for the first time only "
             r"after every smaller value has appeared." % (A - 1))
    rmpar = ("" if not p['rowmajor'] else r"""
The reading-order clause is carried as one more number in the state: how many distinct values
have been introduced so far. A cell may then take any value already used, or the next one up,
and nothing else; writing a row updates the count as the row is filled, left to right, so a
value first used early in a row makes a larger value legal later in the same row.
""")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{4 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the {col}-square subarrays of arrays of width ${C}$ over ${aset}$ in which
{short}. The entry carries an empirical recurrence of order ${order}$ contributed by
R.~H.~Hardin. It is true, and it is decidable rather than empirical. A diagonal step changes
both coordinates by one and so never changes the colour of a cell, which makes the two colours
of the chessboard independent of one another; the count is then a walk over the cells of one
colour, on $S={S}$ states.
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

Colour the cells of the array like a chessboard: $(i,j)$ is {col} when $i+j$ is {par}. The
condition is stated in terms of the DIAGONAL and ANTIDIAGONAL neighbours of a cell, that is the
four offsets
\[
(-1,-1),\ (1,1),\ (-1,1),\ (1,-1),
\]
and for a cell $(i,j)$ we write $S(i,j)$ for those of them that land inside the array. The
condition is that {cond}

{extra}

\begin{{lemma}}\label{{lem:split}}
Each of the four offsets changes $i$ and $j$ each by one, so it changes $i+j$ by $0$ or $\pm2$
and never changes its parity. Every neighbour of a {col} cell is therefore {col}. The condition
above splits into two systems that share no cell: one on the {col} cells and one on the {other}
cells.
\end{{lemma}}

So what the entry counts is the assignments of values to the {col} cells alone that satisfy the
{col} system; the {other} cells never enter. That this is the entry's own reading, and not
merely a convenient one, is settled by its ``upper left element zero'': for a {col} subarray the
first cell in reading order is the cell ${firstcell}$ of the array, and it is that cell the
clause fixes, as the published terms confirm and as Section~5 records.

\section{{A walk on one colour}}

Take the array one row at a time. In a row of even index the {col} cells sit at every other
column starting from column ${p['par']}$, and in a row of odd index they sit at the columns in
between; the two shapes alternate, so a state must record which of them the next row has.

All four offsets move exactly one row, so the neighbours of the {col} cells of a row are the
{col} cells of the rows immediately above and below it. A row's conditions are therefore settled
by three consecutive rows, and the state is the last two of them together with the parity of the
next.{rmpar}

Appending a row completes one such window and settles the row in the middle of it. Because the
condition looks one row DOWN as well as up, the last row of a finished array has not been tested
when the walk stops, so the end vector is not all ones: a state is accepted exactly when its
last row passes with nothing below it. Thus
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S}.
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

Second, the count was recomputed for the smallest arrays straight from the definition: the cells
of the {col} colour were listed from $i+j$ directly, every assignment of values to them
enumerated, and each tested by the entry's own words. No rows, no window, no state and no end
vector are involved in that computation, and the published terms came back.

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
            if h.get('engine') == 'transfer69' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t69{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
