#!/usr/bin/env python3
"""One paper per entry settled by transfer93.

What these entries share is that the condition on a subblock depends only on the multiset of
its entries; what differs is which function of that multiset, the block's shape, and the
scaling factor in front of the count. The general builder would call all of it "a bounded
window of consecutive lines" and would drop the scaling factor, so the condition is written
out here in the entry's own terms.
"""
import json
import os
import re

import localentry as LE
import phibuild
import transfer93
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex
WORD = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
        8: 'eight', 9: 'nine'}


def cond_text(p):
    kind, val, h, w = p['kind'], p['val'], p['h'], p['w']
    B = rf"${h}\times{w}$ subblock"
    if kind == 'median':
        rel = 'equal' if p['rel'] == 'equal' else 'different'
        return (rf"in every {B} the two middle order statistics are {rel}: writing the "
                rf"${h*w}$ entries of the block in nondecreasing order $v_1\le\cdots\le "
                rf"v_{{{h*w}}}$, the lower median is $v_{{{h*w//2}}}$ and the upper median "
                rf"$v_{{{h*w//2+1}}}$, and these must be "
                + ("equal" if p['rel'] == 'equal' else "unequal"))
    if kind in ('distinct', 'allvals'):
        return rf"every {B} holds exactly ${val}$ distinct values"
    if kind == 'ones_ne':
        return rf"no {B} holds exactly ${val}$ entries equal to $1$"
    if kind == 'ones_ge':
        return rf"every {B} holds at least ${val}$ entries equal to $1$"
    return (rf"the multiplicities of the values in every {B}, sorted, are "
            rf"$({', '.join(str(v) for v in val)})$")


def model_section(p, S):
    L, k, h, w = p['L'], p['k'], p['h'], p['w']
    walk = 'column' if p['transposed'] else 'row'
    fixed = ('rows' if p['transposed'] else 'columns') if L != 1 else \
            ('row' if p['transposed'] else 'column')
    dep = w if p['transposed'] else h
    alpha = r'\{' + ','.join(str(i) for i in range(k)) + r'\}'
    out = [r"\section{The count is a walk count}", "",
           rf"The entry counts arrays with ${L}$ {fixed} over the alphabet ${alpha}$, growing "
           rf"one {walk} at a time, and asks that {cond_text(p)}.",
           "",
           rf"That condition does not depend on where in the block a value sits, only on "
           rf"which values the block holds and how many times --- it is a function of the "
           rf"block's multiset of entries. In particular it is decided by ${dep}$ consecutive "
           rf"{walk}s, the ones the block spans, so carrying the previous ${dep-1}$ "
           + ("them" if dep - 1 == 0 else f"{walk}" + ("s" if dep - 1 != 1 else "")) +
           rf" as the state is enough: each new {walk} completes every block that ends on it, "
           rf"and no judgement is left over at the end of the array."]
    if p['frac'] != 1:
        out += ["", rf"The entry counts not the arrays themselves but $1/{p['frac']}$ of "
                    rf"them, so every count below is divided by ${p['frac']}$; the division "
                    rf"comes out exact at every term the entry publishes, which is itself a "
                    rf"check on the model."]
    out += ["", rf"Merging vertices with identical futures leaves $S={S}$. An admissible "
                rf"array is exactly a walk, so with $M$ the adjacency matrix and "
                rf"$\iota,\tau$ the vectors recording which states may begin and end an "
                rf"array,"]
    return "\n".join(out)


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
    p = transfer93.parse_name(e['name'])
    kk = off - sh
    expo = "n" if kk == 0 else ("n-%d" % kk if kk > 0 else "n+%d" % (-kk))
    frac = p['frac']
    scale = ""
    if frac != 1:
        scale = (rf" The entry does not count the arrays themselves but $1/{frac}$ of them, "
                 rf"so every count below is divided by ${frac}$.")
    pref = ('\\tfrac{1}{%d}\\,' % frac) if frac != 1 else ''
    tight = ""
    if off <= nthr - order and nthr - off < len(d):
        j = nthr - off
        if d[j] != sum(int(c) * d[j - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{A condition on the multiset of every subblock: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{7 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is
true, and it is decidable rather than empirical. The entry's condition on a subblock depends
only on which values the block holds and how many times, not on where they sit, so it is
decided by the few consecutive lines the block spans. The admissible windows are the vertices
of a finite digraph and the arrays counted are exactly its walks; hence $a(n)$ is a walk count
on $S={S}$ vertices and is $C$-finite, and whether the conjectured recurrence annihilates it
is settled by a finite exact computation, with the Cayley--Hamilton theorem bounding the
work.{scale}
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

{model_section(p, S)}
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
every array of the given shape one by one, forms each subblock directly and tests the entry's
condition on it. That program shares no code with the transfer matrix, so an error in one does
not hide an error in the other.

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
            if h.get("engine") == "transfer93" and not h.get("FAILS")]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
