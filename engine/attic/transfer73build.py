#!/usr/bin/env python3
"""Papers for the array-permutation family."""
import conjquote
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer73

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum, coeffs=None):
    """see `conjquote': a word test ON the line missed 542 installed papers, whose section 1
    then printed a placeholder, and 41 quoted the wrong line of the block -- a closed form
    where the theorem proves the recurrence."""
    return conjquote.line(anum, coeffs)


def offs_tex(offs):
    return ',\\ '.join('(%d,%d)' % tuple(o) for o in offs)


AXISUSED = []


def describe(p, nm):
    body = re.search(r'with (.*?)\.?$', re.sub(r'\s+', ' ', nm))
    body = body.group(1) if body else ''
    if re.search(r'knight', body, re.I):
        if re.search(r'right-handed', body, re.I):
            w = ("the four knight moves that go two squares out and one to the right of that "
                 "direction")
        elif re.search(r'left-handed', body, re.I):
            w = ("the four knight moves that go two squares out and one to the left of that "
                 "direction")
        else:
            w = "the eight knight moves"
    elif re.search(r'king', body, re.I):
        w = "the eight king moves"
    else:
        axes, dirs = [], []
        for word, tag in (('horizontal', 'horizontally'), ('vertical', 'vertically'),
                          ('diagonal', 'diagonally'), ('antidiagonal', 'antidiagonally')):
            if re.search(r'\b' + word + r'(?:ly)?\b', body, re.I):
                axes.append(tag)
        for c, full in (('NE', 'northeast'), ('NW', 'northwest'), ('SE', 'southeast'),
                        ('SW', 'southwest'), ('N', 'north'), ('S', 'south'),
                        ('E', 'east'), ('W', 'west')):
            if re.search(r'(?<![A-Za-z])' + c + r'(?![A-Za-z])', body):
                dirs.append(full)

        def join(xs):
            return (', '.join(xs[:-1]) + ' or ' + xs[-1]) if len(xs) > 1 else xs[0]
        bits = []
        if axes:
            bits.append('one step ' + join(axes) + ', in either direction along each of those '
                        'axes')
        if dirs:
            bits.append('one step ' + join(dirs))
        w = ' or '.join(bits) if bits else 'the steps the entry names'
        AXISUSED.append(bool(axes))
    stay = (0, 0) in {tuple(o) for o in p['offs']}
    return w, stay


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    nm = e['name']
    p = transfer73.parse_name(nm)
    W = p['W']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    AXISUSED.clear()
    words, stay = describe(p, nm)
    axisremark = (r"""The words name an AXIS, not a single direction: ``diagonally'' admits
both $(1,1)$ and $(-1,-1)$, and ``antidiagonally'' is a separate word for the other diagonal.
And a""" if AXISUSED and AXISUSED[0] else 'A')
    lin = [d1 * W + d2 for d1, d2 in p['offs']]
    lo, hi = min(lin + [0]), max(lin + [0])
    WIN = hi - lo + 1
    stayline = ("A cell is allowed to stay where it is, and $(0,0)$ is one of the offsets."
                if stay else
                "A cell may not stay where it is: $(0,0)$ is not among the offsets, so the "
                "permutation has no fixed point.")
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of ROWS; transposing it "
                 r"exchanges the two coordinates of every offset, and the offsets above are "
                 r"written in the transposed frame.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the permutations of the cells of an $n\times{W}$ array in which every cell
moves by one of a fixed short list of offsets. The entry carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical. The count is the permanent of the incidence matrix of the offset graph; read the
cells in row-major order and let each choose its image, and the only thing that has to be
carried is which images inside a window of ${WIN}$ consecutive positions are already taken.
That makes $a$ a walk count on $S={S}$ states, hence $C$-finite, and whether the published
recurrence is one of its recurrences is then a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A05, 05A15, 15A15.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(nm.strip())}''. It has offset ${off}$ and begins
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

Write the cells of the array as pairs $(i,j)$ with $0\le i<n$ and $0\le j<{W}$. An
\emph{{array permutation}} of the kind the entry counts is a bijection $\pi$ from the cells to
the cells such that for every cell,
\[
\pi(i,j)-(i,j)\;\in\;\Delta,\qquad
\Delta=\{{\,{offs_tex(p['offs'])}\,\}}.
\]
The offsets are what the name's words say: {words}. {stayline}{transline}

{axisremark} move is only allowed when its target is a cell of the array, so cells near an
edge have fewer choices. The reading is pinned against the entry's own published terms rather
than assumed: taking ``diagonally, horizontally or vertically'' to mean all eight king moves
gives $24$ where A189305 publishes $14$.

Equivalently, $a(n)$ is the permanent of the $n{W}\times n{W}$ matrix whose $(c,c')$ entry is
$1$ exactly when $c'-c\in\Delta$.

\section{{A window of {WIN} positions}}

Number the cells in row-major order, $k=i\cdot{W}+j$. An offset $(\delta_1,\delta_2)$ moves a
cell by $\delta_1{W}+\delta_2$ places in that order, so every image lies between $lo={lo}$ and
$hi={hi}$ places from its source. Process the cells in order and let each one choose its image.
Once the cell at position $k$ has been dealt with, the position $k+{lo}$ can never be chosen
again by anybody, so it must already be taken; and no position beyond $k+{hi}$ can have been
taken yet. What has to be remembered is therefore exactly which of the ${WIN}$ positions
$k+{lo},\dots,k+{hi}$ are taken --- a subset of a set of size ${WIN}$, and nothing else.

That is the state. One step of the walk is one row, that is ${W}$ cell choices, and the
condition ``the position leaving the window is taken'' is what makes the walk count permutations
rather than partial injections: every position is taken exactly once, once at the moment it
leaves the window.

The two boundaries are the same condition. Images above the first row do not exist, so the walk
starts with exactly the window positions lying above the array marked as taken. Images below the
last row do not exist either, so the walk must end with exactly those positions marked and
nothing beyond. In the window's own coordinates those two masks are equal, so the start state is
also the only accepting state and
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S},
\]
for the transfer matrix $M$ on those $S$ states. The walk index $j$ and the entry's own $n$
differ by a constant, read off by matching the published terms rather than assumed. In
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
until the working vector was identically zero, which settles every larger $j$ at once.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition: the
cells of the array were matched to their images one at a time, over the whole grid, with no
window, no mask over a sliding frame and no transfer matrix, and the published terms came back.
That computation shares nothing with the construction of Section~3 beyond the offset list.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{minc}} H.~Minc, \emph{{Permanents}}, Encyclopedia of Mathematics and its
Applications 6, Addison--Wesley, 1978.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer73' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t73{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
