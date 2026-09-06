#!/usr/bin/env python3
"""One paper per Hardin constant-stress tiling entry."""
import os, json, re
import localentry as LE, phibuild
from transferbuild import rec_tex

PRE = phibuild.PRE
esc = phibuild.esc


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h["anum"]
    cols, alpha, c, noadj = h["cols"], h["alpha"], h["c"], h["noadj"]
    S, order, nterms, thr = h["S"], h["order"], h["nterms"], h["threshold"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)

    vertex = (rf"""all of $\{{0,\dots,{alpha}\}}^{{{cols}}}$""" if not noadj else
              rf"""those $r\in\{{0,\dots,{alpha}\}}^{{{cols}}}$ with $r_j\ne r_{{j+1}}$ for every
$j$ --- the rows in which no two horizontally adjacent entries are equal""")
    edgecond = (rf"""$\bigl|r_j+s_{{j+1}}-r_{{j+1}}-s_j\bigr|={c}$ for every $j$ with
$1\le j\le{cols}-1$""" if not noadj else
                rf"""$\bigl|r_j+s_{{j+1}}-r_{{j+1}}-s_j\bigr|={c}$ for every $j$ with
$1\le j\le{cols}-1$, and $r_j\ne s_j$ for every $j$""")
    extraline = ("" if not noadj else
                 r""" The condition ``no adjacent elements equal'' splits into a horizontal
part, which constrains a single row and so selects the vertex set, and a vertical part,
which constrains a consecutive pair of rows and so belongs to the edge relation.""")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts ${cols}$-column arrays over $\{{0,\dots,{alpha}\}}$ in which every
$2\times2$ subblock has its diagonal sum differing from its antidiagonal sum by
exactly ${c}${", and in which no two adjacent entries are equal" if noadj else ""}, and it
carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true,
and it is not an empirical matter: the condition constrains only consecutive pairs of rows,
so the rows are the vertices of a finite digraph and an $(n+1)$-row array is a walk of
length $n$. Hence $a(n)=\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$ on $S={S}$ vertices, which
is $C$-finite. Writing $q$ for the characteristic polynomial of the conjectured recurrence,
the residual is $\mathbf{{1}}^{{\!\top}}M^{{\,n-{order}}}q(M)\mathbf{{1}}$, so the recurrence
holds beyond a threshold exactly when that vanishes from then on --- and since the sequence
of those values obeys the monic recurrence given by the characteristic polynomial of $M$,
$S$ consecutive zeros settle every later one. The whole test is finite and exact.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 15B36.\normalsize

\section{{The sequence and the conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset
${int(e['offset'].split(',')[0])}$ and begins
\[
{", ".join(str(x) for x in d[:7])},\ \dots
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
for all $n>{thr}$, which is every $n$ at which a recurrence of order ${order}$ can be
stated.

\section{{The rows form a digraph}}

In a $2\times2$ subblock with top row $(r_j,r_{{j+1}})$ and bottom row $(s_j,s_{{j+1}})$ the
diagonal sum is $r_j+s_{{j+1}}$ and the antidiagonal sum is $r_{{j+1}}+s_j$, so the entry's
condition on that subblock reads
\[
\bigl|\,r_j+s_{{j+1}}-r_{{j+1}}-s_j\,\bigr|\;=\;{c}.
\]
Every such condition involves two consecutive rows only.{extraline}

Let $V$ consist of {vertex}, and put $S=|V|={S}$. For $r,s\in V$ declare $r\to s$ an edge
when {edgecond}. Let $M\in\{{0,1\}}^{{S\times S}}$ be the adjacency matrix and $\mathbf{{1}}$
the all-ones vector.

\begin{{lemma}}\label{{lem:walk}}
The arrays counted by the entry with $n+1$ rows are exactly the walks
$r^{{(0)}}\to\cdots\to r^{{(n)}}$ of length $n$ in this digraph, so
$a(n)=\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$.
\end{{lemma}}

\begin{{proof}}
An array with $n+1$ rows and ${cols}$ columns is a sequence $r^{{(0)}},\dots,r^{{(n)}}$ of
rows. Each of its $2\times2$ subblocks lies in two vertically adjacent rows
$r^{{(i)}},r^{{(i+1)}}$ and two horizontally adjacent columns $j,j+1$, so the array satisfies
the entry's condition on all subblocks precisely when every consecutive pair of rows is an
edge; and the row-internal condition, where present, is exactly membership of $V$. Summing
the walk counts $\bigl(M^{{n}}\bigr)_{{r,s}}$ over all $r$ and $s$ gives
$\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$.
\end{{proof}}

\section{{The criterion}}

Let $q(t)=t^{{{order}}}-\sum_i c_i t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}}.

\begin{{lemma}}\label{{lem:crit}}
For $n\ge{order}$,
$a(n)-\sum_i c_i a(n-i)=\mathbf{{1}}^{{\!\top}}M^{{\,n-{order}}}q(M)\mathbf{{1}}$. Writing
$u_j=\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}$, the recurrence therefore holds for every
$n>t$ exactly when $u_j=0$ for every $j>t-{order}$. Moreover $(u_j)_{{j\ge0}}$ satisfies the
monic linear recurrence whose characteristic polynomial is that of $M$, of degree $S$; so
if $u_j$ vanishes for $S$ consecutive indices it vanishes for every larger index, and the
last nonzero $u_j$ determines $t$ exactly.
\end{{lemma}}

\begin{{proof}}
By Lemma~\ref{{lem:walk}}, $a(n-i)=\mathbf{{1}}^{{\!\top}}M^{{n-i}}\mathbf{{1}}$, so
$a(n)-\sum_i c_i a(n-i)
=\mathbf{{1}}^{{\!\top}}M^{{\,n-{order}}}\bigl(M^{{{order}}}-\sum_i c_i M^{{{order}-i}}\bigr)
\mathbf{{1}}$, which is the identity. Putting $j=n-{order}$ gives the equivalence. For the
last claim, let $\chi$ be the characteristic polynomial of $M$; by Cayley--Hamilton
$\chi(M)=0$, so applying $\chi$ to the shift operator annihilates $(u_j)$, and $\chi$ is
monic of degree $S$, which is exactly the statement that $S$ consecutive zeros propagate
forward.
\end{{proof}}

\section{{The computation}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{thr}$. This is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The vector $q(M)\mathbf{{1}}\in\mathbb{{Z}}^{{S}}$ was formed by ${order}$ matrix--vector
products in exact integer arithmetic and the values $u_j$ evaluated for
$j=0,1,\dots$. They vanish from $j={thr}-{order}+1$ onwards, and the run was continued past
$S$ consecutive zeros, which by Lemma~\ref{{lem:crit}} settles every larger $j$. Hence the
recurrence holds for every $n>{thr}$.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the digraph was built directly from the entry's stated condition and the walk counts
$\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$ compared against the entry's DATA at every one of
the ${nterms}$ published indices; the values agree exactly. That is what ties the digraph to
the sequence: a model reproducing only some published terms would be the wrong model and
was rejected wherever it occurred.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes wherever it applies.

Third, the vanishing test of Lemma~\ref{{lem:crit}} was carried past $S={S}$ consecutive
zeros rather than to a sampled prefix, in exact integer arithmetic.

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
    hits = [h for h in json.load(open("transfer3_hits.json")) if not h.get("FAILS")]
    for h in hits:
        d = f"build/ts{h['anum']}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
