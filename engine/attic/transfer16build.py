#!/usr/bin/env python3
"""One paper per Hardin entry with a two-line-window cell condition over the alphabet."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer16 as TG

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)




WORD = {1: "exactly one", 2: "exactly two", 3: "exactly three", 4: "exactly four"}


def build(h):
    a = h["anum"]
    W, K, S, E = h["fixed"], h["K"], h["S"], h["E"]
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
    scale = rf"{K}!"
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by counting defective colourings}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the colourings of an array with $K={K}$ colours that are proper except at
{WORD.get(E, E)} adjacent pair{"" if E == 1 else "s"}, the colours being introduced in row
major order. Neither feature is local: the number of monochromatic adjacent pairs is a
property of the whole array, and the row major clause fixes a representative of each
relabelling class. Both are removed by machinery already in hand --- the running count of
mistakes goes into the state, capped at ${E}$, and the colour clause disappears into the
identity ${K}!\,a(n)=\sum_i\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n)$ with $D_m$ the derangement
numbers. What is left is a walk count on $S={S}$ vertices, and the empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin follows from a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05C15, 15B36.\normalsize

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

\section{{Mistakes, and the colour clause}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}, entries in $\{{0,\dots,{K}-1\}}$.
Two cells are adjacent when they differ by one of
\[
\mathcal N=\{{{h['nbtex']}\}}
\]
(as ({line} shift, {cross} shift)); each unordered adjacency is represented by exactly one
offset, and every offset has a nonnegative {line} shift, so the pairs inside a {line} are
counted when that {line} is laid down and the pairs joining two {lines} when the later one
is. Call an adjacent pair a \emph{{mistake}} when ${h['tex']}$. The entry asks for exactly
$E={E}$ mistakes.

That is a statement about the whole array, so no bounded window sees it; but the running
number of mistakes can be carried in the state, capped at ${E}$, the states past ${E}$ being
absent because a count that has passed the budget can never come back.

The condition is stated in equalities, so it is invariant under relabelling the colours, and
so is the number of mistakes. ``Colors introduced in row-major order'' keeps exactly one
colouring from each relabelling class, so the entry counts equality PATTERNS with at most
$K={K}$ classes.

\begin{{lemma}}\label{{lem:inv}}
Let $L_i(n)$ count the colourings over $i$ colours with exactly ${E}$ mistakes, and $N_j(n)$
the admissible patterns with exactly $j$ classes. Then
$L_i=\sum_j N_j\,i(i-1)\cdots(i-j+1)$ and
\[
{K}!\,\sum_{{j\le{K}}}N_j(n)=\sum_{{i=0}}^{{{K}}}\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n),
\qquad D_m=m!\sum_{{t=0}}^{{m}}\frac{{(-1)^t}}{{t!}} .
\]
\end{{lemma}}

\begin{{proof}}
A colouring is a pattern together with an injection of its classes into the palette, and a
pattern with $j$ classes admits $i(i-1)\cdots(i-j+1)$ of them, which is the first identity.
Writing the falling factorial as $j!\binom{{i}}{{j}}$ and inverting binomially gives
$j!N_j=\sum_i(-1)^{{j-i}}\binom{{j}}{{i}}L_i$; summing over $j\le{K}$ and exchanging the order
of summation makes the coefficient of $L_i$ equal to $\sum_{{t\le{K}-i}}(-1)^t/(i!\,t!)$,
which multiplied by ${K}!$ is $\binom{{{K}}}{{i}}D_{{{K}-i}}$, an integer.
\end{{proof}}

\section{{Each $L_i$ is a walk count}}

Fix $i$ and take as vertices the pairs $(r,c)$ with $r\in\{{0,\dots,i-1\}}^{{{W}}}$ a {line}
and $0\le c\le{E}$ a running count. Write $\beta(r,s)$ for the number of mistakes joining
{lines} $r$ and $s$ plus the number of mistakes inside $s$. Declare $(r,c)\to(s,c+\beta(r,s))$
an edge when $c+\beta(r,s)\le{E}$, let $\mathbf{{s}}_i$ mark the vertices whose count is the
number of mistakes inside $r$ alone, and $\mathbf{{e}}_i$ those with $c={E}$.

\begin{{lemma}}\label{{lem:walk}}
$L_i(n)=\mathbf{{s}}_i^{{\!\top}}P_i^{{\,L-1}}\mathbf{{e}}_i$ for $L\ge1$, where $P_i$ is the
adjacency matrix of that digraph.
\end{{lemma}}

\begin{{proof}}
A walk of length $L-1$ determines the sequence of $L$ {lines}, and conversely; by induction
the count component after $t$ {lines} is the number of mistakes among the first $t$ {lines},
since each step adds exactly the mistakes joining {lines} $t$ and $t+1$ together with those
inside {line} $t+1$, and each unordered pair is named by exactly one offset. The walk exists
precisely when the running count never exceeds ${E}$, which for a nondecreasing count follows
from its final value being ${E}$, and $\mathbf{{e}}_i$ imposes that final value. The state
carries a {line}, not a boundary, so $L$ {lines} make a walk of length $L-1$.
\end{{proof}}

Assembling the ${K}$ chains block-diagonally into $N$ of size $S={S}$ with the weights of
Lemma~\ref{{lem:inv}} in the start vector $\mathbf{{v}}$ and the end markers in
$\mathbf{{u}}$,
\begin{{equation}}\label{{eq:walk2}}
{scale}\;a(n)\;=\;\mathbf{{v}}^{{\!\top}}N^{{\,L-1}}\mathbf{{u}},\qquad L={Ltex} .
\end{{equation}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and ${Gtex}$.

\begin{{lemma}}\label{{lem:crit}}
With $n_0$ the least index for which $L\ge1$, $o={mult}n_0+{base}-1$ and
$h_j=G^{{j}}N^{{o}}\mathbf{{u}}$, we have for $j\ge{order}$
\[
{scale}\Bigl(a(n_0+j)-\sum_i c_i\,a(n_0+j-i)\Bigr)=\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,
\qquad w=h_{{{order}}}-\sum_i c_ih_{{{order}-i}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for all $m\ge0$, and $m<S$ suffices.
\end{{lemma}}

\begin{{proof}}
Substitute \eqref{{eq:walk2}} and factor; ${scale}$ is a nonzero scalar. Cayley--Hamilton
makes $G^{{S}}$ an integer combination of $I,G,\dots,G^{{S-1}}$, so every later value repeats
that combination of earlier ones.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The digraph was built directly from the definitions above. The vector $w$ was formed by
${order}$ applications of $G$ in exact integer arithmetic and $\mathbf{{v}}^{{\!\top}}G^{{m}}w$
evaluated for $m=0,1,\dots$, again exactly. Every one of those integers vanishes from the
index corresponding to $n={nthr}+1$ onwards, and the run continued until $S+1$ consecutive
zeros had been seen.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the right-hand side of \eqref{{eq:walk2}}, divided by ${scale}$, was evaluated at every
one of the ${nterms}$ published indices and agrees with the entry's DATA exactly, the quotient
coming out an integer each time; no shift was fitted, the number of {lines} being $L={Ltex}$
from the entry's own name and the offset saying which index carries the first published term.
Double-counting an unordered pair, or mistaking the budget, changes the counts at once.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes wherever it applies.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried to the full
Cayley--Hamilton bound in exact integer arithmetic rather than to a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7; falling-factorial
inversion, Section 1.9.)
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("transfer16_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/tg{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
