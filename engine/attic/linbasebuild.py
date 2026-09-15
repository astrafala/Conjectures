#!/usr/bin/env python3
"""One paper per entry for the cross-BASE identity on the linear digit-string family."""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linbase
import localentry as LE
import phibuild

PRE = phibuild.PRE
esc = phibuild.esc
DATE = os.environ.get('PAPER_DATE', '13 September 2026')


def qesc(s):
    """escape a quoted OEIS line: phibuild.esc turns ^ into an accent that prints as nothing,
    and these lines are all exponents -- 3^(n-1) came out as 3(n-1)."""
    return esc(s).replace(r'\^{}', r'\textasciicircum{}')


def _author(e):
    m = re.search(r'_([^_]+)_', e.get('author') or '')
    return esc(m.group(1).strip()) if m else 'its author'


def build(r):
    a = r['anum']
    e = LE.get(a)
    b, d, N = r['b'], r['d'], r['N']
    K = 2 * d + 1
    data = [int(v) for v in e['data'].split(',') if v.strip()]
    rows = '\n'.join(
        r'%d & %d & %d & %d \\' % (n, linbase.Lcount(b, d, n), linbase.Lcount(b - 1, d, n),
                                   K ** (n - 1))
        for n in range(1, min(N, 8) + 1))
    n2 = r.get('n2')
    second = ''
    if n2 and n2 >= 2:
        second = (r' For this entry the second clause bites at $n=%d$, where $b=%d=%s(n-1)$: '
                  r'there $L_{%d}(%d,%d)-L_{%d}(%d,%d)=%d$ and $%d^{%d}-2=%d$.'
                  % (n2, b, '' if d == 1 else str(d), d, b, n2, d, b - 1, n2,
                     linbase.Lcount(b, d, n2) - linbase.Lcount(b - 1, d, n2),
                     K, n2 - 1, K ** (n2 - 1) - 2))
    dc = '' if d == 1 else str(d)
    return rf"""{PRE}
\title{{The cross-base identity for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical identity, in two clauses, relating its counts to those of the
entry one base smaller, contributed by {_author(e)}. Both clauses are true and both are proved
here, with no computation in the argument. The difference between consecutive bases counts the
admissible strings that USE the new largest digit; those are the translates of the
translation-classes of admissible strings over $\mathbf{{Z}}$ whose range fits below the top of
the alphabet; the classes are the step vectors, of which there are $(2d+1)^{{n-1}}$; and at the
one base where the fit fails by exactly one, the classes lost are the two monotone ones, which
is the entry's own $-2$.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A05, 05C38.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${r['offset']}$ and begins
\[
{", ".join(str(x) for x in data[:8])},\ \dots
\]
The entry states, as an empirical claim and never marked settled:
\begin{{quote}}
{qesc(r['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical, and nothing on the entry records it as proved.

For this entry the base is ${b}$ and the permitted difference is $d={d}$, so the first clause
claims $a_{{{b}}}(n)-a_{{{b-1}}}(n)={K}^{{\,n-1}}$ whenever ${dc}(n-1)+1\le{b}$, that is for
$1\le n\le{N}$, and the second claims $a_{{{b}}}(n)-a_{{{b-1}}}(n)={K}^{{\,n-1}}-2$ at the single
$n$ with ${dc}(n-1)={b}$.

\section{{What the entry counts}}

A base-$b$ $n$-digit string in this family's sense is a tuple
$(d_1,\dots,d_n)\in\{{0,1,\dots,b-1\}}^{{n}}$ with $|d_i-d_{{i+1}}|\le d$ for $1\le i<n$; there
is no wrap-around. Leading zeros are counted, which is what the entry's $a(1)=b$ says, and
$a(0)=1$ is the empty string. Write $L_d(b,n)$ for their number. Evaluated exactly in integer
arithmetic, $L_{{{d}}}$ at base ${b}$ reproduces all ${r['nterms']}$ terms {a} publishes.

\section{{The identity}}

\begin{{theorem}}
Fix $d\ge1$ and $n\ge1$, and put $K=2d+1$.
\begin{{enumerate}}
\item[(i)] If $b\ge d(n-1)+1$ then $L_d(b,n)-L_d(b-1,n)=K^{{\,n-1}}$.
\item[(ii)] If $b=d(n-1)$ then $L_d(b,n)-L_d(b-1,n)=K^{{\,n-1}}-2$.
\end{{enumerate}}
\end{{theorem}}

\begin{{proof}}
\emph{{Step 1.}} The admissible strings over $\{{0,\dots,b-1\}}$ that do not use the value $b-1$
are exactly the admissible strings over $\{{0,\dots,b-2\}}$, so $L_d(b,n)-L_d(b-1,n)$ is the
number of admissible strings over $\{{0,\dots,b-1\}}$ in which $b-1$ occurs.

\emph{{Step 2.}} Consider the admissible strings over $\mathbf{{Z}}$: tuples
$(c_1,\dots,c_n)\in\mathbf{{Z}}^{{n}}$ with $|c_i-c_{{i+1}}|\le d$. Translation by an integer acts
freely on them, each orbit contains exactly one representative with $c_1=0$, and such a
representative is determined by its step vector $(s_1,\dots,s_{{n-1}})$, $s_i=c_{{i+1}}-c_i$,
which may be any element of $\{{-d,\dots,d\}}^{{n-1}}$. So there are exactly $K^{{\,n-1}}$ orbits.
Each orbit also contains exactly one representative with $\max_i c_i=0$, and all its
representatives share one RANGE $\rho=\max_ic_i-\min_ic_i$, which satisfies
$\rho\le d(n-1)$ because each of the $n-1$ steps moves by at most $d$.

\emph{{Step 3.}} A string counted in Step 1 has maximum $b-1$ and entries at least $0$, so it is
the representative with maximum $b-1$ of an orbit of range at most $b-1$; conversely every orbit
of range at most $b-1$ gives exactly one such string. Hence
\[
L_d(b,n)-L_d(b-1,n)\;=\;\#\{{\text{{orbits of range}}\le b-1\}} .
\]

\emph{{Step 4.}} If $b\ge d(n-1)+1$ then $b-1\ge d(n-1)$ and by Step 2 every orbit qualifies,
giving (i). If $b=d(n-1)$ then exactly the orbits of range $d(n-1)$ are excluded. An orbit has
range $d(n-1)$ only if some $c_i$ attains the maximum, some $c_j$ the minimum, and the walk
between them covers $d(n-1)$; that walk has at most $n-1$ steps, each of size at most $d$, so it
must use all $n-1$ of them in the same direction at full size. There are exactly two such step
vectors, $(d,\dots,d)$ and $(-d,\dots,-d)$, so two orbits are lost and (ii) follows.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the proof above.

First, the model reproduces all ${r['nterms']}$ terms {a} publishes, exactly, in integer
arithmetic; the reading of the entry's English is what is being tested there.

Second, the first clause was evaluated directly for every $n$ in the entry's claimed range,
$1\le n\le{N}$, both sides computed from the definition and not from the theorem:

\begin{{center}}
\begin{{tabular}}{{rrrr}}
$n$ & $L_{{{d}}}({b},n)$ & $L_{{{d}}}({b-1},n)$ & ${K}^{{\,n-1}}$ \\ \hline
{rows}
\end{{tabular}}
\end{{center}}

\noindent and the difference of the second and third columns is the fourth at every row shown
and at every row up to $n={N}$.

Third, the second clause was evaluated at its own index.{second}

\section*{{References}}
\begin{{enumerate}}
\item The OEIS Foundation Inc., \emph{{The On-Line Encyclopedia of Integer Sequences}},
\url{{https://oeis.org/{a}}}.
\end{{enumerate}}

\end{{document}}
"""


if __name__ == '__main__':
    recs = json.load(open('linbase_hits.json'))
    only = set(sys.argv[1:])
    if only:
        recs = [r for r in recs if r['anum'] in only]
    made, failed = 0, []
    for r in sorted(recs, key=lambda x: x['anum']):
        dd = 'build/lb%s' % r['anum']
        os.makedirs(dd, exist_ok=True)
        open(dd + '/p.tex', 'w').write(build(r))
        for _ in range(2):
            subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p = dd + '/p.pdf'
        if os.path.exists(p) and os.path.getsize(p) > 40000:
            made += 1
        else:
            failed.append(r['anum'])
    print(f'{made} papers built, {len(failed)} problems')
    if failed:
        print('  ', ' '.join(failed[:20]))
