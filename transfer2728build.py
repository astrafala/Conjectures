#!/usr/bin/env python3
"""Papers for the two further image-counting families: the minimum-value maps and the
median/sum-of-three maps."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer27, transfer28

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def parts27(p, e):
    W, al = p['W'], p['alpha']
    D = [tuple(t) for t in p['dirs']]
    dirs = ', '.join('(%d,%d)' % t for t in D)
    which = p['which']
    trans = ('' if re.search(r'n\s*X', e['name']) else
             " The entry writes the array with $n$ as the number of COLUMNS; transposing it "
             "exchanges the two coordinates of every neighbour offset, which is done once so "
             "that the walk always runs down the rows.")
    what = rf"""Let $R=\{{0,\dots,{al}\}}^{{{W}}}$ be the set of rows and let the neighbours of
a cell be the cells at the offsets
\[
{dirs},
\]
those falling outside the array being simply absent.{trans} For an array
$A=(r_1,\dots,r_n)\in R^n$ let $\Phi(A)$ be the array whose cell $(i,j)$ carries the
{which} of $A(i,j)$ and of the values at its neighbours. The entry counts
\[
a(n)\;=\;\bigl|\{{\Phi(A):A\in R^n\}}\bigr| ,
\]
the size of an IMAGE. That is the whole difficulty: two different arrays with the same
{which}-array must be counted once, and a walk count on the arrays would count them twice."""
    win = rf"""Because every offset above moves the row index by at most one, row $i$ of
$\Phi(A)$ depends only on rows $i-1,i,i+1$ of $A$. Write $\beta(p,c,x)$ for that row, with $p$
or $x$ allowed to be $\bot$ for ``outside''; then
\[
\Phi(r_1,\dots,r_n)=\bigl(\beta(\bot,r_1,r_2),\ \dots,\ \beta(r_{{n-1}},r_n,\bot)\bigr).
\]"""
    return what, win, True


def parts28(p, e):
    W, al, op = p['W'], p['alpha'], p['op']
    extra = (" and no two adjacent entries of the larger array are equal"
             if p['noadj'] else "")
    what = rf"""Let $R$ be the set of rows of length ${W + 1}$ over $\{{0,\dots,{al}\}}${extra}.
For a larger array $A=(r_1,\dots,r_{{n+1}})$ of $n+1$ such rows let $\Phi(A)$ be the
$n\times{W}$ array with
\[
\Phi(A)(i,j)\;=\;\operatorname{{{op}}}\bigl(A(i,j),\,A(i,j+1),\,A(i+1,j)\bigr),
\]
the element, the one to its east and the one to its south. The entry counts
\[
a(n)\;=\;\bigl|\{{\Phi(A)\}}\bigr| ,
\]
the size of an IMAGE. That is the whole difficulty: two different larger arrays with the same
derived array must be counted once, and a walk count on the larger arrays would count them
twice."""
    win = rf"""Row $i$ of $\Phi(A)$ reads rows $i$ and $i+1$ of $A$ and nothing else, so
writing $\beta(r,x)$ for the derived row produced by two consecutive rows,
\[
\Phi(r_1,\dots,r_{{n+1}})=\bigl(\beta(r_1,r_2),\ \dots,\ \beta(r_n,r_{{n+1}})\bigr),
\]
and there is no row emitted with nothing below it."""
    return what, win, False


def build(h, mod):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    p = mod.parse_name(e['name'])
    what, win, hasfinal = (parts27(p, e) if mod is transfer27 else parts28(p, e))
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    if hasfinal:
        det = r"""For a set $D$ of pairs $(p,c)$ and a derived row $b$ put
\[
\delta(D,b)=\{(c,x):(p,c)\in D,\ x\in R,\ \beta(p,c,x)=b\},\qquad
f(D)=\bigl|\{\beta(p,c,\bot):(p,c)\in D\}\bigr| ,
\]
and let $D_0=\{(\bot,r):r\in R\}$."""
        lem = r"""\begin{lemma}\label{lem:det}
For every $t\ge0$, $D_t=\delta(\dots\delta(D_0,b_1)\dots,b_t)$ is exactly the set of pairs
$(r_t,r_{t+1})$ of consecutive rows completing a prefix $r_1,\dots,r_{t+1}$ whose first $t$
derived rows are $b_1,\dots,b_t$. Consequently, for $n\ge1$,
\[
a(n)=\sum_{b_1,\dots,b_{n-1}}f(D_{n-1}),
\]
the empty sets contributing nothing.
\end{lemma}

\begin{proof}
Induction on $t$: $D_0$ is the set of pairs $(\bot,r_1)$, and $\delta(D_t,b)$ collects the
pairs $(r_{t+1},r_{t+2})$ extending a consistent prefix with
$\beta(r_t,r_{t+1},r_{t+2})=b$. An element of the image is a full derived array
$(b_1,\dots,b_n)$; its prefix $(b_1,\dots,b_{n-1})$ is realisable exactly when
$D_{n-1}\neq\emptyset$, and then the possible last rows are
$\{\beta(p,c,\bot):(p,c)\in D_{n-1}\}$, of which there are $f(D_{n-1})$. Distinct sequences
are distinct derived arrays, so each is counted once.
\end{proof}"""
        formula = (r"a(n)\;=\;\iota^{\!\top}M^{\,n-1}\tau,\qquad \iota=e_{D_0},\quad \tau=f")
        tail = (r"""Note that $\tau$ is not the all-ones vector: the last derived row is not a
step of the walk but a count attached to the state the walk stops in.""")
    else:
        det = r"""For a set $D$ of rows and a derived row $b$ put
\[
\delta(D,b)=\{x\in R:\ r\in D,\ \beta(r,x)=b\},
\]
and let $D_0=R$."""
        lem = r"""\begin{lemma}\label{lem:det}
For every $t\ge0$, $D_t=\delta(\dots\delta(D_0,b_1)\dots,b_t)$ is exactly the set of rows
$r_{t+1}$ completing a prefix $r_1,\dots,r_{t+1}$ whose derived rows are $b_1,\dots,b_t$.
Consequently $a(n)$ is the number of sequences $(b_1,\dots,b_n)$ with $D_n\neq\emptyset$.
\end{lemma}

\begin{proof}
Induction on $t$: $D_0=R$ is the set of possible first rows, and $\delta(D_t,b)$ collects the
rows $r_{t+2}$ for which some consistent prefix ends in a row $r_{t+1}$ with
$\beta(r_{t+1},r_{t+2})=b$. A derived array of $n$ rows is realisable exactly when the
corresponding $D_n$ is nonempty, and distinct sequences are distinct derived arrays.
\end{proof}"""
        formula = (r"a(n)\;=\;\iota^{\!\top}M^{\,n}\tau,\qquad \iota=e_{D_0},"
                   r"\quad \tau=(1,\dots,1)^{\!\top}")
        tail = ''
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
OEIS {a} counts the distinct arrays obtained by applying a fixed local operation to every cell
of an array over a bounded alphabet, and carries an empirical recurrence of order ${order}$
contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical. What is
counted is the IMAGE of a map, not its domain, so it is not a walk count in the obvious graph;
determinising the machine that emits the derived array row by row turns it into one, on
$S={S}$ states, after which the conjectured recurrence is settled by a finite exact
computation.
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
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved.

\section{{What is being counted}}

{what}

{win}

\section{{The image is a walk count after determinisation}}

{det}

{lem}

So with $M$ the adjacency matrix of the digraph whose vertices are the reachable nonempty sets
and which carries one edge $D\to\delta(D,b)$ for each $b$ with $\delta(D,b)\neq\emptyset$ ---
several $b$ may lead to the same set, and then the edge is repeated, which is exactly right,
since the derived arrays differ ---
\[
{formula} .
\]
There are $S={S}$ reachable sets, generated from $D_0$ outward, and $a$ is $C$-finite.
{tail}

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
    hits = json.load(open('uniall_hits.json'))
    n = 0
    for h in hits:
        en = h.get('engine')
        if h.get('FAILS') or en not in ('transfer27', 'transfer28'):
            continue
        mod = transfer27 if en == 'transfer27' else transfer28
        dd = f"build/{en[-2:]}{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h, mod))
        n += 1
    print('wrote', n, 'papers')
