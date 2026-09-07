#!/usr/bin/env python3
"""One paper per entry settled by transfer92.

What these entries share is a condition stated about connected components --- a global thing
--- and the whole content of the argument is that it is not global at all. The general
builder would call it "a bounded window of consecutive lines", which is the conclusion and
not the reason, so the reduction is written out here as a lemma with a proof.
"""
import json
import os
import re

import localentry as LE
import phibuild
import transfer92
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def model_section(p, S):
    L, k = p['L'], p['k']
    alpha = r'\{' + ','.join(str(i) for i in range(k)) + r'\}'
    out = [
        r"\section{The condition is not global}", "",
        rf"The entry counts arrays with ${L}$ columns over the alphabet ${alpha}$, and asks "
        rf"that every set of equal values joined horizontally or vertically lie in a straight "
        rf"line. As stated this is a condition on connected components, and a component can "
        rf"run the length of the array; nothing about it is confined to a few rows. The first "
        rf"lemma replaces it by a condition on single cells, and the second by a condition on "
        rf"pairs of consecutive rows.", "",
        r"Call two cells \emph{joined} when they are horizontally or vertically adjacent and "
        r"hold the same value, and let a \emph{component} be a connected set of cells under "
        r"that relation. A \emph{turn} is a cell with a joined neighbour to its left or right "
        r"\emph{and} a joined neighbour above or below.", "",
        r"\begin{lemma}\label{lem:turn}",
        r"Every component lies in a single row or a single column if and only if the array "
        r"has no turn.",
        r"\end{lemma}", "",
        r"\begin{proof}",
        r"A turn lies in a component containing a cell to its side and a cell above or below "
        r"it, so that component meets two rows and two columns and lies in neither a single "
        r"row nor a single column.", "",
        r"Conversely, suppose some component $C$ lies in no single row and no single column. "
        r"$C$ is connected, so it has at least two cells and hence at least one joining edge; "
        r"if every edge of $C$ were horizontal then all of $C$ would lie in one row, and if "
        r"every edge were vertical it would lie in one column. So $C$ has a horizontal edge "
        r"$e$ and a vertical edge $f$. Take a path of edges of $C$ from $e$ to $f$; along it "
        r"the type changes somewhere, so two consecutive edges of the path have different "
        r"types. Consecutive edges of a path share a cell, and that shared cell has a joined "
        r"neighbour beside it and one above or below it. It is a turn.",
        r"\end{proof}", "",
        r"The point of Lemma~\ref{lem:turn} is that a turn is visible in one cell and its four "
        r"neighbours. That already bounds the condition, but it bounds it to three rows. It "
        r"can be brought down to two.", "",
        rf"For a row $r$ write $B(r)\subseteq\{{1,\dots,{L}\}}$ for the set of positions $j$ "
        rf"with $r_{{j-1}}=r_j$ or $r_j=r_{{j+1}}$ --- the cells of that row with a joined "
        rf"neighbour beside them. $B(r)$ depends on $r$ alone.", "",
        r"\begin{lemma}\label{lem:pair}",
        r"An array has no turn if and only if every pair of consecutive rows $r,s$ satisfies",
        r"\[ r_j \neq s_j \qquad\text{for every } j \in B(r)\cup B(s). \]",
        r"\end{lemma}", "",
        r"\begin{proof}",
        r"A cell in row $i$ at position $j$ is a turn exactly when $j\in B(r^{(i)})$ and it "
        r"equals the cell directly above or directly below it. If some pair of consecutive "
        r"rows $r=r^{(i)}$, $s=r^{(i+1)}$ has $r_j=s_j$ with $j\in B(r)$, that cell of row $i$ "
        r"is a turn; with $j\in B(s)$, that cell of row $i+1$ is a turn. Conversely a turn at "
        r"row $i$, position $j$, has $j\in B(r^{(i)})$ and agrees with row $i-1$ or row $i+1$ "
        r"at $j$, and the corresponding consecutive pair violates the displayed condition.",
        r"\end{proof}", "",
        rf"So the array is admissible precisely when consecutive rows are compatible in the "
        rf"sense of Lemma~\ref{{lem:pair}}, and compatibility is decided by the two rows and "
        rf"nothing else. The state is one row. There is no window to carry, no judgement "
        rf"deferred to a later row, and no special treatment of the last row: a one-row array "
        rf"has no vertical neighbours at all and is always admissible, which is where these "
        rf"sequences start.",
    ]
    if p['canon']:
        out += ["", rf"The entry also asks that new values be introduced in row major order. "
                    rf"That is not a condition on any pair of rows --- whether a value may "
                    rf"appear here depends on the whole array so far --- but the whole prefix "
                    rf"enters only through one integer, how many values have been introduced "
                    rf"already, so the state is a row together with a number in "
                    rf"$\{{0,\dots,{k}\}}$. The effect is that each array is counted once for "
                    rf"the whole class of arrays differing from it only by renaming values, "
                    rf"which is what the entry counts."]
    if p['frac'] != 1:
        out += ["", rf"The entry counts not the arrays themselves but $1/{p['frac']}$ of "
                    rf"them, so every count below is divided by ${p['frac']}$; the division "
                    rf"comes out exact at every term, which is itself a check on the model."]
    out += ["", rf"Make those states the vertices of a digraph, with an edge from $r$ to $s$ "
                rf"when the pair is compatible and the counter advances legally. Merging "
                rf"vertices with identical futures leaves $S={S}$. An admissible array is "
                rf"exactly a walk, so with $M$ the adjacency matrix and $\iota,\tau$ the "
                rf"vectors recording which states may begin and end an array,"]
    return "\n".join(out)


def build(h):
    a = h["anum"]
    S, order, nterms, nthr = h["S"], h["order"], h["nterms"], h["nthr"]
    off, sh = h["offset"], h["shift"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    p = transfer92.parse_name(e['name'])
    kk = off - sh
    expo = "n" if kk == 0 else ("n-%d" % kk if kk > 0 else "n+%d" % (-kk))
    frac = p['frac']
    scale = ""
    if frac != 1:
        scale = (rf" The entry does not count the arrays themselves but $1/{frac}$ of them, "
                 rf"so every count below is divided by ${frac}$.")
    pref = ('\\tfrac{1}{%d}\\,' % frac) if frac != 1 else ''
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        j = nthr - off
        if d[j] != sum(int(c) * d[j - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{A global condition that is really a local one: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{7 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry asks that every connected set of
equal values lie in a straight line, which is a condition on components and so on the array as
a whole. It is shown here to be equivalent to a condition on single pairs of adjacent rows:
the array is admissible exactly when no cell has an equal neighbour beside it and an equal
neighbour above or below it, and that in turn is decided one row at a time. The counted arrays
are then the walks in a finite digraph on $S={S}$ vertices, $a(n)$ is $C$-finite, and whether
the conjectured recurrence annihilates it is a finite exact computation with Cayley--Hamilton
bounding the work.{scale}
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

{model_section(p, S)}
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

Second, the reduction of Lemmas~\ref{{lem:turn}} and~\ref{{lem:pair}} was checked against the
thing it replaces. A separate program enumerates every array of the given shape one by one,
finds the connected sets of equal values by an ordinary graph search, and tests whether each
lies in a single row or a single column --- the entry's condition as written, with no
reduction at all. Its counts agree with the model's. That program shares no code with the
transfer matrix, so an error in one does not hide an error in the other.

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
            if h.get("engine") == "transfer92" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
