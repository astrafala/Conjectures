#!/usr/bin/env python3
"""Papers for the plane-partition-in-a-box family."""
import os, json, re
import localentry as LE, phibuild

PRE = phibuild.PRE
esc = phibuild.esc


def gf_tex(N):
    out = []
    for k, c in enumerate(N):
        c = int(c)
        if c == 0:
            continue
        b = '' if (abs(c) == 1 and k > 0) else str(abs(c))
        if k == 0:
            t = b or '1'
        elif k == 1:
            t = b + 'x'
        else:
            t = b + f'x^{{{k}}}'
        out.append(('-' if c < 0 else '+') + ' ' + t)
    s = ' '.join(out)
    return s[2:] if s.startswith('+ ') else s


def build(h):
    a = h['anum']
    P, Q, off = h['P'], h['Q'], h['offset']
    e = LE.get(a)
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    modf, rev = e['modified'], e['revision']
    dn, dd, pts = h['degnum'], h['degden'], h['points']
    D = P * Q
    quoted = []
    if h['emp']:
        quoted.append(esc(h['emp']))
    if h['gf']:
        quoted.append(esc(h['gf']))
    gfsec = ''
    if h['gf']:
        gfsec = rf"""
\section{{The generating function}}

By Theorem~\ref{{thm:poly}} the sequence is a polynomial in $n$ of degree ${D}$, and a sequence
that is a polynomial of degree $D$ in its index has generating function $N(x)/(1-x)^{{D+1}}$
with $\deg N\le D$; the coefficients of $N$ are the $(D+1)$-fold finite differences of the
first $D+1$ terms, so $N$ is determined by them and by nothing else. Carrying that out in exact
integer arithmetic gives
\[
\sum_{{n\ge0}}a(n)x^n\;=\;\frac{{{gf_tex(h['gfnum'])}}}{{(1-x)^{{{D + 1}}}}},
\]
which is the generating function conjectured on the entry.
"""
    return rf"""{PRE}
\title{{The empirical product formula for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts ${P}\times{Q}$ matrices over $\{{0,\dots,n\}}$ whose rows and columns are
nondecreasing, and carries a product formula for $a(n)$ marked empirical. Reversing rows and
columns turns such a matrix into a plane partition inside a ${P}\times{Q}\times n$ box, so
MacMahon's box theorem applies; the triple product telescopes in its third index and leaves a
polynomial in $n$ of degree ${D}$. The entry's own expression, cleared of its denominator,
becomes an identity between two polynomials of bounded degree, and is therefore settled by a
finite exact computation. The box count itself is classical and is already recorded on this
entry; what is proved here is the entry's own formula{', and the generating function conjectured for it' if h['gf'] else ''}.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A17, 05A19.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:6])},\ \dots
\]
The entry states, as conjectures contributed by its author and never marked settled:
\begin{{quote}}
{chr(10).join(x + chr(10) for x in quoted)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) these are still
recorded as empirical, and nothing on the entry records them as proved.

\section{{What is being counted}}

A matrix $x$ of shape ${P}\times{Q}$ with entries in $\{{0,\dots,n\}}$, nondecreasing along
every row and down every column, becomes, on reversing the order of the rows and of the
columns, an array that is NONINCREASING along rows and down columns with the same entries. That
is exactly a plane partition whose parts are at most $n$ and whose shape fits inside a
${P}\times{Q}$ rectangle --- a plane partition in a ${P}\times{Q}\times n$ box. The
correspondence is a bijection, being an involution on arrays, so
\[
a(n)\;=\;\mathrm{{PP}}({P},{Q},n).
\]
Note which parameter grows: the shape is FIXED and it is the alphabet $0..n$ that $n$ counts,
so nothing about transfer matrices applies here.

\section{{The box count is a polynomial}}

\begin{{theorem}}[MacMahon]\label{{thm:mm}}
\[
\mathrm{{PP}}(p,q,r)\;=\;\prod_{{i=1}}^{{p}}\prod_{{j=1}}^{{q}}\prod_{{k=1}}^{{r}}
\frac{{i+j+k-1}}{{i+j+k-2}} .
\]
\end{{theorem}}

This is classical; see Stanley~\cite{{stanley}}, and it is already recorded on this entry.

\begin{{theorem}}\label{{thm:poly}}
\[
a(n)\;=\;\prod_{{i=1}}^{{{P}}}\prod_{{j=1}}^{{{Q}}}\frac{{n+i+j-1}}{{i+j-1}},
\]
a polynomial in $n$ of degree ${D}$ with rational coefficients.
\end{{theorem}}

\begin{{proof}}
In Theorem~\ref{{thm:mm}} the inner product over $k$ telescopes: for fixed $i$ and $j$,
\[
\prod_{{k=1}}^{{n}}\frac{{i+j+k-1}}{{i+j+k-2}}\;=\;\frac{{n+i+j-1}}{{i+j-1}} ,
\]
every other factor cancelling against its neighbour. The remaining double product has
${P}\cdot{Q}={D}$ factors, each linear in $n$, and the denominators are constants.
\end{{proof}}

So $a$ is a polynomial, and no appeal to Ehrhart theory or to any general position argument is
needed to see it.

\section{{The entry's expression}}

The entry writes $s=p+q+r-1$ with $(p,q,r)=(n,{Q},{P})$ and claims
\[
a(n)\;=\;\prod_{{i=0}}^{{{P}-1}}\binom{{s}}{{n+i}}\,\frac{{i!}}{{(s-i)^{{{P}-1-i}}}}\;=\;
\frac{{N(n)}}{{D(n)}} .
\]

\begin{{lemma}}\label{{lem:deg}}
$N$ and $D$ are polynomials in $n$ of degrees ${dn}$ and ${dd}$ respectively.
\end{{lemma}}

\begin{{proof}}
With $s=n+{Q}+{P}-1$ one has $s-(n+i)={Q}+{P}-1-i$, a constant, so
\[
\binom{{s}}{{n+i}}=\binom{{s}}{{{Q}+{P}-1-i}}
=\frac{{(s-{Q}-{P}+2+i)(s-{Q}-{P}+3+i)\cdots s}}{{({Q}+{P}-1-i)!}},
\]
a polynomial in $n$ of degree ${Q}+{P}-1-i$. Multiplying over $i=0,\dots,{P}-1$ gives
$\deg N=\sum_{{i=0}}^{{{P}-1}}({Q}+{P}-1-i)={dn}$. The denominator is
$\prod_{{i=0}}^{{{P}-1}}(s-i)^{{{P}-1-i}}$, of degree
$\sum_{{i=0}}^{{{P}-1}}({P}-1-i)={dd}$, and it does not vanish for $n\ge0$.
\end{{proof}}

\begin{{theorem}}
The entry's expression equals $a(n)$ for every $n\ge0$.
\end{{theorem}}

\begin{{proof}}
By Theorem~\ref{{thm:poly}} and Lemma~\ref{{lem:deg}}, $a(n)D(n)-N(n)$ is a polynomial in $n$
of degree at most ${D}+{dd}={dn}$. It was evaluated in exact rational arithmetic at
$n=0,1,\dots,{dn}$, that is at ${pts}$ points, and vanishes at all of them; a nonzero polynomial
of degree at most ${dn}$ has at most ${dn}$ roots, so it is identically zero. Since $D(n)\neq0$
for $n\ge0$, the two expressions agree there.
\end{{proof}}
{gfsec}
\section{{Verification}}

Three checks, each independent of the algebra above.

First, Theorem~\ref{{thm:poly}} reproduces all ${h['nterms']}$ terms the entry publishes,
exactly, in integer arithmetic.

Second, the matrices themselves were counted for the smallest alphabets, directly from the
definition: the nondecreasing rows were listed and the chains of ${P}$ of them increasing
componentwise counted, with no product formula and no plane partitions anywhere. The counts
agree, which is what ties the reversal bijection to the entry's own wording.

Third, the polynomial identity was evaluated over the whole range $n=0,\dots,{dn}$ rather than
sampled, in exact rational arithmetic.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 2, Cambridge
University Press, 1999. (Plane partitions with bounded part size, Section 7.21.)
\bibitem{{macmahon}} P.~A.~MacMahon, \emph{{Combinatory Analysis}}, Volume 2, Cambridge
University Press, 1916.
\bibitem{{andrews}} G.~E.~Andrews, \emph{{The Theory of Partitions}}, Addison--Wesley, 1976.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('transfer79_hits.json')):
        if h.get('FAILS'):
            continue
        dd = f"build/t79{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
        n += 1
    print('wrote', n, 'papers')
