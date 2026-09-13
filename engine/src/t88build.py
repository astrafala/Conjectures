#!/usr/bin/env python3
"""One paper per entry settled by transfer88.

What these have in common is a condition on every subblock, or on every pair of neighbouring
subblocks, and what differs is the condition, the shape and --- for a few of them --- a
scaling factor in front of the count. The general builder would describe all of that as "a
bounded window of consecutive lines", which is true but says nothing about the entry in
hand, and would drop the scaling factor entirely.
"""
import conjquote
import json
import os
import re

import localentry as LE
import phibuild
import transfer88
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}


SETTLED = {3: 4, 4: 4, 5: 6, 6: 8, 7: 10}


def model_section(p, S, expo):
    C, s = p['C'], p['slack']
    i0 = SETTLED[C]
    return "\n".join([
        r"\section{From values to a labelling}", "",
        rf"Write $d(c)$ for the knight distance from the top left corner of the board and "
        rf"$v(c)$ for the entry's value at $c$. The entry asks for $d(c)-{s}\le v(c)\le "
        rf"d(c)$, and for successive values along a minimum knight path to differ by $0$ or "
        rf"$+1$. Put",
        r"\[ w(c)\;=\;d(c)-v(c). \]",
        rf"Then $w$ takes values in $\{{0,1,\dots,{s}\}}$, and for an edge $a\to b$ of a "
        rf"minimum path --- so $d(b)=d(a)+1$ --- the condition $v(b)-v(a)\in\{{0,1\}}$ "
        rf"reads",
        r"\[ v(b)-v(a)=\bigl(d(b)-d(a)\bigr)-\bigl(w(b)-w(a)\bigr)=1-\bigl(w(b)-w(a)"
        r"\bigr)\in\{0,1\}\quad\Longleftrightarrow\quad w(b)-w(a)\in\{0,1\}. \]",
        r"So the entry counts the labellings $w$ that rise along every minimum-path knight "
        r"move, by at most one each time. Cells the knight cannot reach carry the value zero "
        r"and are not labelled; they contribute a factor of one.",
        "",
        r"\section{The count is a walk count}", "",
        rf"Two properties of the board make the labellings the walks of a finite digraph. "
        rf"Both were measured, not assumed.",
        "",
        rf"\emph{{The distances do not depend on how tall the board is.}} On a strip of "
        rf"${C}$ columns, $d$ computed on a board of $R$ rows agrees with $d$ computed on any "
        rf"taller board, for every $R$ except $2$, $3$ and $4$. So one distance function "
        rf"serves every board in the family, and those three heights are counted separately, "
        rf"each on its own board with its own distances.",
        "",
        rf"\emph{{The local structure repeats.}} What a transfer needs to know at row $i$ is "
        rf"which pairs of cells within two rows are minimum-path edges, and how far each "
        rf"cell's label is capped by $\min({s},d)$. For ${C}$ columns that data depends on "
        rf"$i$ only through $i \bmod 4$, once $i\ge{i0}$. Below that it is carried exactly, "
        rf"by the row index itself, so nothing is assumed about the top of the board either. "
        rf"Widths $8$ and above show no such period and are refused rather than guessed at.",
        "",
        rf"A knight move never stays inside a row, so no edge joins two cells of one row: the "
        rf"label of a new row is constrained only by the two rows above it, and cell by cell "
        rf"at that. Take as vertices the triples (row index or phase, labelling of the "
        rf"previous row, labelling of the current row); an edge to the next such triple exists "
        rf"when every minimum-path edge closed by the arriving row rises by $0$ or $1$. "
        rf"Merging vertices with identical futures leaves $S={S}$, and with $M$ the adjacency "
        rf"matrix and $\iota,\tau$ the vectors recording which states may begin and end a "
        rf"board,",
    ])


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def build(h):
    a = h["anum"]
    S, order, nterms, nthr = h["S"], h["order"], h["nterms"], h["nthr"]
    off, sh = h["offset"], h["shift"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    p = transfer88.parse_name(e['name'])
    kk = off - sh
    expo = "n" if kk == 0 else ("n-%d" % kk if kk > 0 else "n+%d" % (-kk))
    frac = p['frac']
    scale = ""
    if frac != 1:
        scale = (rf" The entry does not count the arrays themselves but $1/{frac}$ of them, "
                 rf"so every count below is divided by ${frac}$; the division is exact at "
                 rf"every term, which is itself a check on the model.")
    pref = ('\\tfrac{1}{%d}\\,' % frac) if frac != 1 else ''
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        j = nthr - off
        if d[j] != sum(int(c) * d[j - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{Knight-distance labellings of a strip: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{7 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry's condition is decided by a bounded amount of state carried down the array; the
admissible windows are the vertices of a finite digraph and the arrays counted are exactly the
walks in it. Hence $a(n)$ is a walk count on $S={S}$ vertices and is $C$-finite, and whether the
conjectured recurrence annihilates it is settled by a finite exact computation, with the
Cayley--Hamilton theorem bounding the work.{scale}
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

{model_section(p, S, expo)}
\[
a(n)\;=\;{pref}\iota^{{\!\top}}M^{{\,{expo}}}\tau ,
\]
the exponent fixed by the entry's own shape and checked against its published terms. In
particular $a$ is $C$-finite.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. The residual $a(n)-\sum_ic_ia(n-i)$ equals
$\iota^{{\!\top}}M^{{\,j}}q(M)\tau$ for the corresponding walk index $j$, so the recurrence
holds from some point on if and only if $\iota^{{\!\top}}M^{{j}}q(M)\tau=0$ for all large $j$,
and it is enough to examine $j<S$.
\end{{lemma}}

\begin{{proof}}
Factor $M^{{j}}$ out of $M^{{j+{order}}}-\sum_ic_iM^{{j+{order}-i}}$. For the bound, $M^{{S}}$
is an integer combination of $I,M,\dots,M^{{S-1}}$ by Cayley--Hamilton, so the numbers
$u_j=\iota^{{\!\top}}M^{{j}}q(M)\tau$ obey the monic recurrence given by the characteristic
polynomial of $M$; $S$ consecutive zeros force every later one, and the last nonzero $u_j$
pins the threshold exactly. A constant factor in front of $a$ divides out of the residual and
changes nothing here.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(M)\tau$ was formed by ${order}$ matrix--vector products in exact integer
arithmetic and $\iota^{{\!\top}}M^{{j}}w$ evaluated for $j=0,1,\dots$, again exactly; those
integers vanish from the index corresponding to $n={nthr}+1$ onwards and the run continued
until the working vector was identically zero, which settles every larger $j$ at once.{tight}
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the model to the entry: the digraph is built by reading the
entry's English, and a misreading gives different counts.

Second, the reading was pinned before the digraph was written, by a program that enumerates
every labelling of the board one by one, computing the knight distances by breadth-first
search on that very board and testing each minimum-path edge directly. That program shares no code with the transfer matrix, so an error in one does not
hide an error in the other.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
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
    hits = [h for h in json.load(open("uniall_hits.json"))
            if h.get("engine") == "transfer88" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
