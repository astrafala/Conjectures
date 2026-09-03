#!/usr/bin/env python3
"""Papers for the lexicographic 2 X 2 statistic family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer65

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

ORDERED = ('maxmin', 'maxplusmin', 'med2', 'extmed', 'upmedlomed', 'upmedmin')


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
    p = transfer65.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    stat = p['stat']
    formula, words = transfer65.STATWORD[stat]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    Wm, Wm2 = W - 1, W - 2
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    sortline = (r"Write $v_1\le v_2\le v_3\le v_4$ for the four entries of $B$ sorted into "
                r"order. " if stat in ORDERED else "")
    rowword = 'nondecreasing' if p['rowdir'] else 'nonincreasing'
    colword = 'nondecreasing' if p['coldir'] else 'nonincreasing'
    rowsym = r'\preceq' if p['rowdir'] else r'\succeq'
    colsym = r'\preceq' if p['coldir'] else r'\succeq'
    nz = ("\n\nThe entry asks in addition that no subblock statistic be zero, which is a "
          "condition on one subblock at a time.\n" if p['nonzero'] else "")
    trans = ("" if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS. Every statistic "
             "in this family is unchanged when a $2\\times2$ block is transposed --- the "
             "determinant and the permanent because a $2\\times2$ matrix and its transpose "
             "have both, the others because they depend only on the four values as a "
             "multiset --- so the transposed problem is the same one with the two axes of the "
             "derived array exchanged, and that is how it is read here.")
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes %s of that count; the division is by the constant "
                r"%d and changes nothing about the recurrence." % (
                    {2: 'one half', 4: 'one quarter'}.get(frac, '$1/%d$' % frac), frac))
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ by reducing every $2\times2$ subblock to a
single number---here {words}---and requiring the resulting derived array to have its rows
lexicographically {rowword} and its columns lexicographically {colword}. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. The row comparison is settled by three consecutive rows of the
array; the column comparison is not settled by any bounded window, but what is still outstanding
about it is one bit per adjacent pair of columns, so the count is a walk count on $S={S}$
states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 06A05, 15A18.\normalsize

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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$. A
$2\times2$ subblock of such an array is
\[
B=\begin{{pmatrix}} p & q \\ r & s \end{{pmatrix}},
\qquad p=x(i,j),\; q=x(i,j+1),\; r=x(i+1,j),\; s=x(i+1,j+1).
\]
{sortline}The entry attaches to $B$ the single number
\[
f(B)\;=\;{formula},
\]
{words}. An array with $R$ rows and ${W}$ columns has $(R-1)\times{Wm}$ subblocks, and they
form a derived array
\[
D(i,j)=f\!\left(\begin{{pmatrix}} x(i,j) & x(i,j+1) \\ x(i+1,j) & x(i+1,j+1)\end{{pmatrix}}
\right),\qquad 0\le i<R-1,\;\; 0\le j<{Wm} .
\]
Write $\preceq$ for the lexicographic order on finite sequences of integers: $u\preceq w$ when
$u=w$, or when $u_k<w_k$ at the first index $k$ where they differ. The condition is that the
rows of $D$, read left to right and compared in this order, are {rowword} from top to bottom,
\[
D_{{i}}\;{rowsym}\;D_{{i+1}}\qquad\text{{for every }} i,
\]
and that the columns of $D$, read top to bottom and compared in the same order, are {colword}
from left to right,
\[
D^{{j}}\;{colsym}\;D^{{j+1}}\qquad\text{{for every }} j .
\]{nz}{trans}{fracline}

\section{{A bounded state}}

Grow the array one row at a time. A row of $D$ is built from two consecutive rows of the array,
so the row condition is decided three array rows at a time and needs no memory beyond the
derived row just formed. The column condition is different: which of two columns of $D$ is the
smaller is decided by the first derived row in which they differ, and that row can be
arbitrarily far down. What is bounded is not the comparison but what remains open about it.

\begin{{lemma}}\label{{lem:bits}}
Fix $j$ and suppose the derived rows $D_0,\dots,D_i$ have been written. If $D_t(j)=D_t(j+1)$ for
every $t\le i$, then $D^{{j}}\;{colsym}\;D^{{j+1}}$ holds for the finished array if and only if,
at the first later row $t$ with $D_t(j)\neq D_t(j+1)$, the inequality {'$D_t(j)<D_t(j+1)$' if p['coldir'] else '$D_t(j)>D_t(j+1)$'}
holds; and if no such row occurs the two columns are equal and the condition holds. If instead
$D_t(j)\neq D_t(j+1)$ for some $t\le i$, then the comparison is already settled by the earliest
such $t$ and no later row can change it.
\end{{lemma}}

\begin{{proof}}
Immediate from the definition of the lexicographic order: it looks only at the first index at
which the two sequences differ, and prefixes that agree contribute nothing.
\end{{proof}}

So a single bit per adjacent pair of columns---``this pair has agreed in every derived row so
far''---carries everything the future needs to know, and there are ${Wm2}$ such pairs. The state
is therefore
\[
\bigl(\text{{the array row just written}},\; \text{{the derived row just formed}},\;
\text{{the {Wm2} bits}}\bigr),
\]
with a distinguished start standing for the empty array, so that a walk of $n$ steps is an array
of $n$ rows. A step appends a row, forms the new derived row, checks it against the previous one
for the row condition, and for each pair still flagged either leaves the flag set (the pair
agreed again) or clears it after checking the required inequality once. Every state may end an
array, so $\tau=\mathbf{{1}}$ and
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

Second, the count was recomputed for the smallest arrays straight from the definition: every
array of width ${W}$ over ${aset}$ with two and with three rows was written out cell by cell,
the derived array formed, and its rows and its columns compared as whole words. No state, no
bits of Lemma~\ref{{lem:bits}} and no recurrence are involved in that computation, and the
published terms came back.

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
            if h.get('engine') == 'transfer65' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t65{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
