#!/usr/bin/env python3
"""One paper per entry settled by transfer81.

The general transfer-matrix paper says the entry's condition is local to a window of
consecutive lines. For this family that is only half true, and the half it leaves out is the
interesting one: "new values introduced in row major order" is not a condition on any window
at all --- whether a value may appear here depends on the whole prefix of the array. So these
papers say what the state really is, and why a single counter is enough to carry a condition
that is not local. Writing them through the general builder would have produced a paper whose
section 2 was wrong about its own model.
"""
import conjquote
import json
import os
import re

import localentry as LE
import phibuild
import transfer81
import transferbuild
import uniform

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

COND = {
    'neighbour': (
        "every $2\\times2$ subblock scores the number of its equal diagonal pairs plus the "
        "number of its equal antidiagonal pairs --- a number in $\\{0,1,2\\}$ --- and no "
        "subblock may score what the subblock beside it or the subblock above it scores",
        "the scores of the whole last band, one number per subblock, since the band arriving "
        "next is compared with it subblock by subblock"),
    'band': (
        "every $2\\times2$ subblock scores the number of its equal diagonal pairs plus the "
        "number of its equal antidiagonal pairs, all subblocks lying in one band must score "
        "the same, and consecutive bands must score differently",
        "the single number the last band scored, since a band is constant and only that one "
        "number is compared with the next"),
    'same': (
        "every $2\\times2$ subblock scores the number of its equal diagonal pairs plus the "
        "number of its equal antidiagonal pairs, and every subblock in the array must score "
        "the same",
        "the score fixed by the first band, since every later subblock is compared with it"),
    'lines_exact': (
        "every $3\\times3$ subblock must contain three equal elements in a line --- along one "
        "of its three rows, one of its three columns, or one of its two diagonals --- in "
        "exactly %s of those eight ways",
        None),
    'lines_atleast': (
        "every $3\\times3$ subblock must contain three equal elements in a line --- along one "
        "of its three rows, one of its three columns, or one of its two diagonals --- in at "
        "least %s of those eight ways",
        None),
}
WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five'}


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def model_section(p, S):
    """Section 2, written to the entry actually in hand rather than to the family."""
    W, k, h, kind = p['W'], p['k'], p['h'], p['kind']
    cond, carry = COND[kind]
    if kind.startswith('lines'):
        cond = cond % WORD.get(p['want'], str(p['want']))
    band = W - p['w'] + 1
    rows = k ** W
    alpha = (r'\{' + ','.join(str(i) for i in range(k)) + r'\}' if k <= 4
             else rf'\{{0,1,\dots,{k-1}\}}')
    L = [r"\section{The count is a walk count}", "",
         rf"The entry counts arrays of {W} columns over the alphabet ${alpha}$, "
         rf"and asks two different kinds of thing of them at once."]
    L += ["", rf"\textbf{{The subblock condition is local.}} It says that {cond}. A "
              rf"$ {h}\times{p['w']}$ subblock spans ${h}$ consecutive rows, so a window of "
              rf"${h}$ consecutive rows decides every subblock it closes, and nothing outside "
              rf"that window is consulted."]
    if carry:
        L += ["", rf"What is compared \emph{{across}} windows is carried too: the state holds "
                  rf"{carry}. With ${band}$ subblock{'s' if band != 1 else ''} to a band that "
                  rf"is a bounded amount of bookkeeping and no more."]
    L += ["", r"\textbf{The relabelling condition is not local.} ``New values introduced in "
              r"row major order'' says that, reading the array one row at a time and each row "
              r"left to right, a value may appear for the first time only once every smaller "
              r"value already has. Whether a given entry is allowed here therefore depends on "
              r"the whole prefix of the array, not on any bounded window of it, and no amount "
              r"of widening the window captures it. What saves it is that the prefix matters "
              r"only through one number: let $m$ be how many values have been introduced so "
              r"far. A row $r_1r_2\cdots r_" + str(W) + r"$ may follow precisely when each "
              r"$r_i\le m$ at the moment it is read and each $r_i=m$ raises $m$ by one. So "
              r"$m$, an integer in $\{0,1,\dots," + str(k) + r"\}$, is an exact summary of "
              r"everything the condition needs, and it joins the state.",
          "",
          rf"The vertices of the digraph are therefore the triples (the last ${h-1}$ "
          rf"row{'s' if h - 1 != 1 else ''}, the count $m$, what the last band scored), an "
          rf"edge $u\to v$ meaning that $v$'s new row may follow $u$. Of the ${rows}$ possible "
          rf"rows only those admissible from the current $m$ appear, and states with identical "
          rf"futures are merged, which leaves $S={S}$. An admissible array is exactly a walk, "
          rf"so with $M$ the adjacency matrix and $\iota,\tau$ the vectors recording which "
          rf"states may begin and end an array,"]
    return "\n".join(L)


def build(h):
    a = h["anum"]
    S, order, nterms, nthr = h["S"], h["order"], h["nterms"], h["nthr"]
    off, sh = h["offset"], h["shift"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    p = transfer81.parse_name(e['name'])
    k = off - sh
    expo = "n" if k == 0 else ("n-%d" % k if k > 0 else "n+%d" % (-k))
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    counted = ("Because of the relabelling condition each array is counted once for the whole "
               "class of arrays that differ from it only by renaming the values, so these are "
               "colourings counted up to permutation of the colours.")
    return rf"""{PRE}
\title{{Arrays counted up to renaming: the empirical recurrence for OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry imposes two conditions of different
kinds: a condition on every subblock, which is local, and ``new values introduced in row major
order'', which is not --- it makes the count a count of colourings up to renaming. The first is
handled by a window of consecutive rows; the second by one extra integer, the number of values
introduced so far, which is an exact summary of everything the whole prefix contributes. With
both in the state the arrays are exactly the walks in a digraph on $S={S}$ vertices, so $a(n)$
is $C$-finite and whether the conjectured recurrence annihilates it is settled by a finite
exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
{counted}
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

{model_section(p, S)}
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,{expo}}}\tau ,
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
pins the threshold exactly.
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
the arrays one by one from the entry's own words --- generating every array over the
alphabet, discarding those that fail the relabelling condition, then testing each subblock
directly --- and compares the count with the published terms. That program shares no code
with the transfer matrix, so an error in one does not hide an error in the other.

Third, the conjectured recurrence was evaluated directly on those published terms, with no
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
            if h.get("engine") == "transfer81" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
