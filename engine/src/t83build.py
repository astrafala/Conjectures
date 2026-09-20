#!/usr/bin/env python3
"""One paper per entry settled by transfer83.

What these have in common is a condition on every subblock, or on every pair of neighbouring
subblocks, and what differs is the condition, the shape and --- for a few of them --- a
scaling factor in front of the count. The general builder would describe all of that as "a
bounded window of consecutive lines", which is true but says nothing about the entry in
hand, and would drop the scaling factor entirely.
"""
import conjquote
import json
import os
import re

import localentry as LE
import phibuild
import transfer83
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}


DIRNAME = {(0, -1): 'W', (0, 1): 'E', (-1, 0): 'N', (1, 0): 'S',
           (-1, -1): 'NW', (-1, 1): 'NE', (1, -1): 'SW', (1, 1): 'SE'}


def dirs_text(ds):
    ds = [tuple(d) for d in ds]
    if len(ds) == 8:
        return "its eight king-move neighbours"
    named = {'horizontal': {(0, -1), (0, 1)}, 'vertical': {(-1, 0), (1, 0)},
             'diagonal': {(-1, -1), (1, 1)}, 'antidiagonal': {(-1, 1), (1, -1)}}
    parts = [k for k, v in named.items() if v <= set(ds)]
    if parts and set().union(*[named[k] for k in parts]) == set(ds):
        return "its " + " and ".join(parts) + " neighbours"
    return "its neighbours to the " + ", ".join(DIRNAME[d] for d in ds)


def cond_text(p):
    kind = p['kind']
    if kind == 'cmp':
        rel, join = (("the same number", "as") if p['eq']
                     else ("a different number", "than"))
        return (rf"every element must equal {rel} of {dirs_text(p['d1'])} {join} it does of "
                rf"{dirs_text(p['d2'])}")
    if kind == 'countne':
        return (rf"no element may equal exactly ${p['val']}$ of {dirs_text(p['dirs'])}")
    if kind == 'target':
        c = p['cnt']
        n = ("$%d$" % c[0] if len(c) == 1 else
             ", ".join("$%d$" % x for x in c[:-1]) + " or $%d$" % c[-1])
        return (rf"every entry equal to ${p['cell']}$ must have exactly {n} of "
                rf"{dirs_text(p['dirs'])} equal to ${p['want']}$")
    return (rf"every entry equal to ${p['cell']}$ must have at least one of "
            rf"{dirs_text(p['dirs'])} equal to it")


def model_section(p, S, expo):
    L, k = p['L'], p['k']
    walk = 'column' if p['transposed'] else 'row'
    fixed = 'rows' if p['transposed'] else 'columns'
    alpha = (r'\{' + ','.join(str(i) for i in range(k)) + r'\}' if k <= 4
             else r'\{0,1,\dots,%d\}' % (k - 1))
    L1 = [r"\section{The count is a walk count}", "",
          rf"The entry counts arrays with ${L}$ {fixed} over the alphabet ${alpha}$, growing "
          rf"one {walk} at a time. Its condition is that {cond_text(p)}.",
          "",
          rf"Every cell named there lies at most one step away, so three consecutive {walk}s "
          rf"decide the condition on the middle one completely. Carry two consecutive "
          rf"{walk}s as the state; when a new {walk} arrives, the {walk} it follows has all "
          rf"its neighbours present and is tested then, and the {walk} with nothing after it "
          rf"is tested by the end vector. That is also where the boundary is honest: a cell "
          rf"in the first {walk} has nothing before it and a cell in the last has nothing "
          rf"after it, and a missing neighbour is not a neighbour rather than a wrapped-round "
          rf"one."]
    if p['canon']:
        L1 += ["", rf"The entry also asks that new values be introduced in row major order, "
                   rf"which is not a condition on any window: whether a value may appear here "
                   rf"depends on the whole prefix. It enters through one integer all the same "
                   rf"--- how many values have been introduced so far --- because a {walk} may "
                   rf"follow precisely when each of its entries is at most that count at the "
                   rf"moment it is read, and an entry equal to it raises it by one. The effect "
                   rf"is that each array is counted once for the whole class of arrays "
                   rf"differing from it only by renaming the values."]
    L1 += ["", rf"Vertices with identical futures are merged, which leaves $S={S}$. An "
               rf"admissible array is exactly a walk, so with $M$ the adjacency matrix and "
               rf"$\iota,\tau$ the vectors recording which states may begin and end an array,"]
    return "\n".join(L1)


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def build(h):
    a = h["anum"]
    S, order, nterms, nthr = h["S"], h["order"], h["nterms"], h["nthr"]
    off, sh = h["offset"], h["shift"]
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h["coeffs"].items()}
    p = transfer83.parse_name(e['name'])
    kk = off - sh
    expo = "n" if kk == 0 else ("n-%d" % kk if kk > 0 else "n+%d" % (-kk))
    frac = p['frac']
    scale = ""
    if frac != 1:
        scale = (rf" The entry does not count the arrays themselves but $1/{frac}$ of them, "
                 rf"so every count below is divided by ${frac}$; the division is exact at "
                 rf"every term, which is itself a check on the model.")
    pref = ('\\tfrac{1}{%d}\\,' % frac) if frac != 1 else ''
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        j = nthr - off
        if d[j] != sum(int(c) * d[j - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{A condition on each element and its neighbours: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry's condition names only cells one step apart, so it is decided by a window of
three consecutive lines; the
admissible windows are the vertices of a finite digraph and the arrays counted are exactly the
walks in it. Hence $a(n)$ is a walk count on $S={S}$ vertices and is $C$-finite, and whether the
conjectured recurrence annihilates it is settled by a finite exact computation, with the
Cayley--Hamilton theorem bounding the work.{scale}
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

{model_section(p, S, expo)}
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

Second, the reading was pinned before the digraph was written, by a program that enumerates
every array of the given shape one by one and tests the entry's condition at each cell
directly. That program shares no code with the transfer matrix, so an error in one does not
hide an error in the other.

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
            if h.get("engine") == "transfer83" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
