#!/usr/bin/env python3
"""One paper per Hardin entry with a two-line-window cell condition over the alphabet."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer15 as TF

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)




def build(h):
    a = h["anum"]
    W, alpha, S = h["fixed"], h["alpha"], h["S"]
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, frac, mult = h["base"], h["frac"], h["mult"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    off = h["offset"]
    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    cross, crosses = ("column", "columns") if rowwalk else ("row", "rows")
    Ltex = rf"{mult}n+{base}" if mult != 1 else (rf"n+{base}" if base else "n")
    fracinv = "" if frac == 1 else rf"\tfrac1{{{frac}}}"
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"
    smax = 4 * alpha

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by splitting on the common sum}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{alpha}\}}$ in which all $2\times2$ subblock sums are
EQUAL --- the common value not being named --- and carries an empirical recurrence of order
${order}$ contributed by R.~H.~Hardin. The unnamed value is what stops a transfer matrix from
applying directly, and it costs nothing to remove: an array with at least one $2\times2$
subblock determines its own common sum, so the count splits as a sum over the ${smax}+1$
possible values with nothing counted twice, and each summand is an ordinary walk count. On
the block-diagonal matrix over those values the recurrence is decided by a finite exact
computation on $S={S}$ vertices.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

\section{{The sequence and the conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry carries the following comment:
\begin{{quote}}\small
{esc(conj)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as empirical, and nothing on the entry records it as settled either way.

Written out, the claim is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;{rec_tex(h['coeffs'])}
\end{{equation}}
for all $n>{nthr}$.

\section{{Splitting on the common sum}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}, entries in
$\{{0,\dots,{alpha}\}}$, and every $2\times2$ subblock has the same sum. Since $L\ge2$ and
${W}\ge2$, every such array contains at least one $2\times2$ subblock, and that subblock's
sum is the common value; so each array belongs to exactly one of the classes
\[
A_c=\{{\text{{arrays all of whose }}2\times2\text{{ subblock sums equal }}c\}},
\qquad 0\le c\le {smax},
\]
and $\#\{{\text{{admissible arrays}}\}}=\sum_c |A_c|$ with no array counted twice. The bound
${smax}=4\cdot{alpha}$ is the largest possible subblock sum.

For a fixed $c$ the condition is local, so $|A_c|$ is a walk count. Let
$V=\{{0,\dots,{alpha}\}}^{{{W}}}$ be the possible {lines} and let $M_c$ be the adjacency
matrix of the digraph in which $r\to s$ when
$r_j+r_{{j+1}}+s_j+s_{{j+1}}=c$ for every $j$ with $1\le j\le {W}-1$. Then
$|A_c|=\mathbf{{1}}^{{\!\top}}M_c^{{\,L-1}}\mathbf{{1}}$, since an array of $L$ {lines} is a
sequence of $L$ elements of $V$ and each of its $2\times2$ subblocks lies in two consecutive
{lines} and two consecutive {crosses}.

Writing $N=\bigoplus_{{c=0}}^{{{smax}}}M_c$, of size $S={S}$, and $\mathbf{{v}}$ for the
all-ones vector on it,
\begin{{equation}}\label{{eq:walk}}
a(n)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}N^{{\,L-1}}\mathbf{{1}},\qquad L={Ltex}.
\end{{equation}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and ${Gtex}$.

\begin{{lemma}}\label{{lem:crit}}
With $n_0$ the least index for which $L\ge1$, $o={mult}n_0+{base}-1$ and
$h_j=G^{{j}}N^{{o}}\mathbf{{1}}$, we have for $j\ge{order}$
\[
a(n_0+j)-\sum_i c_i\,a(n_0+j-i)={fracinv}\,\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,
\qquad w=h_{{{order}}}-\sum_i c_ih_{{{order}-i}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for all $m\ge0$, and $m<S$ suffices.
\end{{lemma}}

\begin{{proof}}
Substitute \eqref{{eq:walk}} and factor. By Cayley--Hamilton $G^{{S}}$ is an integer
combination of $I,G,\dots,G^{{S-1}}$, so every later value repeats that combination of
earlier ones.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
Each $M_c$ was built directly from its defining condition. The vector $w$ was formed by
${order}$ applications of $G$ in exact integer arithmetic and $\mathbf{{v}}^{{\!\top}}G^{{m}}w$
evaluated for $m=0,1,\dots$, again exactly. Every one of those integers vanishes from the
index corresponding to $n={nthr}+1$ onwards, and the run continued until $S+1$ consecutive
zeros had been seen.
\end{{proof}}

\begin{{remark}}
The splitting is what makes the argument finite, and it is exact rather than an
over-count only because every array here has a subblock. For a one-{cross} or one-{line}
shape there is no subblock at all, every value of $c$ would be vacuously admissible, and the
sum would count each array ${smax}+1$ times; those shapes are excluded by $L\ge2$ and
${W}\ge2$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the right-hand side of \eqref{{eq:walk}} was evaluated at every one of the ${nterms}$
published indices and agrees with the entry's DATA exactly, with no shift fitted. A double
count in the splitting, or a wrong bound on $c$, would show up here immediately.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes wherever it applies.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried to the full
Cayley--Hamilton bound in exact integer arithmetic rather than to a sampled prefix.

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
    hits = [h for h in json.load(open("transfer15_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/tf{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
