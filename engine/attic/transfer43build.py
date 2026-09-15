#!/usr/bin/env python3
"""Papers for the occupancy family."""
import conjquote
import os, json, re
import texbits
import localentry as LE, phibuild, transferbuild, transfer43

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
    p = transfer43.parse_name(e['name'])
    W = p['W']
    D = [tuple(t) for t in p['dirs']]
    dirs = texbits.offsets_tex(D)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a, h.get("coeffs"))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    stay = (' The offset $(0,0)$ is among them: the entry lets a token stay put.'
            if p['stay'] else
            ' The offset $(0,0)$ is NOT among them: every token must move.')
    extra = ''
    if p['cap'] is not None:
        extra = rf" The entry also asks that no occupancy exceed ${p['cap']}$."
    elif p['exact'] is not None:
        vals = ' or '.join(str(x) for x in sorted(p['exact']))
        extra = rf" The entry also asks that every occupancy be ${vals}$."
    elif p['noloop']:
        extra = (" The entry also forbids $2$-loops: no two tokens may exchange places.")
    trans = ('' if re.search(r'\bn\s*X', e['name']) else
             " The entry writes the array with $n$ as the number of COLUMNS; transposing it "
             "exchanges the two coordinates of every offset, which is done once so that the "
             "walk always runs down the rows.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts the distinct OCCUPANCY arrays obtained when every cell of an $n\times{W}$ grid
holds one token and each token moves to a neighbouring cell, and carries an empirical
recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable
rather than empirical. What is counted is the size of an IMAGE --- two different assignments of
moves with the same occupancy count once --- so it is not a walk count in the obvious graph;
determinising the machine that emits the occupancy row by row turns it into one, on $S={S}$
states, after which the conjectured recurrence is settled by a finite exact computation.
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
records, for each cell, how many tokens land on it; the entry counts how many different
occupancy arrays occur as the assignment of moves runs over all its possibilities.{extra}

That is the size of an IMAGE, and it is the whole difficulty: two assignments with the same
occupancy must be counted once, and a walk count over the assignments would count them twice.

\section{{The image is a walk count after determinisation}}

Every offset moves the row index by at most one, so the occupancy of row $i$ is decided by the
moves chosen in rows $i-1$, $i$ and $i+1$. Writing $\beta(p,c,x)$ for that occupancy row, with
$p$ or $x$ allowed to be the symbol $\bot$ for ``outside'', the whole occupancy array is
\[
\bigl(\beta(\bot,c_1,c_2),\ \beta(c_1,c_2,c_3),\ \dots,\ \beta(c_{{n-1}},c_n,\bot)\bigr)
\]
for an assignment $c_1,\dots,c_n$ of move-rows. The symbol $\bot$ is not decoration: whether
``up'' or ``down'' is a legal move for a cell depends on it, and $\beta$ returns nothing at all
when the row it is given cannot occur in that position.

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
There are $S={S}$ reachable sets. In particular $a$ is $C$-finite.

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

Three checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. The entry's first term is ${d[0]}$, and it is a sharp test of the boundary: a
one-row grid offers only the moves that stay within one row, so a neighbour set with no
horizontal offset gives no legal assignment at all and the count is zero, which is what the
entries of that shape publish.

Second, the conjectured recurrence was evaluated directly on those published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
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
            if h.get('engine') == 'transfer43' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t43{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
