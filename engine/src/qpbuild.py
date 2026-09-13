#!/usr/bin/env python3
"""One paper per entry settled by a model that is NOT a walk.

`unibuild' writes the transfer-matrix paper: the condition is local to a window, the windows
are the vertices of a digraph, the arrays are its walks, and Cayley--Hamilton bounds the work.
That is true of most of this project's engines and false of seven of them. A cusp-form
dimension is not a walk count; neither is a weak ordering counted by a polynomial, a Burnside
sum over a necklace group, a capped multiplicity profile, an Ehrhart quasi-polynomial, or the
value of an automaton's row read as a numeral. Those results were nevertheless written by
`unibuild', so 461 installed papers described a digraph that does not exist, and one of them
told a reader that A063089, the dimension of a space of cusp forms, is a walk on eight
vertices contributed by R. H. Hardin. The mathematics behind each was sound; the sentence
describing it was not, and a paper may not say a false thing about the object its numbers
came from.

This builder writes the same proof for those engines with the model section each one actually
has. The skeleton is unchanged and needs no digraph: every engine here supplies a MONIC linear
recurrence of order S that its model provably satisfies, derived in the paper, and the
residual of the conjectured recurrence obeys the same one, so S + order consecutive vanishing
residuals settle the claim.
"""
import os
import re
import json

import conjquote
import localentry as LE
import phibuild
import transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex
DATE0 = os.environ.get('PAPER_DATE', '12 September 2026')
DATE = DATE0

SHORT = {
    'latpoly': 'an Ehrhart quasi-polynomial',
    'ordpoly': 'an exact polynomial in $n$',
    'necklace': "a Burnside sum over the necklace group",
    'multiset': 'an exact polynomial in $n$',
    'cuspdim': 'the classical dimension formula for cusp forms',
    'ca2d': "a certified growth pattern of the automaton's axis word",
    'ecarow': "a certified growth pattern of the automaton's row word",
    'ecacount': "a certified growth pattern of the automaton's row",
    'ecablock': "a certified block template for the automaton's row",
    'ecarowb': "a certified block template for the automaton's row read as a numeral",
}

MSC = {
    'cuspdim': '11F11, 11F72, 05A15',
    'ca2d': '68Q80, 11B85, 05A15',
    'ecarow': '68Q80, 11B85, 05A15',
    'ecacount': '68Q80, 11B85, 05A15',
    'ecablock': '68Q80, 11B85, 05A15',
    'ecarowb': '68Q80, 11B85, 05A15',
}


def _blocks(en, e):
    """the certificate the engine actually derived, so the reader can check it.

    A paper that says "a template was verified" and never says WHICH template asks to be
    taken on trust. These are short -- a period, a pre-period and a handful of words -- and
    printing them costs nothing.
    """
    import importlib
    eng = importlib.import_module(en)
    p = eng.parse_name(e['name'])
    if p is None:
        return ''
    b = eng.build(p)
    if b is None:
        return ''
    if 'tem' in b:
        tem = b['tem']
    elif 'pairs' in b:
        tem = {r: [('q', L), ('f', '.'), ('q', R)] for r, (L, R) in b['pairs'].items()}
    else:
        return ''
    n0, per = b['n0'], b['p']
    rows = []
    for r in sorted(tem)[:4]:
        if 'tem' not in b:
            L, R = b['pairs'][r]
            tt = lambda w: (r'\texttt{%s}' % w) if w else r'\varepsilon'
            rows.append(r'r=%d:\quad w(n+p) = %s \cdot w(n) \cdot %s'
                        % (r, tt(L), tt(R)))
            continue
        parts = r' \cdot '.join(
            ((r'\texttt{%s}^{\,j}' % blk) if k == 'q' else (r'\texttt{%s}' % blk))
            for k, blk in tem[r] if blk)
        rows.append(r'r=%d:\quad %s' % (r, parts))
    more = '' if len(tem) <= 4 else (r' The remaining %d residue classes are of the same '
                                     r'shape and were verified in the same way.'
                                     % (len(tem) - 4))
    return ('\n\nFor this entry the automaton is rule %d, the period is $p=%d$ and the '
            'pre-period is $n_0=%d$.\nThe certificate is\n'
            r'\begin{gather*}' '\n%s\n' r'\end{gather*}' '%s'
            % (b['rule'], per, n0, ' \\\\\n'.join(rows), more))


def _rowb(h, e):
    """the model section for a row read as a numeral whose growth is in the middle."""
    S = h['S']
    return (r"""
\section{The value is a certified block template}

The entry reads the automaton's row at stage $n$ as a string of digits and takes its value in
base $B$. Nothing is being counted, so there is no digraph. The row does not grow only at its
two ends --- for these rules it gains digits in the MIDDLE of a periodic run --- so the shape
$w(n+p)=L_r+w(n)+R_r$ is unavailable. What holds instead is a block template: writing $r$ for
the residue of $n$ modulo the period $p$ and $j$ for the number of periods past a pre-period
$n_0$,
\[
w(n_0 + r + jp)\;=\;B_0\,Q_1^{\,j}\,B_1\cdots Q_m^{\,j}\,B_m,
\]
with the fixed blocks $B_i$ and the repeated blocks $Q_i$ depending only on $r$. This was
verified for every available $n$, and it is a theorem rather than a fit: the rule is a local
map of radius $1$, so $p$ steps have radius $p$; the $p$-step map was checked by direct
simulation at two consecutive $j$ whose repeated runs are longer than $4p+4|Q_i|$, and for a
larger $j$ the template only inserts further copies of each $Q_i$ inside runs already longer
than $2p$. An output cell near either end sees only input cells the two configurations share
at the same distance from that end, and strictly inside a long run the input is
$|Q_i|$-periodic so the output is too, with period and phase fixed by the two verified steps.
Hence the template propagates to every $j$.""" + _blocks('ecarowb', e) + r"""

\section{The bound}

The row is the light cone, of width $2n+1$, so $\sum_i|Q_i|=2p$. Write $s_i$ for the number of
digits to the right of the $i$-th repeated run, so $s_1=2p$. Concatenation is multiplication by
a power of $B$ and addition, and $v(Q_i^{\,j})=v(Q_i)(B^{|Q_i|j}-1)/(B^{|Q_i|}-1)$, so along a
residue class
\[
a(j)\;=\;\sum_i \big(\alpha_i B^{s_i j} + \beta_i\big) + \gamma,
\]
a $\mathbf{Z}$-linear combination of $B^{s_1 j},\dots,B^{s_m j}$ and $1$ with coefficients that
do not depend on $j$. In the shift $T=S^{\,p}$ that is annihilated by
$\prod_i(T-B^{s_i})(T-1)$. Taking the DISTINCT roots that occur across the $p$ residue classes,
pulling each back to $z^p-\lambda$, and allowing the pre-period to raise the numerator's degree
gives the monic annihilator of order $S=%d$ used below.
""" % S)


def _model(en, h, e):
    """the section that says what the model IS, one per engine, and how S follows."""
    S = h['S']
    if en == 'latpoly':
        return rf"""
\section{{The count is a quasi-polynomial}}

The array has a FIXED number $L$ of entries and an alphabet that grows with $n$. Every
condition the entry imposes is a boolean combination of statements
$\sum_i c_ix_i + c\,n \bowtie 0$ with integer coefficients and $\bowtie$ one of
$=,\ne,<,\le,>,\ge$: the bounds $|x_i|\le n$ or $0\le x_i\le n$, a vanishing sum, a difference
that must not vanish, a pair that must total exactly $n$. Each is homogeneous in $(x,n)$
jointly, so the admissible $x$ for a given $n$ are precisely the integer points at height $n$
of a finite union of relatively open rational cones in $\mathbb{{R}}^{{L+1}}$, and $a(n)$ is
the Ehrhart quasi-polynomial of that union: of degree at most $L$, with period dividing the
heights of the cones' ray generators.

\section{{The bound}}

The period is derived, not assumed. Every ray of every cell of the arrangement is cut out by
$L$ linearly independent hyperplanes taken from the constraint set; writing that $L\times(L+1)$
system as $M$, its null direction has $t$-component $\pm\det$ of the $x$-parts, so the
primitive generator $(x^*,t^*)$ has $t^*$ dividing that determinant. Let $T$ be the set of
those determinants. A simplicial cone in a triangulation has at most $L+1$ rays, each
contributing a factor $1-z^{{t_i}}$ with $t_i\in T$, so
\[
A(z)\;=\;\prod_{{d\,\mid\,t\ \text{{for some}}\ t\in T}}\Phi_d(z)^{{L+1}}
\]
annihilates $a$, and $S=\deg A={S}$. A congruence condition modulo $m$ is counted one residue
class at a time; a class is a coset of $m\mathbb{{Z}}^L$, and a generator primitive in
$\mathbb{{Z}}^{{L+1}}$ must be scaled by a divisor of $m$ to lie in it, so each $t$ is replaced
by $mt$ and nothing else changes.

Over the common denominator the numerator has degree below that of $A$ for every cell of the
arrangement that HAS a ray, because such a cell's numerator collects a fundamental
parallelepiped whose heights are below the sum of its generators' heights. The origin is a cell
too and it has none: its series is the constant $1$, which over $A$ is $A/A$ and reaches degree
exactly $\deg A$. The bound in force is therefore $zA(z)$, of order $S={S}$, and
$a(0),\dots,a(S-1)$, computed exactly, determine every later term. Nothing is fitted, and the
annihilator is tested on terms the model was not asked for before anything is claimed --- a
bound one too small fails that test, which is how this one was found.
"""
    if en == 'ordpoly':
        return rf"""
\section{{The count is a polynomial}}

The array has a FIXED length $L$ and an alphabet $0..n$ that grows. The condition is decided by
the ORDER of the terms alone --- by which are equal and which is larger --- so an admissible
array is described completely by its weak ordering: the ordered set partition of the $L$
positions into $m$ blocks of equal value, blocks listed in increasing order. Every assignment
of $m$ distinct values from $\{{0,\dots,n\}}$ to those blocks, in increasing order, gives one
array, and there are $\binom{{n+1}}{{m}}$ of them. Hence
\[
a(n)\;=\;\sum_{{m=1}}^{{L}} N_m\binom{{n+1}}{{m}},
\]
with $N_m$ the number of admissible weak orderings into $m$ blocks, computed exactly.

\section{{The bound}}

That expression is a polynomial in $n$ of degree at most $L$, so $(z-1)^{{L+1}}$ annihilates
$a$ and $S={S}$. Nothing is fitted and no threshold is guessed: the $N_m$ are counted, not
estimated.
"""
    if en == 'necklace':
        return rf"""
\section{{The count is a Burnside sum}}

A necklace is an orbit of labellings under the rotation group, a bracelet an orbit under the
dihedral group, so by Burnside's lemma $a(n)$ is the average over the group of the number of
labellings a single element fixes. A labelling fixed by $g$ is constant on each orbit of $g$,
so writing $x_j$ for the common value on the $j$-th orbit and $w_j$ for its size, the fixed
labellings with sum zero are the integer solutions of
\[
\sum_j w_jx_j = 0,\qquad |x_j|\le n,
\]
counted exactly by convolution. Summing over the group and dividing by its order gives $a(n)$.

\section{{The bound}}

Each term counts the integer points at height $n$ of the cone
$\{{|x_j|\le t,\ \sum_j w_jx_j=0\}}$, whose rays are cut out by $m$ of the defining
hyperplanes; by Cramer the height of a primitive generator divides the determinant of their
$x$-parts, which is $1$ or one of the $w_j$. With at most $m+1$ rays in a simplicial cone,
$\prod_{{d\mid w_j\ \text{{some}}\ j}}\Phi_d(z)^{{m+1}}$ annihilates that term, and the product
over the group's elements annihilates $a$. One more is added to the order, because the origin
is a cell of that arrangement with no ray at all: its series is the constant $1$, which over
the common denominator has numerator degree equal to the denominator's rather than below it.
So $S={S}$.

A rotation has all its orbits of one size, so its equation reduces to $\sum_jx_j=0$ and every
determinant is $1$. A reflection of an odd bracelet fixes one bead and pairs the rest, giving
weights $1$ and $2$, and forces $x_0=-2(x_1+\cdots)$ to be even; that term has period two, not
one. An earlier version of this bound took $S$ to be the number of beads for both, which is
right for the necklaces and false for the bracelets --- the fifth difference of A208826 is
$-36, 48, -60, \dots$ and never vanishes. The bound above is computed from the orbit sizes.
"""
    if en == 'multiset':
        return rf"""
\section{{The count is a polynomial}}

A NONDECREASING arrangement is determined by its multiset of values, so an admissible
arrangement is exactly an admissible multiset. The condition names how many other entries a
value must be built from, and a condition of that shape cannot distinguish a value occurring
$r+1$ times from one occurring more: the admissible multisets are therefore exactly those
whose multiplicity profile, CAPPED at $r+1$, is one of a finite list, and that list is computed
once by enumeration over the capped profiles.

Given an admissible capped profile with $F$ the total multiplicity of the values capped below
the limit and $t$ the number of values at the cap, the arrangements of length $\ell$ with that
profile number $\binom{{\ell-F-(r+1)t+t-1}}{{t-1}}$, and $a(n)$ is the sum of those binomials
over the list with $\ell$ the entry's own length.

\section{{The bound}}

Each binomial is a polynomial in $\ell$, hence in $n$, of degree $t-1<M$ with $M$ the alphabet
size, so $a$ agrees with a polynomial of degree below $M$ and $(z-1)^{{M}}$ annihilates it:
$S={S}$.

Two kinds of term are outside that polynomial at small lengths, and they are why the threshold
below is not zero. A profile with no value at the cap contributes the indicator
$[\,F=\ell\,]$, which is a single spike rather than a polynomial and is gone once
$\ell$ exceeds every such $F$; and a profile whose slack falls below $-(t-1)$ has the count
$0$ where the binomial polynomial does not vanish. Both live at bounded $\ell$, so above them
$a$ is the polynomial exactly, and on every entry of this family the residual of $(z-1)^{{M}}$
is nonzero at the first few indices and vanishes from then on. The theorem is stated from the
threshold up, and the run of zeros it uses lies entirely above the transient.
"""
    if en == 'cuspdim':
        return rf"""
\section{{The dimension is given in closed form}}

There is no array here and no transfer matrix. For even $k\ge4$ the dimension of the space of
cusp forms is given exactly by Diamond and Shurman, Theorem 3.5.1,
\[
\dim S_k(\Gamma_0(N))=(k-1)(g-1)+\left(\tfrac{{k}}{{2}}-1\right)\varepsilon_\infty
+\left\lfloor\tfrac{{k}}{{4}}\right\rfloor\varepsilon_2
+\left\lfloor\tfrac{{k}}{{3}}\right\rfloor\varepsilon_3 ,
\]
with $\dim S_2=g$ and $\dim S_0=0$. Every quantity on the right is elementary integer
arithmetic in $N$: the index $\mu=N\prod_{{p\mid N}}(1+1/p)$; the elliptic counts
$\varepsilon_2,\varepsilon_3$, which vanish when $4\mid N$ and $9\mid N$ respectively and are
otherwise products of $1+\left(\frac{{-1}}{{p}}\right)$ and $1+\left(\frac{{-3}}{{p}}\right)$
over the primes dividing $N$; the cusp count
$\varepsilon_\infty=\sum_{{d\mid N}}\varphi(\gcd(d,N/d))$; and the genus
$g=1+\mu/12-\varepsilon_2/4-\varepsilon_3/3-\varepsilon_\infty/2$.

\section{{The bound}}

With $k=2n$ the right-hand side is linear in $n$ apart from $\lfloor n/2\rfloor$ and
$\lfloor 2n/3\rfloor$, so for $n\ge2$ --- that is, for the even weights $k\ge4$ the formula
covers --- $a$ is a quasi-polynomial of period $6$ and degree $1$ satisfying
$a(n+6)=a(n)+6A+3\varepsilon_2+4\varepsilon_3$ exactly. That difference equation is annihilated
by $(z^6-1)(z-1)$, and $S={S}$ is at least its degree.

The two remaining indices are genuinely outside it: $\dim S_0=0$ and $\dim S_2=g$ are separate
cases of the theorem, not values of the same expression, and the annihilator does not reach
them --- on every one of these entries the residual of $(z^6-1)(z-1)$ is nonzero at $n=0$ and
$n=1$ and vanishes from $n=2$ on. That costs nothing here: $a(n+2)$ is annihilated everywhere,
the residual below is computed term by term from the closed form rather than through $A$, and
the run of zeros the theorem uses lies entirely above the transient.
"""
    if en in ('ecacount', 'ecablock', 'ecarowb'):
        blk = en != 'ecacount'
        cert = (r'''
w(n_0 + r + jp)\;=\;B_0\,Q_1^{\,j}\,B_1\cdots Q_m^{\,j}\,B_m
''' if blk else r'''
w(n+p)\;=\;L_r + w(n) + R_r
''')
        story = (r'''the row is a concatenation of a bounded number of blocks, of which some are
FIXED and some are REPEATED a number of times growing by one every $p$ steps. Writing $r$ for
the residue of $n$ modulo the period $p$ and $j$ for the number of periods past a pre-period
$n_0$, the automaton was run and''' if blk else r'''the row grows only at its two ends. Writing
$r$ for the residue of $n$ modulo the period $p$, the automaton was run and''')
        after = (r'''was verified for every available $n$, the blocks depending only on $r$. The
row at stage $n$ is the light cone, of width $2n+1$, so $\sum_i|Q_i|=2p$, and counting ON
cells along a residue class gives
\[
\mathrm{on}(n_0+r+jp)\;=\;\sum_i \mathrm{ones}(B_i)\;+\;j\sum_i \mathrm{ones}(Q_i),
\]
which is LINEAR in $j$.''' if blk else r'''was verified for every available $n$ past a
pre-period $n_0$, with $L_r$ and $R_r$ fixed words depending only on $r$. Counting ON cells on
both sides gives
\[
\mathrm{on}(n+p)\;=\;\mathrm{on}(n)+\mathrm{ones}(L_r)+\mathrm{ones}(R_r),
\]
a first-order difference along each class.''')
        bnd = (r'''So $\mathrm{on}$ is quasi-linear in $n$ with period $p$ and is annihilated by
$(z^p-1)^2$. The row has width $2n+1$, so $\mathrm{off}(n)=2n+1-\mathrm{on}(n)$ is quasi-linear
too and $(z-1)^2$ divides $(z^p-1)^2$, giving it the same annihilator; a running total is a
partial sum and contributes one further factor $(z-1)$. The pre-period raises the numerator's
degree by at most $n_0$, so the recurrence of order $2p+1$ is in force from index $n_0+2p+1$
and the order $S=%d$ used below covers all four wordings.''' % S if blk else r'''So
$\mathrm{on}$ is annihilated by $(z^p-1)(z-1)$, and $\mathrm{off}(n)=2n+1-\mathrm{on}(n)$ by
the same polynomial, since the width is linear in $n$; a running total contributes one further
factor $(z-1)$. Allowing the pre-period to raise the numerator's degree gives the monic
annihilator of order $S=%d$ used below.''' % S)
        proof = (r'''

The template is a theorem and not a fit. The rule is a local map of radius $1$, so $p$ steps
have radius $p$. Let the template hold at $j=K$ with every repeated run longer than
$4p+4|Q_i|$, and let $F^{\,p}(T(K))=T(K+1)$ and $F^{\,p}(T(K+1))=T(K+2)$ be verified by direct
simulation --- which they were. For $j>K$, $T(j)$ is $T(K)$ with further copies of each $Q_i$
inserted inside runs already longer than $2p$. An output cell within distance
$|B_0|+|Q_1|K-p$ of the left end sees only input cells that $T(j)$ and $T(K)$ share at the same
left-distance, so it agrees with the corresponding cell of $F^{\,p}(T(K))$; symmetrically at
the right end; and strictly inside a run of length exceeding $2p$ the input is
$|Q_i|$-periodic, so the output there is $|Q_i|$-periodic with the period and phase already
fixed by the two verified steps. Hence $F^{\,p}(T(j))=T(j+1)$ for every $j\ge K$, and two
simulations prove infinitely many.''' if blk else r'''

The certificate is a theorem and not a fit, for the same reason: the rule is a local map of
radius $1$, so verifying the identity at two consecutive $n$ in a class fixes every three-cell
window at both boundaries, and induction carries it to every later $n$.''')
        if en == 'ecarowb':
            return _rowb(h, e)
        nm = e['name'].lower()
        which = 'OFF (white)' if 'off (white)' in nm else 'ON (black)'
        run = ('the running total of its %s cells over the first $n$ iterations' % which
               if nm.startswith('total') else 'the %s cells at stage $n$' % which)
        return rf'''
\section{{What is being counted}}

The entry counts {run} of the automaton. Nothing is being enumerated over a window, so there is
no digraph and no transfer matrix. What settles the sequence is the shape of the row itself:
{story}
\[{cert}\]
{after}{proof}{_blocks(en, e)}

\section{{The bound}}

{bnd}
'''
    if en == 'ca2d':
        import ca2d as _c
        import ca2dgrid as _g
        q = _c.parse_name(e['name'])
        b = _c.build(q) if q else None
        tp = (b or {}).get('tper')
        n0, p = tp if tp else (0, 0)
        return rf"""
\section{{The value is a certified growth}}

The entry reads an axis or a diagonal of the automaton at stage $n$ as a string of digits and
takes its numeric value. Nothing is being counted, so there is no digraph. What settles the
sequence is that the CONFIGURATION is periodic in time:
\[
C(n+{p})\;=\;C(n)\qquad\text{{as configurations of the whole plane, for every }} n\ge {n0}.
\]
This was checked directly, and one instance of it is all that is needed: the automaton is a
deterministic map on configurations, so $C(n_0+{p})=C(n_0)$ forces $C(n_0+k\cdot{p})=C(n_0)$ for
every $k$, and likewise in each residue class. No locality argument and no induction over
boundary windows is involved.

Getting the background right is the whole of the check. A rule taking an empty von Neumann
neighbourhood to a live cell flips the ENTIRE plane, and rule {b['rule'] if b else 0} is read
in that light: comparing two stages by padding the smaller with zeros would compare two
different things.

The reading follows at once. The axis at stage $n$ is the window $|x|\le n$ of a configuration
that is not changing, so the window widening by one cell on each side per step gives
\[
w(n+{p})\;=\;L_r + w(n) + R_r
\]
with $L_r$ and $R_r$ fixed words depending only on the residue $r$ of $n$ modulo ${p}$ --- an
identity that is now a consequence rather than an observation. Concatenation is multiplication
by a power of the base $B$ and addition, so along a class
\[
a(n+{p})\;=\;v(L_r)\,B^{{|w(n)|+|R_r|}} + a(n)\,B^{{|R_r|}} + v(R_r).
\]

\section{{The bound}}

In the shift $T=S^{{\,{p}}}$ that is a first-order recurrence with a geometric forcing term and a
constant, killed by $(T-B^{{|R_r|}})(T-B^{{|L_r|+|R_r|}})(T-1)$. Taking the DISTINCT roots that
occur across the residue classes, pulling each back to $S^{{\,{p}}}-\lambda$, and allowing the
pre-period to raise the numerator's degree gives a monic annihilator of order $S={h['S']}$.
"""
    if en == 'ecarow':
        what = 'a row'
        return rf"""
\section{{The value is a certified growth}}

The entry reads {what} of the automaton at stage $n$ as a string of digits and takes its
numeric value. Nothing is being counted, so there is no digraph. What settles the sequence is
that the string itself grows by a fixed pattern: the automaton was run and the certificate
\[
w(n+p)\;=\;L_r + w(n) + R_r
\]
was verified for every available $n$ in each residue class $r$ of $n$ modulo the period $p$,
after a pre-period $n_0$ during which the shape has not yet settled. Concatenation is
multiplication by a power of the base $B$ and addition, so along a class
\[
a(n+p)\;=\;v(L_r)\,B^{{|w(n)|+|R_r|}} + a(n)\,B^{{|R_r|}} + v(R_r),
\]
with $|w(n)|$ growing by $|L_r|+|R_r|$ every $p$ steps.

\section{{The bound}}

In the shift $T=S^{{\,p}}$ that is a first-order recurrence with a geometric forcing term and a
constant, killed by $(T-B^{{|R_r|}})(T-B^{{|L_r|+|R_r|}})(T-1)$. Taking the DISTINCT roots that
occur across the residue classes, pulling each back to $S^{{\,p}}-\lambda$, and allowing the
pre-period to raise the numerator's degree gives a monic annihilator of order $S={S}$. The
earlier figure, $p+3$, was the one-dimensional count carried over unchanged; with $p$ classes
carrying $p$ different pairs it is too small, and a residual test that trusts it checks too few
coefficients to prove anything.
"""
    raise KeyError(en)


def conj_line(anum, coeffs=None):
    return conjquote.line(anum, coeffs)


def _author(e, conj):
    """who contributed the CONJECTURE, taken from the conjecture line itself.

    `unibuild' printed "contributed by R. H. Hardin" on every paper it wrote. Most of its
    entries are Hardin's and it passed unnoticed, but A063089 is Sloane's and the empirical
    recurrence on it is Colin Barker's, so the sentence credited a conjecture to someone who
    did not make it. An attribution that cannot be read off the entry is omitted instead.
    """
    m = (re.search(r'Conjectures?\s+from\s+_([^_]+)_', conj or '')
         or re.search(r'_([^_]+)_', conj or ''))
    if m:
        return ' contributed by ' + esc(m.group(1).strip())
    return ''                                             # no name on the line, so none given


def build(h):
    a, en = h['anum'], h['engine']
    S, order, nterms, nthr = h['S'], h['order'], h['nterms'], h['nthr']
    off = h['offset']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    conj = conj_line(a, h.get('coeffs'))
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    tight = ''
    if off <= nthr - order and nthr - off < len(d):
        kk = nthr - off
        if d[kk] != sum(int(c) * d[kk - i] for i, c in coeffs.items()):
            tight = (rf' The bound is exact: at $n={nthr}$ the recurrence fails on the '
                     rf"entry's own published terms, so no larger range holds.")
    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved from an exact model}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{{DATE}}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}${_author(e, conj)}. It is true, and it is
decidable rather than empirical. The entry's sequence is given exactly by {SHORT[en]}, from
which $a$ provably satisfies a MONIC linear recurrence of order $S={S}$, derived below and not
assumed. The residual of the conjectured recurrence satisfies the same one, so whether it
annihilates $a$ is settled by a finite exact computation. No transfer matrix is involved and
the count is not a walk.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. {MSC.get(en, '05A15, 05A19, 11P21')}.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(conj) if conj else '(the empirical recurrence quoted in the entry)'}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({e['modified']}, revision {e['revision']})
this is still recorded as empirical, and nothing on the entry records it as proved.
{_model(en, h, e)}
\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
Let $A(z)=z^S-\sum_{{j<S}}\alpha_jz^{{j}}$ be the monic annihilator derived above and
$q(z)=z^{{{order}}}-\sum_ic_iz^{{{order}-i}}$ the characteristic polynomial of the conjectured
recurrence. The residual $r(n)=a(n)-\sum_ic_ia(n-i)$ is a linear combination of shifts of $a$,
so $A$ annihilates $r$ as well. Since $A(0)\ne0$ the recurrence it gives runs in both
directions, and $S$ consecutive zeros of $r$ force $r$ to vanish at every later index.
\end{{lemma}}

\begin{{proof}}
$A$ annihilates $a$, hence every shift of $a$, hence any linear combination of shifts; that is
$r$. A monic recurrence with nonzero constant term determines each term from the $S$ before it
and each from the $S$ after it, so a run of $S$ zeros propagates.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
The terms $a(0),\dots$ were computed exactly in integer arithmetic from the model, extended by
$A$ where the model itself was not evaluated, and $r(n)$ formed for each index. Those integers
vanish from $n={nthr}+1$ onwards, and the run exceeds $S+{order}$, which by
Lemma~\ref{{lem:crit}} settles every larger index at once.{tight}
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer
arithmetic. This is what ties the model to the entry: it is built by reading the entry's
English, and a misreading gives different counts.

Second, the conjectured recurrence was evaluated directly on those published terms, with no
model involved, and holds wherever the proved range and the data overlap.

Third, the derived annihilator $A$ was itself tested on terms it had not been given: the model
was evaluated beyond the $S$ values that determine it and $A$ reproduced them. A bound that is
too small fails this test, which is why it is run.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{beckrobins}} M.~Beck and S.~Robins, \emph{{Computing the Continuous Discretely}},
2nd ed., Springer, 2015. (Ehrhart quasi-polynomials and their periods.)
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\bibitem{{ds}} F.~Diamond and J.~Shurman, \emph{{A First Course in Modular Forms}},
Springer GTM 228, 2005.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    hits = [h for h in json.load(open('uniall_hits.json'))
            if not h.get('FAILS') and h.get('engine') in SHORT]
    for h in hits:
        dd = f"build/un{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f'{dd}/p.tex', 'w').write(build(h))
    print('wrote', len(hits), 'papers')
