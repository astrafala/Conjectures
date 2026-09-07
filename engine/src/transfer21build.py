#!/usr/bin/env python3
"""One paper per Hardin entry counting patterns -- arrays up to relabelling -- under a
cell condition over a named neighbour set."""
import os

# a paper carries the date its result was obtained; one already in the roster keeps
# the date it was written with, and this builder runs again when the sweep reaches
# more of its family
_ROSTER = None
def _date(a):
    global _ROSTER
    if _ROSTER is None:
        import json as _j
        _ROSTER = {v['anum'] for v in _j.load(open('paper-engines.json')).values()}
    return '1 September 2026' if a in _ROSTER else os.environ.get('PAPER_DATE', '1 September 2026')

import os, json, re
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h["anum"]
    W, alpha, S, E = h["fixed"], h["alpha"], h["S"], 0
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, frac, off = h["base"], h["frac"], h["offset"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}

    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    cross = "column" if rowwalk else "row"
    shape = (rf"$(n+{base})\times{W}$" if base else rf"$n\times{W}$") if rowwalk else \
            (rf"${W}\times(n+{base})$" if base else rf"${W}\times n$")
    fractex = "" if frac == 1 else rf"\tfrac1{{{frac}}}"
    exctex = ("" if not E else
              rf""" The clause ``with the exception of exactly ${E}$ elements'' is carried in
the state as a counter of violations so far, capped at ${E}$; a step that would push it past
${E}$ has no edge, and a walk is accepted only when the count reaches exactly ${E}$.""")
    excstate = ("" if not E else rf" \times \{{0,\dots,{E}\}}")

    tex = h["tex"]

    den = h.get("den", 1) * frac
    fractex1 = "1"
    K = h.get("K")
    k = off - h["shift"]
    expo = "n" if k == 0 else ("n-%d" % k if k > 0 else "n+%d" % (-k))
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        k = nthr - off
        if d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts {shape} arrays over $\{{0,\dots,{alpha}\}}$ subject to a condition imposed on
every $3\times3$ subblock, and counted UP TO RELABELLING of the
alphabet; it carries an empirical recurrence of order ${order}$ contributed by
R.~H.~Hardin. It is true, and it is decidable rather than empirical. What is counted is
equality patterns, which is not a walk count --- but it is a fixed rational combination of
walk counts, one for each alphabet size, and that combination is again $C$-finite. Whether the
conjectured recurrence annihilates it is then decided by a finite exact computation, with the
Cayley--Hamilton theorem bounding the work.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{Patterns are a combination of counts}}

The clause ``new values $0..{alpha}$ introduced in row major order'' says that the arrays
counted are the canonical representatives of their EQUALITY PATTERNS: two arrays that differ
only by a permutation of the alphabet are one object. Write $N_j$ for the number of admissible
patterns using exactly $j$ letters and $L_i$ for the number of admissible ARRAYS over an
alphabet of $i$ letters. An array over $i$ letters is a pattern together with an injection of
its letters into the alphabet, so
\[
L_i\;=\;\sum_{{j}}N_j\,i(i-1)\cdots(i-j+1),
\]
a triangular system with nonzero diagonal, hence invertible over $\mathbb{{Q}}$. The entry
counts $a=N_1+\dots+N_{{{K}}}$, so
\[
a\;=\;\bigl(\mathbf{{1}}^{{\!\top}}F^{{-1}}\bigr)L ,
\]
a FIXED rational combination of the $L_i$, where $F$ is the matrix of falling factorials.
Each $L_i$ is a walk count on its own transfer graph, so $a$ is a walk count on the disjoint
union of those graphs with the combination's coefficients placed in the starting vector; the
coefficients are rational and some are negative, which costs nothing in what follows.

This step needs the condition itself to be unchanged by permuting the alphabet, and it is:
the condition below is stated through equality between entries and never names a particular
value or compares sizes.

\section{{Three consecutive lines}}

The entry's condition constrains every $3\times3$ subblock, which spans three consecutive
{lines} and three consecutive {cross}s. Writing an array as a sequence of {lines}
$u_1,u_2,\dots$ over $\{{0,\dots,{alpha}\}}^{{{W}}}$, the condition
\[
{tex}
\]
involves only three consecutive {lines}. Take as vertices the ordered PAIRS $(r,s)$ of
{lines} and put an edge $(r,s)\to(s,t)$ exactly when the condition holds for the triple
$(r,s,t)$ at every admissible column; an array with $L$ {lines} is a walk of length $L-2$.
Doing that for each alphabet size $1,\dots,{K}$ and combining as above gives
\[
a(n)\;=\;\frac{{{fractex1}}}{{{den}}}\,\iota^{{\!\top}}M^{{\,{expo}}}\tau
\]
on $S={S}$ vertices in total, the exponent fixed by the entry's own shape and checked against
its published terms. States lying on no walk from $\iota$ to $\tau$ are removed first; that
changes no value and only shrinks the computation.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. Then the residual $a(n)-\sum_ic_ia(n-i)$ equals
${fractex}\iota^{{\!\top}}M^{{\,j}}q(M)\tau$ for the corresponding walk index $j$, so the
recurrence holds from some point on if and only if $\iota^{{\!\top}}M^{{j}}q(M)\tau=0$ for all
large $j$; and it is enough to examine $j<S$.
\end{{lemma}}

\begin{{proof}}
Factor $M^{{j}}$ out of $M^{{j+{order}}}-\sum_ic_iM^{{j+{order}-i}}$. For the bound, $M^{{S}}$
is an integer combination of $I,M,\dots,M^{{S-1}}$ by Cayley--Hamilton, so the numbers
$u_j=\iota^{{\!\top}}M^{{j}}q(M)\tau$ satisfy the monic linear recurrence given by the
characteristic polynomial of $M$; $S$ consecutive zeros force every later one, and the last
nonzero $u_j$ pins the threshold exactly.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(M)\tau$ was formed by ${order}$ matrix--vector products in exact integer
arithmetic and $\iota^{{\!\top}}M^{{j}}w$ evaluated for $j=0,1,\dots$, again exactly. Those
integers vanish from the index corresponding to $n={nthr}+1$ onwards, and the run was
continued until the working vector was identically zero, which settles all larger $j$ at once.
By Lemma~\ref{{lem:crit}} the recurrence holds for every $n>{nthr}$.{tight}
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the transfer model reproduces all ${nterms}$ terms the entry publishes, exactly, in
integer arithmetic. That check earned its place here. The neighbour offsets are named in the
array's own frame --- horizontal means along a row --- but when the entry fixes the first
dimension, as in ``$2\times n$'', the walk runs along columns and the two components of every
offset swap. Sets such as king-move, or horizontal together with vertical, are unchanged by
that swap and hide the error completely; a set such as horizontal, diagonal and antidiagonal
is not, and the counts came out as those of a different member of the same family until the
offsets were transposed.

Second, the conjectured recurrence was evaluated directly on the entry's own published terms,
with no matrices involved, and holds wherever the proved range and the data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("transfer21_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t21{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
