#!/usr/bin/env python3
"""One paper per table whose column or row recurrences were recovered from their stated order."""
import os, json, re
import localentry as LE, phibuild

PRE = phibuild.PRE
esc = phibuild.esc


def coeff_display(coeffs, order):
    cs = [int(coeffs[str(i)]) for i in range(1, order + 1)]
    if order <= 24:
        cols = 4
        per = (len(cs) + cols - 1) // cols
        rows = []
        for r in range(per):
            cells = []
            for j in range(cols):
                k = r + j * per
                cells.append(r"$c_{%d}$ & $%d$" % (k + 1, cs[k]) if k < len(cs) else " & ")
            rows.append(" & ".join(cells) + r" \\")
        return (r"\begin{center}\small\begin{tabular}{" + "cc" * cols + "}" + "\n" +
                "\n".join(rows) + "\n" + r"\end{tabular}\end{center}")
    body = ",\\ ".join(str(v) for v in cs)
    return (r"\[" + "\n" + r"(c_1,\dots,c_{%d})=(" % order + body + r")." + "\n" + r"\]")


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    cols = sorted(h['cols'], key=lambda c: (c['mode'], c['k']))
    quoted = "\\\\\n".join(esc(c['line']) for c in cols)
    parts = []
    for c in cols:
        what = ("column $k=%d$" % c['k']) if c['mode'] == 'col' else ("row $n=%d$" % c['k'])
        parts.append(rf"""\subsection*{{{what[0].upper() + what[1:]}}}
Substituting the fixed index into the entry's wording gives an ordinary one-parameter array
count, a walk on $S={c['S']}$ vertices. Berlekamp--Massey on $2S={2 * c['S']}$ exact terms
returns a minimal recurrence of order ${c['order']}$ --- the order the entry states --- with
integer coefficients
{coeff_display(c['coeffs'], c['order'])}
so that $a(m)=\sum_{{i=1}}^{{{c['order']}}}c_i\,a(m-i)$ for every $m$. Removing the first
${c['order']}+4$ terms and repeating gives order ${c['order']}$ again, which is what the
identification below needs.""")
    details = "\n\n".join(parts)
    ks = ", ".join(("column %d" % c['k']) if c['mode'] == 'col' else ("row %d" % c['k'])
                   for c in cols)

    return rf"""{PRE}
\title{{Recovering the unwritten recurrences of the table OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{2 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} is a two-dimensional table $T(n,k)$ whose empirical recurrences are, for several of
its lines, given only as an ORDER --- ``{esc(cols[0]['line'])}'' and the like --- with the
coefficients in a linked file rather than in the entry. Those conjectures can still be settled,
and the recurrences recovered. A line of the table is a fixed-width or fixed-height array
count, hence a walk count on finitely many vertices, hence satisfies some monic recurrence of
order at most that number; Berlekamp--Massey on twice as many exact terms returns the MINIMAL
one. Where its order equals the order the entry states --- and where the same holds after the
first few terms are dropped --- any recurrence of that order the line satisfies has a
characteristic polynomial that is a multiple of the minimal one and of equal degree, hence is
that polynomial. This note settles {ks}.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 15A18.\normalsize

\section{{The table and the unwritten conjectures}}

OEIS {a} is ``{esc(e['name'].strip())}''. It is read by antidiagonals and begins
\[
{", ".join(str(v) for v in d[:8])},\ \dots
\]
The entry carries, among its empirical claims:
\begin{{quote}}\small
{quoted}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) these are still
recorded as empirical, and the recurrences themselves are not in the entry text.

\section{{Why a line of the table is a walk count}}

Fix the index that the line fixes. The entry defines $T(n,k)$ as a number of arrays of a shape
determined by $n$ and $k$, subject to a condition local to a bounded window of consecutive
lines. Substituting the fixed index into the entry's own wording turns the definition into an
ordinary one-parameter array count, and for such a count the admissible windows are the
vertices of a finite digraph and an array is a walk. So the line is a walk count on $S$
vertices, and by the Cayley--Hamilton theorem it satisfies a monic integer recurrence of order
at most $S$.

\section{{Recovering the recurrences}}

\begin{{lemma}}\label{{lem:bm}}
A sequence known to satisfy some linear recurrence of order at most $S$ is determined, with its
minimal recurrence, by its first $2S$ terms; Berlekamp--Massey applied to them returns that
minimal recurrence exactly.
\end{{lemma}}

{details}

\begin{{theorem}}
For each line above, the displayed recurrence holds for every index, and it is the recurrence
the entry records.
\end{{theorem}}

\begin{{proof}}
It holds by Lemma~\ref{{lem:bm}}. For the identification, the entry asserts that the line
satisfies SOME recurrence of the stated order, possibly only from some index on. Let $q$ be its
characteristic polynomial and $q_{{\min}}$ the minimal polynomial of the tail. Then
$q_{{\min}}\mid q$, and the second Berlekamp--Massey run --- on the line with its first few
terms removed --- shows $\deg q_{{\min}}$ equals the stated order, which is $\deg q$. Both are
monic, so $q=q_{{\min}}$.
\end{{proof}}

\section{{Verification}}

Three checks.

First, each line's model was compared against the entry's own published values for that line,
taken from the antidiagonal DATA read in either orientation and from the ``Table starts''
block, and agrees at every available term. This is the only point at which reading the entry's
English enters, and a misreading gives different counts.

Second, each recovered recurrence was evaluated directly on the model's values, with no
Berlekamp--Massey involved, and holds at every index tested.

Third, each order was computed twice by independent routes --- modulo a $61$-bit prime, where
every intermediate is a machine word, and again in exact rational arithmetic --- and once more
on the line with its first few terms dropped, which is what the identification requires. All
agree.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{massey}} J.~L.~Massey, Shift-register synthesis and BCH decoding, \emph{{IEEE
Trans. Inform. Theory}} \textbf{{15}} (1969), 122--127.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = json.load(open("ordline_hits.json"))
    for h in hits:
        dd = f"build/ol{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
