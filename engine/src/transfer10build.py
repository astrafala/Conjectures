#!/usr/bin/env python3
"""One paper per Hardin entry with explicit backward offsets and a canonical-form clause."""
import conjquote
import os

_ROSTER = None
def _date(a):
    """the date the result was obtained: a paper already in the roster keeps the
    date it was written with, a new one takes the date the caller gives."""
    global _ROSTER
    if _ROSTER is None:
        import json as _j
        _ROSTER = {v['anum'] for v in _j.load(open('paper-engines.json')).values()}
    return '1 September 2026' if a in _ROSTER else os.environ.get('PAPER_DATE', '1 September 2026')

import os, json, re
import localentry as LE, phibuild, transferbuild, transfer10 as TA

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
    nb = ",\\ ".join(f"({x},{y})" for x, y in h["offs"])
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"
    raw = sum(i ** (2 * W) for i in range(1, K + 1))

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by counting patterns}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays in which no entry may repeat a value found at any of three stated
offsets, and which are moreover written in canonical form (``new values introduced in order
$0..{K - 1}$''). The canonical-form clause is not local and no transfer matrix over the
alphabet sees it; but the condition is stated in equalities, so what is counted is equality
patterns, and the pattern counts are recovered from the counts $L_i$ over an $i$-letter
alphabet by inverting a falling factorial:
${K}!\,a(n)=\sum_i\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n)$ with $D_m$ the derangement numbers.
Some of the offsets reach two {lines} back, so each $L_i$ is a walk count whose states are
ordered pairs of consecutive {lines}; relabelling-invariance makes that chain lumpable,
cutting ${raw}$ pairs to $S={S}$ states. The entry's empirical recurrence of order ${order}$,
contributed by R.~H.~Hardin, then follows from a finite exact computation.
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

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}; write $x_{{t,u}}$ for the entry in
{line} $t$ and {cross} $u$. With
\[
\mathcal N=\{{{nb}\}}
\]
(offsets as ({line} shift, {cross} shift)), the entry's requirement is
\begin{{equation}}\label{{eq:loc}}
{h['tex']}.
\end{{equation}}
Every offset has a nonpositive {line} shift, so the condition at a cell of {line} $t$ is
settled by {lines} $t-2$, $t-1$ and $t$; but some shift is $-2$, so one previous {line} is not
enough state.

The condition is stated purely in equalities, so it is unchanged by any relabelling of the
values and is a property of the \emph{{equality pattern}} of the array --- the partition of
the cells into classes of equal entries. The clause ``new values introduced in order
$0..{K - 1}$'' keeps exactly one array from each relabelling class, so with $K={K}$ values
available the entry counts admissible patterns with at most $K$ classes.

\begin{{lemma}}\label{{lem:inv}}
Let $L_i(n)$ count the arrays over an alphabet of $i$ letters satisfying \eqref{{eq:loc}},
with no canonical-form clause, and $N_j(n)$ the admissible patterns with exactly $j$ classes.
Then $L_i=\sum_j N_j\,i(i-1)\cdots(i-j+1)$ and
\[
{K}!\,\sum_{{j\le {K}}}N_j(n)\;=\;\sum_{{i=0}}^{{{K}}}\binom{{{K}}}{{i}}D_{{{K}-i}}\,L_i(n),
\qquad D_m=m!\sum_{{t=0}}^{{m}}\frac{{(-1)^t}}{{t!}} .
\]
\end{{lemma}}

\begin{{proof}}
A labelled array satisfying the condition is a pattern together with an injection of its
classes into the alphabet, and a pattern with $j$ classes admits $i(i-1)\cdots(i-j+1)$ such
injections; that is the first identity. Writing the falling factorial as $j!\binom{{i}}{{j}}$
gives $L_i=\sum_j(j!N_j)\binom{{i}}{{j}}$, so binomial inversion yields
$j!N_j=\sum_i(-1)^{{j-i}}\binom{{j}}{{i}}L_i$. Summing over $j\le{K}$ and exchanging the
order of summation, the coefficient of $L_i$ is $\sum_{{t\le{K}-i}}(-1)^t/(i!\,t!)$, which on
multiplying by ${K}!$ becomes
$\binom{{{K}}}{{i}}({K}-i)!\sum_{{t\le{K}-i}}(-1)^t/t!=\binom{{{K}}}{{i}}D_{{{K}-i}}$, an
integer.
\end{{proof}}

\section{{Each $L_i$ is a walk count on pairs of {lines}}}

Fix $i$, let $V_i=\{{0,\dots,i-1\}}^{{{W}}}$ and take $\mathcal V=V_i\times V_i$ as vertices.
Declare $(p,c)\to(c,x)$ an edge when every cell of the NEW {line} $x$ satisfies
\eqref{{eq:loc}}, reading $c$ as the {line} one step back and $p$ as the {line} two steps
back. Let $P_i$ be the adjacency matrix and $\mathbf{{s}}_i$ the indicator of the pairs
$(p,c)$ in which $p$ satisfies \eqref{{eq:loc}} with no {line} before it and $c$ satisfies it
with only $p$ before it.

\begin{{lemma}}\label{{lem:walk}}
For $L\ge2$ the arrays of $L$ {lines} satisfying \eqref{{eq:loc}} are exactly the walks
$(r^{{(1)}},r^{{(2)}})\to\cdots\to(r^{{(L-1)}},r^{{(L)}})$ of length $L-2$ starting at a
vertex marked by $\mathbf{{s}}_i$, so
$L_i=\mathbf{{s}}_i^{{\!\top}}P_i^{{\,L-2}}\mathbf{{1}}$.
\end{{lemma}}

\begin{{proof}}
Consecutive vertices overlap in one {line}, so such a walk is precisely a sequence
$r^{{(1)}},\dots,r^{{(L)}}$ of {lines}. The condition at the cells of {line} $t$ for $t\ge3$
is tested exactly once, at the step arriving at $(r^{{(t-1)}},r^{{(t)}})$, and with the
correct earlier {lines}; the cells of {lines} $1$ and $2$ are tested by $\mathbf{{s}}_i$, with
the {lines} that would lie before them absent, which is how the array behaves at its top. No
further condition constrains the end of the array, so the walk may finish anywhere.
\end{{proof}}

\begin{{lemma}}\label{{lem:lump}}
Two vertices with the same equality pattern have, for each target pattern, the same number of
successors carrying it, and the same value of $\mathbf{{s}}_i$. Hence the chain is strongly
lumpable over patterns, and $L_i$ may be computed on the quotient, whose states are the set
partitions of the $2\cdot{W}$ cells of a pair into at most $i$ classes.
\end{{lemma}}

\begin{{proof}}
Equal patterns means $(p',c')=(\sigma(p),\sigma(c))$ for a permutation $\sigma$ of the
alphabet. Condition \eqref{{eq:loc}} is a statement about equalities between entries, so it is
invariant under $\sigma$; therefore $x\mapsto\sigma(x)$ is a bijection between the successor
sets which preserves patterns, and $\mathbf{{s}}_i$ agrees on the two vertices. The number of
pairs with pattern $P$ is $e_P=i(i-1)\cdots(i-|P|+1)$, which supplies the weights.
\end{{proof}}

Assembling the ${K}$ lumped chains block-diagonally into $N$ of size $S={S}$, with the
weights of Lemma~\ref{{lem:inv}} folded into the start vector $\mathbf{{v}}$,
\begin{{equation}}\label{{eq:walk2}}
{scale}\;a(n)\;=\;\mathbf{{v}}^{{\!\top}}N^{{\,L-2}}\mathbf{{1}},\qquad L={Ltex} .
\end{{equation}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and ${Gtex}$.

\begin{{lemma}}\label{{lem:crit}}
With $n_0$ the least index for which $L\ge2$ and $h_j=G^{{j}}N^{{o}}\mathbf{{1}}$,
$o={mult}n_0+{base}-2$, we have for $j\ge{order}$
\[
{scale}\Bigl(a(n_0+j)-\sum_i c_i\,a(n_0+j-i)\Bigr)
=\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,\qquad
w=h_{{{order}}}-\sum_i c_i h_{{{order}-i}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for every $m\ge0$, and it is enough to check
$m=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
Substitute \eqref{{eq:walk2}} and factor; the nonzero scalar ${scale}$ does not affect
vanishing. By Cayley--Hamilton $G^{{S}}$ is an integer combination of $I,G,\dots,G^{{S-1}}$,
so each $\mathbf{{v}}^{{\!\top}}G^{{m}}w$ with $m\ge S$ is the corresponding combination of
earlier values.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The lumped transition counts were built by taking one representative pair for each pattern,
enumerating every {line} $x$ over the alphabet, testing \eqref{{eq:loc}} on $x$, and sorting
the survivors by the pattern of the new pair. The vector $w$ was formed by ${order}$
applications of $G$ in exact integer arithmetic and $\mathbf{{v}}^{{\!\top}}G^{{m}}w$
evaluated for $m=0,1,\dots$, again exactly. Every one of those integers vanishes from the
index corresponding to $n={nthr}+1$ onwards, and the run continued until $S+1$ consecutive
zeros had been seen.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the right-hand side of \eqref{{eq:walk2}}, divided by ${scale}$, was evaluated at every
one of the ${nterms}$ published indices and agrees with the entry's DATA exactly, the quotient
coming out an integer each time; no shift was fitted, the number of {lines} being read off the
entry's own name as $L={Ltex}$ and the entry's offset saying which index the first published
term carries. A misreading of the offsets, of the inversion, or of the treatment of the first
two {lines} would show up here.

Second, the lumped chain was checked against the unlumped one on the small shapes of this
family, the walk counts over the full alphabet agreeing with the weighted sum over patterns
term by term.

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
    hits = [h for h in json.load(open("transfer10_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/ta{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
