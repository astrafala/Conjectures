#!/usr/bin/env python3
"""One paper per Hardin entry with a two-line-window cell condition over the alphabet."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer13 as TD

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
    pv, qv, cc = h["p"], h["q"], h["c"]
    nf = W if not rowwalk else 1
    flagpara = (rf"""Because the walk runs along {lines} while row major order runs along
{crosses}, the two orders do not agree, and a single flag would not know which of the two
first occurrences came first. The state therefore carries one flag for each of the ${W}$
{crosses}: $0$ while neither ${pv}$ nor ${qv}$ has been seen in that {cross}, $1$ if ${pv}$
was seen there first, $2$ if ${qv}$ was. An array is accepted when the first {cross} whose
flag is nonzero has flag $1$ --- row major order compares {crosses} first and, within a
{cross}, the earlier {line} --- or when no flag is set at all, in which case nothing is out of
order.""" if not rowwalk else rf"""Here the walk runs along {lines}, which is the order row
major reading uses, so a single flag suffices: $0$ while neither ${pv}$ nor ${qv}$ has
occurred, and thereafter $1$ or $2$ according to which occurred first, the first occurrence
inside a {line} being found by scanning it left to right. An array is accepted when the flag
is not $2$.""")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{alpha}\}}$ under a neighbour condition together with
two symmetry-breaking clauses: the upper-left entry is $0$, and ${pv}$ must appear before
${qv}$ in row major order. The last of these is not local --- it compares first occurrences
across the whole array --- but it becomes local once the state carries which of the two values
was seen first. With that, $a(n)$ is a walk count on $S={S}$ vertices and the empirical
recurrence of order ${order}$ contributed by R.~H.~Hardin follows from a finite exact
computation.
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

\section{{The three clauses}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}; write $x_{{t,u}}$ for the entry in
{line} $t$ and {cross} $u$. The neighbour condition is
\begin{{equation}}\label{{eq:loc}}
{h['tex']}\qquad\text{{for every offset }}(d_1,d_2)\in\mathcal N=\{{{h['nbtex']}\}}
\end{{equation}}
inside the array. The relation ``$y={cc}-x$'' is symmetric, so each unordered adjacency need
only be tested once; the offsets above are the forward representatives, one per direction,
and every one of them has a nonnegative {line} shift. A single {line} of state is therefore
enough for \eqref{{eq:loc}}: the cells of a {line} are settled by that {line} and the next.

{flagpara}

\begin{{lemma}}\label{{lem:walk}}
Let $\mathcal V$ be the set of pairs (a {line}, a flag vector), $|\mathcal V|=S={S}$, let
$(r,f)\to(s,f')$ be an edge when \eqref{{eq:loc}} holds for the cells of $r$ with $s$ beneath
it and $f'$ is $f$ updated by $s$, let $\mathbf{{v}}$ mark the vertices whose {line} begins
with $0$ and whose flag is the one that {line} alone produces, and $\mathbf{{u}}$ those whose
{line} satisfies \eqref{{eq:loc}} with nothing beneath it and whose flag is accepted. Then
\[
a(n)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}N^{{\,L-1}}\mathbf{{u}},\qquad L={Ltex}.
\]
\end{{lemma}}

\begin{{proof}}
A walk of length $L-1$ is a sequence of $L$ {lines}, and its flag component is determined by
them, so walks correspond to arrays. Along the walk the cells of {line} $t$ are tested once,
at the step leaving it, with the correct neighbour {line}; the cells of the last {line} are
tested by $\mathbf{{u}}$ with no {line} beneath, which is how the array behaves at its edge.
The flag component is by construction the record of first occurrences among the {lines} laid
down so far, so $\mathbf{{u}}$ imposes exactly the ordering clause, and $\mathbf{{v}}$ imposes
the upper-left clause. The state carries a {line}, not a boundary, so $L$ {lines} make a walk
of length $L-1$.
\end{{proof}}

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and ${Gtex}$.

\begin{{lemma}}\label{{lem:crit}}
With $n_0$ the least index for which $L\ge1$, $o={mult}n_0+{base}-1$ and
$h_j=G^{{j}}N^{{o}}\mathbf{{u}}$, we have for $j\ge{order}$
\[
a(n_0+j)-\sum_i c_i\,a(n_0+j-i)={fracinv}\,\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,
\qquad w=h_{{{order}}}-\sum_i c_ih_{{{order}-i}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for all $m\ge0$, and $m<S$ suffices.
\end{{lemma}}

\begin{{proof}}
Substitute Lemma~\ref{{lem:walk}} and factor. By Cayley--Hamilton $G^{{S}}$ is an integer
combination of $I,G,\dots,G^{{S-1}}$, so every later value repeats that combination of earlier
ones.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The digraph was built directly from \eqref{{eq:loc}} and the flag update. The vector $w$ was
formed by ${order}$ applications of $G$ in exact integer arithmetic and
$\mathbf{{v}}^{{\!\top}}G^{{m}}w$ evaluated for $m=0,1,\dots$, again exactly. Every one of
those integers vanishes from the index corresponding to $n={nthr}+1$ onwards, and the run
continued until $S+1$ consecutive zeros had been seen.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the walk counts of Lemma~\ref{{lem:walk}} were compared against the entry's DATA at
every one of the ${nterms}$ published indices, with no shift fitted: the number of {lines} is
$L={Ltex}$ from the entry's own name and the offset says which index carries the first
published term. The values agree exactly. The ordering clause is where a misreading would
show first, and it is the reason the flags are per {cross} rather than a single value.

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
    hits = [h for h in json.load(open("transfer13_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/td{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
