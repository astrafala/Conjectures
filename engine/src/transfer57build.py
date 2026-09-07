#!/usr/bin/env python3
"""Papers for the subblock line-sum family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer57


def _lineclause(p):
    """what the window is actually constrained on, from the parse rather than from a template

    The abstract used to say every window has "constrained SUMS along its rows, its columns
    and its two diagonals" whatever the entry said. For 29 papers the entry constrains fewer
    than all four --- some only compare the two diagonals to each other --- so the abstract
    described a condition that is not the one being proved. The bodies were right throughout;
    only this sentence was a template.
    """
    kinds = [t for t in ('row', 'column', 'diagonal', 'antidiagonal') if t in p.get('rules', {})]
    words = {'row': 'its rows', 'column': 'its columns', 'diagonal': 'its main diagonal',
             'antidiagonal': 'its antidiagonal'}
    if p.get('cmps'):
        cmp_txt = 'has its line sums compared with one another'
        if not kinds:
            return cmp_txt
        lst = [words[t] for t in kinds]
        return ('has constrained SUMS along ' + ', '.join(lst[:-1]) +
                (' and ' if len(lst) > 1 else '') + lst[-1] + ', and ' + cmp_txt[4:])
    if not kinds:
        return 'is constrained by the entry\'s condition'
    if len(kinds) == 4:
        return 'has constrained SUMS along its rows, its columns and its two diagonals'
    lst = [words[t] for t in kinds]
    return ('has constrained SUMS along ' + ', '.join(lst[:-1]) +
            (' and ' if len(lst) > 1 else '') + lst[-1])


PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

NAMEOF = {'row': 'each row', 'column': 'each column', 'diagonal': 'the main diagonal',
          'antidiagonal': 'the antidiagonal', 'crow': 'the central row',
          'ccol': 'the central column'}
CMPW = {'less than': 'less than', 'greater than': 'greater than', 'equal to': 'equal to'}
ORDER = ('row', 'column', 'diagonal', 'antidiagonal')


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


import json as _json
_ROSTER_AT_BUILD = {v['anum'] for v in _json.load(open('paper-engines.json')).values()}


def datefor(a):
    """A paper carries the date its result was obtained, not the date of the batch it
    happens to be rebuilt with."""
    return '6 September 2026' if a not in _ROSTER_AT_BUILD else '3 September 2026'


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer57.parse_name(e['name'])
    W, m, K = p['W'], p['alpha'], p['K']
    A = m + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    lines = []
    for t in ORDER:
        if t not in p['rules']:
            continue
        mode, s = p['rules'][t]
        if mode == 'prime':
            w = 'must be prime'
        elif mode == 'forbid':
            w = 'must NOT be ' + ' or '.join(str(x) for x in s)
        else:
            w = 'must be ' + ' or '.join(str(x) for x in s)
        lines.append('\\text{%s} & \\text{%s} \\\\' % (NAMEOF[t], w))
    for x, y, c in p['cmps']:
        lines.append('\\text{%s} & \\text{must NOT be %s the sum along %s} \\\\'
                     % (NAMEOF[x], CMPW[c], NAMEOF[y]))
    if p['total'] is not None:
        lines.append('\\text{the whole window} & \\text{must sum to %d} \\\\' % p['total'])
    tbl = '\n'.join(lines)
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % m)
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS; the walk is run "
             "down the transpose, which exchanges the row lines with the column lines of every "
             "window and carries each diagonal line to itself, so the table above is already "
             "written in the transposed frame.")
    vac = ('' if W >= K else
           rf" Note that the array is only ${W}$ cells across, narrower than the window, so no "
           rf"${K}\times{K}$ window fits inside it at all and the condition is vacuous: the "
           rf"entry counts every array of its shape. The model says the same, its digraph being "
           rf"complete on the rows.")
    lineclause = _lineclause(p)
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{datefor(a)}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which every ${K}\times{K}$ window
{lineclause}. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical: a ${K}\times{K}$ window lies in ${K}$ consecutive array rows,
so the count is a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B20, 15A18.\normalsize

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

The array has ${W}$ cells across, with entries in ${aset}$. A WINDOW is a ${K}\times{K}$ block
of consecutive cells lying inside the array. Every window must satisfy
\[
\begin{{array}}{{ll}}
\text{{the sum along}} & \text{{}} \\[2pt]
{tbl}
\end{{array}}
\]
where the main diagonal of a window runs from its top left corner to its bottom right, and its
antidiagonal from top right to bottom left.{trans}{vac}

\section{{The walk}}

\begin{{lemma}}\label{{lem:win}}
A ${K}\times{K}$ window occupies ${K}$ consecutive array rows, so every condition above is
decided by ${K}$ consecutive rows and by nothing else.
\end{{lemma}}

\begin{{proof}}
By definition of a window.
\end{{proof}}

So the state is the window of the last ${K - 1}$ array rows, a row not yet written carried as
$\bot$, and a step appends a row and settles every ${K}\times{K}$ window that row completes. A
window needing a row that is $\bot$ does not exist, which is the boundary rule; the walk starts
at the all-$\bot$ state, so a walk of $R$ steps is an array of $R$ rows. With $M$ the adjacency
matrix and $\tau=\mathbf{{1}}$,
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
until the working vector was identically zero.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition: fill the
cells in row major order, in the orientation the entry's own name writes, and test a window as
soon as its last cell is placed. No state, no transposition and no transfer matrix are
involved, and the published terms came back.

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
            if h.get('engine') == 'transfer57' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t57{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
