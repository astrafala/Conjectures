#!/usr/bin/env python3
"""One paper per Hardin entry counting grid permutations with a bounded index change."""
import os, json, re
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h["anum"]
    W, S, R = h["fixed"], h["S"], h["R"]
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, off = h["base"], h["offset"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    A = sorted(tuple(o) for o in h["allowed"])
    aset = ",\\ ".join("(%d,%d)" % o for o in A)
    line, lines = ("row", "rows") if rowwalk else ("column", "columns")
    k = off - h["shift"]
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
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the arrangements of $0,1,\dots,LW-1$ in a grid of $W={W}$ {lines} in which
every value moves from its home cell by an index change on a short list, and it carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. Such an arrangement is a perfect matching between cells and
values, and because a value's row moves by at most $R={R}$, the matching splits into
independent decisions {line} by {line}: after the cells of {lines} $0,\dots,i$ are filled,
every value whose home {line} is at most $i-R$ has been used, and only $2R$ home {lines} are
partly used. Carrying those as bitmasks makes the count a walk on $S={S}$ vertices, so it is
$C$-finite and the conjectured recurrence is decided by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A05, 05A15, 15A15.\normalsize

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

\section{{The object is a matching}}

The grid has $W={W}$ {lines} across and holds each of $0,1,\dots,LW-1$ exactly once. The value
$v$ has a HOME cell, namely its place in the plain row-major filling, and putting $v$ in cell
$(i,j)$ changes its index by $(i-h_i,\,j-h_j)$ where $(h_i,h_j)$ is that home cell. The entry
allows the index changes
\[
(i-h_i,\,j-h_j)\;\in\;\{{{aset}\}},
\]
the list being the entry's own, read with the sign convention its wording uses. An admissible
arrangement is therefore exactly a perfect matching in the bipartite graph joining each cell to
the values it may hold.

\section{{The matching is a walk}}

Let $R={R}$ be the largest $|i-h_i|$ on the list. A value whose home {line} is $h$ can only be
placed in {lines} $h-R,\dots,h+R$. So once the cells of {lines} $0,\dots,i$ are filled, every
value with home {line} at most $i-R$ has been used up, and the only home {lines} that can be
partly used are $i-R+1,\dots,i+R$ --- exactly $2R$ of them. Take as the state the tuple of
$2R$ bitmasks recording which values of those home {lines} are already placed. One step fills
the cells of one further {line}, drawing each of its $W$ values from a home {line} within $R$
and at an allowed column offset, and the home {line} that closes at that step must come out
full. Nonexistent home {lines} --- before the first and after the last --- are carried as
full, which makes the starting and accepting states the same one.

Hence $a$ is a walk count on $S={S}$ vertices,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,{expo}}}\tau ,
\]
the exponent fixed by the entry's own shape and checked against its published terms; in
particular $a$ is $C$-finite.

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $q(t)=t^{{{order}}}-\sum_i c_it^{{{order}-i}}$ be the characteristic polynomial of the
conjectured recurrence. The residual $a(n)-\sum_ic_ia(n-i)$ equals
$\iota^{{\!\top}}M^{{\,j}}q(M)\tau$ for the corresponding walk index $j$, so the recurrence
holds from some point on if and only if $\iota^{{\!\top}}M^{{j}}q(M)\tau=0$ for all large $j$;
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
until the working vector was identically zero, settling every larger $j$ at once.{tight}
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, before any of this was built the reading of the entry's wording was tested against the
entries themselves by brute force: enumerating all $720$ arrangements of a $2\times3$ grid
gives $20$, the first term of A263960, and the $3\times2$ grid gives $9$, the first term of its
transposed companion A263966. Second, the transfer model reproduces all ${nterms}$ terms this
entry publishes, exactly, in integer arithmetic. That check earned its keep: the entries use
two different sign conventions, ``$(\pm,\pm)$ $a,b$'' meaning each coordinate signed
independently and ``$\pm(.,.)$ $a,b$'' meaning the PAIR signed, where the second coordinate may
itself be written negative. Reading the second as the first silently drops a displacement, and
thirteen of the first twenty-three entries tested disagreed with their own data until the two
were separated.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{lp}} L.~Lov\'asz and M.~D.~Plummer, \emph{{Matching Theory}}, AMS Chelsea, 2009.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("transfer22_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t22{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
