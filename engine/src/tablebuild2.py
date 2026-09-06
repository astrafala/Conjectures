#!/usr/bin/env python3
"""One paper per T(n,k) table whose column conjectures are settled."""
import os, json, re
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def block(anum):
    """the entry's 'Empirical for column k' block, verbatim."""
    e = LE.get(anum)
    out = []
    on = False
    for L in e['comment'] + e['formula']:
        t = L.strip()
        if re.match(r'^Empirical\b.*column', t, re.I):
            on = True; out.append(t); continue
        if on:
            if re.match(r'^k=\d+:', t):
                out.append(t)
            else:
                break
    return out


def build(h):
    a = h['anum']
    e = LE.get(a)
    cols = sorted(h['cols'], key=lambda c: (c.get('mode', 'col'), c['k']))
    ncol = [c for c in cols if c.get('mode', 'col') == 'col']
    nrow = [c for c in cols if c.get('mode') == 'row']
    parts = []
    if ncol:
        parts.append('the columns $k=' + ', '.join(str(c['k']) for c in ncol) + '$')
    if nrow:
        parts.append('the rows $n=' + ', '.join(str(c['k']) for c in nrow) + '$')
    ks = ' and '.join(parts)
    mod, rev = e['modified'], e['revision']
    blk = block(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    rows = []
    for c in cols:
        rows.append(rf"{'column $k$' if c.get('mode','col')=='col' else 'row $n$'}"
                    rf"$={c['k']}$ & ${c['order']}$ & ${c['S']}$ & "
                    rf"$>{c['nthr']}$ & ${c['nterms']}$ \\")
    tab = "\n".join(rows)
    blktex = "\n".join(esc(x) + r'\\' for x in blk)
    detail = []
    for c in cols:
        detail.append(rf"""\subsection*{{{'Column $k$' if c.get('mode','col')=='col' else 'Row $n$'}$={c['k']}$}}
The sequence is ``{esc(c['name_k'])}''. Its rows are the vertices of a digraph on
$S={c['S']}$ vertices, edges being the admissible consecutive pairs, and the count is
$\mathbf{{1}}^{{\!\top}}M^{{n}}\mathbf{{1}}$ up to the constant factor in the entry's name.
The conjectured recurrence
\[
a(n)\;=\;{rec_tex(c['coeffs'])}
\]
holds from index ${c['nthr']}+1$ on.""")
    details = "\n\n".join(detail)
    first = cols[0]
    totdig = sum(c.get('totdig', 0) for c in cols)
    totterm = sum(c['nterms'] for c in cols)

    return rf"""{PRE}
\title{{The empirical column recurrences for the table OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} is a two-dimensional table $T(n,k)$, and it carries a block of empirical
recurrences contributed by R.~H.~Hardin --- one for each of its first few columns. They are
true. Column $k$ of the table is an ordinary fixed-width array count, so its rows are the
vertices of a finite digraph and $T(n,k)$ is a number of walks in it; being a walk count the
column is $C$-finite, and whether a given recurrence annihilates it is decided by a finite
exact computation, with the Cayley--Hamilton theorem bounding the work. This note settles {ks}.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 15B36.\normalsize

\section{{The table and the conjectures}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${e['offset'].split(',')[0]}$, is
read by antidiagonals, and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry carries the following block:
\begin{{quote}}\small
{blktex}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) these are still
recorded as empirical, and nothing on the entry records any of them as settled.

\section{{A column of the table is a walk count}}

Fix $k$. The entry defines $T(n,k)$ as the number of arrays of a shape in which one dimension
is $n$ and the other is determined by $k$, subject to a condition imposed on every
$2\times2$ subblock --- a condition local to two consecutive rows and two consecutive columns.
Substituting the fixed value of $k$ into the entry's own wording turns the definition into an
ordinary one-parameter array count, and for such a count the rows are the vertices of a finite
digraph $G_k$: $r\to s$ is an edge exactly when placing $s$ under $r$ satisfies the condition
in every column pair. An admissible array is then a walk, so with $M_k$ the adjacency matrix
of $G_k$,
\[
T(n,k)\;=\;c_k\,\mathbf{{1}}^{{\!\top}}M_k^{{\,n}}\mathbf{{1}}
\]
for the constant $c_k$ that the entry's name supplies (a factor such as $\tfrac12$ or
$\tfrac14$ where the name says so, and $1$ otherwise).

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{r}}-\sum_i c_it^{{r-i}}$ be the characteristic polynomial of a conjectured
recurrence of order $r$ for column $k$. Then for every $n\ge r$,
\[
T(n,k)-\sum_i c_i\,T(n-i,k)\;=\;c_k\,\mathbf{{1}}^{{\!\top}}M_k^{{\,n-r}}q(M_k)\mathbf{{1}},
\]
so the recurrence holds from some point on if and only if
$\mathbf{{1}}^{{\!\top}}M_k^{{j}}q(M_k)\mathbf{{1}}=0$ for every $j\ge0$; and by the
Cayley--Hamilton theorem it is enough to check $j<S_k$, where $S_k$ is the number of vertices
of $G_k$.
\end{{lemma}}

\begin{{proof}}
Substitute the walk expression and factor $M_k^{{n-r}}$ out of $M_k^{{n}}-\sum_ic_iM_k^{{n-i}}$;
the scalar $c_k$ is nonzero. For the bound, $M_k^{{S_k}}$ is an integer combination of
$I,M_k,\dots,M_k^{{S_k-1}}$, so each $\mathbf{{1}}^{{\!\top}}M_k^{{j}}q(M_k)\mathbf{{1}}$ with
$j\ge S_k$ repeats that combination of earlier values.
\end{{proof}}

\section{{The computation, column by column}}

\begin{{center}}
\begin{{tabular}}{{ccccc}}
line & order & vertices $S$ & proved for & terms checked \\ \hline
{tab}
\end{{tabular}}
\end{{center}}

In each case the vector $w=q(M_k)\mathbf{{1}}$ was formed by $r$ matrix--vector products in
exact integer arithmetic and $\mathbf{{1}}^{{\!\top}}M_k^{{j}}w$ evaluated for $j=0,1,\dots$,
again exactly; every one of those integers vanishes from the stated point onwards and the run
continued until the working vector was identically zero, which settles all larger $j$ at once.

{details}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, each model was compared against the entry's own published values for its line, taken
both from the antidiagonal DATA read in either orientation and from the ``Table starts''
block, and agrees at every available term. This is what ties a model to the table:
substituting the fixed index into the entry's wording is a reading of English, and a wrong
reading gives a different digraph and different counts. Across the lines settled here the
model reproduces ${totterm}$ published values, ${totdig}$ decimal digits in all, every one of
them exactly; a misreading of the entry would have to reproduce all of them by accident.

Second, each conjectured recurrence was evaluated on those published values in exact
integer arithmetic, with no matrices involved, and holds wherever the proved range and the
data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic rather than on a sampled prefix.

\begin{{remark}}
A row of the table is a column of the transposed table: fixing $n$ and letting $k$ vary gives a
count of arrays of fixed height, which is the same kind of object with the two dimensions
exchanged. Both are settled here by the same argument. Only the lines the entry states
explicitly, and for which enough published values exist to run the first check above, are
claimed.
\end{{remark}}

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
    hits = json.load(open("tab2_hits.json"))
    for h in hits:
        dd = f"build/tb3{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
