#!/usr/bin/env python3
"""Papers for the turn-constrained occupancy family."""
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer44

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

WORDS = {'straight': ("$d'=d$", "the token arriving at a cell and the token leaving it move "
                      "in the same direction --- the move goes STRAIGHT THROUGH"),
         'loop': ("$d'=-d$", "the two tokens exchange places --- a $2$-LOOP"),
         'left': ("$d\\wedge d'>0$", "the outgoing direction lies to the LEFT of the incoming "
                  "one, the wedge being the cross product of the two offsets read as plane "
                  "vectors")}


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = transfer44.parse_name(e['name'])
    W = p['W']
    D = [tuple(t) for t in p['dirs']]
    dirs = texbits.offsets_tex(D)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    stay = (' The offset $(0,0)$ is among them: the entry lets a token stay put.'
            if p['stay'] else
            ' The offset $(0,0)$ is NOT among them: every token must move.')
    items = '\n'.join(rf"\item {WORDS[k][0]}, that is, {WORDS[k][1]};" for k in p['bad'])
    cap = ''
    if p['cap'] is not None:
        cap = (rf" The entry asks in addition that no occupancy exceed ${p['cap']}$, a "
               r"condition on the array recorded rather than on the moves.")
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS. Transposing it "
             "exchanges the two coordinates of every offset, which is done once so that the "
             "walk always runs down the rows; a transposition is a reflection and reverses "
             "the sense of a turn, so the left-hand test is negated in the transposed frame "
             "rather than being applied in the wrong one.")
    lefted = 'left' in p['bad']
    chir = (r"""
The sense of ``left'' is fixed once and for all. Rows are numbered downwards, so the offset
$(d_1,d_2)$ is the plane vector $(d_2,-d_1)$, and $d\wedge d'$ denotes
$d_2(-d'_1)-(-d_1)d'_2$. A positive value says $d'$ is obtained from $d$ by a rotation through
an angle strictly between $0$ and $\pi$ counterclockwise, which is what a turn to the left is.
The condition is not a $90^\circ$ test: for a neighbour set containing diagonal offsets the
turns of $45^\circ$ and $135^\circ$ are left turns too, and the entry's data distinguishes the
two readings.
""" if lefted else '')
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the distinct OCCUPANCY arrays obtained when every cell of an $n\times{W}$ grid
holds one token, each token moves to a neighbouring cell, and the direction a token leaves a
cell in is restricted by the direction in which another token arrives there. The entry carries
an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. What is counted is the size of an IMAGE --- two different
assignments of moves with the same occupancy count once --- so it is not a walk count in the
obvious graph; determinising the machine that emits the occupancy row by row turns it into
one, on $S={S}$ states, after which the conjectured recurrence is settled by a finite exact
computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 68Q45, 60C05.\normalsize

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

Every cell of an $n\times{W}$ grid holds one token. Each token moves by one of the offsets
\[
{dirs},
\]
a move being available only when it lands inside the grid.{stay}{trans} The OCCUPANCY array
records, for each cell, how many tokens land on it, and the entry counts how many different
occupancy arrays occur as the assignment of moves runs over all its possibilities.

The moves are not free of one another. Suppose the token at a cell $A$ moves by $d$ to the
cell $B$, and the token standing at $B$ moves by $d'$. The entry forbids the ordered pair
$(d,d')$ when
\begin{{itemize}}
{items}
\end{{itemize}}
and imposes nothing else. A token that stays put neither arrives anywhere nor leaves, so a
zero offset on either side of the pair carries no condition at all.{cap}
{chir}
That the count is the size of an IMAGE is the whole difficulty: two assignments with the same
occupancy must be counted once, and a walk count over the assignments would count them twice.

\section{{One window decides everything}}

Write $c_i\in\Delta^{{{W}}}$ for the row of offsets chosen by the cells of row $i$, where
$\Delta$ is the offset set above.

\begin{{lemma}}\label{{lem:win}}
Both the occupancy of row $i$ and every instance of the forbidden pair whose FIRST member is a
move made in row $i$ are determined by $c_{{i-1}},c_i,c_{{i+1}}$, with the convention that an
absent row is the symbol $\bot$.
\end{{lemma}}

\begin{{proof}}
Every offset changes the row index by at most one, so a token landing on a cell of row $i$
started in row $i-1$, $i$ or $i+1$; that is the occupancy. For the pairs, a move made by the
cell $(i,j)$ with offset $d$ lands on the cell $(i+d_1,j+d_2)$, whose row is $i-1$, $i$ or
$i+1$, so the offset $d'$ of that cell is a coordinate of $c_{{i-1}}$, $c_i$ or $c_{{i+1}}$.
Reading a row of the array as $\bot$ makes ``up'' or ``down'' unavailable, which is exactly
the boundary rule.
\end{{proof}}

Each ordered pair is therefore tested exactly once, from the row of the token that makes the
first move of the pair; every row plays that part exactly once along the array.

Let $\beta(p,c,x)$ be the occupancy row of $c$ in the context $(p,x)$, undefined when some
cell of $c$ has no room to move or when some forbidden pair occurs. The occupancy array of an
assignment $c_1,\dots,c_n$ is
\[
\bigl(\beta(\bot,c_1,c_2),\ \beta(c_1,c_2,c_3),\ \dots,\ \beta(c_{{n-1}},c_n,\bot)\bigr).
\]

\section{{The image is a walk count after determinisation}}

Determinise. For a set $D$ of pairs $(p,c)$ and an occupancy row $b$ put
\[
\delta(D,b)=\{{(c,x):(p,c)\in D,\ \beta(p,c,x)=b\}},\qquad
f(D)=\bigl|\{{\beta(p,c,\bot):(p,c)\in D,\ \beta(p,c,\bot)\ \text{{defined}}\}}\bigr| ,
\]
and let $D_0=\{{(\bot,c):c\}}$. An induction on the number of rows shows $D_t$ is exactly the
set of pairs of consecutive move-rows completing a prefix with the emitted occupancy rows, so
that with $M$ the adjacency matrix of the digraph on the reachable nonempty sets, one edge per
occupancy row it admits,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad \iota=e_{{D_0}},\quad \tau=f .
\]
The last row is counted by $f$ and not by an edge: it is emitted with nothing below it, so it
is a property of the state the walk stops in and $\tau$ is not the all-ones vector. There are
$S={S}$ reachable sets. In particular $a$ is $C$-finite.

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

Second, the count was recomputed for the smallest grids straight from the definition ---
enumerate every assignment of offsets to cells, discard the assignments containing a forbidden
pair, form the occupancy array, and count the distinct arrays --- with the forbidden-pair test
written out from the entry's wording rather than taken from the model. The published terms
came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{hu}} J.~E.~Hopcroft, R.~Motwani and J.~D.~Ullman, \emph{{Introduction to Automata
Theory, Languages, and Computation}}, 3rd ed., Addison--Wesley, 2006. (The subset
construction, Section 2.3.)
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer44' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t44{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
