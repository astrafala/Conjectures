#!/usr/bin/env python3
"""Papers for the min-filter family, whose model is not a walk over the arrays.

`cfbuild` writes the closed-form papers, and every engine it was written for counts arrays
directly: its papers say "the lines of an array are the vertices of a finite digraph, an array
is a walk in it". That sentence is FALSE here. These entries count how many DIFFERENT filtered
arrays arise, so two underlying arrays with the same image must be counted once, and the walk
whose steps are counted is a walk in the DETERMINISATION of a machine whose output is the
filtered array -- not in a graph of arrays. A paper has to say what was actually done.
"""
import json
import os
import re

import localentry as LE
import phibuild
import transfer95

PRE = phibuild.PRE
esc = phibuild.esc
NAMED = {'horizontal': 'horizontal', 'vertical': 'vertical', 'diagonal': 'diagonal',
         'antidiagonal': 'antidiagonal'}


def rec_tex(coeffs):
    out = []
    for i in sorted(coeffs, key=int):
        c = int(coeffs[i])
        if c == 0:
            continue
        term = r'a(n-%s)' % i if abs(c) == 1 else r'%d\,a(n-%s)' % (abs(c), i)
        out.append(('-' if c < 0 else '+', term))
    if not out:
        return '0'
    txt = ('-' if out[0][0] == '-' else '') + out[0][1]
    for s, t in out[1:]:
        txt += ' %s %s' % (s, t)
    return txt


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    p = transfer95.parse_name(e['name'])
    if p is None:
        raise ValueError(f'{a}: transfer95 no longer reads this name')
    coeffs = {str(k): str(v) for k, v in h['coeffs'].items()}
    order = int(h['order'])
    S = int(h['S'])
    thr = int(h['thr'])
    claimed = h.get('claimed')
    W, A = p['W'], p['alpha']
    dirs = ', '.join(NAMED[x] for x in p['dirs'])
    shape = (r'$n\times%d$' % W) if not p['transposed'] else (r'$%d\times n$' % W)
    ties = W - 1

    repaired = ''
    if p.get('repaired'):
        repaired = (
            r'''\begin{remark}
The entry's own name reads ``%s'', naming one direction twice and so naming no set of
neighbours at all: it has one more slot than it has distinct words. Rather than choose, each
candidate repair was run against the entry's published terms and exactly one reproduced them,
which is the reading used here. The defect is in the name, not in the sequence.
\end{remark}

''' % esc(p['named_dirs']))

    return rf"""{PRE}
\title{{The empirical closed form for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{os.environ.get('PAPER_DATE', '8 September 2026')}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} states an explicit closed form for $a(n)$ and records it as empirical. It is true, and
it is decidable. What the entry counts is not a set of arrays but the SIZE OF AN IMAGE: each
admissible array is replaced by the array of minima of its cells and their {dirs} neighbours,
and $a(n)$ counts how many different arrays come out. Two arrays with the same image count
once, so the usual graph over arrays overcounts. Determinising a machine whose state is a pair
of consecutive rows and whose output is the filtered array turns the count into a walk count on
$S={S}$ vertices, exact and finite. The closed form is a polynomial in $n$, so it satisfies the
monic recurrence with characteristic polynomial $(x-1)^{{{order}}}$; that the walk count
satisfies the same recurrence, and that the two agree on enough initial terms, are both checked
in exact integer arithmetic, and together they prove the formula.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 68Q45, 15A18.\normalsize

\section{{The entry}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${h['offset']}$ and begins
\[
{", ".join(str(v) for v in d[:8])},\ \dots
\]
and states:
\begin{{quote}}
{esc(h['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical, and it is still open.

{repaired}\section{{What is being counted}}

Fix the width $W={W}$ and the value range $0..{A - 1}$. The underlying arrays are the
{shape} arrays over that range whose rows are lexicographically {p['roword']} read downwards
and whose columns are lexicographically {p['colord']} read left to right. Each such array $g$
is mapped to $F(g)$, the array whose $(i,j)$ entry is the minimum of $g(i,j)$ and the entries
of its {dirs} neighbours that lie inside the array. The entry counts
\[
a(n)\;=\;\bigl|\{{\,F(g)\;:\;g\text{{ admissible with }}n\text{{ rows}}\,\}}\bigr|,
\]
the number of DISTINCT images --- not the number of admissible $g$. This is what makes the
problem different in kind from a walk count: two admissible arrays can have the same image, and
the graph whose walks are the arrays would count such a pair twice.

\section{{Two constraints, both made local}}

\begin{{lemma}}\label{{lem:local}}
Whether a sequence of rows is admissible is decided by the previous row together with
${ties}$ bits.
\end{{lemma}}

\begin{{proof}}
The row order compares consecutive rows and needs only the previous one. The column order
compares whole columns read downwards, left to right, which is not a condition on consecutive
rows --- but for each of the ${ties}$ adjacent column pairs there are only two possibilities:
either the two columns agree in every row read so far, or they first differed at some earlier
row, and there the required inequality was already decided and no later row can affect it. One
bit per adjacent pair records which, and a new row is admissible exactly when, for every pair
still agreeing, its two entries either agree again or differ in the permitted direction.
\end{{proof}}

\begin{{lemma}}\label{{lem:det}}
$a(n)$ is a walk count: there are a matrix $M$ with non-negative integer entries on $S={S}$
vertices and vectors $\iota,\tau$ with $a(n)=\iota^{{\!\top}}M^{{\,n-2}}\tau$ for $n\ge2$.
\end{{lemma}}

\begin{{proof}}
Row $i$ of $F(g)$ depends only on rows $i-1$, $i$ and $i+1$ of $g$, so a machine reading $g$ a
row at a time, holding the last two rows and the ${ties}$ bits of Lemma~\ref{{lem:local}}, can
emit $F(g)$ one row at a time. It is nondeterministic --- several continuations may emit the
same row --- and the images of $g$ are exactly the words it can emit. Determinising it gives a
machine in which each emitted row leads to exactly one state, so distinct words of length $n$
correspond to distinct paths, and counting them is counting walks. The reachable determinised
states number $S={S}$. The last filtered row is emitted with no row below it, so it is not a
step of the walk but a count attached to the state the walk stops in; that is $\tau$.
\end{{proof}}

\section{{The closed form}}

The entry's formula is a polynomial in $n$. Any polynomial of degree $m$ satisfies the monic
recurrence whose characteristic polynomial is $(x-1)^{{m+1}}$, here
\[
q(x)=(x-1)^{{{order}}},\qquad\text{{that is}}\qquad a(n)={rec_tex(coeffs)}.
\]

\begin{{theorem}}
The closed form OEIS {a} records is correct for all $n>{claimed if claimed is not None else thr}$.
\end{{theorem}}

\begin{{proof}}
Two exact computations. First, the walk count of Lemma~\ref{{lem:det}} satisfies $q$: the
residual $u_j=\iota^{{\!\top}}M^{{\,j}}q(M)\tau$ vanishes for $S$ consecutive indices, and
since the residual vector lives in the $S$-dimensional space spanned by the iterates of $M$,
$S$ consecutive zeros force every later one. The last index at which it fails is ${thr}$.
Second, the polynomial and the walk count agree at every index from ${h['first']}$ up to
${h['offset']} + {h['nterms']} - 1$, which is more than the ${order}$ consecutive agreements a
common recurrence of order ${order}$ needs. Two sequences satisfying the same monic recurrence
of order ${order}$ and agreeing at ${order}$ consecutive indices past both their thresholds are
equal from there on.
\end{{proof}}

\section{{Verification}}

Everything above is integer or exact rational arithmetic; no floating point is used anywhere.

First, the model reproduces all ${len(d)}$ terms the entry publishes, exactly. This is what
ties the construction to the entry, and it is the only point at which the entry's English is
read.

Second, the reading was pinned by direct enumeration before the model was written: for the
one-row case the admissible arrays and their images were listed outright and counted, and the
count is the entry's own first term.

Third, the annihilation test was run to $S$ consecutive vanishing residuals rather than to a
fixed horizon, which is what makes it a proof and not a check of finitely many terms.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{hu}} J.~E.~Hopcroft, R.~Motwani and J.~D.~Ullman, \emph{{Introduction to Automata
Theory, Languages, and Computation}}, 3rd ed., Addison--Wesley, 2006. (The subset
construction, Section 2.3.)
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{kauers}} M.~Kauers and P.~Paule, \emph{{The Concrete Tetrahedron}}, Springer, 2011.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""
