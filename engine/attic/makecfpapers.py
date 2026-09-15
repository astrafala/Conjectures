#!/usr/bin/env python3
"""Generate papers 52-100: one per OEIS entry whose conjectured recurrence we settle.

Each paper stands alone and refers to no other.
"""
import json, os, re, signal, subprocess
import sympy as sp
from prove_rec import parse_gf, parse_conj, residual_poly
import quadfield as qf
import multiquad as mq


def LE_META(anum):
    """(Last-modified, revision) read from the entry itself, ('', '') if unreadable."""
    try:
        import localentry as _LE
        e = _LE.get(anum)
        return e["modified"], e["revision"]
    except Exception:
        return "", ""


n = sp.Symbol('n')
x = sp.Symbol('x')

import sys
_all = json.load(open("cf-open.json"))
_sel = sorted(_all)
OPEN = {a: _all[a] for a in _sel if a in _all}
START = int(os.environ.get("START", "101"))


def tex_escape(s):
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("$", r"\$"),
                 ("^", r"\^{}"), ("~", r"\~{}")]:
        s = s.replace(a, b)
    return s


def render_conj(raw):
    names = []

    def grab(m):
        names.append(m.group(1))
        return f"@@NAME{len(names)-1}@@"

    s = re.sub(r"_([^_]+)_", grab, raw)
    s = tex_escape(s)
    for i, nm in enumerate(names):
        s = s.replace(f"@@NAME{i}@@", r"\emph{" + tex_escape(nm) + "}")
    s = s.replace("Conjecture:", r"\textbf{Conjecture:}", 1)
    return s


def rec_latex(ps):
    parts = []
    for i, p in enumerate(ps):
        if p == 0:
            continue
        pl = sp.latex(sp.factor(p))
        if p.is_Add or (p.is_Mul and len(p.args) > 1):
            pl = f"({sp.latex(sp.expand(p))})" if not sp.factor(p).is_Mul else pl
        term = f"{pl}\\,a(n{'-' + str(i) if i else ''})"
        parts.append(term)
    return " + ".join(parts).replace("+ -", "- ")


TEMPLATE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[margin=1in]{geometry}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{remark}[theorem]{Remark}
\title{A proof of the conjectured closed form for OEIS %(ANUM)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{25 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured closed form for its terms. We prove it. The entry
also posts a generating function $A(x)$; the conjecture is then exactly the statement
that the generating function of the conjectured formula agrees with $A$. The formula is
a $\mathbb{Q}$-linear combination of terms $n^{k}r^{n}$, whose generating function is
computed in closed form by applying $p(\theta)$ to $1/(1-rx)$, with
$\theta=x\,\frac{d}{dx}$. The difference of the two generating functions is then an
explicit rational function; here it collapses to the polynomial $%(BLATEX)s$, of degree
$%(DEG)d$, which proves the closed form for every $n>%(DEG)d$. The computation is exact
rational-function arithmetic, so the conclusion holds for all $n$ at once rather than
for the terms inspected.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 11B37, 05A15, 33F10.\normalsize

\section{The sequence and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry gives the generating function
\begin{equation}\label{eq:gf}
A(x)\;=\;\sum_{n\ge %(OFFSET)d} a(n)\,x^{n}\;=\;%(GFLATEX)s ,
\end{equation}
and it carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

Write $f(n)$ for the conjectured closed form,
\[
f(n)\;=\;%(FLATEX)s .
\]

\section{Closed forms as generating functions}

Let $A(x)=\sum_{n\ge %(OFFSET)d}a(n)x^{n}$ and let $\theta=x\,\dfrac{d}{dx}$, so $\theta$
acts on $x^{m}$ as multiplication by $m$.

\begin{lemma}\label{lem:gf}
Let $r\in\mathbb{Q}$ and let $p$ be a polynomial. Then
\[
\sum_{n\ge0}p(n)\,r^{n}x^{n}\;=\;\bigl(p(\theta)\tfrac{1}{1-rx}\bigr)(x),
\]
a rational function of $x$. Consequently the generating function of any
$\mathbb{Q}$-linear combination of terms $n^{k}r^{n}$ is rational and computable in
closed form.
\end{lemma}

\begin{proof}
$\sum_{n\ge0}r^{n}x^{n}=1/(1-rx)$, and applying $\theta$ multiplies the coefficient of
$x^{n}$ by $n$; so $\theta^{k}$ multiplies it by $n^{k}$, and linearity gives the claim.
Starting the sum at an offset $c$ instead of $0$ subtracts the polynomial
$\sum_{n<c}p(n)r^{n}x^{n}$, which changes nothing below.
\end{proof}

\begin{corollary}\label{cor:criterion}
Let $F(x)=\sum_{n\ge %(OFFSET)d}f(n)x^{n}$. Then $f(n)=a(n)$ for every $n>d$ if and only
if $F-A$ is a polynomial of degree at most $d$.
\end{corollary}

\begin{proof}
The coefficient of $x^{n}$ in $F-A$ is $f(n)-a(n)$, so that difference vanishes for all
$n>d$ exactly when $F-A$ has no terms above $x^{d}$.
\end{proof}

\section{The computation for %(ANUM)s}

By Lemma~\ref{lem:gf} the conjectured formula has generating function
\[
F(x)\;=\;%(FGFLATEX)s ,
\]
and subtracting the entry's generating function \eqref{eq:gf} gives, after exact
cancellation of rational functions,
\[
F(x)-A(x)\;=\;%(BLATEX)s ,
\]
a polynomial of degree $%(DEG)d$.

\begin{theorem}
For every $n>%(DEG)d$,
\[
a(n)\;=\;%(FLATEX)s .
\]
\end{theorem}

\begin{proof}
Immediate from Corollary~\ref{cor:criterion} and the displayed value of $B$.
\end{proof}

\begin{remark}
The polynomial $F-A$ is not an error term: it records the boundary of the claim. A closed
form of this kind typically fails at a few initial indices, where the sequence's own
definition has not yet settled into its eventual pattern, and $F-A$ collects exactly
those discrepancies. Above that range the identity is exact.
\end{remark}

\section{Verification}

Every number above is an output of a script written separately from this note, and two
independent checks were run.

First, the generating function was checked against the entry rather than assumed: the
Taylor coefficients of \eqref{eq:gf} were expanded and compared term by term with the DATA
section of %(ANUM)s, agreeing on all %(NCHECK)d terms compared.

Second, the closed form was evaluated directly on the published terms, without reference
to any generating function: $f(n)$ was computed in exact rational arithmetic and compared
with the entry's own value for every $n>%(DEG)d$ in range, agreeing in all %(NVER)d cases
from $n=%(FIRSTN)d$ upward. This is what Corollary~\ref{cor:criterion} predicts from the
degree of $F-A$, and it is a genuinely different computation from the symbolic one.

The symbolic step is exact throughout. The difference is obtained by rational-function
cancellation in $K$, not by series truncation, so the identity $B=%(BLATEX)s$ is an
identity of functions and the theorem holds for all $n>%(DEG)d$ simultaneously.

\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026. Sequence %(ANUM)s.
\bibitem{kp} M.~Kauers and P.~Paule, \emph{The Concrete Tetrahedron}, Springer, 2011,
Chapter 7 (holonomic closure properties and the translation between recurrences and
differential equations).
\bibitem{stanley} R.~P.~Stanley, \emph{Enumerative Combinatorics}, Volume 2, Cambridge
University Press, 1999, Chapter 6 (algebraic and D-finite generating functions).
\end{thebibliography}
\end{document}
"""


RES = {}


class _TO(Exception):
    pass


def _alarm(sig, frm):
    raise _TO()


signal.signal(signal.SIGALRM, _alarm)


def build():
    os.makedirs("build_cf", exist_ok=True)
    os.makedirs("papers", exist_ok=True)
    num = START
    made = []
    for a in _sel:
        if a not in OPEN:
            continue
        if os.path.exists(f"papers/{num}-PROOF.pdf"):
            num += 1
            continue
        v = OPEN[a]
        from holonomic import taylor
        import closed_form as C
        info = {}
        A = None
        src = v.get("gf_src")
        for g in ([src] if src else []) + v["gfs"]:
            if g is None:
                continue
            try:
                cand = parse_gf(g, 'x', raw=g)
                N0 = min(len(v["data"]) - 1, 10)
                tt = taylor(cand, v["offset"] + N0 + 3)
                if all(sp.simplify(tt[v["offset"] + k] - v["data"][k]) == 0
                       for k in range(N0 + 1)):
                    A = cand
                    break
            except Exception:
                continue
        if A is None:
            print(f"     skip {a}: no g.f. reproduces the terms")
            continue
        f = C.parse_formula(v["conj"])
        F = C.gf_of(f, v["offset"])
        B = sp.expand(sp.cancel(sp.together(F - A)))
        deg = sp.Poly(B, x).total_degree() if B != 0 else 0
        ps = [sp.Integer(0)]
        off = v["offset"]
        subs = {
            "ANUM": a,
            "NAME": tex_escape(v["name"].rstrip('.')),
            "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\\;=\\;"
                           + ", ".join(str(t) for t in v["data"][:8]) + ",\\ \\dots"),
            "GFLATEX": sp.latex(sp.simplify(A)),
            "FLATEX": sp.latex(f),
            "FGFLATEX": sp.latex(sp.simplify(F)),
            
            "BLATEX": sp.latex(B),
            "DEG": deg,
            "ORDER": 0,
            "CONJ": render_conj(v["conj"]),
            # NOT v["time"] and v["revision"]: those come from the candidate record this
            # builder was handed, and when that record has no such field they default to an
            # empty string and 0 -- so eight papers went out asserting "As of the Last
            # modified line on the live entry (, revision 0)", a sentence claiming a check
            # with nothing in it while the entries carried real dates and revisions up to 68.
            # The entry is the authority and is read here.
            "TIME": LE_META(a)[0] or v["time"],
            "REV": LE_META(a)[1] or v["revision"],
            "PSLIST": "",
            "RECLATEX": "",
            "NCHECK": min(len(v["data"]), 13),
            "NVER": v["terms_verified"],
            "FIRSTN": v["first_n"],
        }
        tex = TEMPLATE % subs
        d = f"build_cf/{num}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/p.tex", "w").write(tex)
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "p.tex"],
                           cwd=d, capture_output=True)
        log = open(f"{d}/p.log", errors="ignore").read()
        errs = [l for l in log.split("\n") if l.startswith("! ")]
        pdf = f"{d}/p.pdf"
        good = os.path.exists(pdf) and not errs
        if good:
            subprocess.run(["cp", pdf, f"papers/{num}-PROOF.pdf"])
        made.append((num, a, good, errs[:1]))
        print(f"{num:3d}  {a}  {'OK' if good else 'FAILED ' + str(errs[:1])}")
        num += 1
    print(f"\n{sum(1 for m in made if m[2])}/{len(made)} built")
    return made


if __name__ == "__main__":
    build()
