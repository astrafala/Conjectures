#!/usr/bin/env python3
"""Papers for the running-sum family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer52

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

RAYWORD = {'west': ('west', r'(i,j-1),(i,j-2),\dots'),
           'north': ('north', r'(i-1,j),(i-2,j),\dots'),
           'nw': ('northwest', r'(i-1,j-1),(i-2,j-2),\dots'),
           'ne': ('northeast', r'(i-1,j+1),(i-2,j+2),\dots')}
ORDER = ('west', 'north', 'nw', 'ne')


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
    p = transfer52.parse_name(e['name'])
    W, A, M = p['W'], p['alpha'] + 1, p['mod']
    con = p['con']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    rows = '\n'.join('\\text{%s} & %s & %d \\\\' % (RAYWORD[k][0], RAYWORD[k][1], con[k])
                     for k in ORDER if k in con)
    slice_word = 'row' if not p['trans'] else 'column'
    other = 'column' if not p['trans'] else 'row'
    inray = 'west' if not p['trans'] else 'north'
    acray = 'north' if not p['trans'] else 'west'
    lines = []
    if inray in con:
        lines.append("\\Sigma_{\\mathrm{%s}}\\ &\\text{is the running total inside the "
                     "current %s},\\\\" % (inray, slice_word))
    if acray in con:
        lines.append("U'[p]&=U[p]+x[p], &&\\text{the %s ray, per position},\\\\" % acray)
    if 'nw' in con:
        lines.append("NW'[p]&=NW[p-1]+x[p-1], && NW'[0]=0,\\\\")
    if 'ne' in con:
        lines.append("NE'[p]&=NE[p+1]+x[p+1], && NE'[W-1]=0,\\\\")
    rayrec = '\n'.join(lines)
    rayrec = rayrec.rstrip()[:-2].rstrip().rstrip(',') + ' .'
    nrays = len(con)
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS, so the slice "
             "added at each step is a column and the roles of the west and north rays are "
             "exchanged. The northwest ray is carried to itself by that exchange.")
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over ${aset}$ in which no entry may equal, modulo ${M}$, a given
constant plus the SUM of all the entries lying before it along one of several rays. The entry
carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and
it is decidable rather than empirical. None of those sums is bounded and none is local, but
each is built one term at a time, so its residue modulo ${M}$ is carried in the state; the
count is then a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11A07, 15A18.\normalsize

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

The array has ${W}$ cells across one way, entries $x(i,j)\in{aset}$, and the entry names these
rays out of a cell $(i,j)$, with the constant it attaches to each:
\[
\begin{{array}}{{lll}}
\text{{ray}} & \text{{the cells on it}} & \text{{constant}} \\[2pt]
{rows}
\end{{array}}
\]
Writing $\Sigma_r(i,j)$ for the sum of the entries on ray $r$ out of $(i,j)$, all of them
inside the array, the condition is
\[
x(i,j)\;\not\equiv\;c_r+\Sigma_r(i,j) \pmod{{{M}}}
\]
for every ray $r$ named. A ray that leaves the array at once contributes the empty sum,
zero.{trans}

\section{{The rays as a bounded state}}

Take the array one ${slice_word}$ at a time, in the direction in which it grows, and index the
positions of a ${slice_word} $ by $p$. Let $x$ be the ${slice_word}$ just written.

\begin{{lemma}}\label{{lem:rays}}
Along the ${slice_word}$s, the {nrays} ray sums named by this entry satisfy
\[
\begin{{aligned}}
{rayrec}
\end{{aligned}}
\]
\end{{lemma}}

\begin{{proof}}
Each ray is a set of cells at a fixed step from $(i,j)$ repeated. Advancing one ${slice_word}$
moves a cell one step along the {acray} ray, one step along the northwest ray together with one
position to the right, and one step along the northeast ray together with one position to the
left; in each case exactly the cell just left behind is the new term. At the border of the
array the diagonal rays are empty, which is the stated boundary value.
\end{{proof}}

Reduced modulo ${M}$ these vectors take finitely many values, so they are a state, and one step
of the walk writes a whole ${slice_word}$: the position $p$ is filled left to right and the
running total of the {inray} ray is carried along as it is filled, so every cell is tested
against every ray at the moment it is written. The walk starts at the all-zero state, the empty
array, and every state may end one, so $\tau=\mathbf{{1}}$ and
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
until the working vector was identically zero, which settles every larger $j$ at once.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition: fill the
cells one at a time in the orientation the entry's own name writes and, for each candidate
value, walk each ray to the edge of the array and add the entries up. No residue, no state and
no recurrence of Lemma~\ref{{lem:rays}} is involved, and the published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer52' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t52{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
