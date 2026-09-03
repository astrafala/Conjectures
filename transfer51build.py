#!/usr/bin/env python3
"""Papers for the row/column divisibility family."""
import os, json, re
import localentry as LE, phibuild, transferbuild, transfer51

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
    p = transfer51.parse_name(e['name'])
    W, b, A = p['W'], p['base'], p['alpha'] + 1
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    modf, rev = e['modified'], e['revision']
    conj = conj_line(a)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    # these are words, not mathematics: inside $...$ the space in `not divisible' is lost
    rw = ('not divisible' if p['rowneg'] else 'divisible')
    cw = ('not divisible' if p['colneg'] else 'divisible')
    aset = (r'\{' + ','.join(str(t) for t in range(A)) + r'\}' if A <= 4 else
            r'\{0,1,\dots,%d\}' % (A - 1))
    lex = p['lex']
    lextxt = ('' if not lex else rf"""
The entry adds that the rows and the columns are each in lexicographic {lex} order. Comparing
two ROWS needs only the previous row, so it is carried in the state. Comparing two COLUMNS is
settled by the FIRST array row in which they differ, so the state carries one bit for each
adjacent pair of columns --- whether that pair has been equal in every row so far. A row that
would put an adjacent pair in the wrong order is rejected at once, and a pair that is still
equal at the end is in order, equality being allowed.""")
    trans = ('' if not p['trans'] else
             " The entry writes the array with $n$ as the number of COLUMNS. The walk is run "
             "down the transpose, which exchanges the row condition with the column condition; "
             "both readings put the FIRST digit in the most significant place, so nothing else "
             "changes under that exchange.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by transfer matrix}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{3 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of width ${W}$ over ${aset}$ whose rows, read as base-${b}$
numbers, are {rw} by ${p['rowmod']}$ and whose columns, read the same way, are {cw} by
${p['colmod']}$. The entry carries an empirical recurrence of order ${order}$ contributed by
R.~H.~Hardin. It is true, and it is decidable rather than empirical. A column's value depends on
every row of the array, so the condition is not local; but its RESIDUE is built one row at a
time by Horner's rule, and the vector of column residues is a state of bounded size. The count
is then a walk count on $S={S}$ states.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11A63, 15A18.\normalsize

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

The array has ${W}$ cells across and entries $x(i,j)\in{aset}$, the digits of
base ${b}$. Row $i$ of an array with $R$ rows is the number
\[
\rho_i\;=\;\sum_{{j=1}}^{{{W}}}x(i,j)\,{b}^{{{W}-j}} ,
\]
the LEFT digit being the most significant, and column $j$ is
\[
\gamma_j\;=\;\sum_{{i=1}}^{{R}}x(i,j)\,{b}^{{R-i}} ,
\]
the TOP digit being the most significant. The entry asks that every $\rho_i$ be {rw} by
${p['rowmod']}$ and every $\gamma_j$ be {cw} by ${p['colmod']}$.{trans}
{lextxt}

\section{{Column residues by Horner's rule}}

The row condition is a condition on one row and is imposed as each row is chosen. The column
condition is not local: $\gamma_j$ depends on every row. What is local is its residue.

\begin{{lemma}}\label{{lem:horner}}
Let $\gamma_j^{{(i)}}$ be the value of column $j$ of the first $i$ rows, read the same way.
Then $\gamma_j^{{(0)}}=0$ and
\[
\gamma_j^{{(i)}}\;=\;{b}\,\gamma_j^{{(i-1)}}+x(i,j),
\qquad\text{{hence}}\qquad
\gamma_j^{{(i)}}\bmod {p['colmod']}\;=\;
\bigl({b}\,(\gamma_j^{{(i-1)}}\bmod {p['colmod']})+x(i,j)\bigr)\bmod {p['colmod']} .
\]
\end{{lemma}}

\begin{{proof}}
Adding a row at the BOTTOM shifts every earlier digit one place up in significance, which is
multiplication by ${b}$, and puts the new digit in the units place. Reduction modulo
${p['colmod']}$ commutes with both operations.
\end{{proof}}

So the vector $\bigl(\gamma_1\bmod {p['colmod']},\dots,\gamma_{{{W}}}\bmod
{p['colmod']}\bigr)$ is a state: at most ${p['colmod']}^{{{W}}}$ of them, and each array row
that satisfies the row condition carries one such vector to another. The walk starts at the
all-zero vector, which is the empty array, and the END vector picks out the residue vectors in
which every entry is {cw} by ${p['colmod']}$ --- so the end vector is not the all-ones
vector, and the column condition is imposed once, at the end, exactly as the entry states it.
With $M$ the adjacency matrix,
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
until the working vector was identically zero, which settles every larger $j$ at once.
\end{{proof}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic.

Second, the count was recomputed for the smallest arrays straight from the definition:
enumerate every array of that size, turn each row and each column into a base-${b}$ number with
the first digit most significant, and test the divisibility directly. Neither Horner's rule nor
any residue state is involved, and the published terms came back.

Third, the conjectured recurrence was evaluated directly on the published terms, with no
matrices involved, and holds wherever the proved range and the data overlap.

Fourth, the annihilation test of Lemma~\ref{{lem:crit}} was carried out in exact integer
arithmetic on the whole vector rather than on a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{knuth}} D.~E.~Knuth, \emph{{The Art of Computer Programming}}, Volume 2, 3rd ed.,
Addison--Wesley, 1997. (Evaluation of polynomials, Section 4.6.4.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if h.get('engine') == 'transfer51' and not h.get('FAILS')]
    for h in hits:
        dd = f"build/t51{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
    print('wrote', len(hits), 'papers')
