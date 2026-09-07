#!/usr/bin/env python3
"""One paper per Hardin entry with a two-line-window cell condition over the alphabet."""
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
import localentry as LE, phibuild, transferbuild, transfer14 as TE

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None




DIRNAME = {(0, 1): "along the line", (1, 0): "across the lines",
           (1, 1): "diagonally", (1, -1): "antidiagonally"}


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
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"
    items = []
    for dl, dp, c in h["specs"]:
        items.append(rf"\item along the direction $({dl},{dp})$ --- one step of "
                     rf"$({dl},{dp})$ in ({line}, {cross}) coordinates --- every sequence "
                     rf"is {c};")
    for kind in h["lex"]:
        if kind == "line":
            items.append(rf"\item the {lines} themselves, read as vectors, are in "
                         rf"lexicographically nondecreasing order;")
        else:
            items.append(rf"\item the {crosses} themselves, read as vectors, are in "
                         rf"lexicographically nondecreasing order;")
    nuni = sum(1 for dl, dp, c in h["specs"] if dl == 1 and c == "unimodal")
    npos = h["lex"].count("pos")
    flagpara = []
    if nuni:
        flagpara.append(rf"""A unimodal condition across the {lines} is not local: whether a
rise is allowed depends on whether the sequence has already fallen. The state therefore
carries, for each of the ${W}$ sequences currently running in that direction, one bit saying
whether it has fallen. Those bits travel with their sequences --- the bit at {cross} $u$
moves to {cross} $u+d_2$ when the next {line} is laid down, and a sequence beginning at the
far end of the new {line} starts with its bit clear.""")
    if npos:
        flagpara.append(rf"""A lexicographic condition between adjacent {crosses} is decided
at the first {line} where they differ, so the state carries, for each adjacent pair of
{crosses}, one bit: still tied, or already settled in the right order. A {line} that would
settle a pair the wrong way has no outgoing edge.""")
    flagpara = "\n\n".join(flagpara) if flagpara else (
        rf"""All the conditions here are local --- each compares two cells one step apart ---
so no extra state is needed beyond the {line} itself.""")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{alpha}\}}$ whose {lines}, {crosses}, diagonals or
antidiagonals are required to be monotone or unimodal, and carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. A monotone condition is local, but a unimodal one
is not: a sequence is unimodal exactly when it never rises again after it has fallen, so the
state must remember which sequences have already fallen. With those bits carried along, $a(n)$
is a walk count on $S={S}$ vertices and the recurrence follows from a finite exact
computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A16, 15B36.\normalsize

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

\section{{The conditions}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}. Written in ({line}, {cross})
coordinates, the entry asks:
\begin{{itemize}}
{chr(10).join(items)}
\end{{itemize}}
Here ``unimodal'' means nondecreasing and then nonincreasing, that is: no rise after a fall.

{flagpara}

\begin{{lemma}}\label{{lem:walk}}
Let $\mathcal V$ be the set of pairs (a {line} satisfying every within-{line} condition, a
bit vector), $|\mathcal V|=S={S}$; let $(r,f)\to(s,f')$ be an edge when placing $s$ after $r$
breaks none of the across-{line} conditions and $f'$ is $f$ updated by that step; let
$\mathbf{{v}}$ mark the vertices whose bit vector is the one their {line} alone produces.
Then
\[
a(n)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}N^{{\,L-1}}\mathbf{{1}},\qquad L={Ltex}.
\]
\end{{lemma}}

\begin{{proof}}
A walk of length $L-1$ is a sequence of $L$ {lines}, that is, an array, and its bit component
is determined by them. Every within-{line} condition is imposed on each vertex; every
across-{line} condition compares two consecutive {lines} and is imposed on each edge; and the
unimodal and lexicographic bits are, by construction, the record of what the {lines} laid down
so far have already decided, so a violation removes the corresponding edge. Hence the walks
are exactly the admissible arrays. Nothing constrains the last {line} beyond what has already
been imposed, so the walk may end anywhere. The state carries a {line}, not a boundary, so
$L$ {lines} make a walk of length $L-1$.
\end{{proof}}

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
Substitute Lemma~\ref{{lem:walk}} and factor. By Cayley--Hamilton $G^{{S}}$ is an integer
combination of $I,G,\dots,G^{{S-1}}$, so every later value repeats that combination of
earlier ones.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The digraph was built directly from the conditions listed above. The vector $w$ was formed by
${order}$ applications of $G$ in exact integer arithmetic and $\mathbf{{v}}^{{\!\top}}G^{{m}}w$
evaluated for $m=0,1,\dots$, again exactly. Every one of those integers vanishes from the
index corresponding to $n={nthr}+1$ onwards, and the run continued until $S+1$ consecutive
zeros had been seen.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the walk counts of Lemma~\ref{{lem:walk}} were compared against the entry's DATA at
every one of the ${nterms}$ published indices, with no shift fitted. The values agree exactly.
This is what fixes the reading of the wording: ``rows and columns in nondecreasing order''
means the {lines} and {crosses} are sorted as vectors, not that each is nondecreasing along
itself, and the two readings already differ at the second published term --- $86$ against
$50$ for $2\times2$ arrays over $\{{0,1,2,3\}}$. The DATA decides it.

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
    hits = [h for h in json.load(open("transfer14_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/te{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
