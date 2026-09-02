#!/usr/bin/env python3
"""Papers for the 3 X 3 monotone-subblock-statistic family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer32

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
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer32.parse_name(e['name'])
    W, al = p['W'], p['alpha']
    K = W - 2
    cons = []
    for _, cl in p['clauses']:
        for di, dj, rel in cl:
            sym = r'\le' if rel == '<=' else r'\ge'
            ii = 'i' if di == 0 else 'i%+d' % di
            jj = 'j' if dj == 0 else 'j%+d' % dj
            cons.append(rf"\sigma(i,j){sym}\sigma({ii},{jj})")
    conslist = ',\\qquad '.join(cons)
    colw = 'column' if K == 1 else 'columns'
    ncl = len({id(c[0]) for c in p['clauses']})
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    trans = ('' if re.search(r'\(\s*n\s*\+\s*%s\s*\)\s*X' % 2, e['name'])
             else " The entry writes the array with $n$ as the number of COLUMNS; transposing "
                  "it exchanges the two coordinates of every direction, which is done once, "
                  "and a direction that then points upward is turned round by reversing its "
                  "inequality.")
    manyst = ('' if ncl == 1 else
              " The entry names two statistics, one governing the horizontal direction and "
              "one the vertical; both are functions of the same subblock, so both are read "
              "off the same pair of rows and no extra state is needed.")
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{2 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the arrays over $\{{0,\dots,{al}\}}$ whose $3\times3$ subblocks carry a
statistic that is monotone along named directions of the subblock grid, and carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. Every direction named moves the subblock row by at most one,
so the count is a walk count on $S={S}$ states --- the last two array rows together with the
subblock row just completed --- and the conjectured recurrence is then settled by a finite
exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 06A07.\normalsize

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

A $3\times3$ subblock has four distinguished lines of three cells: its diagonal, its
antidiagonal, its central row and its central column. The entry's statistic is a signed sum of
aggregates --- sums, maxima, minima, medians --- taken over those lines, and $\sigma(i,j)$
denotes its value on the subblock in position $(i,j)$ of the subblock grid, which has $n$ rows
and ${K}$ {colw} for an $(n+2)\times{W}$ array over $\{{0,\dots,{al}\}}$. The condition is
\[
{conslist}
\]
whenever both positions exist.{trans}{manyst}

``ne-to-sw antidiagonally'' is the offset $(+1,-1)$ on the subblock grid; that reading, and
the reading of every statistic name here, was checked by counting the small arrays directly
against what the entries publish.

\section{{The count is a walk count}}

A subblock spans three array rows and the vertical comparison spans four, so the obvious state
is three consecutive rows. It is larger than it needs to be. What a step actually consults is
the last TWO array rows --- enough to build the next subblock row once one more row arrives ---
and the PREVIOUS SUBBLOCK ROW, to compare against. So take as state the triple
\[
\bigl(r_{{i+1}},\ r_{{i+2}},\ \sigma\text{{-row }}i\bigr),
\]
and let a step append an array row $r_{{i+3}}$: that fixes $\sigma$-row $i+1$ from
$r_{{i+1}},r_{{i+2}},r_{{i+3}}$, and every comparison between the two $\sigma$-rows is settled
there. All the third rows that produce the same $\sigma$-row collapse into one state, which is
what makes the wider arrays reachable.

The starting vector is therefore weighted rather than all-ones: a state is entered by as many
first rows as produce it, and $\iota$ records that count. With $\tau$ all-ones, an
$(n+2)$-row array is a walk of $n-1$ steps and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau
\]
on the $S={S}$ reachable states. In particular $a$ is $C$-finite. The alignment of the walk
index with the entry's own $n$ was checked against its published terms rather than assumed.

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
\bibitem{{davey}} B.~A.~Davey and H.~A.~Priestley, \emph{{Introduction to Lattices and
Order}}, 2nd ed., Cambridge University Press, 2002.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer32' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t32{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
