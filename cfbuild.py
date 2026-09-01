#!/usr/bin/env python3
"""One paper per entry whose conjecture is an explicit closed form."""
import os, json, re
import sympy
import localentry as LE, phibuild, closedform as CF

PRE = phibuild.PRE
esc = phibuild.esc
n = sympy.Symbol('n')

WINDOW = {
    'transfer3': "a condition on every $2\\times2$ subblock, hence on two consecutive lines",
    'transfer6': "a condition on every $2\\times2$ subblock, hence on two consecutive lines",
    'transfer9': "a condition on a bounded window of consecutive lines",
    'transfer14': "a condition on a bounded window of consecutive lines",
}


def q_tex(mult):
    parts = []
    for b, d in sorted(mult.items(), key=lambda z: -int(z[0])):
        e = '' if d + 1 == 1 else '^{%d}' % (d + 1)
        parts.append(r"(x-%d)%s" % (int(b), e))
    return "".join(parts)


def rec_tex(coeffs):
    out = []
    for i in sorted(coeffs):
        c = int(coeffs[i])
        if c == 0:
            continue
        s = '-' if c < 0 else '+'
        m = abs(c)
        term = r"a(n-%d)" % i if m == 1 else r"%d\,a(n-%d)" % (m, i)
        out.append((s, term))
    if not out:
        return "0"
    first = out[0]
    txt = ("-" if first[0] == '-' else "") + first[1]
    for s, t in out[1:]:
        txt += " %s %s" % (s, t)
    return txt


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    expr = sympy.sympify(h['expr'], locals={'n': n}, rational=True)
    mult = CF.bases(expr)
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    order, thr, first, off, S = h['order'], h['thr'], h['first'], h['offset'], h['S']
    mod, rev = e['modified'], e['revision']
    ftex = sympy.latex(expr)
    kinds = ("a polynomial in $n$" if list(mult) == [1] else
             "a sum of exponentials with polynomial coefficients")
    deg1 = "; the closed form is %s, so this is $(x-1)^{%d}$" % (kinds, order) \
        if list(mult) == [1] else ""
    win = WINDOW.get(h['engine'], "a condition on a bounded window of consecutive lines")
    lo = max(thr + 1, off)
    below = ("" if first >= lo else rf"""
Below $n={lo}$ the recurrence argument gives nothing, since \eqref{{eq:rec}} is only
established for $a$ from $n={thr + 1}$ on. The remaining indices $n={first},\dots,{lo-1}$ were
therefore checked one at a time, directly against the walk count in exact integer arithmetic,
and agree.""")
    tight = ("the closed form holds from the entry's first term onwards" if first == off
             else "at $n=%d$ the closed form and the sequence differ, so no larger range is "
                  "available" % (first - 1))
    nd = len(d)

    return rf"""{PRE}
\title{{The empirical closed form for OEIS {a}, proved}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{1 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical closed form for $a(n)$ --- not a recurrence relating
consecutive terms but an explicit formula. It is true, and it is decidable rather than
empirical. The entry counts arrays subject to {win}, so the lines of an array are the
vertices of a finite digraph, an array is a walk in it, and $a(n)$ is a walk count on
$S={S}$ vertices. Any function of the form $\sum_j p_j(n)\lambda_j^{{\,n}}$ satisfies the
monic linear recurrence whose characteristic polynomial is
$\prod_j(x-\lambda_j)^{{\deg p_j+1}}$; here that polynomial is $q(x)={q_tex(mult)}$, of degree
${order}$. Two things are then checked exactly: that the walk count satisfies the same
recurrence from some index on, which the Cayley--Hamilton theorem reduces to a finite
computation, and that the two sequences agree at ${order}$ consecutive indices past that
point. A monic recurrence determines every later term from its predecessors, so agreement
there is agreement for good.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 15A18.\normalsize

\section{{The conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry states, as a conjecture contributed by its author and never marked settled:
\begin{{quote}}
{esc(h['line'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) this is still
recorded as empirical, and nothing on the entry records it as proved. Write
\[
f(n)\;=\;{ftex}.
\]

\section{{The count is a walk count}}

The entry's defining condition is local: it is {win}. Take as vertices the
admissible configurations of such a window and put an edge from $u$ to $v$ when $v$ may
follow $u$, which the condition decides by inspection. An admissible array is then exactly a
walk, so with $M$ the adjacency matrix of that digraph on $S={S}$ vertices, and $u,w$ the
vectors recording which windows may start and end an array,
\[
a(n)\;=\;u^{{\!\top}}M^{{\,g(n)}}w
\]
for the linear function $g$ that the entry's shape supplies. In particular $a$ is
$C$-finite: it satisfies some monic integer linear recurrence, though not necessarily a short
one.

\section{{A closed form is a recurrence}}

\begin{{lemma}}\label{{lem:ann}}
Let $f(m)=\sum_{{j}}p_j(m)\lambda_j^{{\,m}}$ with the $\lambda_j$ distinct and the $p_j$
polynomials, and put $q(x)=\prod_j(x-\lambda_j)^{{\deg p_j+1}}$. Then $q$ applied to the shift
operator annihilates $f$: writing $q(x)=x^{{r}}-\sum_{{i=1}}^{{r}}c_ix^{{r-i}}$,
\[
f(m)\;=\;\sum_{{i=1}}^{{r}}c_i\,f(m-i)\qquad\text{{for every }}m.
\]
\end{{lemma}}

\begin{{proof}}
The shift operator $E$ acts on $m\mapsto\lambda^{{m}}p(m)$ as
$(E-\lambda)\bigl(\lambda^{{m}}p(m)\bigr)=\lambda^{{m+1}}\bigl(p(m+1)-p(m)\bigr)$, and
$p(m+1)-p(m)$ has degree one less than $p$. So $(E-\lambda)^{{\deg p+1}}$ kills
$\lambda^{{m}}p(m)$, and the factors of $q$ commute.
\end{{proof}}

Here $q(x)={q_tex(mult)}$, of degree ${order}${deg1}, and the recurrence it encodes is
\begin{{equation}}\label{{eq:rec}}
a(n)\;=\;{rec_tex(coeffs)}.
\end{{equation}}

\section{{The proof}}

\begin{{lemma}}\label{{lem:crit}}
With $q$ as above, $a$ satisfies \eqref{{eq:rec}} for all large $n$ if and only if
$u^{{\!\top}}M^{{\,j}}q(M)w=0$ for every $j\ge0$, and it is enough to check $j<S$.
\end{{lemma}}

\begin{{proof}}
Substituting the walk expression, the residual $a(n)-\sum_ic_ia(n-i)$ equals
$u^{{\!\top}}M^{{\,g(n)-r}}q(M)w$ up to the fixed linear reparametrisation $g$. For the bound,
$M^{{S}}$ is an integer combination of $I,M,\dots,M^{{S-1}}$ by Cayley--Hamilton, so the values
$u^{{\!\top}}M^{{j}}q(M)w$ satisfy the monic recurrence given by the characteristic polynomial of
$M$; $S$ consecutive zeros therefore force all later ones, and the last nonzero value pins the
threshold exactly.
\end{{proof}}

\begin{{theorem}}
$a(n)=f(n)$ for every $n\ge{first}$.
\end{{theorem}}

\begin{{proof}}
The vector $w'=q(M)w$ was formed by ${order}$ matrix--vector products in exact integer
arithmetic, and $u^{{\!\top}}M^{{j}}w'$ evaluated for $j=0,1,\dots$, again exactly. Those integers
vanish from the point corresponding to $n={thr + 1}$ onwards, and the run was continued until the
working vector was identically zero, which settles every larger $j$ at once. So $a$ satisfies
\eqref{{eq:rec}} for every $n>{thr}$. By Lemma~\ref{{lem:ann}} $f$ satisfies \eqref{{eq:rec}}
identically. Both were then evaluated in exact arithmetic at the ${order}$ consecutive indices
$n={lo},\dots,{lo + order - 1}$ and agree at each. A monic recurrence of order ${order}$
determines $a(m)$ from $a(m-1),\dots,a(m-{order})$, and for every $m\ge{lo + order}$ both
$m>{thr}$ and $m-{order}\ge{lo}$ hold, so induction on $m$ gives $a(m)=f(m)$ for every
$m\ge{lo}$.{below}
\end{{proof}}

The range is tight in the sense that was checked: {tight}.

\section{{Verification}}

Four checks, each independent of the algebra above.

First, the walk model reproduces every one of the ${nd}$ terms the entry publishes,
exactly, in integer arithmetic. This is what ties the model to the entry: the model is built
by reading the entry's English, and a misreading gives a different digraph and different
counts.

Second, the closed form was evaluated in exact rational arithmetic --- not floating point ---
at every published term from $n={first}$ on, and agrees with the entry's own DATA at each.

Third, the annihilation test of Lemma~\ref{{lem:crit}} was carried out exactly, and the model
and the closed form were then compared directly at sixty consecutive indices beyond
$n={first}$, far past where the proof already settles the matter.

Fourth, the closed form was deliberately perturbed --- by a constant and by a term linear in
$n$ --- and each perturbed form was rejected by the same comparison, so the test is not one
that anything would pass.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7; $C$-finite sequences,
Section 4.1.)
\bibitem{{kp}} M.~Kauers and P.~Paule, \emph{{The Concrete Tetrahedron}}, Springer, 2011.
(Closed forms and linear recurrences with constant coefficients.)
\bibitem{{horn}} R.~A.~Horn and C.~R.~Johnson, \emph{{Matrix Analysis}}, 2nd ed., Cambridge
University Press, 2013.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("cf_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/cf{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
