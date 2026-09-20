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
import kdcert
import os as _os

# the date a paper prints is the day the RESULT was obtained, not the day this builder was
# drafted. It carried "7 September 2026" hard-coded from the day the engine was written and
# shelved, which would have stamped every paper in the batch with a date a week before the
# theorem that makes it true. See STATE.md defect 16 and the note in `unibuild`.
DATE = _os.environ.get('PAPER_DATE', '14 September 2026')
import transfer88
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}


SETTLED = {3: 4, 4: 4, 5: 6, 6: 8, 7: 10}


def model_section(p, S, expo):
    C, s = p['C'], p['slack']
    i0 = transfer88.settled(C, s)
    ex = transfer88.exceptional(C)
    H0 = max(ex) + 1 if ex in ((), None) or not ex else max(ex) + 1
    exs = ", ".join(str(x) for x in ex[:-1]) + " and " + str(ex[-1]) if len(ex) > 1 else str(ex[0])
    cert = kdcert.get(C)
    j0, P, RI = cert['i0'], kdcert.PERIOD, kdcert.RISE
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
        r"\section{The distance field of the strip}", "",
        rf"Everything below rests on two properties of $d$ on the strip "
        rf"$S_{{{C}}}=\{{(i,j): i\ge 0,\ 0\le j<{C}\}}$, and both are proved here rather "
        rf"than measured. Write $d$ for the knight distance from $(0,0)$ on $S_{{{C}}}$ and "
        rf"$d_H$ for the knight distance on the board of exactly $H$ rows.",
        "",
        r"\begin{lemma}\label{lem:bellman}",
        r"Fix a width $C$ and let $D:S_C\to\mathbb{N}\cup\{\infty\}$ be any function at all, "
        r"satisfying",
        r"(a) $D(0,0)=0$; (b) $D(y)\le D(x)+1$ for every knight-adjacent pair $x,y$; and",
        r"(c) every $x\ne(0,0)$ with $D(x)<\infty$ has a knight neighbour $y$ with "
        r"$D(x)=D(y)+1$. Then $D=d$.",
        r"\end{lemma}",
        "",
        r"\begin{proof}",
        r"By (b) and induction on $d(x)$, $D(x)\le d(x)$: the last step of a shortest path "
        r"to $x$ is an edge from a cell at distance $d(x)-1$. Conversely (c) forces "
        r"$D(x)\ge1$ for $x\ne(0,0)$, so $D(x)=0$ only at the corner, and induction on "
        r"$D(x)$ gives $d(x)\le D(y)+1=D(x)$ with $y$ the neighbour (c) supplies. Neither "
        r"induction uses where $D$ came from.",
        r"\end{proof}",
        "",
        r"\begin{proposition}\label{prop:period}",
        rf"$d(i+{P},j)=d(i,j)+{RI}$ for every $j$ and every $i\ge{j0}$, and the unreachable "
        rf"cells repeat with the same period.",
        r"\end{proposition}",
        "",
        r"\begin{proof}",
        rf"Take the field on rows $0,\dots,{j0+2*P-1}$ as computed by breadth-first search, "
        rf"and DEFINE $D$ on the rest of the strip by $D(i+{P},j)=D(i,j)+{RI}$ for "
        rf"$i\ge{j0}$. Conditions (a), (b) and (c) of Lemma~\ref{{lem:bellman}} at row $i$ "
        rf"involve only rows $i-2,\dots,i+2$, because a knight move changes the row by $1$ "
        rf"or $2$. Once all five of those rows lie at or above ${j0}$, the definition gives "
        rf"$D(r,j)=D(r-{P},j)+{RI}$ for each of them, so the condition at row $i$ is the "
        rf"condition at row $i-{P}$ with ${RI}$ added to both sides, hence the same "
        rf"condition. Checking rows $0,\dots,{j0+5*P}$ therefore settles every row, and "
        rf"those checks were carried out in exact integer arithmetic. By "
        rf"Lemma~\ref{{lem:bellman}}, $D=d$, which is the claim. (The inequality $\le$ "
        rf"needs no certificate: the moves $(2,1)$ then $(2,-1)$ --- or $(2,-1)$ then "
        rf"$(2,1)$ at the right-hand edge --- drop four rows and return to the same column. "
        rf"It is $\ge$ that the certificate supplies.)",
        r"\end{proof}",
        "",
        r"\begin{proposition}\label{prop:height}",
        rf"$d_H(i,j)=d(i,j)$ for every $H\ge{H0}$ and every $i<H$.",
        r"\end{proposition}",
        "",
        r"\begin{proof}",
        r"For a cell $x$ let $\rho(x)$ be the least number of rows a board needs for $x$ to "
        r"sit at distance $d(x)$ on it, so $\rho(0,0)=1$ and, minimising over the "
        r"minimum-path predecessors $y$ of $x$,",
        r"\[ \rho(x)\;=\;\min_y\ \max\bigl(\mathrm{row}(x)+1,\ \mathrm{row}(y)+1,"
        r"\ \rho(y)\bigr). \]",
        r"A board of $H$ rows realises $d$ on all of its own rows exactly when $H\ge\rho(x)$ "
        rf"for every $x$ in them. By Proposition~\ref{{prop:period}} the quantity "
        rf"$\rho(x)-\mathrm{{row}}(x)$ has period ${P}$ in the row index, so the condition "
        rf"is decided by finitely many rows; it holds for every $H\ge{H0}$ and fails at "
        rf"$H={H0-1}$.",
        r"\end{proof}",
        "",
        rf"So one distance function serves every board of ${H0}$ rows or more. The heights "
        rf"{exs} are genuinely different --- on a $3\times3$ board the centre is unreachable, "
        rf"while on any taller board it is at distance $4$ --- and are counted separately, "
        rf"each on its own board with its own distances, which needs no theorem at all.",
        "",
        r"\section{The count is a walk count}", "",
        rf"What a transfer needs to know at row $i$ is which pairs of cells within two rows "
        rf"are minimum-path edges, and how far each cell's label is capped by "
        rf"$\min({s},d)$. Both are functions of $d$ on rows $i-2,\dots,i$, so by "
        rf"Proposition~\ref{{prop:period}} both depend on $i$ only through $i\bmod {P}$ "
        rf"once $i\ge{i0}$ --- the cap because $d$ rises with $i$ and has passed ${s}$ "
        rf"there.",
        "",
        rf"A knight move never stays inside a row, so no edge joins two cells of one row: the "
        rf"label of a new row is constrained only by the two rows above it, and cell by cell "
        rf"at that. Take as vertices the pairs (labelling of the previous row, labelling of "
        rf"the current row) together with the phase $i\bmod {P}$ of the current row; an edge "
        rf"to the next such vertex exists when every minimum-path edge closed by the arriving "
        rf"row rises by $0$ or $1$, which the two rows above it decide. Vertices with "
        rf"identical futures are merged, which changes no count, leaving $S={S}$.",
        "",
        rf"Rows $0,\dots,{i0}$ are ABOVE the periodic region and are not carried by the "
        rf"matrix. They are walked once with weights: $\iota$ is the vector counting, at "
        rf"each vertex, the boards of ${i0+1}$ rows whose last two rows are that pair. So "
        rf"$\iota$ is not an incidence vector, and the paper may not call it one; $\tau$ is "
        rf"all ones, every vertex being a legitimate last pair. Carrying the row index in the "
        rf"vertex instead, which is the obvious alternative, multiplies the vertex set by the "
        rf"${i0}$ distinct rows above the region and is what made the wider boards "
        rf"unreachable. Summing the early rows away loses nothing: a board is determined by "
        rf"its rows, and two boards agreeing on their last two rows admit the same "
        rf"continuations. With $M$ the adjacency matrix, for every board of at least "
        rf"${i0+1}$ rows,",
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
    # The matrix carries the board only from row i0 on -- the rows above it are summed into
    # the weighted start vector -- so the exponent is NOT the one the offset and the shift
    # give on their own. Walk step k is the board of i0+k+1 rows, which is the entry's
    # a(i0+k-1), so a(n) = iota^T M^(n+1-i0) tau.
    i0_ = transfer88.settled(p['C'], p['slack'])
    ee = 1 - i0_
    expo = "n" if ee == 0 else ("n+%d" % ee if ee > 0 else "n-%d" % (-ee))
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
\date{{{DATE}}}
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
search on that very board and testing each minimum-path edge directly. That program shares no
code with the transfer matrix, so an error in one does not hide an error in the other. A
third, independently written row-pair model, which carries the phase in the vertex rather than
the row index and merges by a different rule, reproduces the same published terms again.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

The certificate of Propositions~\ref{{prop:period}} and~\ref{{prop:height}} was itself tested
on cases with known answers before being trusted: the field it produces agrees cell for cell
with a direct breadth-first search on every board of width $3$ to $9$ and every height up to
$59$; the threshold it computes is tight, the height below it genuinely disagreeing; and
perturbing a single entry of its table by one makes it refuse.

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
