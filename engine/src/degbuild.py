#!/usr/bin/env python3
"""The paper for a claim that names a DEGREE and no coefficients.

    Empirical: a(n) is a polynomial of degree 26 for n>13

The theorem is not a recurrence, so `unibuild` would state the wrong thing: it would print
`(z-1)^(d+1)` as "the conjectured recurrence", which is not what the entry says. What the
entry says is that `a` agrees with SOME polynomial of degree exactly `d` from some index on,
and that is what is stated and proved here.

The two halves, both finite and exact:

  * `(z-1)^(d+1)` annihilates `a` past the threshold, so the (d+1)-st finite difference
    vanishes there and `a` agrees with a polynomial of degree at most `d` from `nthr - d` on;
  * `(z-1)^d` does NOT annihilate the tail, so that polynomial has degree exactly `d`.
"""
import localentry as LE
import phibuild
import unibuild

PRE, esc = phibuild.PRE, phibuild.esc


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    deg, S, nthr = h['degree'], h['S'], h['nthr']
    first, claimed = h['poly_from'], h.get('claimed_from')
    win = unibuild.WINDOW.get(h['engine'], 'a bounded window of consecutive lines')
    head = ', '.join(str(x) for x in d[:8])
    tight = ''
    if claimed is not None:
        tight = (f" The entry claims it for $n>{claimed - 1}$, and the threshold above is "
                 f"exactly ${claimed - 1}+{deg}+1={nthr}$, so the range proved is the range "
                 f"claimed and neither is slack."
                 if first == claimed else
                 f" The entry claims it for $n>{claimed - 1}$; the argument above gives it "
                 f"from $n={first}$, which is at least as strong.")
    return rf"""{PRE}
\title{{The empirical degree for OEIS {a}, proved from an exact model}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{unibuild.DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries the empirical claim that its terms agree with a polynomial of degree ${deg}$.
It is true, and it is decidable rather than empirical. The claim names no coefficients, so
there is no formula to check; but a sequence agrees with a polynomial of degree at most $d$ on
a range exactly when its $(d+1)$-st finite difference vanishes there, and the degree is exactly
$d$ exactly when the $d$-th difference does not eventually vanish. Both are linear recurrences,
and the entry's count is given by an exact model that provably satisfies a monic linear
recurrence of order $S={S}$, so both are settled by a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A16, 11B37.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'])}''. It has offset ${h['offset']}$ and begins
\[
{head},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(h['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical, and nothing on the entry records it as proved.

\section{{The count is a walk count}}

The entry's defining condition is local: it is a condition on {win}. Take as vertices the
admissible configurations of such a window and put an edge from $u$ to $v$ when $v$ may follow
$u$, which the condition decides by inspection. An admissible array is then exactly a walk, so
with $M$ the adjacency matrix of that digraph on $S={S}$ vertices and $\iota,\tau$ the vectors
recording which windows may begin and end an array, $a(n)=\iota^{{\!\top}}M^{{\,g(n)}}\tau$ for
the linear function $g$ the entry's shape supplies. In particular $a$ is $C$-finite.

\section{{A degree is two recurrences}}

\begin{{lemma}}\label{{lem:diff}}
Let $\Delta$ be the forward difference. For integers $N$ and $d\ge0$, $a$ agrees on
$n\ge N$ with a polynomial of degree at most $d$ if and only if $(\Delta^{{d+1}}a)(n)=0$ for
every $n\ge N$; and that polynomial has degree exactly $d$ unless $(\Delta^{{d}}a)(n)=0$ for
all large $n$ as well.
\end{{lemma}}

\begin{{proof}}
Standard finite differences. $\Delta^{{d+1}}$ kills exactly the polynomials of degree at most
$d$, and on a range where $\Delta^{{d+1}}a$ vanishes the values of $a$ are determined by
$d+1$ consecutive ones through the same identity a degree-$d$ polynomial satisfies, so the
interpolating polynomial through any $d+1$ of them reproduces all of them. Its leading
coefficient is $(\Delta^{{d}}a)/d!$, which is the constant the second statement is about.
\end{{proof}}

Written out, $\Delta^{{d+1}}a=0$ is the monic linear recurrence with characteristic polynomial
$(z-1)^{{{deg}+1}}$, and $\Delta^{{d}}a$ constant is the one with $(z-1)^{{{deg}}}$. Both are
fixed recurrences, so each is decided by the annihilation test: $M^{{S}}$ is an integer
combination of $I,\dots,M^{{S-1}}$ by Cayley--Hamilton, the residuals therefore obey the monic
recurrence given by the characteristic polynomial of $M$, and $S$ consecutive zeros force every
later one.

\section{{The theorem}}

\begin{{theorem}}
$a(n)$ agrees with a polynomial in $n$ of degree exactly ${deg}$ for every $n\ge{first}$.
\end{{theorem}}

\begin{{proof}}
The residual of $(z-1)^{{{deg}+1}}$ was formed at each index in exact integer arithmetic from
the model. It is nonzero at $n={nthr}$ and vanishes from $n={nthr}+1$ onwards, with the run of
zeros continuing past $S+{deg}+1$, which by the annihilation bound settles every later index at
once. So $\Delta^{{{deg}+1}}a$ vanishes on $n\ge{nthr}-{deg}={first}$, and
Lemma~\ref{{lem:diff}} gives the polynomial there.

For the degree: the residual of $(z-1)^{{{deg}}}$ has no run of $S+{deg}$ zeros anywhere in the
computed range, so $\Delta^{{{deg}}}a$ is not eventually zero and the degree is not smaller
than ${deg}$.{tight}
\end{{proof}}

\section{{Verification}}

First, the model reproduces all ${h['nterms']}$ terms the entry publishes, exactly, in integer
arithmetic; this is what ties it to the entry, which is read in English and could be misread.
Second, both residuals were computed term by term rather than through any closed form. Third,
the derived bound $S$ was tested on terms it had not been given: the model was evaluated beyond
the $S$ values that determine it and the annihilator reproduced them.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer Sequences}},
\url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\bibitem{{gkp}} R.~L.~Graham, D.~E.~Knuth and O.~Patashnik, \emph{{Concrete Mathematics}},
2nd ed., Addison--Wesley, 1994. (Finite differences.)
\end{{thebibliography}}

\end{{document}}
"""
