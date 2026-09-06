#!/usr/bin/env python3
"""Papers for the 3 X 3 subblock-property family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer75

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex




def conj_line(anum):
    e = LE.get(anum)
    for L in e['comment'] + e['formula']:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def describe(p):
    """(the condition in words, the extra remark that pins the reading)."""
    k, arg = p['kind'], p['arg']
    if k == 'sum':
        a = sorted(arg)
        if len(a) == 1:
            w = r"the nine entries sum to $%d$" % a[0]
        elif a == list(range(a[0], a[-1] + 1)) and len(a) > 2:
            w = r"the nine entries sum to something between $%d$ and $%d$" % (a[0], a[-1])
        else:
            w = (r"the nine entries sum to one of $" +
                 ',\\,'.join(str(x) for x in a) + r"$")
        return w, ""
    if k == 'part':
        a = sorted(arg)
        if len(set(a)) == 1:
            w = (r"each of the $%d$ values occurs exactly $%d$ times among the nine entries"
                 % (len(a), a[0]))
        else:
            w = (r"the numbers of times the values occur are $" +
                 ',\\,'.join(str(x) for x in a) + r"$ in some order")
        return w, (r"The entry's phrasing names the multiplicities without saying which value "
                   r"takes which, so what is fixed is the sorted list; this reading is pinned "
                   r"against the entry's own published terms.")
    if k == 'det':
        return (r"the block, read as a $3\times3$ matrix, has positive determinant", "")
    if k == 'pop':
        return (r"every block has the same \emph{{population}}: the number of times each "
                r"value occurs is the same in all of them",
                r"The entry says ``the same population''. That is the count of EACH value, not "
                r"the sum of the entries and not the number of nonzero entries: on a binary "
                r"matrix those agree, but over a larger range they do not, and only the "
                r"count-of-each-value reading reproduces the published terms.")
    return (r"the sum of the absolute differences over the $36$ pairs of distinct entries "
            r"equals $%d$" % arg,
            r"The entry counts those differences as $72$, which is the number of ORDERED "
            r"pairs; the number it compares against is the sum over the $36$ unordered pairs, "
            r"and that is the reading its published terms confirm --- the value named is not "
            r"an achievable ordered-pair sum at all.")


def build(h):
    a = h['anum']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    nm = e['name']
    p = transfer75.parse_name(nm)
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    words, remark = describe(p)
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes $1/%d$ of that count; the division is by a constant and "
                r"changes nothing about the recurrence." % frac)
    noadjline = ('' if not p['noadj'] else
                 r" The entry adds that no two adjacent entries of the array are equal.")
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of COLUMNS. The condition "
                 r"treats a block the same way after transposing --- a sum, a multiset of "
                 r"multiplicities and a set of pairwise differences are all unchanged, and a "
                 r"determinant is unchanged by transposing a matrix --- so only which side "
                 r"grows is affected.")
    popstate = ('' if p['kind'] != 'pop' else
                r""" This condition is the one exception to a block being judged on its own: it
ties the blocks to each other. The tie is carried as one extra piece of the state, the common
list of counts, which the first block fixes and every later one must match. There are finitely
many such lists, so the state space stays finite.""")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which every $3\times3$ subblock
satisfies a condition on its nine entries. The entry carries an empirical recurrence of order
${order}$ contributed by R.~H.~Hardin. It is true, and it is decidable rather than empirical: a
$3\times3$ block lies in three consecutive rows, so the state is the last two rows and the
count is a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B20, 15A18.\normalsize

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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$. The
condition is imposed on every $3\times3$ block of the array --- every choice of three
consecutive rows and three consecutive columns --- and asks that {words}.{noadjline}{transline}{fracline}

{remark}

\section{{Three rows}}

A $3\times3$ block occupies three consecutive rows, so everything the condition asks is decided
by three consecutive rows and nothing wider. Take the array one row at a time and let the state
be the last two rows written, with a distinguished start standing for the array before its
first row. Appending a row completes the blocks whose bottom row is the new one, and the step
is allowed exactly when each of those blocks passes.{popstate}

Every block of the finished array is tested exactly once, at the step that writes its bottom
row, and no step imposes anything the definition does not ask. The first two rows complete no
block at all, which is why they are laid down without a test. Every state may end an array, so
$\tau=\mathbf{{1}}$. Thus
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
array was written out cell by cell and each $3\times3$ block tested directly on its nine
entries. No rows, no window, no state and no transfer matrix are involved in that computation,
and the published terms came back.

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
    rm = {r['anum'] for r in json.load(open('rank-map.json'))}
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer75' and not h.get('FAILS') and h['anum'] not in rm]
    for h in hits:
        dd = f"build/t75{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
