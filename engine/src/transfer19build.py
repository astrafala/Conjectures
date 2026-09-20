#!/usr/bin/env python3
"""One paper per Hardin entry whose condition is imposed on every cell over a named
neighbour set."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild

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
    W, alpha, S, E = h["fixed"], h["alpha"], h["S"], h["exc"]
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, frac, off = h["base"], h["frac"], h["offset"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}

    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    # The pair vertex set is enormously redundant, and the model actually used removes the
    # redundancy before the states exist. A paper must describe the digraph its numbers came
    # from, so the identification is stated here whenever it was applied.
    pairs = (alpha + 1) ** (2 * W) * (E + 1)
    merge = "" if S == pairs else (
        r" Most of those pairs are indistinguishable, and exactly so. Every offset named "
        r"above has $|dj|\le 1$, so whether the cell at column $j$ of the middle {line} is "
        r"satisfied depends on the three {lines} only through their windows at $j-1,j,j+1$. "
        r"Collect for each $j$ the indicator over the window of the {line} below, and call "
        r"that tuple $P(r,s)$: the number of cells any $t$ violates is read off $P$, so is "
        r"the number violated at the bottom edge, and the successor $(s,t)$ carries $P(s,t)$, "
        r"which does not mention $r$. Hence two pairs $(r,s)$ and $(r',s)$ with the same $P$ "
        r"have the same outgoing {lines} and the same successors, and the vertex is "
        r"$(s,P{excstate2})$. That leaves $S={S}$ vertices in place of ${pairs}$."
    ).format(line=line, lines=lines, S=S, pairs=pairs,
             excstate2=("" if not E else r",c"))

    shape = (rf"$(n+{base})\times{W}$" if base else rf"$n\times{W}$") if rowwalk else \
            (rf"${W}\times(n+{base})$" if base else rf"${W}\times n$")
    fractex = "" if frac == 1 else rf"\tfrac1{{{frac}}}"
    exctex = ("" if not E else
              rf""" The clause ``with the exception of exactly ${E}$ {'element' if E == 1 else 'elements'}'' is carried in
the state as a counter of violations so far, capped at ${E}$; a step that would push it past
${E}$ has no edge, and a walk is accepted only when the count reaches exactly ${E}$.""")
    excstate = ("" if not E else rf" \times \{{0,\dots,{E}\}}")
    # a stored offset comes back from JSON as a list, not a tuple
    olist = [tuple(o) for o in
             (h.get("offs") or __import__("transfer19").parse_name(h["name"])["offs"])]
    nnb = len(olist)
    offs = ", ".join("(%d,%d)" % o for o in olist)
    k = off - h["shift"]
    expo = "n" if k == 0 else ("n-%d" % k if k > 0 else "n+%d" % (-k))
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
every CELL over a neighbour set the entry names, and it carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical. A cell's neighbourhood meets three consecutive {lines}, so the state of a transfer
matrix is a pair of consecutive {lines} and each step settles the middle one; an array is a
walk, and $a(n)$ is a walk count on $S={S}$ vertices, which is $C$-finite. Whether the
conjectured recurrence annihilates it is then decided by a finite exact computation, with the
Cayley--Hamilton theorem bounding the work.
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

\section{{Cells, not blocks}}

The entry names the neighbours it means --- horizontal is left and right, vertical is up and
down, diagonal is northwest-to-southeast, antidiagonal is northeast-to-southwest, king-move is
all eight --- and every such set lies inside the $3\times3$ square centred on the cell. Here
the set is $\{{{offs}\}}$, written as offsets (row, column) from the cell. Every cell carries
the condition
\[
{h['tex']},
\]
and the count of neighbours enters it, so the boundary is not a detail that can be papered
over: a cell in the interior has ${nnb}$ neighbours in this set and a cell on the boundary
fewer, and a condition such as ``a strict majority of its neighbours'' therefore means
different things at the two. In particular one cannot pad the array with a border of zeros ---
that would give every cell the full ${nnb}$ and change what is being counted. The outside is
therefore carried
explicitly, as a sentinel {line} above the first and below the last and as a sentinel column
either side, and a neighbour that falls outside is simply absent from both counts.

Write an array as a sequence of {lines} $u_1,\dots,u_L$, each in
$\{{0,\dots,{alpha}\}}^{{{W}}}$. The neighbourhood of a cell in {line} $u_i$ meets $u_{{i-1}}$,
$u_i$ and $u_{{i+1}}$ and nothing else. Take as vertices the pairs
$(r,s)\in(\{{0,\dots,{alpha}\}}^{{{W}}}\cup\{{\varnothing\}})\times\{{0,\dots,{alpha}\}}^{{{W}}}{excstate}$,
and put an edge $(r,s)\to(s,t)$ when {line} $s$ satisfies the condition at every one of its
${W}$ cells, given $r$ above and $t$ below. An array with $L$ {lines} is then a walk of length
$L-1$ starting at $(\varnothing,u_1)$, each step settling one {line}, and the last {line} is
settled by the terminal weight, which evaluates it with $\varnothing$ below.{exctex}{merge} Hence,
with $M$ the adjacency matrix on $S={S}$ vertices, $\iota$ the starting vector and $\tau$ the
terminal weight,
\[
a(n)\;=\;{fractex}\,\iota^{{\!\top}}M^{{\,{expo}}}\tau ,
\]
the exponent fixed by the entry's own shape and checked against its published terms. In
particular $a$ is $C$-finite.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. Then the residual $a(n)-\sum_ic_ia(n-i)$ equals
${fractex}\iota^{{\!\top}}M^{{\,j}}q(M)\tau$ for the corresponding walk index $j$, so the
recurrence holds from some point on if and only if $\iota^{{\!\top}}M^{{j}}q(M)\tau=0$ for all
large $j$; and it is enough to examine $j<S$.
\end{{lemma}}

\begin{{proof}}
Factor $M^{{j}}$ out of $M^{{j+{order}}}-\sum_ic_iM^{{j+{order}-i}}$. For the bound, $M^{{S}}$
is an integer combination of $I,M,\dots,M^{{S-1}}$ by Cayley--Hamilton, so the numbers
$u_j=\iota^{{\!\top}}M^{{j}}q(M)\tau$ satisfy the monic linear recurrence given by the
characteristic polynomial of $M$; $S$ consecutive zeros force every later one, and the last
nonzero $u_j$ pins the threshold exactly.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(M)\tau$ was formed by ${order}$ matrix--vector products in exact integer
arithmetic and $\iota^{{\!\top}}M^{{j}}w$ evaluated for $j=0,1,\dots$, again exactly. Those
integers vanish from the index corresponding to $n={nthr}+1$ onwards, and the run was
continued until the working vector was identically zero, which settles all larger $j$ at once.
By Lemma~\ref{{lem:crit}} the recurrence holds for every $n>{nthr}$.{tight}
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the transfer model reproduces all ${nterms}$ terms the entry publishes, exactly, in
integer arithmetic. That check earned its place here. The neighbour offsets are named in the
array's own frame --- horizontal means along a row --- but when the entry fixes the first
dimension, as in ``$2\times n$'', the walk runs along columns and the two components of every
offset swap. Sets such as king-move, or horizontal together with vertical, are unchanged by
that swap and hide the error completely; a set such as horizontal, diagonal and antidiagonal
is not, and the counts came out as those of a different member of the same family until the
offsets were transposed.

Second, the conjectured recurrence was evaluated directly on the entry's own published terms,
with no matrices involved, and holds wherever the proved range and the data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

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
    hits = [h for h in json.load(open("transfer19_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t19{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
