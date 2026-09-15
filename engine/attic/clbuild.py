#!/usr/bin/env python3
"""One paper per CLOSED FORM settled against the Ehrhart model.

Most of Hardin's fixed-length entries carry an empirical RECURRENCE and the sweep settles
those. A few carry an empirical polynomial instead --- "Empirical: a(n) = (16/3)*n^3 -
(4/3)*n" --- and the recurrence sweep passes them over because there is no recurrence to
parse. The same model settles them and the argument is shorter: `latpoly' gives a(n) exactly
and a derived monic annihilator A of order S, a polynomial of degree d is annihilated by
(z-1)^(d+1), so the difference is annihilated by A(z)(z-1)^(d+1) and S + d + 1 consecutive
agreements force agreement everywhere.
"""
import json
import os
import re
import sys

import localentry as LE
import phibuild
import qpbuild

PRE = phibuild.PRE
esc = phibuild.esc
DATE = os.environ.get('PAPER_DATE', '13 September 2026')


def build(h):
    a = h['anum']
    S, d = h['S'], h['deg']
    e = LE.get(a)
    data = [int(v) for v in e['data'].split(',') if v.strip()]
    off = int(e['offset'].split(',')[0])
    conj = h['line']
    return rf"""{PRE}
\title{{The empirical closed form for OEIS {a}, proved from an exact model}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical closed form: a polynomial in $n$ of degree ${d}$, recorded on the
entry and never marked settled. It is true. The entry's count is given exactly by an Ehrhart
quasi-polynomial, from which $a$ provably satisfies a monic linear recurrence of order $S={S}$
derived below; a polynomial of degree ${d}$ satisfies $(z-1)^{{{d}+1}}$; so the difference
satisfies the product, and ${S}+{d}+1$ consecutive agreements settle it. No transfer matrix is
involved and the count is not a walk.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A19, 11P21.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in data[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical, and nothing on the entry records it as proved.
{qpbuild._model('latpoly', h, e)}
\section{{The proof}}

\begin{{theorem}}
The empirical closed form holds for every $n$.
\end{{theorem}}

\begin{{proof}}
Write $P$ for the claimed polynomial and $r(n)=a(n)-P(n)$. The annihilator $A$ derived above
kills $a$, and $(z-1)^{{{d}+1}}$ kills $P$, so $A(z)(z-1)^{{{d}+1}}$ --- monic, of order
${S}+{d}+1$ --- kills $r$. The model was evaluated exactly in integer arithmetic and $P$ in
exact rational arithmetic at every index from $n={off}$ to $n={off}+{S}+{d}+1$, and $r$ vanished
at all of them. A monic recurrence with ${S}+{d}+1$ consecutive zeros has every later term zero,
so $r\equiv0$.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the model reproduces all ${len(data)}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the model to the entry: it is built by reading the entry's
English, and a misreading gives different counts.

Second, the claimed polynomial was evaluated directly on those published terms, in exact
rational arithmetic and with no model involved, and agrees with every one of them.

Third, the derived annihilator was itself tested on terms the model was not asked for: the
model was evaluated beyond the $S$ values that determine it and $A$ reproduced them. A bound
that is too small fails this test, which is why it is run.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{beckrobins}} M.~Beck and S.~Robins, \emph{{Computing the Continuous Discretely}},
2nd ed., Springer, 2015. (Ehrhart quasi-polynomials and their periods.)
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    import subprocess
    v = json.load(open('deep-check/latpoly-closed-verdicts.json'))
    made, bad = 0, []
    for a, r in sorted(v.items()):
        if not r.get('ok'):
            continue
        h = dict(r, anum=a, engine='latpoly')
        dd = 'build/cl%s' % a
        os.makedirs(dd, exist_ok=True)
        open(dd + '/p.tex', 'w').write(build(h))
        for _ in range(2):
            subprocess.run(['pdflatex', '-interaction=nonstopmode', 'p.tex'], cwd=dd,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(dd + '/p.pdf') and os.path.getsize(dd + '/p.pdf') > 50000:
            made += 1
        else:
            bad.append(a)
    print('closed-form papers built', made, 'problems', bad)
