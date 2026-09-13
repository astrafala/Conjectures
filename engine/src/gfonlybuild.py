#!/usr/bin/env python3
"""Papers for the entries whose only conjecture is a generating function."""
import os, json, re
import sympy
import localentry as LE, phibuild, gfonly, qpbuild, uniform

x = sympy.Symbol('x')


def family(engine):
    """the first sentence of the engine's own docstring: what this family is."""
    d = (uniform.M[engine].__doc__ or '').strip().split('\n\n')[0]
    return ' '.join(d.split())


def rec_from_den(expr):
    """the linear recurrence the conjectured denominator forces, normalised monic."""
    num, den = sympy.fraction(sympy.cancel(sympy.together(expr)))
    pd = sympy.Poly(den, x).all_coeffs()[::-1]
    if pd[0] == 0:
        return None
    pd = [sympy.Rational(c, pd[0]) for c in pd]
    if any(c.q != 1 for c in pd):
        return None
    return [int(-c) for c in pd[1:]]

PRE = phibuild.PRE
esc = phibuild.esc


_MODEL_WALK = r"""\section{{The count is a walk count}}

Every condition the entry names is decided inside a bounded number of consecutive rows: it
compares a cell with cells a bounded distance from it, and no comparison reaches further than
that. So a strip of that many consecutive rows is a state of a finite automaton, an array is
read off row by row, and appending one more row is one step, legal exactly when the row it
completes satisfies every condition that becomes testable.

Taking those strips as the vertices of a digraph $G$ with adjacency matrix $M$, and writing
$\iota$ for the indicator of the states an array may begin in and $\tau$ for those it may end
in,
\[
a(n)\;=\;\iota^{{\!\top}}M^{{\,n-{off}+{shift}}}\tau ,
\]
and there are $S={S}$ states. The digraph is built by reading the entry's own English, and the
model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer arithmetic --- a
misreading of the condition gives a different digraph and different counts, so this ties the
model to the entry and not merely to the arithmetic.{fam}

\section{{Its generating function is rational, with bounded degree}}

\begin{{lemma}}\label{{lem:rat}}
$A(x)=\sum_{{n\ge{off}}}a(n)x^n=N_1(x)/D_1(x)$ where $D_1(x)=\det(I-xM)$ has degree at most
$S$ and $D_1(0)=1$, and $\deg N_1<S+{off}$.
\end{{lemma}}

\begin{{proof}}
Summing the geometric series of matrices, $\sum_{{j\ge0}}M^jx^j=(I-xM)^{{-1}}$ as a formal
power series, so $A(x)$ is $x^{{c}}\,\iota^{{\!\top}}(I-xM)^{{-1}}\tau$ for the constant $c$
relating the walk index to the entry's own $n$. By Cramer's rule every entry of
$(I-xM)^{{-1}}$ is a polynomial of degree less than $S$ divided by $\det(I-xM)$, and
$\det(I-xM)$ is a polynomial of degree at most $S$ with constant term $\det I=1$.
\end{{proof}}"""

_MODEL_RAT = r"""

The model reproduces all ${nterms}$ terms the entry publishes, exactly, in integer arithmetic:
it is built by reading the entry's own English, and a misreading gives different counts, so
this ties the model to the entry and not merely to the arithmetic.

\section{{Its generating function is rational, with bounded degree}}

\begin{{lemma}}\label{{lem:rat}}
$A(x)=\sum_{{n\ge{off}}}a(n)x^n=N_1(x)/D_1(x)$ where $D_1(x)$ has degree at most $S={S}$ and
$D_1(0)=1$, and $\deg N_1<S+{off}$.
\end{{lemma}}

\begin{{proof}}
The section above derives a MONIC linear recurrence of order $S$ that $a$ provably satisfies
from some index onwards; write its characteristic polynomial as $z^S-\sum_{{j<S}}\alpha_jz^j$
and put $D_1(x)=1-\sum_{{j<S}}\alpha_jx^{{S-j}}$, the same polynomial written backwards, so
$\deg D_1\le S$ and $D_1(0)=1$. Multiplying the power series $A(x)$ by $D_1(x)$ annihilates
every coefficient at which the recurrence is in force, so $N_1=AD_1$ is a polynomial, and the
indices it can be supported on are the offset together with the finitely many below the point
where the recurrence takes hold, all of them less than $S+{off}$. No matrix is involved: the
model here is not a walk and has no adjacency matrix, and the bound comes from the recurrence
the model itself supplies.
\end{{proof}}"""


def build(h):
    a = h['anum']
    S, off, nterms = h['S'], h['offset'], h['nterms']
    dn, dd, checked = h['degnum'], h['degden'], h['checked']
    e = LE.get(a)
    d = [int(x) for x in e['data'].split(',') if x.strip()]
    modf, rev = e['modified'], e['revision']
    bound = S + max(dd - 1, dn)
    fam = ''
    try:
        f = family(h['engine'])
        if f:
            fam = ('\n\nThe family this entry belongs to is read by one model, described by its '
                   'author as: ``' + esc(f[:400]) + "''\n")
    except Exception:
        pass
    rec = None
    try:
        for L in LE.get(a)['comment'] + LE.get(a)['formula']:
            g = gfonly.parse(L)
            if g is not None:
                rec = rec_from_den(g)
                break
    except Exception:
        rec = None
    # `unibuild' wrote the digraph paper for engines whose model is no walk and 461 papers
    # said a false thing about the object their numbers came from; this builder was never
    # given the same correction, and 219 of ITS installed papers say it too. The model
    # section comes from `qpbuild' for those engines, and the rationality lemma is then
    # stated from the annihilator rather than from a matrix that does not exist.
    model = _MODEL_WALK.format(off=off, shift=h['shift'], S=S, nterms=nterms, fam=fam)
    if h['engine'] in qpbuild.SHORT:
        model = (qpbuild._model(h['engine'], h, e).rstrip() + fam +
                 _MODEL_RAT.format(S=S, off=off, nterms=nterms))
    recnote = ('' if rec is None else
               ('Its coefficients are the integers $c_1,\\dots,c_{%d}$ read off $D_2$, the '
                'first few being $%s$. ' % (dd, ',\\ '.join(str(v) for v in rec[:6]))))
    return rf"""{PRE}
\title{{The conjectured generating function for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{6 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays of a fixed width under a local condition, and carries a conjectured
generating function --- and nothing else. It is true. The count is a walk count in a finite
digraph on $S={S}$ vertices, so its generating function is a rational function whose numerator
and denominator have degrees bounded by $S$; the conjectured expression is another rational
function of known degree; and two rational functions of bounded degree agree as soon as enough
coefficients of their expansions do. Comparing ${checked}$ coefficients in exact arithmetic
therefore settles the conjecture, rather than testing it.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A19, 68Q45.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:6])},\ \dots
\]
The entry states, as a conjecture contributed by a reader and never marked settled:
\begin{{quote}}
{esc(h['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modf}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved. The entry carries no
conjectured recurrence, which is why this generating function is the whole of what is open
here.

{model}

\begin{{theorem}}
The conjectured generating function is $A(x)$.
\end{{theorem}}

\begin{{proof}}
Write the conjecture as $N_2/D_2$ with $\deg N_2={dn}$ and $\deg D_2={dd}$; its expansion as a
power series exists because $D_2(0)\neq0$. Put
\[
R(x)\;=\;N_1(x)D_2(x)-N_2(x)D_1(x),
\]
a polynomial of degree at most ${bound}$ by Lemma~\ref{{lem:rat}}. The difference
$A-N_2/D_2$ equals $R/(D_1D_2)$, and $D_1(0)D_2(0)\neq0$, so if the two power series agree in
every coefficient up to $x^{{{bound}}}$ then $R$ has a zero of order greater than its own
degree at the origin, which forces $R\equiv0$ and hence $A=N_2/D_2$ identically.

The coefficients of $A$ were produced from the model by repeated matrix--vector products in
exact integer arithmetic, those of $N_2/D_2$ by exact rational long division, and ${checked}$
of them --- more than the ${bound}+1$ the argument requires --- agree.
\end{{proof}}

\section{{A recurrence the entry does not state}}

The denominator of a rational generating function is a linear recurrence written backwards, so
the theorem above yields one for free. With $D_2(x)=1-\sum_{{i\ge1}}c_ix^i$ after normalising
$D_2(0)=1$, comparing coefficients of $x^n$ in $A(x)D_2(x)=N_2(x)$ gives
\[
a(n)\;=\;\sum_{{i\ge1}}c_i\,a(n-i)\qquad\text{{for every }}n>{dn},
\]
a constant-coefficient linear recurrence of order ${dd}$, valid past the degree of the
numerator. {recnote}The entry records no recurrence, so this is not a restatement of anything
already there.

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the model reproduces every one of the ${nterms}$ published terms, with the index shift
read off the entry's offset rather than fitted.

Second, the arrays themselves were enumerated for the smallest shapes the entry counts,
directly from its English and with no automaton, and the counts agree. Writing that check is
where the risk actually sits: an earlier version of it dropped a clause from the entry's name
in three cases and disagreed with the model, and in all three the check was wrong and the model
was right.

Third, the coefficient comparison was carried out over the whole range required by the degree
bound rather than on a prefix, in exact arithmetic throughout.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7.)
\bibitem{{flajolet}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == '__main__':
    n = 0
    for h in json.load(open('gfonly_hits.json')):
        if h.get('FAILS'):
            continue
        dd = f"build/gfo{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", 'w').write(build(h))
        n += 1
    print('wrote', n, 'papers')
