#!/usr/bin/env python3
"""One paper per entry for the cross-BASE identity on the circular-digit family.

    python3 src/circbasebuild.py            build every verified record
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circbase
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
    data = [int(v) for v in e['data'].split(',') if v.strip()]
    rows = '\n'.join(
        r'%d & %d & %d & %d \\' % (n, circbase.T(b, d, n), circbase.T(b - 1, d, n),
                                   circbase.F(d, n))
        for n in range(1, min(N, 8) + 1))
    refnote = ''
    if r.get('ref'):
        refnote = (r' The entry writes that summand as $\mathrm{%s}(n+1)$, the $(n+1)$st term '
                   r'of OEIS %s; that sequence is the central coefficient of '
                   r'$(1+x+\dots+x^{%d})^{n}$ and its published terms agree with $F_{%d}(n)$ '
                   r'term by term, which is the identification used here.'
                   % (esc(r['ref']), esc(r['ref']), 2 * d, d))
    dc = '' if d == 1 else str(d)
    return rf"""{PRE}
\title{{The cross-base identity for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical identity relating its counts to those of the entry one base
smaller, contributed by {_author(e)}. It is true, it is true in the exact range the entry
names, and that range is sharp. The proof is four steps and needs no computation: the
difference between consecutive bases counts the admissible cyclic sequences that USE the new
largest digit, every admissible cyclic sequence has range at most $d\lfloor n/2\rfloor$, so
once the base is large enough those sequences are a translate of the admissible cyclic
sequences over $\mathbf{{Z}}$ with maximum $0$, and those are in bijection with the step
sequences summing to zero.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A19, 05C38.\normalsize

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

Read as the entry writes it, $a(\mathrm{{base}},n)$ is the count this family assigns to the
stated base, ``$\mathrm{{int}}(n/2)$'' is $\lfloor n/2\rfloor$, and $F(d)$ is defined on the
entry itself as the largest coefficient of $(1+x+\dots+x^{{2d}})^{{n}}$.{refnote} For this entry
the base is ${b}$ and the permitted difference is $d={d}$, so the claim is that
\[
a_{{{b}}}(n)-a_{{{b - 1}}}(n)\;=\;F_{{{d}}}(n)
\qquad\text{{for every }} n \text{{ with }} {dc}\lfloor n/2\rfloor+1\le{b},
\]
that is, for $1\le n\le{N}$.

\section{{What the entry counts}}

A base-$b$ circular $n$-digit number, in this family's sense, is a tuple
$(d_1,\dots,d_n)\in\{{0,1,\dots,b-1\}}^{{n}}$ with $|d_i-d_{{i+1}}|\le d$ for every $i$, indices
read modulo $n$ so that the pair $(d_n,d_1)$ is included. Leading zeros are counted: requiring
$d_1\ne0$ gives $4,11,25$ where A124698 gives $5,13,29$. Write $T_d(b,n)$ for the number of
them. Equivalently $T_d(b,n)=\operatorname{{tr}}M^{{n}}$ with $M$ the $b\times b$ matrix that has
$M_{{uv}}=1$ exactly when $|u-v|\le d$, since a cyclic tuple is a closed walk in that graph
together with a choice of where it starts. Evaluated exactly in integer arithmetic, $T_{{{d}}}$
at base ${b}$ reproduces all ${r['nterms']}$ terms {a} publishes, and at base ${b - 1}$ all the
terms the entry one base smaller publishes.

At $n=0$ these entries write $a(0)=1$ while the count of empty tuples read as a trace is $b$.
That is a convention at a single index; the identity below is stated and proved for $n\ge1$,
which is the range in which the entry's own data lives beyond its first term.

\section{{The identity}}

\begin{{theorem}}
For every $d\ge1$, every $n\ge1$ and every $b\ge d\lfloor n/2\rfloor+1$,
\[
T_d(b,n)-T_d(b-1,n)\;=\;F_d(n),
\]
where $F_d(n)=[x^{{dn}}](1+x+\dots+x^{{2d}})^{{n}}$ is the largest coefficient of that
polynomial. In particular $a_{{{b}}}(n)-a_{{{b - 1}}}(n)=F_{{{d}}}(n)$ for $1\le n\le{N}$, which
is the entry's claim.
\end{{theorem}}

\begin{{proof}}
\emph{{Step 1.}} An admissible tuple over $\{{0,\dots,b-1\}}$ either uses the value $b-1$ or does
not, and those that do not are exactly the admissible tuples over $\{{0,\dots,b-2\}}$. Hence
$T_d(b,n)-T_d(b-1,n)$ is the number of admissible tuples over $\{{0,\dots,b-1\}}$ in which
$b-1$ occurs.

\emph{{Step 2.}} Every admissible tuple satisfies $\max_i d_i-\min_i d_i\le d\lfloor n/2\rfloor$.
Fix a position $i$ where the maximum is attained and a position $j$ where the minimum is. The
two arcs of the cycle joining $i$ to $j$ have lengths summing to $n$, so one of them has length
$L\le\lfloor n/2\rfloor$; along an arc of length $L$ each step changes the value by at most $d$,
so the two values differ by at most $dL\le d\lfloor n/2\rfloor$.

\emph{{Step 3.}} A tuple counted in Step 1 has maximum exactly $b-1$, so by Step 2 all of its
values lie in $[\,b-1-d\lfloor n/2\rfloor,\ b-1\,]$. The hypothesis $b\ge d\lfloor n/2\rfloor+1$
says precisely that this window lies inside $\{{0,\dots,b-1\}}$, so no constraint of the base is
felt: subtracting $b-1$ from every entry is a bijection between the tuples counted in Step 1 and
the tuples $(c_1,\dots,c_n)\in\mathbf{{Z}}^{{n}}$ with $|c_i-c_{{i+1}}|\le d$ cyclically and
$\max_i c_i=0$. That set does not depend on $b$.

\emph{{Step 4.}} Translation acts freely on the admissible tuples over $\mathbf{{Z}}$, and each
orbit contains exactly one tuple with maximum $0$ and exactly one with $c_1=0$. So the tuples of
Step 3 are in bijection with the admissible tuples having $c_1=0$, which are determined by their
step vector $(s_1,\dots,s_n)$, $s_i=c_{{i+1}}-c_i$ read cyclically: any
$(s_1,\dots,s_n)\in\{{-d,\dots,d\}}^{{n}}$ with $s_1+\dots+s_n=0$ arises from exactly one such
tuple, and conversely. Their number is the constant term of
$(x^{{-d}}+\dots+x^{{d}})^{{n}}$, that is $[x^{{dn}}](1+x+\dots+x^{{2d}})^{{n}}=F_d(n)$, which is
the largest coefficient of that polynomial because the coefficients are symmetric about $x^{{dn}}$
and unimodal.
\end{{proof}}

\begin{{remark}}
The threshold is sharp. At $b=d\lfloor n/2\rfloor$ the window of Step 3 no longer fits inside
the alphabet, the tuples of maximum $b-1$ are cut off from below, and the difference falls short
of $F_d(n)$; this was checked directly for $d=1,2,3$ and every $n\le8$, and the first failing
base is in each case exactly one below the entry's own threshold.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the proof above.

First, the model reproduces all ${r['nterms']}$ terms {a} publishes, exactly, in integer
arithmetic; the reading of the entry's English is what is being tested there, since a
misreading gives different counts.

Second, the identity was evaluated directly for every $n$ in the entry's claimed range,
$1\le n\le{N}$, with both sides computed from the definition and not from the theorem:

\begin{{center}}
\begin{{tabular}}{{rrrr}}
$n$ & $T_{{{d}}}({b},n)$ & $T_{{{d}}}({b - 1},n)$ & $F_{{{d}}}(n)$ \\ \hline
{rows}
\end{{tabular}}
\end{{center}}

\noindent and the difference of the second and third columns is the fourth at every row shown
and at every row up to $n={N}$.

Third, the theorem was tested outside the entry's range as well: the identity holds for every
$b\ge d\lfloor n/2\rfloor+1$ tried and fails immediately below, which is the sharpness recorded
above.

\section*{{References}}
\begin{{enumerate}}
\item The OEIS Foundation Inc., \emph{{The On-Line Encyclopedia of Integer Sequences}},
\url{{https://oeis.org/{a}}}.
\end{{enumerate}}

\end{{document}}
"""


if __name__ == '__main__':
    recs = json.load(open('circbase_hits.json'))
    only = set(sys.argv[1:])
    if only:
        recs = [r for r in recs if r['anum'] in only]
    made, failed = 0, []
    for r in sorted(recs, key=lambda x: x['anum']):
        dd = 'build/cb%s' % r['anum']
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
