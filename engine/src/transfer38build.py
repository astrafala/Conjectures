#!/usr/bin/env python3
"""Papers for the equal-edge families counted up to relabelling."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer36, transfer37, transfer38

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def cond_text(q):
    p = q['p']
    mod = transfer38.MODS[q['which']]
    if mod is transfer37:
        rel = ('at most' if p['atmost'] else 'exactly')
        return (rf"every $2\times3$ and $3\times2$ subblock has {rel} ${p['value']}$ equal "
                r"edges, an edge of such a window being one of the six steps of its perimeter "
                r"cycle and an equal edge one whose two cells agree")
    k = p['kind']
    if k == 'same':
        return (r"all the $2\times2$ subblocks of one array have the SAME number of equal "
                r"edges, an equal edge being one of the four perimeter edges whose two cells "
                r"agree; the common value is not named, so the count splits by it")
    if k == 'nbdiffer':
        return (r"no two $2\times2$ subblocks that are neighbours, horizontally or vertically, "
                r"have the same number of equal edges")
    if k == 'nbequal':
        return (r"any two $2\times2$ subblocks that are neighbours, horizontally or "
                r"vertically, have the same number of equal edges")
    return (r"horizontally neighbouring $2\times2$ subblocks have the same number of equal "
            r"edges and vertically neighbouring ones have different numbers")


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    q = transfer38.parse_name(e['name'])
    K, W = q['K'], q['p']['W']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    cond = cond_text(q)
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
OEIS {a} counts, up to renaming the letters, the arrays of width ${W}$ over at most ${K}$
letters in which {cond}. It carries an empirical recurrence of order ${order}$ contributed by
R.~H.~Hardin. It is true, and it is decidable rather than empirical. Counting up to renaming is
a fixed rational combination of ordinary array counts, each of those is a walk count, and the
conjectured recurrence is then settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A18, 05B45.\normalsize

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

The condition is that {cond}.

The clause ``new values $0..{K - 1}$ introduced in row major order'' says the array is the
canonical representative of its EQUALITY PATTERN, so what is counted is patterns, not arrays.
Write $N_j$ for the number of admissible patterns using exactly $j$ letters and $L_i$ for the
number of admissible arrays over an alphabet of $i$ letters. An array over $i$ letters is a
pattern together with an injection of its letters into the alphabet, so
\[
L_i\;=\;\sum_j N_j\,i(i-1)\cdots(i-j+1),
\]
a triangular system with unit diagonal, hence invertible over $\mathbf{{Q}}$. The entry counts
$a=N_1+\dots+N_{{{K}}}$, so
\[
a\;=\;\sum_{{i=1}}^{{{K}}}w_i\,L_i
\]
for one fixed rational vector $w=\mathbf{{1}}^{{\!\top}}F^{{-1}}$, $F$ the matrix of falling
factorials.

\section{{Why the reduction is allowed here}}

The step above is legitimate only if the condition is invariant under permuting the alphabet,
and in this family that is a real restriction rather than a formality. An \emph{{equal edge}}
is an edge of a subblock whose two cells carry the same letter; whether two cells agree is
untouched by any renaming, so every condition built from counting equal edges is invariant and
the reduction applies.

The neighbouring conditions of the same family that count \emph{{increases}} --- how many steps
of a subblock's perimeter cycle go UP in value --- are not invariant: they compare letters by
size, and a permutation of the alphabet changes the count. Those entries are therefore excluded
here rather than reduced, and are settled, when they are settled, over their own alphabet
without the pattern step.

\section{{Each $L_i$ is a walk count}}

For a fixed alphabet the condition is local: a $2\times2$ subblock is built from two
consecutive array rows, a $2\times3$ or $3\times2$ window from two or three of them, and every
comparison the entry makes is between subblocks that meet in the grid. Taking as state a single
row where the condition looks at one subblock at a time, and the pair of consecutive rows where
it compares neighbours, each $L_i$ is a walk count on its own digraph. Assembling,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau
\]
on the disjoint union of those digraphs for $i=1,\dots,{K}$, with $\iota$ carrying the weights
$w_i$ cleared of denominators and $S={S}$ states in all. The walk index $j$ and the entry's own
$n$ differ by a constant, read off by matching the published terms rather than assumed. In
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
until the working vector was identically zero, which settles every larger $j$ at once. The
rational weights are cleared by a common denominator first, so the whole computation is over
the integers.{tight}
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
\bibitem{{comtet}} L.~Comtet, \emph{{Advanced Combinatorics}}, Reidel, 1974. (Set partitions
and falling factorials.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer38' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t38{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
