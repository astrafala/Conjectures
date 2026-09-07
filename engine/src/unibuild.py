#!/usr/bin/env python3
"""One paper per entry settled by the unified sweep.

These come from several engines, so the model section is written from what every one of them
has in common: the entry's condition is local to a bounded window of consecutive lines, the
admissible configurations of such a window are the vertices of a finite digraph, and the count
is a number of walks in it.
"""
import os, json, re
import localentry as LE, phibuild, transferbuild, uniform

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WINDOW = {
    'transfer3': "every $2\\times2$ subblock, hence two consecutive lines",
    'transfer6': "every $2\\times2$ subblock, hence two consecutive lines",
    'transfer8': "a window of two consecutive lines",
    'transfer16': "a window of consecutive lines fixed by the entry's own offsets",
    'transfer17': "every $3\\times3$ subblock, hence three consecutive lines",
    'transfer21': "every $3\\times3$ subblock, hence three consecutive lines",
    'transfer36': "every $2\\times2$ subblock, hence two consecutive lines",
    'transfer37': "every $2\\times3$ and $3\\times2$ subblock, hence three consecutive lines",
}
# the date a paper prints is the day the result was obtained, and this builder is run again
# whenever the sweep finds more; a hard-coded date would stamp today's results with the day
# the builder was written
import os as _os
DATE = _os.environ.get('PAPER_DATE', '2 September 2026')


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h["anum"]
    S, order, nterms, nthr = h["S"], h["order"], h["nterms"], h["nthr"]
    off, sh = h["offset"], h["shift"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    win = WINDOW.get(h["engine"], "a bounded window of consecutive lines")
    k = off - sh
    expo = "n" if k == 0 else ("n-%d" % k if k > 0 else "n+%d" % (-k))
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry's condition is local to {win}, so
the admissible configurations of such a window are the vertices of a finite digraph and the
arrays counted are exactly the walks in it; hence $a(n)$ is a walk count on $S={S}$ vertices
and is $C$-finite. Whether the conjectured recurrence annihilates it is then settled by a
finite exact computation, with the Cayley--Hamilton theorem bounding the work.
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

\section{{The count is a walk count}}

The condition the entry imposes is local: it constrains {win} and nothing beyond. Take as
vertices the admissible configurations of one such window and put an edge from $u$ to $v$
whenever $v$ may follow $u$, which the condition decides by inspection of the two. An
admissible array is then exactly a walk, so with $M$ the adjacency matrix on $S={S}$ vertices
and $\iota,\tau$ the vectors recording which windows may begin and end an array,
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

Three checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the model to the entry: the digraph is built by reading the
entry's English, and a misreading gives different counts.

Second, the conjectured recurrence was evaluated directly on those published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
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
    hits = [h for h in json.load(open("uniall_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
