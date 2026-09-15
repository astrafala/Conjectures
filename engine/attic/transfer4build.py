#!/usr/bin/env python3
"""One paper per Hardin pattern-avoidance array entry."""
import conjquote
import os, json, re
import localentry as LE, phibuild
from transferbuild import rec_tex

PRE = phibuild.PRE
esc = phibuild.esc


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers and 41 quoted the
    wrong line of the block -- a closed form where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def pat(p):
    return "(" + ",".join(str(v) for v in p) + ")"


def build(h):
    a = h["anum"]
    K, alpha, H, V, L = h["K"], h["alpha"], h["H"], h["V"], h["L"]
    S, order, nterms, thr, nrows = h["S"], h["order"], h["nterms"], h["threshold"], h["nrows"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    conj = conj_line(a, h.get("coeffs"))
    Hs = ", ".join(pat(p) for p in H)
    Vs = ", ".join(pat(p) for p in V)
    L1 = L - 1
    transposed = bool(re.search(r'\d+\s*[xX]\s*n', e["name"]))
    dirn = ("columns" if transposed else "rows")
    other = ("rows" if transposed else "columns")
    note = (r"""The entry's array has a fixed number of rows and a growing number of
columns, so the roles of the two directions are exchanged: what the entry calls the
horizontal direction runs along the growing side. The transfer below is written in the
growing direction throughout.""" if transposed else "")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{alpha}\}}$ of width ${K}$ that avoid the patterns
${Hs}$ along one axis and ${Vs}$ along the other, and carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true. The patterns have length ${L}$, so
the constraint across the growing direction ties together ${L}$ consecutive {dirn}: taking a
window of ${L-1}$ consecutive {dirn} as a state makes the array a walk in a finite digraph
on $S={S}$ vertices, and $a(n)=\mathbf{{1}}^{{\!\top}}P^{{\,n-{L-1}}}\mathbf{{1}}$. Writing $q$
for the characteristic polynomial of the conjectured recurrence, the residual is
$\mathbf{{1}}^{{\!\top}}P^{{\,n-{L-1}-{order}}}q(P)\mathbf{{1}}$, which vanishes identically
beyond a threshold that the computation pins down exactly. Finite, exact, integer.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 68R15, 15B36.\normalsize

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
As of the ``Last modified'' line on the live entry ({e['modified']}, revision
{e['revision']}) the statement is still recorded as empirical, and nothing on the entry
records it as settled either way.

Written out, the claim is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;{rec_tex(h['coeffs'])}
\end{{equation}}
for all $n>{thr}$. {note}

\section{{The array as a walk}}

Call a {dirn[:-1]} \emph{{admissible}} if the word it forms contains none of the patterns
${Hs}$ as ${L}$ consecutive entries. There are ${nrows}$ admissible {dirn}; that condition
involves a single {dirn[:-1]} only.

The remaining patterns ${Vs}$ are forbidden along the other axis, so each of them
constrains ${L}$ consecutive {dirn} at a fixed position of the {other[:-1]}. Take as state a
window $w=\bigl(w^{{(1)}},\dots,w^{{({L1})}}\bigr)$ of ${L-1}$ consecutive admissible
{dirn}, so $S={S}$, and declare $w\to w'$ an edge when $w'$ is $w$ with its first entry
dropped and one further admissible {dirn[:-1]} $t$ appended, subject to: for every position
$j$, the ${L}$-tuple read down the {other[:-1]} $j$ across $w^{{(1)}},\dots,w^{{({L1})}},t$
is none of ${Vs}$. Let $P$ be the adjacency matrix.

\begin{{lemma}}\label{{lem:walk}}
$a(n)=\mathbf{{1}}^{{\!\top}}P^{{\,n-{L-1}}}\mathbf{{1}}$ for every $n\ge{L-1}$.
\end{{lemma}}

\begin{{proof}}
An array of the entry's kind with $n$ {dirn} is a sequence of $n$ admissible {dirn} in
which no forbidden pattern appears along the other axis. Reading it as the sequence of its
overlapping windows of length ${L-1}$ turns it into a walk: consecutive windows overlap in
${L-2}$ {dirn} by construction, and the edge condition is exactly the requirement on the one
new ${L}$-tuple that each step creates. Conversely a walk reassembles into such an array,
and the two constructions are mutually inverse. A walk of length $n-{L-1}$ visits $n-{L-2}$
windows, that is $n$ {dirn}; summing over all starting and ending states gives
$\mathbf{{1}}^{{\!\top}}P^{{\,n-{L-1}}}\mathbf{{1}}$.
\end{{proof}}

\section{{The criterion}}

Let $q(t)=t^{{{order}}}-\sum_i c_i t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}} and $u_j=\mathbf{{1}}^{{\!\top}}P^{{j}}q(P)\mathbf{{1}}$.

\begin{{lemma}}\label{{lem:crit}}
$a(n)-\sum_i c_i a(n-i)=u_{{\,n-{L-1}-{order}}}$ whenever $n-{order}\ge{L-1}$. Hence
\eqref{{eq:conj}} holds for every $n>t$ exactly when $u_j=0$ for every
$j>t-{L-1}-{order}$. Moreover $(u_j)$ satisfies the monic linear recurrence whose
characteristic polynomial is that of $P$, of degree $S$, so $S$ consecutive zeros force all
later ones and the last nonzero $u_j$ pins $t$ down exactly.
\end{{lemma}}

\begin{{proof}}
Substituting Lemma~\ref{{lem:walk}} into the left side and factoring out
$P^{{\,n-{L-1}-{order}}}$ gives the identity. The equivalence follows by letting the exponent
run. For the last claim, Cayley--Hamilton gives $\chi(P)=0$ for the characteristic
polynomial $\chi$ of $P$, so $\chi$ applied to the shift annihilates $(u_j)$; being monic of
degree $S$, it propagates $S$ consecutive zeros forward.
\end{{proof}}

\section{{The computation}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{thr}$. This is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The vector $q(P)\mathbf{{1}}\in\mathbb{{Z}}^{{S}}$ was formed by ${order}$ matrix--vector
products in exact integer arithmetic and the $u_j$ evaluated in turn. They vanish from the
index corresponding to $n={thr}+1$ onwards, and the run was continued past $S$ consecutive
zeros, which by Lemma~\ref{{lem:crit}} settles every larger index.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the digraph was built directly from the entry's stated patterns and the walk counts
compared against the entry's DATA at every one of the ${nterms}$ published indices; the
values agree exactly, including the initial count of ${nrows}$ admissible {dirn}. That is
what ties the digraph to the sequence, and a model reproducing only part of the published
data was rejected wherever it occurred.

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
    hits = [h for h in json.load(open("transfer4_hits.json")) if not h.get("FAILS")]
    for h in hits:
        d = f"build/pa{h['anum']}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
