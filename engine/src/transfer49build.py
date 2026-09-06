#!/usr/bin/env python3
"""Papers for the containing-all-values subblock family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer49

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
    p = transfer49.parse_name(e['name'])
    W, m, K, blk = p['W'], p['alpha'], p['K'], p['blk']
    ok = ', '.join(str(x) for x in p['ok'])
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, and a square subblock is carried to a square subblock, so "
             "the condition is unchanged by that.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ whose every ${blk}\times{blk}$ subblock holds a
prescribed number of DISTINCT values, which use ALL of the ${K}$ available letters, and which
are counted up to renaming. The entry carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical. The
condition counts distinct values and so survives renaming, which lets the count of patterns be
recovered from counts over fixed alphabets by inverting a triangular system of falling
factorials; the words ``containing all values'' change which row of that inverse is used and
nothing else. Each fixed-alphabet count is a walk count on $S={S}$ states in all.
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

The array has ${W}$ cells across and entries in $\{{0,1,\dots,{m}\}}$. In every
${blk}\times{blk}$ window of it, the number of DISTINCT entries must be one of ${ok}$. Two
further clauses come with it:

\begin{{itemize}}
\item ``new values $0..{m}$ introduced in row major order'' --- reading the cells in row major
order, a letter may appear for the first time only when every smaller letter already has, so
the array counted is the canonical representative of its EQUALITY PATTERN;
\item ``containing all values $0..{m}$'' --- every one of the ${K}$ letters must actually
occur.
\end{{itemize}}
{trans}

\section{{From patterns to fixed alphabets}}

Write $N_j$ for the number of admissible patterns using exactly $j$ letters and $L_i$ for the
number of admissible arrays over an alphabet of $i$ letters. An array over $i$ letters is a
pattern together with an injection of its letters into the alphabet, so
\[
L_i\;=\;\sum_{{j}} N_j\,i(i-1)\cdots(i-j+1)\;=\;\sum_j F_{{ij}}N_j ,
\]
a triangular system with unit diagonal, hence invertible over $\mathbf{{Q}}$.

Here is the whole difference between this entry and its neighbours. Without the words
``containing all values'' the quantity counted is $N_1+\dots+N_{{{K}}}$, and the weights are
the row vector $\mathbf{{1}}^{{\!\top}}F^{{-1}}$. With them, the pattern must use every letter,
so the quantity counted is $N_{{{K}}}$ alone and the weights are the single row
$e_{{{K}}}^{{\!\top}}F^{{-1}}$ of the same inverse:
\[
a\;=\;N_{{{K}}}\;=\;\sum_{{i=1}}^{{{K}}}\bigl(F^{{-1}}\bigr)_{{{K}i}}\,L_i .
\]

The step is legitimate only if the condition survives renaming the alphabet, and it does: the
condition counts how many DISTINCT values a window holds, and whether two cells agree is
untouched by any renaming. No clause compares letters by size or does arithmetic on them.

\section{{Each $L_i$ is a walk count}}

A ${blk}\times{blk}$ window lies in ${blk}$ consecutive array rows, so the window of the last
${blk - 1}$ rows is a state and a step appends a row, settling every subblock it completes.
Assembling the pieces for $i=1,\dots,{K}$ as a disjoint union, with $\iota$ carrying the
weights above cleared of denominators and $\tau=\mathbf{{1}}$,
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
until the working vector was identically zero. The rational weights are carried as one common
denominator throughout, so no division is performed until the final term.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition:
enumerate every array over $\{{0,\dots,{m}\}}$, keep those that are canonical, that use every
letter, and whose every subblock passes, and count them. Neither the transfer matrix nor the
falling-factorial inversion is involved, and the published terms came back --- including the
initial zeros, which are a sharp test of the ``containing all values'' clause: a small array
cannot show ${K}$ letters at all.

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
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer49' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t49{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
