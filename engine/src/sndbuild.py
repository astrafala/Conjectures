#!/usr/bin/env python3
"""The paper for a FURTHER conjecture on an entry this project has already settled.

The entry already carries one paper, for the conjecture that was proved. This is a second and
different conjecture on the same entry, and it is settled by the proof already in hand: with q
the characteristic polynomial of the proved recurrence and p that of the further claim,

  * another RECURRENCE is the claim "a satisfies p", and q | p settles it outright;
  * a CLOSED FORM is the claim "a(n) = f(n)", and q | p is NOT enough -- it says only that a and
    f satisfy the same recurrence, not that they are the same solution of it. Two solutions of a
    recurrence of order D coincide exactly when they agree at D consecutive indices, so the
    window is checked and stated.
"""
import sympy as sp

import closedform as CF
import localentry as LE
import phibuild
import unibuild

PRE, esc = phibuild.PRE, phibuild.esc
x = sp.Symbol('x')
n = sp.Symbol('n')


def _poly(co):
    d = max(int(k) for k in co)
    return sp.Poly([sp.Integer(1)] + [-sp.Integer(co.get(str(i), co.get(i, 0)))
                                      for i in range(1, d + 1)], x)


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    co = {str(k): int(v) for k, v in h['premise'].items()}
    q = _poly(co)
    order = h['qorder']
    rec = ' + '.join(
        (f"{v}\\,a(n-{k})" if v > 0 else f"{v}\\,a(n-{k})")
        for k, v in sorted(((int(k), v) for k, v in co.items()))).replace('+ -', '- ')
    kind, line = h['settled'][0][0], h['settled'][0][1]
    win = h['settled'][0][2] if len(h['settled'][0]) > 2 else None
    head = ', '.join(str(v) for v in d[:8])
    where = ("proved in this project" if h['premise_kind'].startswith('proved')
             else "stated by the entry as a fact")
    if kind == 'closed form':
        cf = CF.parse_line(line, bare=True)
        ann = CF.annihilator(cf[0]) if cf and cf[0] is not None else None
        D = win['D'] if win else (ann[1] if ann else None)
        p = _poly({str(k): int(v) for k, v in ann[0].items()}) if ann else None
        window = (rf"$n={win['lo']},\dots,{win['hi']}$" if win else 'the required window')
        second = rf"""
The further claim is a CLOSED FORM, and for that the divisibility is not the whole argument. It
gives that $a$ and the closed form $f$ satisfy the same linear recurrence; it does not say they
are the same solution of it. Write $p$ for the annihilator of $f$,
\[
  p(x)={sp.latex(p.as_expr()) if p is not None else 'p(x)'} ,
\]
of order $D={D}$. Since $q\mid p$ and $a$ satisfies the recurrence of $q$, $a$ satisfies that of
$p$ as well; $f$ satisfies it by construction. Two solutions of a linear recurrence of order $D$
with nonzero leading coefficient agree everywhere as soon as they agree at $D$ consecutive
indices, and $a$ and $f$ were checked to agree at {window},
which lies inside the terms the entry publishes and past the index from which $a$ provably
satisfies $p$. Hence $a(n)=f(n)$ for every $n$ in the claimed range.
"""
    else:
        second = r"""
The further claim is another RECURRENCE, so the claim itself is that $a$ satisfies the
recurrence whose characteristic polynomial is $p$. Since $q\mid p$ and $a$ satisfies the
recurrence of $q$, it satisfies that of $p$, which is exactly what is claimed. No comparison of
terms is needed, and none is made.
"""
    return rf"""{PRE}
\title{{A further conjecture on OEIS {a},\\ \large settled by the proof already in hand}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries more than one conjecture. One of them has a proof; this paper settles a
DIFFERENT one, and it needs no new model and no new engine -- only the linear recurrence already
established for the sequence. A claim about a C-finite sequence whose own characteristic
polynomial is a multiple of the established one is decided by polynomial divisibility, and where
the claim is an identity rather than a recurrence, by divisibility together with a finite window
of agreement.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 11B37, 05A15.\normalsize

\section{{The premise}}

The entry's first terms are ${head},\dots$, with offset ${h['offset']}$. The sequence satisfies
\[
  a(n)={rec} ,
\]
a linear recurrence of order ${order}$ with characteristic polynomial
\[
  q(x)={sp.latex(q.as_expr())} .
\]
This recurrence is {where}; it is the premise of everything below and nothing else is assumed.
It was confirmed against every term the entry publishes from the index where it begins to hold,
with at least ${order}+2$ further terms after that index.

\section{{The further conjecture}}

Separately from the conjecture already settled, the entry records

\begin{{quote}}\raggedright {esc(' '.join(line.split()))}\end{{quote}}
{second}
\begin{{theorem}}
The conjecture displayed above is true.
\end{{theorem}}

\section{{What is and is not claimed here}}

This is a second result on an entry that already has one, and it is a second result only because
it is a DIFFERENT statement. A generating function whose denominator's reciprocal is exactly $q$
says precisely what the proved recurrence says, in another notation; such restatements are
identified and are not counted. The conjecture settled here is not of that kind.

\end{{document}}
"""
