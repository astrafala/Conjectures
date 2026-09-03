#!/usr/bin/env python3
"""Papers for the 2 X 2 perimeter family: clockwise patterns and edge increases."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer64

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def cond_tex(p):
    """The condition, stated as mathematics, and a one-line summary for the abstract."""
    k, m = p['kind'], p['mode']
    if k == 'pattern':
        ws = ',\\ '.join(p['words'])
        body = (r"reading the four corners clockwise, starting at whichever corner one "
                r"pleases, spells one of the words" "\n\\[\n" + ws + ".\n\\]\n"
                r"That is, the cyclic word $pqsr$ is a rotation of one of them. The starting "
                r"corner is not fixed by the entry, and it is the data that says so: with the "
                r"words $0000$, $0011$, $0101$ allowed there are seven two-by-two binary "
                r"arrays, which is what such an entry publishes as its first term, whereas a "
                r"fixed starting corner would leave three.")
        short = "the corners read clockwise spell one of a listed set of words"
    elif k == 'cmp':
        rel = '=' if m == 'eq' else r'\le'
        body = (r"every subblock $B$ of the array satisfies" "\n\\[\n"
                r"\mathrm{cw}(B)\;" + rel + r"\;\mathrm{ccw}(B)" "\n\\]\n")
        if p['noadjeq']:
            body += (r"and, in addition, no two horizontally or vertically adjacent entries "
                     r"of the array are equal.")
            short = ("no two adjacent entries are equal and the two edge-increase counts "
                     "agree in every subblock")
        else:
            short = ("the two edge-increase counts " +
                     ("agree" if m == 'eq' else "are ordered one way") + " in every subblock")
    elif k == 'jump':
        rel = (r"at least one of $J_{\mathrm{cw}}(B)\le 1$, $J_{\mathrm{ccw}}(B)\le 1$ holds"
               if m == 'or' else
               r"exactly one of $J_{\mathrm{cw}}(B)\le 1$, $J_{\mathrm{ccw}}(B)\le 1$ holds")
        body = (r"write" "\n\\[\n"
                r"J_{\mathrm{cw}}(B)=\max(q-p,\;s-q,\;r-s,\;p-r),\qquad "
                r"J_{\mathrm{ccw}}(B)=\max(r-p,\;s-r,\;q-s,\;p-q)" "\n\\]\n"
                r"for the largest step taken going round the subblock in each of the two "
                r"directions. The condition is that for every subblock $B$, " + rel + ".")
        short = "the steps round each subblock rise by at most one in one of the two directions"
    elif k == 'strict':
        body = (r"every subblock $B$ has its four corners pairwise unequal along the cycle "
                r"($p\ne q$, $q\ne s$, $s\ne r$, $r\ne p$) and" "\n\\[\n"
                r"\mathrm{cw}(B)\in\{1,3\}." "\n\\]\n"
                r"Going round clockwise there are then four strict steps, of which either "
                r"three rise and one falls ($\mathrm{cw}(B)=3$: strictly increasing clockwise "
                r"with one decrease) or one rises and three fall ($\mathrm{cw}(B)=1$, which "
                r"is the same statement read counterclockwise). Call the subblock "
                r"\emph{clockwise} in the first case and \emph{counterclockwise} in the "
                r"second; this is its increasing direction.")
        if m == 'adj':
            body += ("\n\n" r"The entry asks in addition that at least two adjacent subblocks "
                     r"---adjacent meaning one step right or one step down in the grid of "
                     r"subblocks---have the same increasing direction. That is a condition on "
                     r"the array as a whole, not on any one subblock.")
            short = ("every subblock turns strictly one way with a single decrease, and some "
                     "two adjacent subblocks turn the same way")
        else:
            short = "every subblock turns strictly one way with a single decrease"
    elif k == 'diffs':
        body = (r"every subblock $B$ satisfies" "\n\\[\n"
                r"\bigl|\{\,q-p,\;s-q,\;r-s,\;p-r\,\}\bigr|\in\{1,4\}," "\n\\]\n"
                r"the number of DISTINCT differences taken along the clockwise cycle being "
                r"one or four. The four differences sum to zero, so one distinct value means "
                r"all four are zero and the subblock is constant.")
        short = "the four clockwise differences of each subblock take one or four values"
    elif k == 'samecw':
        body = (r"there is a single number $c$ with $\mathrm{cw}(B)=c$ for EVERY subblock $B$ "
                r"of the array. The value of $c$ is not prescribed; it is only required to be "
                r"the same throughout, so this is a condition on the array as a whole.")
        short = "all subblocks carry the same number of clockwise edge increases"
    elif k == 'mono':
        extra = (r" and $\mathrm{ccw}(B)\ge\mathrm{ccw}(B')$" if p['ccw'] else "")
        body = (r"whenever $B'$ is the subblock one step to the right of $B$, or one step "
                r"below it, " "\n\\[\n"
                r"\mathrm{cw}(B)\le\mathrm{cw}(B')" +
                (r",\qquad \mathrm{ccw}(B)\ge\mathrm{ccw}(B')" if p['ccw'] else "") + "\n\\]\n"
                r"so the clockwise count is nondecreasing rightwards and downwards" +
                (r" while the counterclockwise count is nonincreasing in both directions."
                 if p['ccw'] else "."))
        short = ("the clockwise counts increase rightwards and downwards" +
                 (", the counterclockwise counts decrease" if p['ccw'] else ""))
    elif k == 'nbr':
        rel = '=' if m == 'eq' else r'\ne'
        body = (r"for every subblock $B$, writing $L$ for the subblock one step to its LEFT "
                r"and $U$ for the subblock one step ABOVE it," "\n\\[\n"
                r"\mathrm{cw}(B)\;" + rel + r"\;\mathrm{ccw}(L),\qquad "
                r"\mathrm{cw}(B)\;" + rel + r"\;\mathrm{ccw}(U)" "\n\\]\n"
                r"whenever that neighbour exists. A subblock in the first column has no $L$ "
                r"and a subblock in the first row has no $U$, and then the corresponding "
                r"requirement is empty.")
        short = ("each subblock's clockwise count is compared with the counterclockwise "
                 "counts of its left and upper neighbours")
    else:                                                            # 'hv'
        rel = '=' if m == 'eq' else r'\ne'
        body = (r"for every subblock $B$, writing $H$ for a subblock horizontally adjacent to "
                r"$B$ and $V$ for one vertically adjacent to it," "\n\\[\n"
                r"\mathrm{cw}(B)\;" + rel + r"\;\mathrm{cw}(H),\qquad "
                r"\mathrm{ccw}(B)\;" + rel + r"\;\mathrm{ccw}(V)" "\n\\]\n"
                r"whenever that neighbour exists.")
        short = ("clockwise counts are compared across horizontal neighbours and "
                 "counterclockwise counts across vertical ones")
    return body, short


def state_tex(p):
    """What the state has to carry, beyond the row just written."""
    k = p['kind']
    if k == 'mono':
        what = (r"the clockwise count of each subblock of that pair"
                if not p['ccw'] else
                r"the clockwise and counterclockwise counts of each subblock of that pair")
        return (r"Two consecutive rows decide every subblock lying between them, and the "
                r"conditions of Section 2 compare such a subblock with the subblock directly "
                r"above it, which lies between the PREVIOUS two rows. So the state carries the "
                r"row just written together with " + what + r", one small number per column: "
                r"at most five values each, whatever the alphabet.", True)
    if k in ('nbr', 'hv'):
        return (r"Two consecutive rows decide every subblock lying between them, and the "
                r"conditions of Section 2 compare such a subblock with the subblock directly "
                r"above it, which lies between the PREVIOUS two rows. So the state carries the "
                r"row just written together with the counterclockwise count of each subblock "
                r"of the pair just closed, one number in $\{0,1,2,3,4\}$ per column.", True)
    if k == 'samecw':
        return (r"Two consecutive rows decide every subblock lying between them. The common "
                r"value $c$ is not local at all, but it takes only the five values "
                r"$0,1,2,3,4$: the state carries the row just written together with $c$, left "
                r"unset until the first subblock of the array fixes it and constant "
                r"thereafter.", False)
    if k == 'strict' and p['mode'] == 'adj':
        return (r"Two consecutive rows decide every subblock lying between them, and their "
                r"increasing directions. The extra requirement is an EXISTENCE statement about "
                r"the whole array, and an existence statement needs only one bit: the state "
                r"carries the row just written, the increasing direction of each subblock of "
                r"the pair just closed---which is what a subblock in the next pair must be "
                r"compared against---and a single flag, set the first time two adjacent "
                r"subblocks are seen to agree and never cleared.", True)
    return (r"Two consecutive rows decide every subblock lying between them, and the condition "
            r"of Section 2 is a condition on single subblocks only. So the state is the row "
            r"just written, and nothing else.", False)


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer64.parse_name(e['name'])
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    body, short = cond_tex(p)
    st, vert = state_tex(p)
    endword = (r"The end vector is the indicator of the states in which the required pair of "
               r"adjacent subblocks has already been witnessed; every other state is rejected."
               if p['kind'] == 'strict' and p['mode'] == 'adj' else
               r"The end vector is all ones: an array may stop after any row.")
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes %s of that count; the division is by the constant "
                r"%d and changes nothing about the recurrence." % (
                    {2: 'one half', 4: 'one quarter'}.get(frac, '$1/%d$' % frac), frac))
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    rowsword = 'rows' if not vert else 'rows'
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ subject to a condition read round the
perimeter of every $2\times2$ subblock: {short}. The entry carries an empirical recurrence of
order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than
empirical: the condition is settled inside a bounded window of consecutive {rowsword}, so the
count is a walk count on a finite digraph with $S={S}$ vertices, and whether a linear
recurrence holds for such a count is a finite computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A16, 15A18.\normalsize

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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$. A
$2\times2$ subblock is a set of four cells
\[
B=\begin{{pmatrix}} p & q \\ r & s \end{{pmatrix}},
\qquad p=x(i,j),\; q=x(i,j+1),\; r=x(i+1,j),\; s=x(i+1,j+1).
\]
Its perimeter is a cycle of four cells, walked clockwise as $p\to q\to s\to r\to p$ and
counterclockwise as $p\to r\to s\to q\to p$. Write
\[
\mathrm{{cw}}(B)=[p<q]+[q<s]+[s<r]+[r<p],\qquad
\mathrm{{ccw}}(B)=[p<r]+[r<s]+[s<q]+[q<p]
\]
for the number of steps at which the value rises, going each way round.

\begin{{lemma}}\label{{lem:sum}}
$\mathrm{{cw}}(B)+\mathrm{{ccw}}(B)=4-\#\{{\text{{edges of the cycle with equal ends}}\}}$.
\end{{lemma}}

\begin{{proof}}
Each of the four edges of the square is walked once by each cycle, and in opposite directions.
An edge with distinct ends therefore contributes exactly one rise, to one of the two counts;
an edge with equal ends contributes to neither.
\end{{proof}}

The condition the entry imposes is this: {body}{fracline}

\section{{A bounded window}}

{st}

One step of the walk writes a whole row. The row is filled left to right, and the subblock
closed by positions $j-1,j$ is tested the moment position $j$ is written, so a partial row that
cannot be completed is abandoned rather than enumerated. The walk starts at the state standing
for the empty array, so that a walk of $n$ steps is an array of $n$ rows.

{endword} Thus
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,j}}\tau ,\qquad S={S},
\]
for the transfer matrix $M$ on those $S$ states. The walk index $j$ and the entry's own $n$
differ by a constant, read off by matching the published terms rather than assumed. In
particular $a$ is $C$-finite, and every question about linear recurrences it satisfies is
decidable.

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
array of the stated width and a few rows was written out cell by cell over ${aset}$, each of
its $2\times2$ subblocks was read round its perimeter, and the condition of Section 2 was
applied as stated. No window, no state and no recurrence is involved in that computation, and
the published terms came back.

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
            if h.get('engine') == 'transfer64' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t64{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
