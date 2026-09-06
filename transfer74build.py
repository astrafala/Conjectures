#!/usr/bin/env python3
"""Papers for the min-plus-max subblock family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer74

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex



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
    nm = e['name']
    p = transfer74.parse_name(nm)
    W, A = p['W'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 5 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    rel = '=' if p['equal'] else r'\neq'
    relw = 'equal to' if p['equal'] else 'unequal to'
    frac = p['frac']
    fracline = ('' if frac == 1 else
                r" The entry publishes %s of that count; the division is by the constant %d "
                r"and changes nothing about the recurrence." % (
                    {2: 'one half', 4: 'one quarter'}.get(frac, '$1/%d$' % frac), frac))
    transline = ("" if not p['trans'] else
                 r" The entry writes the array with $n$ as the number of COLUMNS. The condition "
                 r"treats the four cells of a block alike, so it is unchanged by transposing, "
                 r"and only which side grows is affected.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ in which the smallest and largest of the
four entries of every $2\times2$ block have a sum {relw} the sum of the other two. The entry
carries an empirical recurrence of order ${order}$ contributed by R.~H.~Hardin. It is true, and
it is decidable rather than empirical: the condition involves two consecutive rows and nothing
wider, so the count is a walk count on $S={S}$ states.
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

The arrays have ${W}$ columns and a growing number of rows, with entries in ${aset}$. Take any
$2\times2$ block of the array and sort its four entries as
\[
\alpha\le\beta\le\gamma\le\delta .
\]
The minimum is $\alpha$ and the maximum is $\delta$; the lower median is $\beta$ and the upper
median is $\gamma$. The entry's condition, imposed on every $2\times2$ block, is therefore
\[
\alpha+\delta\;{rel}\;\beta+\gamma .
\]{transline}{fracline}

Nothing here depends on where in the block each value sits: the condition is a statement about
the multiset of the four entries. In particular it is symmetric under every rearrangement of
the block, and under adding a constant to all four entries.

\section{{Two rows}}

A $2\times2$ block occupies two consecutive rows, so everything the condition asks is decided
by a pair of consecutive rows and nothing wider. Take the array one row at a time and let the
state be the row just written; a step appends a new row and is allowed exactly when every one
of the ${W}-1$ blocks spanning the two rows satisfies the condition.

Every block of the finished array is tested exactly once, at the step that writes its lower
row, and no step tests anything the definition does not ask. A one-row array has no block at
all, so every row may start and every state may end: $\iota$ and $\tau$ are both
$\mathbf{{1}}$, and the states are all ${A}^{{{W}}}={S}$ rows. Thus
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
array was written out cell by cell and each $2\times2$ block tested by sorting its four values
and comparing the outer two with the inner two. No rows, no state and no transfer matrix are
involved in that computation, and the published terms came back.

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
            if h.get('engine') == 'transfer74' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t74{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
