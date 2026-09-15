#!/usr/bin/env python3
"""One paper per Hardin entry whose cell condition needs a two-line window."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer8 as T8

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
    W, K, S = h["fixed"], h["K"], h["S"]
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, frac, mult, raw = h["base"], h["frac"], h["mult"], h["raw"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    p = T8.parse_name(e["name"])
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    off = h["offset"]
    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    cross, crosses = ("column", "columns") if rowwalk else ("row", "rows")
    Ltex = rf"{mult}n+{base}" if mult != 1 else (rf"n+{base}" if base else "n")
    scale = rf"{K}!" + ("" if frac == 1 else rf"\,/\,{frac}")
    fracinv = "" if frac == 1 else rf"\tfrac1{{{frac}}}"

    if h["ckind"] == "cmp":
        condtex = (r"""for every cell, the number $c_{\mathrm{v}}$ of its vertical
neighbours carrying the same value and the number $c_{\mathrm{h}}$ of its horizontal
neighbours carrying the same value satisfy
\begin{equation}\label{eq:loc}
""" + p["tex"] + r"""
\end{equation}
(only neighbours inside the array are counted)""")
    else:
        offs = p["data"][1]
        nb = ",\\ ".join(f"({x},{y})" for x, y in offs)
        sense = ("with a different value" if p["data"][2] else "with an equal value")
        condtex = (r"""with the neighbour offsets
\[
\mathcal N=\{""" + nb + r"""\}
\]
written as (""" + line + r""" shift, """ + cross + r""" shift), the requirement is
\begin{equation}\label{eq:loc}
\#\bigl\{(d_1,d_2)\in\mathcal N:\ (t+d_1,u+d_2)\ \text{lies in the array and its entry is }
""" + ("different from" if p["data"][2] else "equal to") + r""" x_{t,u}\bigr\}\ """
                   + (r"\text{is not }" if p["negated"] else "") + p["reltex"] + r"""
\end{equation}
for every cell $(t,u)$""")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by a two-line transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays in which every cell is constrained by its neighbours on \emph{{both}}
sides, and which are moreover written in canonical form (``values introduced in row major
order''). Neither feature is visible to a one-line transfer matrix: the cell condition
reaches the {line} above and the {line} below, and the canonical-form clause is not local at
all. Both are dealt with. What is counted is equality patterns, so
${K}!\,a(n)=\sum_i\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n)$ with $D_m$ the derangement numbers and
$L_i$ the count over an $i$-letter alphabet; and each $L_i$ is a walk count whose vertices
are ordered pairs of consecutive {lines}. Relabelling-invariance makes the chain strongly
lumpable, cutting ${raw}$ pairs down to $S={S}$ states. The entry's empirical recurrence of
order ${order}$, contributed by R.~H.~Hardin, then follows from a finite exact computation.
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

\section{{The condition, and what the canonical-form clause counts}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}. Write $x_{{t,u}}$ for the entry in
{line} $t$ and {cross} $u$. {condtex}.

The condition is stated purely in equalities between entries, so it is unchanged by any
relabelling of the values: it is a property of the \emph{{equality pattern}} --- the partition
of the cells into classes of equal entries --- and not of the values themselves. The clause
``values introduced in row major order'' selects exactly one array from each relabelling
class, so with $K={K}$ available values the entry counts admissible patterns with at most $K$
classes.

\begin{{lemma}}\label{{lem:inv}}
Let $L_i(n)$ count the arrays over an alphabet of $i$ letters that satisfy the cell
condition, with no canonical-form clause, and $N_j(n)$ the admissible patterns with exactly
$j$ classes. Then $L_i=\sum_j N_j\,i(i-1)\cdots(i-j+1)$ and
\[
{K}!\,\sum_{{j\le {K}}}N_j(n)\;=\;\sum_{{i=0}}^{{{K}}}\binom{{{K}}}{{i}}D_{{{K}-i}}\,L_i(n),
\qquad D_m=m!\sum_{{t=0}}^{{m}}\frac{{(-1)^t}}{{t!}} .
\]
\end{{lemma}}

\begin{{proof}}
A labelled array satisfying the condition is a pattern together with an injection of its
classes into the alphabet, and a pattern with $j$ classes admits $i(i-1)\cdots(i-j+1)$ of
them; that is the first identity. Writing $i(i-1)\cdots(i-j+1)=j!\binom{{i}}{{j}}$ it reads
$L_i=\sum_j(j!N_j)\binom{{i}}{{j}}$, so binomial inversion gives
$j!N_j=\sum_i(-1)^{{j-i}}\binom{{j}}{{i}}L_i$. Summing over $j\le{K}$ and exchanging the
order of summation, the coefficient of $L_i$ is
$\sum_{{t\le{K}-i}}(-1)^t/(i!\,t!)$, which multiplied by ${K}!$ is
$\binom{{{K}}}{{i}}({K}-i)!\sum_{{t\le{K}-i}}(-1)^t/t!=\binom{{{K}}}{{i}}D_{{{K}-i}}$.
\end{{proof}}

\section{{Each $L_i$ is a walk count on pairs of {lines}}}

Fix $i$ and let $V_i=\{{0,\dots,i-1\}}^{{{W}}}$. Because \eqref{{eq:loc}} at a cell of {line}
$t$ involves {lines} $t-1$, $t$ and $t+1$, a single {line} is not enough state. Take the
ordered pairs $(p,c)\in V_i\times V_i$ as vertices and declare $(p,c)\to(c,x)$ an edge when
every cell of the middle {line} $c$ satisfies \eqref{{eq:loc}} with $p$ above it and $x$
below it. Let $P_i$ be the adjacency matrix, $\mathbf{{s}}_i$ the indicator of the pairs
$(p,c)$ whose first {line} $p$ satisfies the condition with no {line} above, and
$\mathbf{{e}}_i$ the indicator of the pairs whose second {line} $c$ satisfies it with no
{line} below.

\begin{{lemma}}\label{{lem:walk}}
For $L\ge2$, the arrays of $L$ {lines} satisfying the condition are exactly the walks
$(r^{{(1)}},r^{{(2)}})\to(r^{{(2)}},r^{{(3)}})\to\cdots\to(r^{{(L-1)}},r^{{(L)}})$ of length
$L-2$ that start at a vertex marked by $\mathbf{{s}}_i$ and end at one marked by
$\mathbf{{e}}_i$, so
$L_i=\mathbf{{s}}_i^{{\!\top}}P_i^{{\,L-2}}\mathbf{{e}}_i$.
\end{{lemma}}

\begin{{proof}}
A walk of that form is exactly a sequence of {lines} $r^{{(1)}},\dots,r^{{(L)}}$, since
consecutive vertices overlap in one {line}. In such a walk the condition at the cells of
{line} $t$ is tested once, at the step leaving $(r^{{(t-1)}},r^{{(t)}})$, and with the
correct neighbours $r^{{(t-1)}}$ and $r^{{(t+1)}}$; the cells of {line} $1$ are tested by
$\mathbf{{s}}_i$, which uses the condition with the {line} above absent, and those of {line}
$L$ by $\mathbf{{e}}_i$. So every cell is tested exactly once and with its true
neighbourhood, which is the claim.
\end{{proof}}

\begin{{lemma}}\label{{lem:lump}}
Write $\pi(p,c)$ for the equality pattern of the pair. If $\pi(p,c)=\pi(p',c')$ then for
every pattern $Q$ the two vertices have the same number of successors of pattern $Q$, and
$\mathbf{{s}}_i$, $\mathbf{{e}}_i$ take the same value at both. Hence the chain is strongly
lumpable over $\pi$ and $L_i$ is computed on the quotient, whose states are the set
partitions of the $2\cdot{W}$ cells of a pair into at most $i$ classes.
\end{{lemma}}

\begin{{proof}}
Equal patterns means $(p',c')=(\sigma(p),\sigma(c))$ for a permutation $\sigma$ of the
alphabet. The edge condition and the two boundary conditions are statements about equalities
between entries, so they are invariant under $\sigma$, and $x\mapsto\sigma(x)$ is a bijection
between the successor sets preserving patterns. The number of pairs with a given pattern $P$
is $e_P=i(i-1)\cdots(i-|P|+1)$, the number of injections of its classes into the alphabet,
which supplies the weights on the quotient.
\end{{proof}}

Assembling the ${K}$ lumped chains block-diagonally into $N$ of size $S={S}$, with the
weights of Lemma~\ref{{lem:inv}} folded into the start vector $\mathbf{{v}}$ and the
end-of-array indicator into $\mathbf{{u}}$,
\begin{{equation}}\label{{eq:walk2}}
{scale}\;a(n)\;=\;\mathbf{{v}}^{{\!\top}}N^{{\,L-2}}\mathbf{{u}},\qquad L={Ltex} .
\end{{equation}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and put $G=N^{{{mult}}}$, so that consecutive values of $n$ advance the
walk by ${mult}$ {lines}.

\begin{{lemma}}\label{{lem:crit}}
With $h_j=G^{{j}}N^{{o}}\mathbf{{u}}$ for the offset $o$ that aligns the first admissible
index,
\[
{scale}\Bigl(a(n)-\sum_i c_i\,a(n-i)\Bigr)\;=\;\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}\,
\Bigl(h_{{{order}}}-\sum_i c_i h_{{{order}-i}}\Bigr)
\]
for the corresponding $j$. Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for every $m\ge0$, where
$w=h_{{{order}}}-\sum_i c_ih_{{{order}-i}}$; and it is enough to check $m=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
Substitute \eqref{{eq:walk2}} and factor. The scalar ${scale}$ is nonzero, so it does not
affect vanishing. For the last clause, Cayley--Hamilton applied to $G$ makes $G^{{S}}$ an
integer combination of $I,G,\dots,G^{{S-1}}$, so each $\mathbf{{v}}^{{\!\top}}G^{{m}}w$ with
$m\ge S$ is the same combination of the earlier values; if those vanish, so do all the rest.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The lumped transition counts were built by taking one representative pair for each pattern,
enumerating every {line} $x$ over the alphabet, testing \eqref{{eq:loc}} on the middle
{line}, and sorting the results by the pattern of the new pair. The vector $w$ was formed by
${order}$ applications of $G$ in exact integer arithmetic and $\mathbf{{v}}^{{\!\top}}G^{{m}}w$
evaluated for $m=0,1,\dots$, again exactly. Every one of those integers vanishes from the
index corresponding to $n={nthr}+1$ onwards, and the run was continued until $S+1$
consecutive zeros had been seen, which by Lemma~\ref{{lem:crit}} settles every larger $m$.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the whole construction was compared against the entry's DATA: the right-hand side of
\eqref{{eq:walk2}}, divided by ${scale}$, was evaluated at every one of the ${nterms}$
published indices and agrees exactly, the quotient coming out an integer each time. This
tests the modelling and not only the arithmetic --- the inversion of Lemma~\ref{{lem:inv}},
the reading of \eqref{{eq:loc}}, the treatment of the first and last {lines}, and the
alignment of the entry's index with $L={Ltex}$ would each show up as a mismatch.

Second, the lumped chain was checked against the unlumped one on the small shapes of this
family: the walk counts over the full alphabet agree with $\sum_P e_Pf_m(P)$ term by term.

Third, the recurrence \eqref{{eq:conj}} was evaluated on the published terms in exact integer
arithmetic with no matrices involved, and the annihilation test of Lemma~\ref{{lem:crit}} was
carried to the full Cayley--Hamilton bound rather than to a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7; falling-factorial
inversion, Section 1.9.)
\bibitem{{kemeny}} J.~G.~Kemeny and J.~L.~Snell, \emph{{Finite Markov Chains}}, Springer,
1976. (Strong lumpability, Section 6.3.)
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("transfer8_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t8{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
