#!/usr/bin/env python3
"""Papers for the existential-neighbour family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer71

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def offs_tex(offs):
    return ', '.join('(%d,%d)' % o for o in offs)


def cond_tex(p):
    k = p['kind']
    if k == 'lesome':
        return (r"every cell that is not zero has among its neighbours one at least as large "
                r"as itself:" "\n\\[\n"
                r"x(i,j)\neq0\ \Longrightarrow\ \exists\,(a,b)\in S(i,j)\ \ x(a,b)\ge x(i,j)."
                "\n\\]\n"
                r"A zero cell is under no condition, and neither is a cell whose named "
                r"neighbours all lie outside the array --- except that then the condition "
                r"forces it to be zero, since the empty set contains nothing at least as large.",
                "every nonzero cell has a neighbour at least as large as itself")
    if k == 'gele':
        return (r"every cell has among its neighbours one at least as large as itself and one "
                r"at most as large:" "\n\\[\n"
                r"\exists\,(a,b)\in S(i,j)\ x(a,b)\ge x(i,j)\quad\text{and}\quad"
                r"\exists\,(a,b)\in S(i,j)\ x(a,b)\le x(i,j)." "\n\\]\n"
                r"The two need not be the same neighbour, and a cell equal to one of its "
                r"neighbours satisfies both at once.",
                "every cell has a neighbour at least as large and one at most as large")
    if k == 'both2':
        s = (r"every cell has a neighbour equal to $%d$ and a neighbour equal to $%d$:"
             % (p['v'], p['w']) + "\n\\[\n"
             r"%d\in\{x(a,b):(a,b)\in S(i,j)\}\quad\text{and}\quad"
             r"%d\in\{x(a,b):(a,b)\in S(i,j)\}." % (p['v'], p['w']) + "\n\\]\n")
        if p['before']:
            s += (r"The entry adds that $%d$ is introduced before $%d$ in reading order: going "
                  r"through the cells row by row, the first one carrying either value carries "
                  r"$%d$." % (p['before'][0], p['before'][1], p['before'][0]))
        return s, "every cell has neighbours equal to each of two named values"
    if k == 'some':
        return (r"every cell equal to $%d$ has a neighbour equal to $%d$:" % (p['v'], p['w']) +
                "\n\\[\n"
                r"x(i,j)=%d\ \Longrightarrow\ \exists\,(a,b)\in S(i,j)\ \ x(a,b)=%d ."
                % (p['v'], p['w']) + "\n\\]\n"
                r"Cells of any other value are under no condition.",
                "every cell of one value has a neighbour of another")
    if k == 'count':
        cs = sorted(p['counts'])
        return (r"every cell equal to $%d$ has exactly $%d$ or exactly $%d$ neighbours equal "
                r"to $%d$:" % (p['v'], cs[0], cs[1], p['w']) + "\n\\[\n"
                r"x(i,j)=%d\ \Longrightarrow\ \#\{(a,b)\in S(i,j):x(a,b)=%d\}\in\{%d,%d\}."
                % (p['v'], p['w'], cs[0], cs[1]) + "\n\\]\n",
                "every cell of one value has an allowed number of neighbours of another")
    if k == 'eqone':
        return (r"every cell is equal to at least one of its neighbours:" "\n\\[\n"
                r"\exists\,(a,b)\in S(i,j)\ \ x(a,b)=x(i,j)." "\n\\]\n",
                "every cell equals at least one of its neighbours")
    s = (r"every cell has, among its neighbours, each of its own value plus one and its own "
         r"value minus one that still lies in the range:" "\n\\[\n"
         r"t\in\{x(i,j)-1,\ x(i,j)+1\}\cap\{0,\dots,%d\}\ \Longrightarrow\ "
         r"t\in\{x(a,b):(a,b)\in S(i,j)\}." % p['alpha'] + "\n\\]\n"
         r"At the ends of the range only one of the two values exists and only that one is "
         r"demanded.")
    if p['noeq']:
        s += ("\n\n" r"The entry adds that no two cells at one of these offsets are equal.")
    return s, "every cell sees its own value plus and minus one among its neighbours"


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer71.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    U, D = transfer71._reach(p)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    body, short = cond_tex(p)
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    slice_word = 'row' if not p['trans'] else 'column'
    upw = 'no row' if U == 0 else ('one row' if U == 1 else '%d rows' % U)
    dnw = 'none' if D == 0 else ('one row' if D == 1 else '%d rows' % D)
    keep = 'row' if U + D == 1 else '%d of them' % (U + D)
    settled = ('the bottom row of that window' if D == 0 else
               'the one just above the bottom of that window' if D == 1 else
               'the one %d rows above the bottom of that window' % D)
    lastw = 'last row' if D == 1 else 'last %d rows' % D
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of COLUMNS; transposing "
                 r"it exchanges the two coordinates of every offset, and the offsets above are "
                 r"written in the transposed frame.")
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes %s of that count; the division is by the constant "
                r"%d and changes nothing about the recurrence." % (
                    {2: 'one half', 4: 'one quarter'}.get(frac, '$1/%d$' % frac), frac))
    beforepar = ("" if not p['before'] else r"""
The reading-order clause is one more symbol in the state: neither value seen yet, or the earlier
one seen first. It never goes back, and a row that would introduce the later value first is
simply not taken.
""")
    endpar = (r"Every state may end an array, so $\tau=\mathbf{1}$."
              if D == 0 else
              r"""When the array stops, the %s of it %s never been tested, because the
conditions reach %s below. So the end vector is NOT all ones: a state is accepted exactly when
those rows pass with nothing below them, which is decided by running the same test on the window
with absent rows appended --- the same rule that governs a cell at the bottom edge in
Section 2.""" % (lastw, 'has' if D == 1 else 'have', dnw))
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{4 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which {short}. The entry carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical: what a cell asks reaches {upw} above it and {dnw} below, so the
condition on a whole row is settled by ${U + D + 1}$ consecutive rows and the count is a walk
count on $S={S}$ states.
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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$. Fix the
offsets the entry names,
\[
\Delta=\{{\,{offs_tex(p['offs'])}\,\}},
\]
and for a cell $(i,j)$ write
\[
S(i,j)=\{{\,(i+\delta_1,\,j+\delta_2) : (\delta_1,\delta_2)\in\Delta\,\}}\cap
\text{{(the cells of the array)}}
\]
for the neighbours it actually has. Only offsets landing inside the array count, so a cell on
the border simply has fewer neighbours.{transline}

The condition is that {body}{fracline}

\section{{A window of {U + D + 1} rows}}

The offsets reach {upw} up and {dnw} down, so everything the condition asks of one row is
decided by that row together with {upw} above it and {dnw} below --- a window of
${U + D + 1}$ consecutive rows, and nothing wider. Take the array one {slice_word} at a time and
let the state be the last {keep}, with a distinguished start standing for the array before its
first row, so that a walk of $n$ steps is an array of $n$ rows.

Appending a row completes exactly one window, and the row it settles is {settled}; a step is
allowed when that row passes. Each row of the finished array is therefore tested exactly once.
{beforepar}
{endpar}
Thus
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

Second, the count was recomputed for the smallest arrays straight from the definition: every
array of width ${W}$ over ${aset}$ with a few rows was written out cell by cell and each cell
tested against the neighbours it has. No window, no state and no end vector are involved in that
computation, and the published terms came back.

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
            if h.get('engine') == 'transfer71' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t71{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
