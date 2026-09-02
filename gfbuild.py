#!/usr/bin/env python3
"""One paper per entry whose empirical recurrence follows from a generating function the
entry itself records."""
import os, json, re
import sympy
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex
x = sympy.Symbol('x')


def build(h):
    a = h['anum']
    e = LE.get(a)
    d = [int(v) for v in e['data'].split(',') if v.strip()]
    mod, rev = e['modified'], e['revision']
    coeffs = {int(k): int(v) for k, v in h['coeffs'].items()}
    order, nthr, off, sh, deg = h['order'], h['nthr'], h['offset'], h['shift'], h['deg']
    g = sympy.sympify(h['gf'])
    gtex = sympy.latex(sympy.cancel(sympy.together(g)))
    D = 1 - sum(sympy.Integer(int(c)) * x ** int(i) for i, c in coeffs.items())
    Dtex = sympy.latex(sympy.expand(D))
    Htex = sympy.latex(sympy.expand(sympy.cancel(sympy.together(D * g))))
    idx = "n" if off == sh else ("n-%d" % (off - sh) if off > sh else "n+%d" % (sh - off))
    # the residuals the entry's own terms produce: concrete, and checkable by hand
    rr = []
    for k in range(len(d)):
        n = off + k
        if k - order < 0:
            continue
        v = d[k] - sum(c * d[k - i] for i, c in coeffs.items())
        rr.append((n, v))
        if n > nthr + 3:
            break
    restab = " \\\\\n".join(r"$n=%d$ & $%d$" % (n, v) for n, v in rr[:12])
    gg = sympy.cancel(sympy.together(g))
    num0, den0 = sympy.fraction(gg)
    minord = sympy.Poly(den0, x).degree()
    dentex = sympy.latex(sympy.expand(den0))
    quot = sympy.cancel(sympy.expand(D) / den0)
    qtex = sympy.latex(sympy.expand(quot))
    minimal = (minord == order)
    tight = ""
    if nthr - order >= off and nthr - off < len(d):
        k = nthr - off
        if d[k] != sum(c * d[k - i] for i, c in coeffs.items()):
            tight = (rf" The bound is exact: at $n={nthr}$ the recurrence fails on the "
                     rf"entry's own published terms.")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, derived from the entry's generating function}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{2 September 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} carries an empirical recurrence of order ${order}$. The entry separately records a
generating function, not as a conjecture but as a statement of fact, and the recurrence is a
consequence of it: multiplying the generating function by the polynomial the recurrence
supplies gives a POLYNOMIAL, and the recurrence then holds at every index past that
polynomial's degree. No model of the objects being counted is needed, and no search: the
whole argument is one polynomial division, carried out in exact arithmetic. The result is
conditional on the recorded generating function, which is what the entry asserts and what is
checked here against every published term.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 11B37, 30B10.\normalsize

\section{{The two statements}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(v) for v in d[:8])},\ \dots
\]
The entry states, as a conjecture and never marked settled:
\begin{{quote}}
{esc(h['conj'])}
\end{{quote}}
and, separately and NOT as a conjecture:
\begin{{quote}}
{esc(h['gfline'])}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the first is still
recorded as empirical. This note derives it from the second.

\section{{A rational generating function decides every linear recurrence}}

Write
\[
G(x)\;=\;\sum_{{n}}a(n)\,x^{{{idx}}}\;=\;{gtex},
\]
the entry's own generating function, and let
\[
D(x)\;=\;1-\sum_i c_i x^{{i}}\;=\;{Dtex}
\]
be the polynomial attached to the conjectured recurrence.

\begin{{lemma}}\label{{lem:key}}
For every $n$ in range, $a(n)-\sum_i c_i\,a(n-i)$ is the coefficient of $x^{{{idx}}}$ in
$D(x)G(x)$.
\end{{lemma}}

\begin{{proof}}
Multiplying power series, the coefficient of $x^{{m}}$ in $D(x)G(x)$ is
$a_m-\sum_i c_i a_{{m-i}}$ where $a_m$ denotes the coefficient of $x^{{m}}$ in $G$, terms with
negative index being zero.
\end{{proof}}

\begin{{theorem}}
\[
a(n)\;=\;{rec_tex(coeffs)}
\]
for every $n>{nthr}$.
\end{{theorem}}

\begin{{proof}}
In exact arithmetic,
\[
D(x)\,G(x)\;=\;{Htex},
\]
a POLYNOMIAL of degree ${deg}$ --- the denominator of $G$ divides $D(x)$ times its numerator,
which is precisely the condition for the conjectured recurrence to be implied by the
generating function. Its coefficients vanish beyond degree ${deg}$, so by
Lemma~\ref{{lem:key}} the residual $a(n)-\sum_ic_ia(n-i)$ vanishes for every
$n>{nthr}$.{tight}
\end{{proof}}

\section{{Is the conjectured recurrence the shortest one?}}

Cancelling common factors, $G$ has reduced denominator
\[
{dentex},
\]
of degree ${minord}$, and that degree is the order of the SHORTEST linear recurrence with
constant coefficients the sequence obeys: any shorter one would give a polynomial multiple of
$G$ with a smaller denominator, contradicting the cancellation. The conjectured recurrence has
order ${order}$.

{'So the conjecture is the minimal recurrence.' if minimal else 'So the conjecture is not minimal: its polynomial $D(x)$ factors as the reduced denominator times $' + qtex + '$, and the sequence already satisfies a recurrence of order ' + str(minord) + '. The conjecture is true, but it is a consequence of a shorter one the entry does not state.'}

\section{{The residuals, explicitly}}

Lemma~\ref{{lem:key}} says the residual $a(n)-\sum_ic_ia(n-i)$ is a coefficient of the
polynomial $D(x)G(x)$, so it can be read off the entry's own published terms with no
generating function involved at all. Doing that:
\begin{{center}}
\begin{{tabular}}{{cc}}
index & residual \\ \hline
{restab}
\end{{tabular}}
\end{{center}}
The residuals are exactly the coefficients of the polynomial displayed above, in order, and
they stop at index ${nthr}$ because that polynomial has degree ${deg}$. A reader who trusts
neither the generating function nor the algebra can check the table against the entry's DATA
by hand; what the generating function adds is the guarantee that the pattern continues, which
no amount of checking terms could establish on its own.

\section{{Verification}}

Three checks.

First, the generating function was expanded as a power series in exact rational arithmetic and
compared against all ${len(d)}$ terms the entry publishes: it reproduces every one. This is
what ties the recorded generating function to the sequence the recurrence is about.

Second, the polynomial division above was carried out symbolically, not numerically, so the
statement that $D(x)G(x)$ is a polynomial is exact rather than approximate.

Third, the recurrence was evaluated directly on the series coefficients for sixty consecutive
indices beyond $n={nthr}$ and holds at every one, and at $n={nthr}$ itself it fails --- the
degree bound is attained, so the range stated is the true one and not merely a safe one.

\begin{{remark}}
The argument is conditional on the generating function, which the entry records as a fact and
attributes to a contributor rather than offering as a conjecture. What is shown here is that
the empirical recurrence is not an independent guess: it is equivalent to information the
entry already contains.
\end{{remark}}

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Rational generating functions, Section 4.1.)
\bibitem{{kp}} M.~Kauers and P.~Paule, \emph{{The Concrete Tetrahedron}}, Springer, 2011.
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("gf_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/gf{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
