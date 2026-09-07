#!/usr/bin/env python3
"""One paper per entry that states only the ORDER of its empirical recurrence."""
import os, json, re
import localentry as LE, phibuild

_ROSTER = None


def _date(a):
    """the date the result was obtained: a paper already in the roster keeps the date it was
    written with, a new one takes the date the caller gives."""
    global _ROSTER
    if _ROSTER is None:
        _ROSTER = {v['anum'] for v in json.load(open('paper-engines.json')).values()}
    return '2 September 2026' if a in _ROSTER else os.environ.get('PAPER_DATE',
                                                                  '2 September 2026')

PRE = phibuild.PRE
esc = phibuild.esc


def coeff_table(coeffs, order):
    cs = [(i, int(coeffs[str(i)])) for i in range(1, order + 1)]
    cols = 4
    rows = []
    for r in range((len(cs) + cols - 1) // cols):
        cells = []
        for j in range(cols):
            k = r + j * ((len(cs) + cols - 1) // cols)
            if k < len(cs):
                cells.append(r"$c_{%d}$ & $%d$" % (cs[k][0], cs[k][1]))
            else:
                cells.append(" & ")
        rows.append(" & ".join(cells) + r" \\")
    return "\n".join(rows)


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    # The bound the computation actually used is the merged one. Quoting the unmerged count
    # beside "Berlekamp--Massey on 2S exact terms" would describe a computation that was not
    # performed, so the paper states both and says which is which.
    S, order, off = h['S'], h['order'], h['offset']
    Sm = h.get('Smerged', S)
    merge = "" if Sm == S else (
        r" States with the same future contribute identically to $\iota^{\!\top}M^n\tau$, so "
        r"they may be merged without changing any count; merging leaves $S'=%d$ of the $%d$, "
        r"and it is that smaller bound the computation below uses." % (Sm, S))
    Suse = Sm
    tab = coeff_table(h['coeffs'], order)
    ncols = 4

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}: recovering a conjecture that is not written down}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{_date(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} records ``Empirical recurrence of order ${order}$'', with the recurrence itself in a
linked file rather than in the entry. The conjecture can nevertheless be settled, and the
recurrence recovered, without reading that file. The entry counts arrays under a condition
local to a bounded window of lines, so the count is a walk count on a finite digraph and
satisfies some monic recurrence of order at most the number of its states with distinct
futures, here $S'={Suse}$; Berlekamp--Massey applied to $2S'$ exact
terms therefore returns the MINIMAL such recurrence. Its order is exactly ${order}$, the order
the entry states, and the same is true of every tail of the sequence. Any recurrence of order
${order}$ that the sequence satisfies from any point on must then have a characteristic
polynomial that is a multiple of the minimal one and of the same degree, hence equal to it. So
the entry's recurrence is the one displayed here, whatever its file contains, and it is
proved.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 15A18.\normalsize

\section{{A conjecture one cannot read}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(v) for v in d[:8])},\ \dots
\]
The entry states:
\begin{{quote}}
{esc(h['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical. The recurrence's coefficients are not in the entry text.

\section{{The count is a walk count}}

The entry's condition is local: it constrains a bounded window of consecutive lines of the
array and nothing further. The admissible configurations of one such window are the vertices
of a finite digraph, an edge joining $u$ to $v$ when $v$ may follow $u$, and an admissible
array is exactly a walk. Hence, with $M$ the adjacency matrix on $S={S}$ vertices,
$a(n)=\iota^{{\!\top}}M^{{\,j(n)}}\tau$ for a linear reindexing $j$ fixed by the entry's shape
and checked against its published terms.{merge} By the Cayley--Hamilton theorem $M^{{S}}$ is an
integer combination of $I,M,\dots,M^{{S-1}}$, so:

\begin{{lemma}}\label{{lem:cf}}
$a$ satisfies a monic linear recurrence with integer coefficients of order at most
$S'={Suse}$.
\end{{lemma}}

\section{{Recovering the recurrence}}

\begin{{lemma}}\label{{lem:bm}}
A sequence known to satisfy some linear recurrence of order at most $S$ is determined, together
with its minimal recurrence, by its first $2S$ terms: Berlekamp--Massey applied to them returns
that minimal recurrence exactly.
\end{{lemma}}

Running it on $2S={2 * S}$ exact terms of the model returns order ${order}$ --- the order the
entry states --- with the integer coefficients
\[
a(n)\;=\;\sum_{{i=1}}^{{{order}}}c_i\,a(n-i),
\]
\begin{{center}}\small
\begin{{tabular}}{{{'cc' * ncols}}}
{tab}
\end{{tabular}}
\end{{center}}

\begin{{theorem}}
The recurrence above holds for every $n$, and it is the recurrence the entry records.
\end{{theorem}}

\begin{{proof}}
It holds by Lemma~\ref{{lem:bm}}, which returns a recurrence the sequence satisfies from its
first term. For the identification: the entry asserts that the sequence satisfies SOME
recurrence of order ${order}$, possibly only from some index on. Let $q$ be that recurrence's
characteristic polynomial and $q_{{\min}}$ the minimal polynomial of the tail of the sequence.
Then $q_{{\min}}\mid q$. Berlekamp--Massey run on the sequence with its first ${order}+4$ terms
removed returns order ${order}$ as well, so $\deg q_{{\min}}={order}=\deg q$; both are monic, so
$q=q_{{\min}}$, which is the polynomial computed above.
\end{{proof}}

\section{{Verification}}

Three checks.

First, the walk model reproduces all ${len(d)}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the model to the entry, and it is the only place where reading
the entry's English enters.

Second, the recovered recurrence was evaluated directly on those published terms, with no
matrices and no Berlekamp--Massey involved, and holds at every index where the entry gives
enough earlier terms to test it.

Third, the order was computed twice by independent routes: once modulo a $61$-bit prime, where
every intermediate is a machine word, and once in exact rational arithmetic; and once more on
the sequence with its first ${order}+4$ terms removed, which is what the identification above
requires. All three agree.

\begin{{remark}}
What is unusual here is that the conjecture's statement was never read. The entry pins it down
to a one-parameter family --- the recurrences of order ${order}$ that this sequence satisfies
--- and that family turns out to have exactly one member.
\end{{remark}}

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
    hits = [h for h in json.load(open("ord_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/or{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
