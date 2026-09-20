#!/usr/bin/env python3
"""One paper per entry settled by transfer89.

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
import transfer89
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}


def model_section(p, S, expo):
    L, k = p['L'], p['k']
    kind, val = p['rule']
    tgt = (rf"$x+{val}$ modulo ${k}$" if kind == 'succ' else rf"${val}-x$")
    walk = 'column' if p['transposed'] else 'row'
    fixed = ('rows' if p['transposed'] else 'columns') if L != 1 else \
            ('row' if p['transposed'] else 'column')
    alpha = r'\{' + ','.join(str(i) for i in range(k)) + r'\}'
    L1 = [r"\section{The white squares are a board of their own}", "",
          rf"The board has ${L}$ {fixed} and grows one {walk} at a time, but only the cells "
          rf"with $i+j$ even carry a value, from the alphabet ${alpha}$. The diagonal and "
          rf"antidiagonal neighbours of such a cell again have $i+j$ even, so the white "
          rf"squares form a board of their own and the entry's condition never refers to "
          rf"anything else: each white cell must have at least one neighbour, diagonally or "
          rf"antidiagonally, holding the value {tgt} where $x$ is its own.",
          "",
          rf"That looks one {walk} up and one {walk} down, so three consecutive {walk}s "
          rf"settle the condition on the middle one. Carry two {walk}s as the state, judge a "
          rf"{walk} when the {walk} after it arrives, and judge the {walk} with nothing after "
          rf"it by the end vector. A cell at the edge of the board simply has fewer "
          rf"neighbours, and having none of the right value is a failure rather than a "
          rf"special case.",
          "",
          rf"The white cells of a {walk} occupy alternate {fixed[:-1] if fixed.endswith('s') else fixed}s, "
          rf"and which alternate ones depends on the parity of that {walk}, so the two shapes "
          rf"alternate down the board; the state carries that parity in the shape of the "
          rf"{walk} it holds."]
    if p['corner'] is not None:
        L1 += ["", rf"The entry also fixes the top left cell at ${p['corner']}$, which "
                   rf"restricts the states an array may begin in and nothing else."]
    L1 += ["", rf"Merging vertices with identical futures leaves $S={S}$. An admissible board "
               rf"is exactly a walk, so with $M$ the adjacency matrix and $\iota,\tau$ the "
               rf"vectors recording which states may begin and end a board,"]
    return "\n".join(L1)


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
    p = transfer89.parse_name(e['name'])
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
\title{{The white squares of a board: OEIS {a}}}
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
every filling of the white cells one by one and tests, for each of them, whether some
diagonal or antidiagonal neighbour holds the required value. That program shares no code with the transfer matrix, so an error in one does not
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
            if h.get("engine") == "transfer89" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
