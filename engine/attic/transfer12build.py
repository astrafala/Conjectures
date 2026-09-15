#!/usr/bin/env python3
"""One paper per Hardin entry with a cell condition and an exception budget."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex
WORD = {0: "no", 1: "exactly one", 2: "exactly two", 3: "exactly three", 4: "exactly four"}


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


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
    scale = rf"{K}!" + ("" if frac == 1 else rf"\,/\,{frac}")
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by counting patterns with a budget}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} imposes three things at once: a condition on each cell that reaches one {line} up and
one {line} down; a global budget allowing {WORD.get(E, E)} cell{"" if E == 1 else "s"} to
break it; and the clause ``new values introduced in order $0$ sequentially upwards'', which
says the array is written in canonical form. None of the three is visible to a plain transfer
matrix over {lines}. All three are handled: the state is a pair of consecutive {lines}
together with the number of offending cells so far, capped at the budget; and the
canonical-form clause is removed by counting equality patterns instead of arrays, through the
identity ${K}!\,a(n)=\sum_i\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n)$ with $D_m$ the derangement
numbers. The empirical recurrence of order ${order}$ contributed by R.~H.~Hardin then follows
from a finite exact computation on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A18, 15B36.\normalsize

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

\section{{The condition, the budget, and the canonical form}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}; write $x_{{t,u}}$ for the entry in
{line} $t$ and {cross} $u$. With the neighbour offsets
\[
\mathcal N=\{{{h['nbtex']}\}}
\]
as ({line} shift, {cross} shift), counting only positions inside the array, call a cell
$(t,u)$ \emph{{offending}} when
\[
{h['tex']} .
\]
The entry asks for arrays in which exactly $E={E}$ cells offend.

Since $\mathcal N$ contains offsets of both signs in the {line} direction, a cell of {line}
$t$ is judged by {lines} $t-1$, $t$ and $t+1$ together, so a state carrying one {line} is not
enough; and the number of offending cells is a property of the whole array, so no bounded
window sees it either. Both are fixed by the same device: states are ordered pairs of
consecutive {lines} together with a running count $v\in\{{0,1,\dots,{E}\}}$, and a count that
would exceed ${E}$ is simply not represented --- an array that passes it can never come back
under it.

The condition is stated in equalities between entries, so it is invariant under relabelling
the values, and so is the number of offending cells. The clause ``new values introduced in
order $0$ sequentially upwards'' keeps exactly one array from each relabelling class, so what
the entry counts is admissible equality PATTERNS with at most $K={K}$ classes.

\begin{{lemma}}\label{{lem:inv}}
Let $L_i(n)$ count the arrays over an alphabet of $i$ letters with exactly ${E}$ offending
cells, and $N_j(n)$ the admissible patterns with exactly $j$ classes. Then
$L_i=\sum_j N_j\,i(i-1)\cdots(i-j+1)$ and
\[
{K}!\,\sum_{{j\le{K}}}N_j(n)=\sum_{{i=0}}^{{{K}}}\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n),
\qquad D_m=m!\sum_{{t=0}}^{{m}}\frac{{(-1)^t}}{{t!}} .
\]
\end{{lemma}}

\begin{{proof}}
A labelled array is a pattern together with an injection of its classes into the alphabet,
and a pattern with $j$ classes admits $i(i-1)\cdots(i-j+1)$ of them, which gives the first
identity. Writing the falling factorial as $j!\binom{{i}}{{j}}$ and inverting binomially,
$j!N_j=\sum_i(-1)^{{j-i}}\binom{{j}}{{i}}L_i$; summing over $j\le{K}$ and exchanging the
order of summation makes the coefficient of $L_i$ equal to
$\sum_{{t\le{K}-i}}(-1)^t/(i!\,t!)$, which multiplied by ${K}!$ is
$\binom{{{K}}}{{i}}D_{{{K}-i}}$, an integer.
\end{{proof}}

\section{{Each $L_i$ is a walk count}}

Fix $i$, let $V_i=\{{0,\dots,i-1\}}^{{{W}}}$, and take the triples $(p,c,v)$ with
$p,c\in V_i$ and $0\le v\le{E}$ as vertices. Write $\mathrm{{viol}}(b\mid a,x)$ for the number
of offending cells in the {line} $b$ when $a$ lies above it and $x$ below (either may be
absent, in which case the corresponding neighbours simply do not exist). Declare
\[
(p,c,v)\ \longrightarrow\ (c,x,\,v+\mathrm{{viol}}(c\mid p,x))
\]
an edge whenever the new count is at most ${E}$. Let $\mathbf{{s}}_i$ mark the vertices with
$v=\mathrm{{viol}}(p\mid\text{{--}},c)$ and $\mathbf{{e}}_i$ those with
$v+\mathrm{{viol}}(c\mid p,\text{{--}})={E}$.

\begin{{lemma}}\label{{lem:walk}}
For $L\ge2$, $L_i=\mathbf{{s}}_i^{{\!\top}}P_i^{{\,L-2}}\mathbf{{e}}_i$, where $P_i$ is the
adjacency matrix of that digraph.
\end{{lemma}}

\begin{{proof}}
Consecutive vertices overlap in one {line}, so a walk of length $L-2$ is exactly a sequence
of $L$ {lines}, that is, an array. Along it, the cells of {line} $t$ for $2\le t\le L-1$ are
judged once, at the step leaving $(r^{{(t-1)}},r^{{(t)}},\cdot)$, with their true neighbours;
those of {line} $1$ are judged by $\mathbf{{s}}_i$ with no {line} above, and those of {line}
$L$ by $\mathbf{{e}}_i$ with no {line} below. Hence the running count is the number of
offending cells among the {lines} judged so far, and the walk exists exactly when that total
never exceeds ${E}$; since the total only grows, that is implied by the final value being
${E}$, which $\mathbf{{e}}_i$ imposes.
\end{{proof}}

Assembling the ${K}$ chains block-diagonally into $N$ of size $S={S}$ with the weights of
Lemma~\ref{{lem:inv}} in the start vector $\mathbf{{v}}$ and the end markers in
$\mathbf{{u}}$,
\begin{{equation}}\label{{eq:walk2}}
{scale}\;a(n)\;=\;\mathbf{{v}}^{{\!\top}}N^{{\,L-2}}\mathbf{{u}},\qquad L={Ltex} .
\end{{equation}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and ${Gtex}$.

\begin{{lemma}}\label{{lem:crit}}
With $n_0$ the least index for which $L\ge2$, $o={mult}n_0+{base}-2$ and
$h_j=G^{{j}}N^{{o}}\mathbf{{u}}$, we have for $j\ge{order}$
\[
{scale}\Bigl(a(n_0+j)-\sum_i c_i\,a(n_0+j-i)\Bigr)=\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,
\qquad w=h_{{{order}}}-\sum_i c_i h_{{{order}-i}} .
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
coming out an integer each time; no shift was fitted, the number of {lines} being
$L={Ltex}$ from the entry's own name and the offset saying which index the first published
term carries. A misreading of the offending-cell rule, of the budget, or of the inversion in
Lemma~\ref{{lem:inv}} would change the counts and be rejected here.

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
    hits = [h for h in json.load(open("transfer12_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/tc{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
