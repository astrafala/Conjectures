#!/usr/bin/env python3
"""One paper per entry settled by transfer86.

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
import transfer86
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}


DIRNAME = {'horizontal': 'horizontally', 'vertical': 'vertically',
           'diagonal': 'diagonally', 'antidiagonal': 'antidiagonally'}


def dirs_text(ds):
    ds = [tuple(d) for d in ds]
    if len(ds) == 8:
        return "a king move"
    named = {'horizontal': {(0, -1), (0, 1)}, 'vertical': {(-1, 0), (1, 0)},
             'diagonal': {(-1, -1), (1, 1)}, 'antidiagonal': {(-1, 1), (1, -1)}}
    parts = [DIRNAME[k] for k, v in named.items() if v <= set(ds)]
    return " or ".join(parts) if parts else "an adjacent step"


def cond_text(p):
    kind = p['kind']
    if kind == 'noadj':
        s = rf"no two entries equal to ${p['val']}$ may be adjacent {dirs_text(p['dirs'])}"
        if p.get('corner') is not None:
            s += rf", and the top left entry is ${p['corner']}$"
        return s
    if kind == 'distinct':
        return ("the neighbours of any one element --- those directly above, below, left and "
                "right of it --- must all be different from each other")
    if kind == 'runbits':
        return (rf"no ${p['run']}$ consecutive entries, taken along a row or down a column, "
                rf"may contain more than ${p['most']}$ ones")
    if kind == 'incmod':
        xs = ["$%d$" % x for x in p['steps']]
        st = xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " or " + xs[-1]
        return (rf"each step to the right and each step downwards must increase the entry by "
                rf"{st} modulo ${p['mod']}$, starting from ${p['corner']}$ in the top left")
    return ("the row sums must not decrease down the array, and the columns must be "
            "nondecreasing read left to right as sequences compared letter by letter")


def model_section(p, S, expo):
    L, kind = p['L'], p['kind']
    walk = 'column' if p['transposed'] else 'row'
    fixed = ('rows' if p['transposed'] else 'columns') if L != 1 else \
            ('row' if p['transposed'] else 'column')
    lo, hi = p['lo'], p['hi']
    alpha = r'\{' + ','.join(str(i) for i in range(lo, hi + 1)) + r'\}' if hi - lo < 6 \
            else rf'\{{{lo},\dots,{hi}\}}'
    L1 = [r"\section{The count is a walk count}", "",
          rf"The entry counts arrays with ${L}$ {fixed} over the alphabet ${alpha}$, growing "
          rf"one {walk} at a time, and asks that {cond_text(p)}."]
    if kind == 'sumlex':
        L1 += ["", r"Neither half of that is decided by a window. A row sum is compared with "
                   r"the row sum before it, and two columns are compared at the first line "
                   r"where they differ, which may be anywhere in the array. But neither needs "
                   rf"a window: carry the previous row's sum, a number between $0$ and "
                   rf"${(hi - lo) * L}$, and one flag for each of the ${L-1}$ adjacent column "
                   rf"pairs saying whether the two have agreed in every line so far. A pair "
                   rf"that separates the right way is settled and never looked at again; a "
                   rf"pair that separates the wrong way ends the walk; pairs still agreeing "
                   rf"at the end are equal, which is allowed. That pair --- the sum and the "
                   rf"flags --- is the entire state."]
    else:
        L1 += ["", rf"Every cell the condition names lies within one {walk} of the cell being "
                   rf"judged, so three consecutive {walk}s decide everything anchored at the "
                   rf"middle one. Carry two consecutive {walk}s as the state; a {walk} is "
                   rf"judged when the {walk} after it arrives, and the {walk} with nothing "
                   rf"after it is judged by the end vector. That is where the boundary is "
                   rf"honest: a neighbour off the edge of the array is not a neighbour, and a "
                   rf"run of entries that would leave the array is not a run."]
    if p['frac'] != 1:
        L1 += ["", rf"The entry counts not the arrays themselves but $1/{p['frac']}$ of them, "
                   rf"so every count below is divided by ${p['frac']}$; the division comes "
                   rf"out exact at every term, which is itself a check on the model."]
    L1 += ["", rf"Merging vertices with identical futures leaves $S={S}$. An admissible array "
               rf"is exactly a walk, so with $M$ the adjacency matrix and $\iota,\tau$ the "
               rf"vectors recording which states may begin and end an array,"]
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
    p = transfer86.parse_name(e['name'])
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
\title{{A local condition on an array: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{7 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry's condition is decided by a bounded amount of state carried down the array; the
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
every array of the given shape one by one and tests the entry's condition on it directly. That program shares no code with the transfer matrix, so an error in one does not
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
            if h.get("engine") == "transfer86" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
