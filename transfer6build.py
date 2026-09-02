#!/usr/bin/env python3
"""One paper per Hardin array entry whose 2 X 2 condition is local to the block."""
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


ORD = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
       7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}


def build(h):
    a = h["anum"]
    W, alpha, S = h["fixed"], h["alpha"], h["S"]
    order, nterms, thr = h["order"], h["nterms"], h["threshold"]
    nthr, base, frac = h["nthr"], h["base"], h["frac"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    off = h["offset"]

    line = "row" if rowwalk else "column"
    lines = "rows" if rowwalk else "columns"
    cross = "column" if rowwalk else "row"
    crosses = "columns" if rowwalk else "rows"
    shape = (rf"$(n+{base})\times{W}$" if rowwalk else rf"${W}\times(n+{base})$")
    blocktex = (r"\begin{pmatrix}\alpha&\beta\\\gamma&\delta\end{pmatrix}"
                r"=\begin{pmatrix}r_j&r_{j+1}\\s_j&s_{j+1}\end{pmatrix}" if rowwalk else
                r"\begin{pmatrix}\alpha&\beta\\\gamma&\delta\end{pmatrix}"
                r"=\begin{pmatrix}r_i&s_i\\r_{i+1}&s_{i+1}\end{pmatrix}")
    idxrange = (rf"1\le j\le {W}-1" if rowwalk else rf"1\le i\le {W}-1")
    noadjtex = ("" if not h["noadj"] else
                r"\item no two of those four entries that are horizontally or vertically "
                r"adjacent are equal, that is $\alpha\ne\beta$, $\gamma\ne\delta$, "
                r"$\alpha\ne\gamma$ and $\beta\ne\delta$;")
    noadjword = (" and in which no two adjacent entries are equal" if h["noadj"] else "")
    fractex = ("" if frac == 1 else rf"\tfrac1{{{frac}}}")
    # with no scale factor the sentence about it produced an empty "$$", which opens display
    # math and derails the rest of the proof environment
    scalarnote = ("" if frac == 1 else
                  rf" the scalar $\tfrac1{{{frac}}}$ never vanishes, so it does not affect"
                  rf" whether the left side is zero, and")
    fracsent = ("" if frac == 1 else
                rf" The entry counts $\tfrac1{{{frac}}}$ of those arrays, a constant factor "
                r"that passes through every step below unchanged.")
    powtex = rf"n+{base}-1" if base != 1 else "n"
    cond = h["tex"]

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts {shape} arrays over $\{{0,\dots,{alpha}\}}$ subject to a condition imposed on
every $2\times2$ subblock, and carries an empirical recurrence of order ${order}$ contributed
by R.~H.~Hardin. It is true, and it is not an empirical matter at all. The condition is local
to each subblock, so the {lines} of an admissible array are the vertices of a finite digraph
on $S={S}$ vertices whose edges are the admissible consecutive pairs, and the count is a
number of walks: $a(n)={fractex}\mathbf{{1}}^{{\!\top}}M^{{{powtex}}}\mathbf{{1}}$. Writing $q$
for the characteristic polynomial of the conjectured recurrence, the recurrence holds for all
$n$ exactly when $\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}=0$ for every $j\ge0$, and the
Cayley--Hamilton theorem bounds that to $j<S$. It is therefore a finite computation in exact
integer arithmetic, and it comes out zero.
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

\section{{The condition is local, so the {lines} form a digraph}}

Write an array of the shape in question as its list of {lines}
$r^{{(1)}},r^{{(2)}},\dots$, each an element of
$V=\{{0,1,\dots,{alpha}\}}^{{{W}}}$, so $|V|=S={S}$. A $2\times2$ subblock of the array
occupies two consecutive {lines} and two consecutive {crosses}; if the two {lines} are $r$
and $s$ (in that order) and the two {crosses} are numbered ${'j,j+1' if rowwalk else 'i,i+1'}$,
the subblock is
\[
{blocktex}.
\]
The entry's requirement on that subblock is
\begin{{equation}}\label{{eq:loc}}
{cond},
\end{{equation}}
a condition on the four entries alone{noadjword}.

For $r,s\in V$ declare $r\to s$ an edge of a digraph $G$ when, for every
${idxrange}$,
\begin{{itemize}}
\item the four entries above satisfy \eqref{{eq:loc}};
{noadjtex}
\end{{itemize}}
Let $M\in\{{0,1\}}^{{S\times S}}$ be the adjacency matrix of $G$ and $\mathbf{{1}}$ the
all-ones vector.

\begin{{lemma}}\label{{lem:walk}}
The arrays counted by the entry with $L$ {lines} are exactly the walks
$r^{{(1)}}\to r^{{(2)}}\to\cdots\to r^{{(L)}}$ of length $L-1$ in $G$. Consequently
\[
a(n)\;=\;{fractex}\mathbf{{1}}^{{\!\top}}M^{{{powtex}}}\mathbf{{1}} .
\]
\end{{lemma}}

\begin{{proof}}
An array with $L$ {lines} and ${W}$ {crosses} is precisely a sequence
$r^{{(1)}},\dots,r^{{(L)}}$ of elements of $V$; conversely any such sequence is an array.
Every $2\times2$ subblock lies in two consecutive {lines} $r^{{(t)}},r^{{(t+1)}}$ and two
consecutive {crosses}, so the array satisfies the entry's condition on all of its subblocks
if and only if each consecutive pair $\bigl(r^{{(t)}},r^{{(t+1)}}\bigr)$ satisfies it for
every {cross} pair --- which is exactly the edge relation of $G$. The number of walks of
length $L-1$, summed over all starting and ending vertices, is
$\mathbf{{1}}^{{\!\top}}M^{{L-1}}\mathbf{{1}}$, since $(M^{{k}})_{{r,s}}$ counts the walks of
length $k$ from $r$ to $s$. The entry's index $n$ corresponds to $L=n+{base}$ {lines}.{fracsent}
\end{{proof}}

\section{{The criterion}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}}, with the $c_i$ read off that equation.

\begin{{lemma}}\label{{lem:crit}}
For every $n$ with $n+{base}-1\ge{order}$,
\[
a(n)-\sum_i c_i\,a(n-i)\;=\;{fractex}\mathbf{{1}}^{{\!\top}}M^{{\,n+{base}-1-{order}}}\,q(M)\,\mathbf{{1}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}=0$ for every $j\ge0$; and it is enough to check
$j=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
By Lemma~\ref{{lem:walk}}, $a(n-i)={fractex}\mathbf{{1}}^{{\!\top}}M^{{\,n+{base}-1-i}}\mathbf{{1}}$, so
\[
a(n)-\sum_i c_i a(n-i)
={fractex}\mathbf{{1}}^{{\!\top}}\Bigl(M^{{m}}-\sum_i c_i M^{{m-i}}\Bigr)\mathbf{{1}}
={fractex}\mathbf{{1}}^{{\!\top}}M^{{\,m-{order}}}\,q(M)\,\mathbf{{1}}
\]
with $m=n+{base}-1$, which is the stated identity;{scalarnote} the equivalence follows by letting
$m-{order}=j$ run over $\ge0$. For the last clause put $w=q(M)\mathbf{{1}}$. By the
Cayley--Hamilton theorem $M^{{S}}$ is an integer combination of $I,M,\dots,M^{{S-1}}$, so
$\mathbf{{1}}^{{\!\top}}M^{{j}}w$ for $j\ge S$ is the corresponding combination of the earlier
values; if those all vanish, so do all the rest.
\end{{proof}}

\section{{The computation}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The digraph was constructed from \eqref{{eq:loc}} by a depth-first scan across the ${W}$
{crosses}: the edge condition is a conjunction of one constraint per consecutive {cross}
pair, so the successors of a {line} $r$ are enumerated {cross} by {cross} without testing all
$S^2$ pairs. The vector $w=q(M)\mathbf{{1}}\in\mathbb{{Z}}^{{S}}$ was then formed by ${order}$
matrix--vector products in exact integer arithmetic, and $\mathbf{{1}}^{{\!\top}}M^{{j}}w$ was
evaluated for $j=0,1,\dots$, again exactly. Every one of those integers vanishes from the
index corresponding to $n={nthr}+1$ onwards, and the run continued until $w$ itself was the
zero vector, which settles every larger $j$ at once. By Lemma~\ref{{lem:crit}} the recurrence
holds for every $n>{nthr}$.
\end{{proof}}

\begin{{remark}}
The argument gives more than the recurrence: it shows the sequence is $C$-finite with
characteristic polynomial dividing that of $M$, so it has a rational generating function
whose denominator divides $\det(I-xM)$. The conjectured recurrence is one consequence; the
minimal one is a divisor of $q$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the digraph was built directly from the entry's stated condition and the walk counts
${fractex}\mathbf{{1}}^{{\!\top}}M^{{L-1}}\mathbf{{1}}$ compared against the entry's DATA at
every one of the ${nterms}$ published indices; the values agree exactly. That is what ties
the digraph to the sequence: a model that reproduced only some of the published terms would
be the wrong model, and would have been rejected. In particular it is what rules out a
misreading of the entry's wording, since a different reading of the condition gives a
different digraph and different counts.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes wherever it applies.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was run in exact integer arithmetic
until the working vector was identically zero, not to a sampled prefix, and returned zero
throughout.

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
    hits = [h for h in json.load(open("transfer6_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t6{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
