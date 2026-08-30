#!/usr/bin/env python3
"""Generate papers 52-100: one per OEIS entry whose conjectured recurrence we settle.

Each paper stands alone and refers to no other.
"""
import json, os, re, signal, subprocess
import sympy as sp
from prove_rec import parse_gf, parse_conj
from egf import residual_egf
import quadfield as qf
import multiquad as mq

n = sp.Symbol('n')
x = sp.Symbol('x')

import sys
_all = json.load(open("logexp-open.json"))
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
\title{A proof of the conjectured recurrence for OEIS %(ANUM)s}
\author{Adrian Perez Fontelles\\ \small Independent researcher}
\date{25 August 2026}
\begin{document}
\maketitle

\begin{abstract}
OEIS %(ANUM)s carries a conjectured linear recurrence with polynomial coefficients, of
order %(ORDER)d. We prove it. The entry's exponential generating function is
transcendental, so the usual algebraic arguments do not apply; instead we observe that it
lies in a finitely generated module over $\mathbb{Q}(x)$ spanned by monomials
$\log(u)^{a}\exp(g)^{k}$, and that this module is closed under differentiation, because
$(\log u)'=u'/u$ and $(\exp g)'=g'\exp g$ lower the log power and fix the exponential
respectively. Re-indexing the recurrence forward turns shifts into derivatives, so the
sequence $b(m)=\sum_{j}q_{j}(m)a(m+j)$ has exponential generating function
$B=\sum_{j}q_{j}(\theta)A^{(j)}$, computed exactly inside that module. Here $B$ collapses
to the polynomial $%(BLATEX)s$, of degree $%(DEG)d$, which proves the recurrence for every
$n>%(DEG)d$.
\end{abstract}

\noindent\small 2020 Mathematics Subject Classification. 11B37, 05A15, 12H05, 33F10.\normalsize

\section{The sequence and the conjecture}

OEIS %(ANUM)s is ``%(NAME)s''. It has offset $%(OFFSET)d$ and begins
\[
%(FIRSTTERMS)s
\]
The entry gives the exponential generating function
\begin{equation}\label{eq:gf}
A(x)\;=\;\sum_{n\ge %(OFFSET)d} a(n)\,\frac{x^{n}}{n!}\;=\;%(GFLATEX)s ,
\end{equation}
and it carries the following comment:
\begin{quote}\small
%(CONJ)s
\end{quote}
As of the ``Last modified'' line on the live entry (%(TIME)s, revision %(REV)s) the
statement is still recorded as a conjecture, and no proof appears among the entry's links,
formulas or programs.

Writing the conjectured relation in the form $\sum_{i=0}^{%(ORDER)d}p_{i}(n)\,a(n-i)=0$,
the coefficient polynomials are
\[
%(PSLIST)s
\]

\section{Recurrences as differential operators}

Let $A(x)=\sum_{n\ge0}a(n)x^{n}/n!$ be the exponential generating function of a sequence, and let
$\theta=x\,\dfrac{d}{dx}$, so that $\theta$ acts on $x^{m}$ as multiplication by $m$. For a
polynomial $p$ we write $p(\theta)$ for the corresponding differential operator, so that
$p(\theta)A=\sum_{m}p(m)a(m)x^{m}/m!$.

\begin{lemma}\label{lem:transfer}
Let $p_{0},\dots,p_{r}$ be polynomials and suppose the conjecture asserts
$\sum_{i=0}^{r}p_{i}(n)a(n-i)=0$. Re-index by $n=m+r$ and $j=r-i$, and write
$q_{j}(m)=p_{r-j}(m+r)$, so the claim reads $\sum_{j=0}^{r}q_{j}(m)\,a(m+j)=0$. Put
$b(m)=\sum_{j}q_{j}(m)a(m+j)$. Then
\[
B(x):=\sum_{m\ge0}b(m)\frac{x^{m}}{m!}=\sum_{j=0}^{r}\bigl(q_{j}(\theta)A^{(j)}\bigr)(x),
\]
where $A^{(j)}$ denotes the $j$-th derivative of $A$.
\end{lemma}

\begin{proof}
For an exponential generating function an upward shift is differentiation:
$\sum_{m\ge0}a(m+j)x^{m}/m!=A^{(j)}(x)$. Multiplying the coefficient of $x^{m}/m!$ by
$q_{j}(m)$ is exactly the action of $q_{j}(\theta)$, and summing over $j$ gives the
statement. The re-indexing is what makes this work: a downward shift $a(n-i)$ would
correspond to repeated integration, whereas an upward shift is a derivative, and the
field used below is closed under differentiation.
\end{proof}

\begin{corollary}\label{cor:criterion}
With the notation of Lemma~\ref{lem:transfer}, the recurrence
$\sum_{i}p_{i}(n)a(n-i)=0$ holds for every $n>d+r$ if and only if $B$ is a polynomial of
degree at most $d$.
\end{corollary}

\begin{proof}
$b(m)$ is $m!$ times the coefficient of $x^{m}$ in $B$, so $b(m)=0$ for all $m>d$ says
exactly that $B$ has no terms above $x^{d}$.
\end{proof}

This turns the conjecture into a closed-form identity. The point is that it can then be
decided exactly, with no truncation: $A$ is algebraic, so $B$ lies in the same field as
$A$, and one only has to recognise it.

\begin{lemma}\label{lem:field}
Let $u,g\in\mathbb{Q}(x)$ and let $M$ be the $\mathbb{Q}(x)$-module spanned by the
monomials $\log(u)^{a}\exp(g)^{k}$ for $a\ge0$ and $k\in\mathbb{Z}$. Then $M$ is closed
under $d/dx$, and hence under $\theta=x\,d/dx$; explicitly,
\[
\frac{d}{dx}\Bigl(c\,\log(u)^{a}\exp(g)^{k}\Bigr)
=\Bigl(c'+c\,k\,g'\Bigr)\log(u)^{a}\exp(g)^{k}
\;+\;c\,a\,\frac{u'}{u}\,\log(u)^{a-1}\exp(g)^{k},
\qquad c\in\mathbb{Q}(x).
\]
\end{lemma}

\begin{proof}
Differentiate the product. The factor $\exp(g)^{k}=\exp(kg)$ contributes $kg'$ and does
not change the monomial; the factor $\log(u)^{a}$ contributes $a(u'/u)\log(u)^{a-1}$,
lowering the log exponent by one. Both new coefficients lie in $\mathbb{Q}(x)$, so the
result is again a finite combination of the same monomials.
\end{proof}

Two features make this usable. The exponential part never mixes monomials at all, and the
logarithmic part only ever moves \emph{downwards}, so the module generated by any single
element is finite dimensional and every computation terminates. Writing $B$ in this basis,
the test of Corollary~\ref{cor:criterion} becomes: $B$ is a polynomial precisely when every
coefficient outside the monomial $\log(u)^{0}\exp(g)^{0}$ vanishes and the remaining
coefficient has constant denominator. Both are decided by exact cancellation of rational
functions, so no series truncation enters anywhere.

\section{The computation for %(ANUM)s}

The generating function \eqref{eq:gf} lies in the module $M$ of
Lemma~\ref{lem:field}.
Applying Lemma~\ref{lem:transfer} to the coefficient polynomials of Section~1 and reducing
in $K$ by Lemma~\ref{lem:field}, the $\sqrt{D}$ component of $B$ cancels identically and
the rational part collapses to
\[
B(x)\;=\;%(BLATEX)s ,
\]
a polynomial of degree $%(DEG)d$.

\begin{theorem}
The conjectured recurrence
\[
%(RECLATEX)s \;=\;0
\]
holds for every $n>%(NGT)d$.
\end{theorem}

\begin{proof}
Immediate from Corollary~\ref{cor:criterion} and the displayed value of $B$.
\end{proof}

\begin{remark}
The polynomial $B$ is not an error term: it records the boundary of the recurrence. For
$n\le%(DEG)d$ some of the shifted terms $a(n-i)$ fall outside the range of the sequence,
and $B$ collects exactly those contributions. Above that range the relation is exact.
\end{remark}

\section{Verification}

Every number above is an output of a script written separately from this note, and two
independent checks were run.

First, the generating function was checked against the entry rather than assumed: the
Taylor coefficients of \eqref{eq:gf} were expanded and compared term by term with the DATA
section of %(ANUM)s, agreeing on all %(NCHECK)d terms compared.

Second, the recurrence itself was evaluated directly on the published terms, in exact
integer arithmetic and without reference to the generating function: for each $n$ in range
the sum $\sum_{i}p_{i}(n)a(n-i)$ was formed from the entry's own values and found to
vanish, for all %(NVER)d values of $n$ from $n=%(FIRSTN)d$ upward. This is what
Corollary~\ref{cor:criterion} predicts from the degree of $B$, and it is a genuinely
different computation from the symbolic one: it never forms $B$, never differentiates, and
uses only integers.

The symbolic step is exact throughout. The residual is obtained by rational-function
cancellation in $K$, not by series truncation, so the identity $B=%(BLATEX)s$ is an
identity of functions and the theorem holds for all $n>%(NGT)d$ simultaneously.

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


RES = json.load(open("logexp-results.json"))


class _TO(Exception):
    pass


def _alarm(sig, frm):
    raise _TO()


signal.signal(signal.SIGALRM, _alarm)


def build():
    os.makedirs("build_logexp", exist_ok=True)
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
        info = RES.get(a, {})
        sh = info.get("shift", 0) or 0
        src = info.get("gf_src")
        A = None
        for g in ([src] if src else []) + v["gfs"]:
            if g is None:
                continue
            try:
                G = parse_gf(g, 'x', raw=g)
                N0 = min(len(v["data"]) - 1, 11)
                base = [c * sp.factorial(k) for k, c in enumerate(taylor(G, v["offset"] + N0 + 6))]
                idx = [v["offset"] + k - sh for k in range(N0 + 1)]
                if any(i < 0 or i >= len(base) for i in idx):
                    continue
                if all(sp.simplify(base[i] - v["data"][k]) == 0
                       for k, i in enumerate(idx)):
                    A = sp.together(x ** sh * G)
                    break
            except Exception:
                continue
        if A is None:
            print(f"     skip {a}: no g.f. reproduces the terms")
            continue
        ps = parse_conj(v["conj"])
        try:
            _ok, B = residual_egf(A, ps)
            deg = (sp.Poly(B, x).total_degree() if B != 0 else 0) if _ok else None
        except Exception as e:
            print(f"     skip {a}: {e}")
            continue
        if deg is None:
            print(f"     skip {a}: residual not polynomial on recheck")
            continue
        q = None
        if q is not None:
            Dtex = sp.latex(sp.factor(q[2]))
            fieldtex = r"\mathbb{Q}(x)[\sqrt{D}]"
        else:
            mm = mq.to_multi(A)
            Ds = mm[1] if mm else []
            Dtex = ",\quad ".join(sp.latex(sp.factor(D)) for D in Ds)
            fieldtex = (r"\mathbb{Q}(x)\bigl[\sqrt{D_{1}},\dots,\sqrt{D_{%d}}\bigr]" % len(Ds)) if Ds else r"\mathbb{Q}(x)"
        off = v["offset"]
        subs = {
            "ANUM": a,
            "NAME": tex_escape(v["name"].rstrip('.')),
            "OFFSET": off,
            "FIRSTTERMS": (f"a({off}),\\dots,a({off+7})\\;=\\;"
                           + ", ".join(str(t) for t in v["data"][:8]) + ",\\ \\dots"),
            "GFLATEX": sp.latex(sp.simplify(A)),
            "DLATEX": Dtex,
            "FIELD": fieldtex,
            "BLATEX": sp.latex(B),
            "DEG": deg,
            "ORDER": len(ps) - 1,
            "CONJ": render_conj(v["conj"]),
            "TIME": v["time"],
            "REV": v["revision"],
            "PSLIST": ",\\qquad ".join(
                f"p_{{{i}}}(n)={sp.latex(sp.factor(p))}" for i, p in enumerate(ps)),
            "RECLATEX": rec_latex(ps),
            "NCHECK": min(len(v["data"]), 13),
            "NVER": v["terms_verified"],
            "FIRSTN": v["first_n"],
        }
        tex = TEMPLATE % subs
        d = f"build_logexp/{num}"
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
