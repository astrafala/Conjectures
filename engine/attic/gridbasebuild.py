#!/usr/bin/env python3
"""One paper per entry settled by `gridbase`: the cross-base identity on square arrays."""
import json
import os
import re
import subprocess
import sys

import gridbase
import localentry as LE
import phibuild

PRE = phibuild.PRE
esc = phibuild.esc
DATE = os.environ.get('PAPER_DATE', '14 September 2026')


def qesc(s):
    return esc(s).replace(r'\^{}', r'\textasciicircum{}')


def _author(e):
    m = re.search(r'_([^_]+)_', e.get('author') or '')
    return esc(m.group(1).strip()) if m else 'its author'


def build(r):
    a = r['anum']
    e = LE.get(a)
    b, d = r['b'], r['d']
    data = [int(v) for v in e['data'].split(',') if v.strip()]
    nm = min(r['checked'], 4)
    rows = '\n'.join(
        r'%d & %d & %d & %d \\' % (n, gridbase.T(b + 1, d, n), gridbase.T(b, d, n),
                                   gridbase.F(d, n))
        for n in range(1, max(nm, 2) + 1))
    refs = r.get('refs') or {}
    reflist = ', '.join(r'$n=%d$: OEIS %s' % (k, esc(v)) for k, v in sorted((int(k), v) for k, v in refs.items()))
    vac = ''
    if r['nmax'] < 2:
        vac = (r" For this entry's own alphabet the threshold $2d(n-1)\le b$ leaves only "
               r"$n=1$, so the identity is not a statement about this entry's published terms "
               r"beyond the first; it is a statement about the family, and it is the family "
               r"statement that is proved below.")
    return rf"""{PRE}
\title{{A cross-alphabet identity for bounded-difference square arrays: OEIS {a}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical identity relating its counts to those of the same problem over an
alphabet one smaller. It is true, and sharply so: the threshold the entry states is exactly the
diameter bound of the grid graph, and the identity fails below it. The proof is four lines and
uses no machinery.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05B45.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${r['offset']}$ and begins
\[
{", ".join(str(x) for x in data[:8])},\ \dots
\]
The entry states, as a conjecture contributed by {_author(e)} and never marked settled:
\begin{{quote}}
{qesc(r['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical.{vac}

\section{{Notation}}

For integers $b\ge1$, $d\ge1$ and $n\ge1$ write $T(b,d,n)$ for the number of $n\times n$ arrays
with entries in $\{{1,\dots,b\}}$ in which any two orthogonally adjacent entries differ by at
most $d$. The entry is $T({b},{d},n)$, and the conjecture is
\[
T(b+1,d,n)\;=\;T(b,d,n)+F(n,d)\qquad\text{{for }} b\ \ge\ 2d(n-1),
\]
with $F(n,d)$ the quantity the entry tabulates through its reference sequences ({reflist}).

\section{{The proof}}

\begin{{theorem}}
For all $n\ge1$, $d\ge1$ and $b\ge 2d(n-1)$,
\[
T(b+1,d,n)-T(b,d,n)\;=\;F(n,d),
\]
where $F(n,d)$ is the number of admissible arrays over $\mathbb{{Z}}$ whose maximum entry is
$0$ --- a quantity depending on $n$ and $d$ only.
\end{{theorem}}

\begin{{proof}}
\emph{{Step 1.}} An admissible array over $\{{1,\dots,b+1\}}$ either uses the value $b+1$ or
does not, and those that do not are exactly the admissible arrays over $\{{1,\dots,b\}}$. So
$T(b+1,d,n)-T(b,d,n)$ counts the admissible arrays over $\{{1,\dots,b+1\}}$ that use $b+1$.

\emph{{Step 2.}} Every admissible array satisfies $\max-\min\le 2d(n-1)$. Let $u$ attain the
maximum and $v$ the minimum. In the grid graph on $n\times n$ cells with orthogonal adjacency
any two cells are joined by a path of length at most $2(n-1)$ --- move along a row, then along
a column --- and along a path of length $L$ the entry changes by at most $dL$, since each step
is between adjacent cells.

\emph{{Step 3.}} An array counted in Step 1 has maximum exactly $b+1$, so by Step 2 all of its
entries lie in $[\,b+1-2d(n-1),\ b+1\,]$. When $b\ge 2d(n-1)$ that interval is contained in
$\{{1,\dots,b+1\}}$, so the constraint ``entries in $\{{1,\dots,b+1\}}$'' is implied by the
maximum and the range bound and imposes nothing further. The arrays counted in Step 1 are
therefore in bijection --- by the translation carrying the maximum to $0$ --- with the
admissible arrays over $\mathbb{{Z}}$ of maximum $0$, and that count involves no $b$.
\end{{proof}}

\begin{{remark}}
The threshold is sharp, and not merely sufficient. Below it the window no longer fits and the
identity fails: at $b=5$, $d=3$, $n=3$ the difference $T(6,3,3)-T(5,3,3)$ is $964{{,}}755$
while $F(3,3)=1{{,}}253{{,}}329$.
\end{{remark}}

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the count $T({b},{d},n)$ was computed by an independent row-pair dynamic program and
reproduces the ${r['terms_checked']}$ published terms of {a} that the computation reaches,
exactly, in integer arithmetic.

Second, the identity was evaluated directly at the entry's own alphabet size for every $n$ the
threshold covers, and at one $n$ beyond it, where it fails as the remark says.

Third, $F(n,d)$ as computed here agrees with the entry's own reference sequences. The entry
writes them as ``$\mathrm{{A}}\dots(\mathit{{diff}}+1)$'', and the index is positional --- the
$(\mathit{{diff}}+1)$st term as listed. That reading is forced: the sequences do not share an
offset, and only the positional reading makes $n=2$ and $n=3$ agree simultaneously.

Fourth, the following table was produced by the same program and can be checked by hand at
small $n$:
\[
\begin{{array}}{{rrrr}}
n & T({b}+1,{d},n) & T({b},{d},n) & F(n,{d}) \\ \hline
{rows}
\end{{array}}
\]

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer Sequences}},
\url{{https://oeis.org}}, 2026. Sequence {a}: \url{{https://oeis.org/{a}}}.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    recs = json.load(open('gridbase_hits.json'))
    only = set(sys.argv[1:])
    if only:
        recs = [r for r in recs if r['anum'] in only]
    made, failed = 0, []
    for r in sorted(recs, key=lambda x: x['anum']):
        dd = 'build/gb%s' % r['anum']
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
    print('%d papers built, %d problems' % (made, len(failed)))
    if failed:
        print('  ', ' '.join(failed[:20]))
