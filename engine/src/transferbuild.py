#!/usr/bin/env python3
"""One paper per Hardin 2 X 2-subblock array entry."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transfer2 as T

PRE = phibuild.PRE
esc = phibuild.esc


def modinfo(anum):
    e = LE.get(anum)
    return e["modified"], e["revision"]


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def rec_tex(coeffs):
    parts = []
    for i in sorted(int(k) for k in coeffs):
        c = int(coeffs[str(i)]) if isinstance(coeffs, dict) and str(i) in coeffs else int(coeffs[i])
        sign = "+" if c > 0 else "-"
        mag = abs(c)
        term = (rf"a(n-{i})" if mag == 1 else rf"{mag}\,a(n-{i})")
        parts.append((sign, term))
    s = ""
    for k, (sign, term) in enumerate(parts):
        if k == 0:
            s += ("" if sign == "+" else "-") + term
        else:
            s += f" {sign} {term}"
    return s


def build(h):
    a = h["anum"]
    cols, alpha, sums, extra = h["cols"], h["alpha"], h["sums"], h["extra"]
    S, order, nterms = h["S"], h["order"], h["nterms"]
    thr = h["threshold"]
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    sumtex = ", ".join(str(s) for s in sums[:-1]) + (" or " if len(sums) > 1 else "") + str(sums[-1])
    setname = rf"\{{{', '.join(str(s) for s in sums)}\}}"
    extratex = (r", and in which no $2\times2$ subblock has exactly two nonzero entries"
                if extra else "")
    extracond = (r"\item the four entries $r_j,r_{j+1},s_j,s_{j+1}$ do not include exactly "
                 r"two nonzero ones, that is $\#\bigl\{v\in\{r_j,r_{j+1},s_j,s_{j+1}\}: "
                 r"v\ne0\bigr\}\ne2$;" if extra else "")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts ${cols}$-column arrays over $\{{0,\dots,{alpha}\}}$ in which every
$2\times2$ subblock sums to one of ${setname}${extratex}, and carries an empirical
recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is not an
empirical matter at all: the rows of such an array are the vertices of a finite digraph in
which the admissible row-to-row steps are the edges, so $a(n)=\mathbf{{1}}^{{\!\top}}M^{{n}}
\mathbf{{1}}$ for the adjacency matrix $M$ of that digraph, on $S={S}$ vertices. Writing
$q$ for the characteristic polynomial of the conjectured recurrence, the recurrence holds
for every $n$ exactly when $\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}=0$ for all
$j\ge0$, and the Cayley--Hamilton theorem bounds that to $j<S$. It is therefore a finite
computation in exact integer arithmetic, and it comes out zero.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 15B36.\normalsize

\section{{The sequence and the conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${int(e['offset'].split(',')[0])}$
and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
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

Let $V=\{{0,1,\dots,{alpha}\}}^{{{cols}}}$, the set of possible rows, so $|V|=S={S}$. For
$r,s\in V$ declare $r\to s$ an edge when, for every $j$ with $1\le j\le {cols}-1$,
\begin{{itemize}}
\item $r_j+r_{{j+1}}+s_j+s_{{j+1}}\in{setname}$;
{extracond}
\end{{itemize}}
that is, when placing the row $s$ directly under the row $r$ satisfies the entry's
condition on every $2\times2$ subblock formed by those two rows. Let $M\in\{{0,1\}}^{{S\times
S}}$ be the adjacency matrix of this digraph and $\mathbf{{1}}$ the all-ones vector.

\begin{{lemma}}\label{{lem:walk}}
The arrays counted by the entry with $n+1$ rows are exactly the walks
$r^{{(0)}}\to r^{{(1)}}\to\cdots\to r^{{(n)}}$ of length $n$ in this digraph. Consequently
\[
a(n)\;=\;\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}} .
\]
\end{{lemma}}

\begin{{proof}}
An array with $n+1$ rows and ${cols}$ columns is precisely a sequence
$r^{{(0)}},\dots,r^{{(n)}}$ of elements of $V$. Every $2\times2$ subblock of the array lies
in two vertically adjacent rows $r^{{(i)}},r^{{(i+1)}}$ and in two horizontally adjacent
columns $j,j+1$; so the array satisfies the entry's condition on all of its $2\times2$
subblocks if and only if each consecutive pair $\bigl(r^{{(i)}},r^{{(i+1)}}\bigr)$ satisfies
it on all column pairs, which is exactly the edge relation. Counting walks of length $n$ by
summing over all starting and ending vertices gives
$\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$, since
$\bigl(M^{{n}}\bigr)_{{r,s}}$ is the number of walks of length $n$ from $r$ to $s$.
\end{{proof}}

\section{{The criterion}}

Let $q(t)=t^{{{order}}}-\sum_{{i}}c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}}, with the $c_i$ read off that equation.

\begin{{lemma}}\label{{lem:crit}}
For every $n\ge{order}$,
\[
a(n)-\sum_i c_i\,a(n-i)\;=\;\mathbf{{1}}^{{\!\top}}M^{{\,n-{order}}}\,q(M)\,\mathbf{{1}} .
\]
Hence \eqref{{eq:conj}} holds for every $n\ge{order}$ if and only if
$\mathbf{{1}}^{{\!\top}}M^{{j}}q(M)\mathbf{{1}}=0$ for every $j\ge0$; and it is enough to
check $j=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
By Lemma~\ref{{lem:walk}}, $a(n-i)=\mathbf{{1}}^{{\!\top}}M^{{n-i}}\mathbf{{1}}$, so
\[
a(n)-\sum_i c_i a(n-i)
=\mathbf{{1}}^{{\!\top}}\Bigl(M^{{n}}-\sum_i c_i M^{{n-i}}\Bigr)\mathbf{{1}}
=\mathbf{{1}}^{{\!\top}}M^{{\,n-{order}}}\Bigl(M^{{{order}}}-\sum_i c_i M^{{{order}-i}}\Bigr)\mathbf{{1}},
\]
which is the stated identity. The equivalence follows by letting $n-{order}=j$ run over
$\ge0$. For the last clause put $w=q(M)\mathbf{{1}}$. By the Cayley--Hamilton theorem
$M^{{S}}$ is an integer combination of $I,M,\dots,M^{{S-1}}$, so
$\mathbf{{1}}^{{\!\top}}M^{{j}}w$ for $j\ge S$ is the corresponding combination of the
earlier values; if those all vanish, so do all the rest.
\end{{proof}}

\section{{The computation}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{thr}$. This is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The vector $w=q(M)\mathbf{{1}}\in\mathbb{{Z}}^{{S}}$ was formed by ${order}$ matrix--vector
products in exact integer arithmetic, and $\mathbf{{1}}^{{\!\top}}M^{{j}}w$ was evaluated for
$j=0,1,\dots$ in exact integer arithmetic. Every one of those integers is $0$ from
$j={thr}-{order}+1$ onwards, and the run was continued past $S$ consecutive zeros, which by
Lemma~\ref{{lem:crit}} settles every larger $j$ as well. Hence the recurrence holds for
every $n>{thr}$.
\end{{proof}}

\begin{{remark}}
The argument gives more than the recurrence: it shows the sequence is $C$-finite with
characteristic polynomial dividing that of $M$, so it has a rational generating function
whose denominator divides $\det(I-xM)$. The conjectured recurrence is one consequence; the
minimal one is a divisor of $q$.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the digraph was built directly from the entry's stated condition and the walk counts
$\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$ compared against the entry's DATA at every one of
the ${nterms}$ published indices; the values agree exactly. That is what ties the digraph to
the sequence: a model that reproduced only some of the published terms would be the wrong
model, and would have been rejected.

Second, the recurrence \eqref{{eq:conj}} was evaluated on those published terms in exact
integer arithmetic, with no matrices involved, and vanishes wherever it applies.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was run to the full Cayley--Hamilton
bound $j<S={S}$ rather than to a sampled prefix, in exact integer arithmetic, and returned
zero throughout.

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
    hits = [h for h in json.load(open("transfer_hits.json")) if not h.get("FAILS")]
    for h in hits:
        d = f"build/tm{h['anum']}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
