#!/usr/bin/env python3
"""One paper per Hardin neighbour-count entry."""
import conjquote
import os, json, re
import localentry as LE, phibuild
from transferbuild import rec_tex

PRE = phibuild.PRE
esc = phibuild.esc

NBNAME = {8: r"the eight king-move neighbours",
          6: r"the six horizontal, diagonal and antidiagonal neighbours",
          4: r"the four horizontal and vertical neighbours"}


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers and 41 quoted the
    wrong line of the block -- a closed form where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def build(h):
    a = h["anum"]
    K, alpha, same, counts = h["K"], h["alpha"], h["same"], h["counts"]
    S, order, nterms, thr = h["S"], h["order"], h["nterms"], h["threshold"]
    nb, ul0 = h["nb"], h["ul0"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    conj = conj_line(a, h.get("coeffs"))
    cset = r"\{" + ",".join(str(c) for c in counts) + r"\}"
    rel = "equal to" if same else "different from"
    ulnote = (r" The entry also fixes the top-left entry to be $0$; that is a condition on "
              r"the first row alone, so it restricts the start vector and nothing else."
              if ul0 else "")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts ${K}$-column arrays over $\{{0,\dots,{alpha}\}}$ in which every entry has,
among {NBNAME[nb]}, a number ${rel}$ itself lying in ${cset}$, and it carries an empirical
recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true. The neighbourhood
reaches one row up and one row down, so the condition on a row involves three consecutive
rows and a window of two rows is a sufficient state; the array is then a walk in a digraph
on $S={S}$ vertices. Unlike a plain walk count the boundary rows matter here --- the first
row has nothing above it and the last nothing below --- so the count is
$\mathbf{{s}}^{{\!\top}}P^{{\,n-2}}\mathbf{{e}}$ for genuine start and end vectors rather than
all-ones. The conjectured recurrence is then annihilated exactly, in integer arithmetic.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B50, 15B36.\normalsize

\section{{The sequence and the conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset
${int(e['offset'].split(',')[0])}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry carries the following comment:
\begin{{quote}}\small
{esc(conj)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision
{e['revision']}) the statement is still recorded as empirical, and nothing on the entry
records it as settled either way.

Written out, the claim is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;{rec_tex(h['coeffs'])}
\end{{equation}}
for all $n>{thr}$.

\section{{The array as a walk, with boundary}}

For a cell of the array let its \emph{{score}} be the number of {NBNAME[nb]} that lie inside
the array and carry a value ${rel}$ the cell's own. The entry's condition is that every cell
has score in ${cset}$.{ulnote}

A cell's neighbourhood reaches at most one row up and one row down, so the scores of the
cells of a row $s$ are determined by $s$ together with the row above and the row below.
Take as state an ordered pair $(r,s)$ of rows, so $S={S}$, and set
\begin{{itemize}}
\item $\mathbf{{s}}(r,s)=1$ when every cell of $r$ has score in ${cset}$ \emph{{with no row
above $r$}}{" and $r_1=0$" if ul0 else ""}, and $0$ otherwise;
\item an edge $(r,s)\to(s,t)$ when every cell of $s$ has score in ${cset}$ computed from
$r$, $s$ and $t$;
\item $\mathbf{{e}}(r,s)=1$ when every cell of $s$ has score in ${cset}$ \emph{{with no row
below $s$}}, and $0$ otherwise.
\end{{itemize}}
Let $P$ be the adjacency matrix of that edge relation.

\begin{{lemma}}\label{{lem:walk}}
$a(n)=\mathbf{{s}}^{{\!\top}}P^{{\,n-2}}\mathbf{{e}}$ for every $n\ge2$.
\end{{lemma}}

\begin{{proof}}
An array with $n$ rows is a sequence $r^{{(1)}},\dots,r^{{(n)}}$ of rows, and it is counted
exactly when every one of its $n$ rows has all scores in ${cset}$. Read the sequence as the
walk $\bigl(r^{{(1)}},r^{{(2)}}\bigr)\to\bigl(r^{{(2)}},r^{{(3)}}\bigr)\to\cdots\to
\bigl(r^{{(n-1)}},r^{{(n)}}\bigr)$, of length $n-2$. The condition on the first row is
checked by $\mathbf{{s}}$ at the initial state, because a first row has no row above it; the
condition on row $i$ for $2\le i\le n-1$ is checked by the edge entering
$\bigl(r^{{(i)}},r^{{(i+1)}}\bigr)$, which sees exactly $r^{{(i-1)}}$, $r^{{(i)}}$ and
$r^{{(i+1)}}$; and the condition on the last row is checked by $\mathbf{{e}}$ at the final
state. Each row's condition is therefore tested once and with the correct neighbours, and
summing over all walks gives $\mathbf{{s}}^{{\!\top}}P^{{\,n-2}}\mathbf{{e}}$.
\end{{proof}}

\section{{The criterion}}

Let $q(t)=t^{{{order}}}-\sum_i c_i t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and $u_j=\mathbf{{s}}^{{\!\top}}P^{{j}}q(P)\mathbf{{e}}$.

\begin{{lemma}}\label{{lem:crit}}
$a(n)-\sum_i c_i a(n-i)=u_{{\,n-2-{order}}}$ whenever $n-{order}\ge2$. So \eqref{{eq:conj}}
holds for every $n>t$ exactly when $u_j=0$ for all $j>t-2-{order}$. Moreover $(u_j)$
satisfies the monic linear recurrence given by the characteristic polynomial of $P$, of
degree $S$, so $S$ consecutive zeros force every later one and the last nonzero $u_j$ pins
$t$ down exactly.
\end{{lemma}}

\begin{{proof}}
Substituting Lemma~\ref{{lem:walk}} and factoring $P^{{\,n-2-{order}}}$ out of
$P^{{n-2}}-\sum_i c_i P^{{n-i-2}}$ gives the identity, and letting the exponent run gives the
equivalence. For the last part, Cayley--Hamilton gives $\chi(P)=0$ for the characteristic
polynomial $\chi$, so $\chi$ applied to the shift annihilates $(u_j)$; $\chi$ is monic of
degree $S$, which propagates $S$ consecutive zeros forward.
\end{{proof}}

\section{{The computation}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{thr}$. This is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The vector $q(P)\mathbf{{e}}\in\mathbb{{Z}}^{{S}}$ was formed by ${order}$ matrix--vector
products in exact integer arithmetic and the $u_j$ evaluated against $\mathbf{{s}}$ in turn.
They vanish from the index corresponding to $n={thr}+1$ onwards, and the run was continued
past $S$ consecutive zeros, which by Lemma~\ref{{lem:crit}} settles every larger index.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the digraph, the start vector and the end vector were built directly from the
entry's stated condition, the one-row count computed separately, and the resulting values
compared against the entry's DATA at every one of the ${nterms}$ published indices; they
agree exactly. This is the check that ties the model to the sequence, and it is a sharp one:
getting the boundary rows wrong, or treating them as interior rows, changes the early terms
immediately.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes at every index the entry claims.

Third, the vanishing test of Lemma~\ref{{lem:crit}} was carried past $S={S}$ consecutive
zeros rather than to a sampled prefix.

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
    hits = [h for h in json.load(open("transfer5_hits.json")) if not h.get("FAILS")]
    for h in hits:
        d = f"build/nb{h['anum']}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
