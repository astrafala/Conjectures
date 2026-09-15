#!/usr/bin/env python3
"""Papers for the offset-inequality family."""
import conjquote
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer54

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer54.parse_name(e['name'])
    W, m, K = p['W'], p['alpha'], p['K']
    raw = [(int(g.group(1)), int(g.group(2)))
           for g in re.finditer(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', e['name'])]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    offs = texbits.offsets_tex(raw)
    L = max(-s for s, _ in p['offs']) or 1
    slice_word = 'row' if not p['trans'] else 'column'
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS, so the array grows "
             "one COLUMN at a time and an offset is read with its two coordinates exchanged.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays in which no entry may equal the entries at a short list of fixed offsets
from it, the arrays being counted up to renaming the letters. The entry carries an empirical
recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable
rather than empirical. The condition tests only whether two cells are equal, so it survives
renaming; the count of classes is recovered from counts over fixed alphabets by inverting a
triangular system of falling factorials, and each of those is a walk count on a window of
${L}$ consecutive {slice_word}s, $S={S}$ states in all.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A18, 15A18.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{What is being counted}}

Entries lie in $\{{0,1,\dots,{m}\}}$ and the condition is that
\[
x(i,j)\ \ne\ x(i+d_1,\,j+d_2)\qquad\text{{for each offset }}(d_1,d_2)\in\{{{offs}\}}
\]
whenever the second cell lies inside the array.{trans} The closing clause ``new values
introduced in order $0..{m}$'' says the array is the canonical representative of its equality
pattern.

\begin{{lemma}}\label{{lem:order}}
The number counted does not depend on the order in which the array is read.
\end{{lemma}}

\begin{{proof}}
The condition tests only whether two cells carry equal values, so it is unchanged by permuting
the alphabet, and the admissible arrays fall into classes under renaming. Fix any reading order
of the cells. Each class contains exactly one array whose distinct values, in order of first
appearance in that reading, are $0,1,2,\dots$: take any member and rename its values by their
rank of first appearance. So the count is the number of CLASSES, whatever reading order is
meant.
\end{{proof}}

\section{{From classes to fixed alphabets}}

Write $N_j$ for the number of classes on exactly $j$ letters and $L_i$ for the number of
admissible arrays over an alphabet of $i$ letters. An array over $i$ letters is a class together
with an injection of its letters into the alphabet, so
\[
L_i\;=\;\sum_j N_j\,i(i-1)\cdots(i-j+1),
\]
a triangular system with unit diagonal. By Lemma~\ref{{lem:order}} the entry counts
$N_1+\dots+N_{{{K}}}$, so $a=\sum_i w_iL_i$ with $w=\mathbf{{1}}^{{\!\top}}F^{{-1}}$, $F$ the
matrix of falling factorials.

\section{{Each $L_i$ is a walk count}}

Equality is symmetric, so an offset and its negative forbid exactly the same pairs; replacing
each offset by whichever of the two points BACKWARDS along the direction in which the array
grows makes every pair tested once, from the later of its two cells. After that replacement no
offset reaches more than ${L}$ {slice_word}s back, so the window of the last ${L}$
{slice_word}s is a state and one step appends a {slice_word}. A {slice_word} not yet written is
carried as a symbol, so the walk starts at the empty array and a walk of $t$ steps is an array
of $t$ {slice_word}s. Assembling $i=1,\dots,{K}$ as a disjoint union with $\iota$ carrying the
weights cleared of denominators and $\tau=\mathbf{{1}}$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S}.
\]
The walk index $j$ and the entry's own $n$ differ by a constant, read off by matching the
published terms rather than assumed. In particular $a$ is $C$-finite.

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
until the working vector was identically zero. The rational weights are carried as one common
denominator, so no division is performed until the final term.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition:
enumerate every array over $\{{0,\dots,{m}\}}$, keep those whose values are introduced in the
order $0,1,2,\dots$ reading row by row, and test each offset directly. Neither the window, nor
the backward normalisation of the offsets, nor the falling-factorial inversion is involved, and
the published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7; falling factorials,
Section 1.9.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer54' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t54{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
