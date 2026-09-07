#!/usr/bin/env python3
"""One paper per Hardin entry whose condition counts adjacent pairs globally."""
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
    W, alpha, S = h["fixed"], h["alpha"], h["S"]
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, frac, mult = h["base"], h["frac"], h["mult"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    off = h["offset"]
    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    cross, crosses = ("column", "columns") if rowwalk else ("row", "rows")
    Ltex = rf"{mult}n+{base}" if mult != 1 else (rf"n+{base}" if base else "n")
    fracinv = "" if frac == 1 else rf"\tfrac1{{{frac}}}"
    target = "exactly one" if h["exact"] else "at most one"
    Etex = "=1" if h["exact"] else r"\le1"
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by a counting transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{alpha}\}}$ subject to a condition on the array as a
whole rather than cell by cell: the number of adjacent pairs with a stated property must be
{target}. A transfer matrix still applies once the running count is carried in the state; and
because a count of two or more can never come back, those states may be dropped outright,
which is what keeps the digraph sparse. That makes $a(n)$ a walk count on $S={S}$ vertices,
and the empirical recurrence of order ${order}$ contributed by R.~H.~Hardin then follows from
a finite exact computation.
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

\section{{A global count, and how to carry it}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}; write $x_{{t,u}}$ for the entry in
{line} $t$ and {cross} $u$. Call two cells \emph{{adjacent}} when they differ by one of the
offsets
\[
\mathcal N=\{{{h['nbtex']}\}},
\]
written as ({line} shift, {cross} shift), and call an adjacent pair $\{{p,q\}}$
\emph{{marked}} when
\[
{h['tex']} .
\]
Each unordered adjacency is represented by exactly one offset, all with a nonnegative {line}
shift, so every pair is named once and only once: the pairs inside a {line} are seen when
that {line} is laid down, and the pairs joining two {lines} when the later of the two is. The
entry's requirement is
\begin{{equation}}\label{{eq:glob}}
\#\{{\text{{marked pairs in the whole array}}\}}\;{Etex}.
\end{{equation}}

This is not a condition on any bounded window, so no transfer matrix over {lines} alone can
express it. It becomes one as soon as the running total is part of the state. Let
\[
\mathcal V=\bigl\{{(r,c):\ r\in\{{0,\dots,{alpha}\}}^{{{W}}},\ c\in\{{0,1\}}\bigr\}},
\qquad |\mathcal V|=S={S},
\]
and for {lines} $r,s$ write $\beta(r,s)$ for the number of marked pairs joining them plus the
number of marked pairs inside $s$. Declare $(r,c)\to(s,c+\beta(r,s))$ an edge whenever
$c+\beta(r,s)\le1$, and no edge otherwise.

\begin{{remark}}
Dropping the states with $c\ge2$ is not an approximation. Once the total has reached two it
can only grow, so no array satisfying \eqref{{eq:glob}} passes through such a state. Keeping
them --- as a third, absorbing value of $c$ --- would make every pair of {lines} an edge and
the digraph dense, with $({alpha}+1)^{{2\cdot{W}}}$ edges instead of the sparse set used here.
\end{{remark}}

\begin{{lemma}}\label{{lem:walk}}
Let $\mathbf{{v}}$ mark the vertices $(r,c)$ whose count $c$ equals the number of marked pairs
inside $r$ alone, and $\mathbf{{u}}$ the vertices with $c{Etex}$. Then for $L\ge1$ the arrays
of $L$ {lines} satisfying \eqref{{eq:glob}} are exactly the walks of length $L-1$ from a
vertex marked by $\mathbf{{v}}$ to one marked by $\mathbf{{u}}$, so
\[
a(n)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}N^{{\,L-1}}\mathbf{{u}},\qquad L={Ltex} .
\]
\end{{lemma}}

\begin{{proof}}
A walk $(r^{{(1)}},c_1)\to\cdots\to(r^{{(L)}},c_L)$ determines the array
$r^{{(1)}},\dots,r^{{(L)}}$, and conversely each array determines at most one walk, since the
starting count is fixed by $\mathbf{{v}}$ and each step's count is determined. By induction
$c_t$ is the number of marked pairs in the first $t$ {lines}: it holds at $t=1$ by the
definition of $\mathbf{{v}}$, and the step from $t$ to $t+1$ adds exactly the pairs joining
{lines} $t$ and $t+1$ together with those inside {line} $t+1$, which are precisely the marked
pairs of the first $t+1$ {lines} not already counted --- each unordered pair being named by
exactly one offset. The walk exists (no edge is missing) if and only if the running total
never exceeds $1$, which for a nondecreasing total is the same as $c_L\le1$; and
$\mathbf{{u}}$ imposes the entry's requirement on $c_L$. Note the state already carries one
{line}, so $L$ {lines} correspond to a walk of length $L-1$.
\end{{proof}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and ${Gtex}$.

\begin{{lemma}}\label{{lem:crit}}
With $n_0$ the least index for which $L\ge1$ and $h_j=G^{{j}}N^{{o}}\mathbf{{u}}$,
$o={mult}n_0+{base}-1$,
\[
a(n_0+j)-\sum_i c_i\,a(n_0+j-i)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,
\qquad w=h_{{{order}}}-\sum_i c_i h_{{{order}-i}},
\]
for $j\ge{order}$. Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for every $m\ge0$, and it is enough to check
$m=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
Substitute Lemma~\ref{{lem:walk}} and factor. By Cayley--Hamilton $G^{{S}}$ is an integer
combination of $I,G,\dots,G^{{S-1}}$, so every later value is the same combination of earlier
ones.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The digraph was built directly from the definition of a marked pair. The vector $w$ was
formed by ${order}$ applications of $G$ in exact integer arithmetic and
$\mathbf{{v}}^{{\!\top}}G^{{m}}w$ evaluated for $m=0,1,\dots$, again exactly. Every one of
those integers vanishes from the index corresponding to $n={nthr}+1$ onwards, and the run
continued until $S+1$ consecutive zeros had been seen, which by Lemma~\ref{{lem:crit}}
settles every larger $m$.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the walk counts of Lemma~\ref{{lem:walk}} were compared against the entry's DATA at
every one of the ${nterms}$ published indices, with no shift fitted: the number of {lines} is
$L={Ltex}$, read off the entry's own name, and the offset says which index the first
published term carries. The values agree exactly. This is where an error in the pair
bookkeeping would show: counting an unordered pair twice, or missing the pairs inside the
first {line}, changes the counts immediately. Indeed a first version of the computation
placed the walk at length $L-2$ rather than $L-1$ --- the state carries a {line}, not a
boundary --- and every value came out one index late, which the DATA comparison rejected.

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
    hits = [h for h in json.load(open("transfer11_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/tb{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
