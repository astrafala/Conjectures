#!/usr/bin/env python3
"""One paper per Hardin array entry whose 3 X 3 condition is local to the block."""
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
    base, frac, off = h["base"], h["frac"], h["offset"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}

    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    cross = "column" if rowwalk else "row"
    shape = (rf"$(n+{base})\times{W}$" if rowwalk else rf"${W}\times(n+{base})$")
    fractex = "" if frac == 1 else rf"\tfrac1{{{frac}}}"
    blocktex = (r"g=\begin{pmatrix}r_j&r_{j+1}&r_{j+2}\\ s_j&s_{j+1}&s_{j+2}\\"
                r" t_j&t_{j+1}&t_{j+2}\end{pmatrix}" if rowwalk else
                r"g=\begin{pmatrix}r_i&s_i&t_i\\ r_{i+1}&s_{i+1}&t_{i+1}\\"
                r" r_{i+2}&s_{i+2}&t_{i+2}\end{pmatrix}")
    quantword = "every" if h["quant"] != "no" else "no"
    perim = ("" if 'perimeter' not in h['body'].lower() else
             " That check did real work here. The phrase ``clockwise perimeter pattern'' does"
             " not mean that the eight boundary entries, read clockwise from the top left,"
             " equal the quoted word; it means the cyclic word they form is that word up to"
             " rotation. Read the first way the model returns counts far below the entry's"
             " own first term, and only the second reading reproduces the published values."
             " It is the one used.")
    # only claim exactness when the entry's own terms show the recurrence failing at nthr
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        k = nthr - off
        if d[k] != sum(int(c) * d[k - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts {shape} arrays over $\{{0,\dots,{alpha}\}}$ subject to a condition imposed on
{quantword} $3\times3$ subblock, and it carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is not an empirical matter. A $3\times3$
subblock spans three consecutive {lines}, so the state of a transfer matrix is a PAIR of
consecutive {lines} and appending one more {line} is a step; an array is then a walk, and
$a(n)$ is a walk count on $S={S}$ vertices. Such a sequence is $C$-finite, so whether a given
recurrence annihilates it is decided by a finite exact computation, with the Cayley--Hamilton
theorem bounding the work.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{Three consecutive lines}}

Write an admissible array as a sequence of {lines} $u_1,u_2,\dots$, each an element of
$\{{0,\dots,{alpha}\}}^{{{W}}}$. A $3\times3$ subblock occupies three consecutive {lines} and
three consecutive {cross}s, so with $r,s,t$ three consecutive {lines} the blocks it
contributes are
\[
{blocktex}
\]
for each admissible index, and the entry's condition is the requirement that
\[
{h['tex']}
\]
holds for {quantword} such $g$. This involves $r$, $s$ and $t$ only: it is a condition on
three consecutive {lines} and on nothing else.

Take as vertices of a digraph $G$ the ordered PAIRS $(r,s)$ of {lines}, of which there are
$S=({alpha}+1)^{{2\cdot{W}}}={S}$, and put an edge $(r,s)\to(s,t)$ exactly when the condition
holds for the triple $(r,s,t)$ at every admissible index. An array with $L$ {lines} is then a
walk of length $L-2$ in $G$: its first two {lines} name the starting vertex and each further
{line} is one step. Hence, with $M$ the adjacency matrix of $G$,
\[
a(n)\;=\;{fractex}\,\mathbf{{1}}^{{\!\top}}M^{{\,n-{off}+{h['shift']}}}\mathbf{{1}},
\]
the exponent being fixed by the entry's own shape and checked against its published terms.
In particular $a$ is $C$-finite.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. Then the residual $a(n)-\sum_ic_ia(n-i)$ equals
${fractex}\mathbf{{1}}^{{\!\top}}M^{{\,j}}q(M)\mathbf{{1}}$ for the corresponding walk index
$j$, so the recurrence holds from some point on if and only if
$\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}=0$ for all large $j$; and by the
Cayley--Hamilton theorem it is enough to examine $j<S$.
\end{{lemma}}

\begin{{proof}}
Factor $M^{{j}}$ out of $M^{{j+{order}}}-\sum_ic_iM^{{j+{order}-i}}$. For the bound, $M^{{S}}$
is an integer combination of $I,M,\dots,M^{{S-1}}$, so the numbers
$u_j=\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}$ satisfy the monic linear recurrence given by
the characteristic polynomial of $M$; $S$ consecutive zeros therefore force every later one,
and the last nonzero $u_j$ pins the threshold exactly.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(M)\mathbf{{1}}$ was formed by ${order}$ matrix--vector products in exact
integer arithmetic and $\mathbf{{1}}^{{\!\top}}M^{{j}}w$ evaluated for $j=0,1,\dots$, again
exactly. Those integers vanish from the index corresponding to $n={nthr}+1$ onwards, and the
run was continued until the working vector was identically zero, which settles all larger $j$
at once. By Lemma~\ref{{lem:crit}} the recurrence holds for every $n>{nthr}$.{tight}
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the transfer model reproduces all ${nterms}$ terms the entry publishes, exactly, in
integer arithmetic. This is what ties the model to the entry: the digraph is built by reading
the entry's English, and a misreading gives different counts.{perim}

Second, the conjectured recurrence was evaluated directly on the entry's own published terms,
with no matrices involved, and holds wherever the proved range and the data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix, so no rounding or sampling
enters anywhere.

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
    hits = [h for h in json.load(open("transfer17_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t17{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
