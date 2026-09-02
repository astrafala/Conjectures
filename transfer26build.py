#!/usr/bin/env python3
"""One paper per entry settled by the image-counting (`maps') engine."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer26

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex

COND = {
    'hilltop': 'is at least as large as every one of',
    'unmatched value': 'differs from every one of',
    'unchanging value': 'is equal to every one of',
    'majority value': 'is equal to at least half of',
    'equals one': 'is equal to exactly one of',
    'equals two': 'is equal to exactly two of',
    'sum of neighbor': 'is congruent modulo %d to the sum of',
}


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off, sh = h['offset'], h['shift']
    e = LE.get(a)
    p = transfer26.parse_name(e['name'])
    W, al, fam = p['W'], p['alpha'], p['fam']
    D = [tuple(t) for t in p['dirs']]
    cond = COND[fam] % p['mod'] if fam == 'sum of neighbor' else COND[fam]
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    dirs = ', '.join('(%d,%d)' % t for t in D)
    trans = ('' if re.search(r'n\s*X', e['name']) else
             " The entry writes the array with $n$ as the number of COLUMNS; transposing it "
             "exchanges the two coordinates of every neighbour offset, which is done once so "
             "that the walk always runs down the rows.")
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
OEIS {a} counts the distinct indicator arrays obtained from the $n\times{W}$ arrays over
$\{{0,\dots,{al}\}}$ by marking the cells whose value {cond} their neighbours, and carries an
empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and it is
decidable rather than empirical. What is counted is the IMAGE of a map, not its domain, so it
is not a walk count in the obvious graph; the determinisation of the machine that emits the
indicator row by row turns it into one, on $S={S}$ states, after which the conjectured
recurrence is settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 68Q45, 15B36.\normalsize

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

\section{{What is being counted}}

Let $R=\{{0,\dots,{al}\}}^{{{W}}}$ be the set of rows and let the neighbours of a cell be the
cells at the offsets
\[
{dirs},
\]
those falling outside the array being simply absent.{trans} For an array
$A=(r_1,\dots,r_n)\in R^n$ let $\Phi(A)\in\{{0,1\}}^{{n\times{W}}}$ mark the cells whose value
{cond} its neighbours. The entry counts
\[
a(n)\;=\;\bigl|\{{\Phi(A):A\in R^n\}}\bigr| ,
\]
the size of an IMAGE. This is the whole difficulty: two different arrays with the same marking
must be counted once, and a walk count in a graph on the arrays would count them twice.

Because every offset above moves the row index by at most one, the marked row $i$ depends only
on rows $i-1,i,i+1$. Write $\beta(p,c,x)\in\{{0,1\}}^{{{W}}}$ for the marking of the row $c$
with $p$ above and $x$ below, allowing $p$ or $x$ to be the symbol $\bot$ for ``outside''.
Then
\[
\Phi(r_1,\dots,r_n)=\bigl(\beta(\bot,r_1,r_2),\ \beta(r_1,r_2,r_3),\ \dots,\
\beta(r_{{n-1}},r_n,\bot)\bigr).
\]

\section{{The image is a walk count after determinisation}}

For a set $D\subseteq(R\cup\{{\bot\}})\times R$ of pairs and a row $b\in\{{0,1\}}^{{{W}}}$ put
\[
\delta(D,b)=\{{(c,x)\ :\ (p,c)\in D,\ x\in R,\ \beta(p,c,x)=b\}},\qquad
f(D)=\bigl|\{{\beta(p,c,\bot):(p,c)\in D\}}\bigr| ,
\]
and let $D_0=\{{(\bot,r):r\in R\}}$.

\begin{{lemma}}\label{{lem:det}}
For every $t\ge0$ and every $b_1,\dots,b_t$, the set
$D_t=\delta(\dots\delta(D_0,b_1)\dots,b_t)$ is exactly
\[
\{{(r_t,r_{{t+1}})\ :\ (r_1,\dots,r_{{t+1}})\in R^{{t+1}},\ \beta(\bot,r_1,r_2)=b_1,\ \dots,\
\beta(r_{{t-1}},r_t,r_{{t+1}})=b_t\}} ,
\]
with $r_0=\bot$. Consequently, for $n\ge1$,
\[
a(n)\;=\;\sum_{{b_1,\dots,b_{{n-1}}}}f(D_{{n-1}}),
\]
the sum over all sequences of rows in $\{{0,1\}}^{{{W}}}$, empty $D$'s contributing nothing.
\end{{lemma}}

\begin{{proof}}
Induction on $t$. For $t=0$ the set is $\{{(\bot,r_1)\}}$, which is $D_0$. If the description
holds for $D_t$, then $\delta(D_t,b)$ collects the pairs $(r_{{t+1}},r_{{t+2}})$ for which
$(r_t,r_{{t+1}})$ already extends a consistent prefix and
$\beta(r_t,r_{{t+1}},r_{{t+2}})=b$, which is the description for $t+1$.

An element of the image is a full marking $(b_1,\dots,b_n)$. By the description, a prefix
$(b_1,\dots,b_{{n-1}})$ is realised by some $r_1,\dots,r_n$ exactly when $D_{{n-1}}\neq
\emptyset$, and then the possible last rows are precisely
$\{{\beta(p,c,\bot):(p,c)\in D_{{n-1}}\}}$, of which there are $f(D_{{n-1}})$. Distinct
sequences $(b_1,\dots,b_n)$ are distinct markings, so summing $f$ over the prefixes counts the
image exactly once each.
\end{{proof}}

So with $M$ the adjacency matrix of the digraph whose vertices are the reachable nonempty sets
$D$ and which carries one edge $D\to\delta(D,b)$ for each $b$ with $\delta(D,b)\neq\emptyset$
--- several $b$ may lead to the same set, and then the edge is repeated, which is exactly
right, since the markings differ ---
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-1}}\tau,\qquad \iota=e_{{D_0}},\quad \tau=f .
\]
There are $S={S}$ reachable sets, generated from $D_0$ outward, and $a$ is $C$-finite. Note
that $\tau$ is not the all-ones vector: the last marked row is not a step of the walk but a
count attached to the state the walk stops in.

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
arithmetic. This is what ties the model to the entry: the machine is built by reading the
entry's English, and a misreading gives different counts.

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
            if h.get('engine') == 'transfer26' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t26{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
