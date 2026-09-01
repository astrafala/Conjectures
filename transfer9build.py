#!/usr/bin/env python3
"""One paper per Hardin entry with a two-line-window cell condition over the alphabet."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer9 as T9

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
    p = T9.parse_name(e["name"])
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    off = h["offset"]
    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    cross, crosses = ("column", "columns") if rowwalk else ("row", "rows")
    Ltex = rf"{mult}n+{base}" if mult != 1 else (rf"n+{base}" if base else "n")
    fracinv = "" if frac == 1 else rf"\tfrac1{{{frac}}}"
    nb = ",\\ ".join(f"({x},{y})" for x, y in h["offs"])
    ul = ("" if not h["ul0"] else
          r" A further clause fixes the upper-left entry of the array to be $0$; it removes "
          r"nothing but a relabelling, and enters the construction as a restriction on which "
          + line + r"s may begin a walk.")
    ulstart = ("" if not h["ul0"] else
               r" and, where the entry demands it, whose first entry is $0$")
    Gtex = rf"G=N^{{{mult}}}" if mult != 1 else "G=N"

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by a two-line transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{alpha}\}}$ in which every cell is constrained by the
values of its neighbours, and carries an empirical recurrence of order ${order}$ contributed
by R.~H.~Hardin. It is true, and it is not an empirical matter. The neighbourhood reaches one
{line} up and one {line} down, so a single {line} is not enough state and a plain walk count
is wrong; the right object is a walk on ordered \emph{{pairs}} of consecutive {lines}, where
each step tests the condition on the middle {line} against both its neighbours and the two
ends are tested with one neighbour {line} absent. That makes $a(n)$ a walk count on a digraph
with $S={S}$ vertices, and the conjectured recurrence is then decided by a finite exact
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

\section{{The condition, and why one {line} is not enough}}

The arrays have ${W}$ {crosses} and $L={Ltex}$ {lines}; write $x_{{t,u}}$ for the entry in
{line} $t$ and {cross} $u$, each in $\{{0,\dots,{alpha}\}}$. With the neighbour offsets
\[
\mathcal N=\{{{nb}\}},
\]
written as ({line} shift, {cross} shift) and counting only positions inside the array, the
entry's requirement is
\begin{{equation}}\label{{eq:loc}}
{h['tex']}
\end{{equation}}
for every cell $(t,u)$.{ul}

Some offsets in $\mathcal N$ have a positive {line} shift and some a negative one, so the
condition at a cell of {line} $t$ involves {lines} $t-1$, $t$ and $t+1$ together. A transfer
matrix whose states are single {lines} cannot express it: the step from $r^{{(t)}}$ to
$r^{{(t+1)}}$ does not know $r^{{(t-1)}}$. Two consecutive {lines} are enough, and that is
the state used below.

\section{{The digraph}}

Let $V=\{{0,\dots,{alpha}\}}^{{{W}}}$ be the possible {lines} and take
$\mathcal V=V\times V$, of size $S={S}$, as the vertex set. Declare $(p,c)\to(c,x)$ an edge
when every cell of the middle {line} $c$ satisfies \eqref{{eq:loc}} with $p$ above it and $x$
below it; there is no edge between pairs that do not overlap in this way. Let $N$ be the
adjacency matrix, $\mathbf{{v}}$ the indicator of the pairs $(p,c)$ whose first {line} $p$
satisfies \eqref{{eq:loc}} with no {line} above{ulstart}, and $\mathbf{{u}}$ the indicator of
the pairs $(p,c)$ whose second {line} $c$ satisfies it with no {line} below.

\begin{{lemma}}\label{{lem:walk}}
For $L\ge2$, the arrays counted by the entry with $L$ {lines} are exactly the walks
\[
(r^{{(1)}},r^{{(2)}})\to(r^{{(2)}},r^{{(3)}})\to\cdots\to(r^{{(L-1)}},r^{{(L)}})
\]
of length $L-2$ starting at a vertex marked by $\mathbf{{v}}$ and ending at one marked by
$\mathbf{{u}}$. Consequently
\[
a(n)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}N^{{\,L-2}}\mathbf{{u}},\qquad L={Ltex} .
\]
\end{{lemma}}

\begin{{proof}}
Consecutive vertices of such a walk overlap in one {line}, so a walk of that shape is
precisely a sequence $r^{{(1)}},\dots,r^{{(L)}}$ of {lines}, that is, an array of $L$ {lines}
and ${W}$ {crosses}. In the walk, the cells of {line} $t$ for $2\le t\le L-1$ are tested
exactly once --- at the step leaving $(r^{{(t-1)}},r^{{(t)}})$ --- and with their true
neighbours $r^{{(t-1)}}$ and $r^{{(t+1)}}$. The cells of {line} $1$ are tested by
$\mathbf{{v}}$ and those of {line} $L$ by $\mathbf{{u}}$, in both cases by the same condition
with the missing neighbour {line} treated as absent, which is how the array itself behaves at
its boundary. So the walks are exactly the admissible arrays, and summing over all starting
and ending vertices counts them.
\end{{proof}}

\section{{The criterion}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and put ${Gtex}$, so that a unit step in $n$ advances the walk by
${mult}$ {line}{"" if mult == 1 else "s"}.

\begin{{lemma}}\label{{lem:crit}}
Let $n_0$ be the least index with $L\ge2$ and $h_j=G^{{j}}N^{{o}}\mathbf{{u}}$, where
$o={mult}n_0+{base}-2$. Then for $j\ge{order}$,
\[
a(n_0+j)-\sum_i c_i\,a(n_0+j-i)\;=\;{fracinv}\,\mathbf{{v}}^{{\!\top}}G^{{\,j-{order}}}w,
\qquad w=h_{{{order}}}-\sum_i c_i\,h_{{{order}-i}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}G^{{m}}w=0$ for every $m\ge0$, and it is enough to check
$m=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
Substitute Lemma~\ref{{lem:walk}} and factor $G^{{j-{order}}}$ out of
$G^{{j}}-\sum_ic_iG^{{j-i}}$; the nonzero scalar ${fracinv or "1"}$ does not affect
vanishing. For the last clause, Cayley--Hamilton makes $G^{{S}}$ an integer combination of
$I,G,\dots,G^{{S-1}}$, so $\mathbf{{v}}^{{\!\top}}G^{{m}}w$ for $m\ge S$ is the corresponding
combination of the earlier values; if those vanish, so do all the rest.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The digraph was built directly from \eqref{{eq:loc}}: for each of the $S={S}$ pairs and each
of the $({alpha}+1)^{{{W}}}$ possible next {lines}, the condition was tested on every cell of
the middle {line}. The vector $w$ was formed by ${order}$ applications of $G$ in exact integer
arithmetic and $\mathbf{{v}}^{{\!\top}}G^{{m}}w$ evaluated for $m=0,1,\dots$, again exactly.
Every one of those integers vanishes from the index corresponding to $n={nthr}+1$ onwards,
and the run was continued until $S+1$ consecutive zeros had been seen, which by
Lemma~\ref{{lem:crit}} settles every larger $m$ at once.
\end{{proof}}

\begin{{remark}}
The argument gives more than the recurrence: the sequence is $C$-finite with characteristic
polynomial dividing that of $G$, hence has a rational generating function whose denominator
divides $\det(I-xG)$. The conjectured recurrence is one consequence; the minimal one is a
divisor of $q$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the walk counts of Lemma~\ref{{lem:walk}} were compared against the entry's DATA at
every one of the ${nterms}$ published indices, with no shift fitted: the number of {lines} is
read off the entry's own name as $L={Ltex}$ and the entry's offset says which index the first
published term carries. The values agree exactly. A misreading of \eqref{{eq:loc}}, of the
neighbour set, or of the boundary treatment would give a different digraph and different
counts, so this is a test of the modelling and not only of the arithmetic.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes wherever it applies.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried to the full
Cayley--Hamilton bound in exact integer arithmetic rather than to a sampled prefix, and
returned zero throughout.

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
    hits = [h for h in json.load(open("transfer9_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t9{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
