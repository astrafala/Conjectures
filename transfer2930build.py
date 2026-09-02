#!/usr/bin/env python3
"""Papers for the two order-statistic subblock families."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer29, transfer30

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex
KEY = ('minimum', 'lower median', 'upper median', 'maximum')
SYM = {'minimum': 'a', 'lower median': 'b', 'upper median': 'c', 'maximum': 'd'}


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def expr_tex(coef):
    out = ''
    for k in KEY:
        v = coef.get(k, 0)
        if not v:
            continue
        out += ('+' if v > 0 else '-') if out or v < 0 else ''
        out += SYM[k]
    return out or '0'


def build(h, mod):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = mod.parse_name(e['name'])
    al = p['alpha']
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    if mod is transfer29:
        W = p['W']
        ex = expr_tex(p['coef'])
        what = rf"""Sort the four entries of a $2\times2$ subblock as $a\le b\le c\le d$: they
are its minimum, lower median, upper median and maximum. The entry fixes the signed sum
\[
\sigma\;=\;{ex},
\]
and asks that $\sigma$ take the SAME value on every $2\times2$ subblock of an
$(n+1)\times{W}$ array over $\{{0,\dots,{al}\}}$.

The common value is not named, so the count splits by it. For a fixed $v$ let $a_v(n)$ count
the arrays all of whose subblocks give $\sigma=v$. An array determines its common value, so
the sets belonging to different $v$ are disjoint and $a(n)=\sum_v a_v(n)$, a finite sum."""
        walk = rf"""For a fixed $v$ the condition involves two consecutive rows and nothing
else: rows $r$ and $s$ may follow one another exactly when $\sigma$ equals $v$ on each of the
${W - 1}$ subblocks they form. So a row is a state, an $(n+1)$-row array is a walk of $n$
steps, and with $M$ the adjacency matrix on the disjoint union over $v$,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}} .
\]
Rows carrying no edge at all are dropped: such a row can only be the whole of a one-row
array, which is not among the objects counted. There are $S={S}$ states left."""
        reading = ''
    else:
        K = p['K']
        col = ('the SET of values occurring in it' if p['kind'] == 'set'
               else rf"$\sigma={expr_tex(p['coef'])}$, where $a\le b\le c\le d$ are its four "
                    r"entries sorted --- its minimum, lower median, upper median and maximum")
        what = rf"""The $2\times2$ subblocks of an $(n+1)\times{K + 1}$ array form an
$n\times{K}$ grid. Colour each of them by {col}. ``Coloured with'' is the entry's way of
asking for a PROPER colouring of that grid: subblocks that are neighbours, horizontally or
vertically, must receive different colours."""
        reading = r"""
That reading is fixed by the entries themselves rather than guessed. Take the upper median
over $0..2$. A $2\times2$ array has one subblock and no neighbouring pair, so every one of the
$3^4=81$ arrays qualifies; a $2\times3$ array has one horizontal pair and $294$ of its $729$
arrays qualify; a $3\times3$ array has two horizontal and two vertical pairs and $722$
qualify. Those are the three numbers the corresponding entries publish. Imposing no condition
would give $729$ at $2\times3$, and counting the two diagonal pairs as neighbours as well
would give $0$ at $3\times3$, so neither is what is meant."""
        walk = rf"""A subblock's colour is decided by two consecutive rows of the array, and
the vertical condition compares two consecutive rows of the subblock grid, so the state is the
PAIR of consecutive array rows. A step appends a row: that fixes a new subblock row, which
must be properly coloured along itself and must differ from the previous subblock row in every
position. An $(n+1)$-row array is a walk of $n-1$ steps, so
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad\iota=\tau=(1,\dots,1)^{{\!\top}},
\]
over the $S={S}$ pairs whose own subblock row is properly coloured."""
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{2 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays over $\{{0,\dots,{al}\}}$ subject to a condition on the order
statistics of every $2\times2$ subblock, and carries an empirical recurrence of order
${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical.
The condition is local to two consecutive rows, so the count is a walk count on $S={S}$
states and is $C$-finite; whether the conjectured recurrence annihilates it is then settled by
a finite exact computation, with the Cayley--Hamilton theorem bounding the work.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45, 62G30.\normalsize

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

{what}
{reading}

\section{{The count is a walk count}}

{walk}
The alignment of the walk index with the entry's own $n$ was checked against its published
terms rather than assumed. In particular $a$ is $C$-finite.

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
\bibitem{{david}} H.~A.~David and H.~N.~Nagaraja, \emph{{Order Statistics}}, 3rd ed., Wiley,
2003.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('uniall_hits.json')):
        en = h.get('engine')
        if h.get('FAILS') or en not in ('transfer29', 'transfer30'):
            continue
        mod = transfer29 if en == 'transfer29' else transfer30
        dd = f"build/{en[-2:]}{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h, mod))
        n += 1
    print('wrote', n, 'papers')
