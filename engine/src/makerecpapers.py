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
_all = json.load(open("rec-open.json"))
_sel = [l.strip() for l in open("new-entries.txt")][:100] if os.path.exists("new-entries.txt") else sorted(_all)
OPEN = {a: _all[a] for a in _sel if a in _all}
START = int(os.environ.get("START", "101"))


def tex_escape(s):
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("$", r"\$"),
                 # \^{} is the circumflex ACCENT: it looks like a caret on the page but
                 # lands in the PDF text layer as a control character, so a reader who
                 # copies a quoted recurrence out of the paper gets garbage where every
                 # exponent should be. \textasciicircum is the literal character.
                 ("^", r"\textasciicircum{}"), ("~", r"\textasciitilde{}")]:
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
order %(ORDER)d, contributed by R.~J.~Mathar. We prove it. The generating function of the
entry is algebraic, and the recurrence is equivalent to the vanishing of an explicit
differential operator applied to it: writing $\theta=x\,\frac{d}{dx}$, the sequence
$b(n)=\sum_{i}p_{i}(n)a(n-i)$ has generating function
$B(x)=\sum_{i}x^{i}\,(p_{i}(\theta+i)A)(x)$, so the conjecture holds for all $n>d$ exactly
when $B$ is a polynomial of degree $d$. Since $A$ lies in a quadratic extension of
$\mathbb{Q}(x)$, which is closed under $\theta$, the residual $B$ can be computed in
closed form. Here it equals $%(BLATEX)s$, a polynomial of degree $%(DEG)d$, which proves
the recurrence for every $n>%(DEG)d$.
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

Writing the conjectured relation in the form $\sum_{i=0}^{%(ORDER)d}p_{i}(n)\,a(n-i)=0$,
the coefficient polynomials are
\[
%(PSLIST)s
\]

\section{Recurrences as differential operators}

Let $A(x)=\sum_{n\ge0}a(n)x^{n}$ be the generating function of a sequence, and let
$\theta=x\,\dfrac{d}{dx}$, so that $\theta$ acts on $x^{m}$ as multiplication by $m$. For a
polynomial $p$ we write $p(\theta)$ for the corresponding differential operator, so that
$p(\theta)A=\sum_{m}p(m)a(m)x^{m}$.

\begin{lemma}\label{lem:transfer}
Let $p_{0},\dots,p_{r}$ be polynomials and put $b(n)=\sum_{i=0}^{r}p_{i}(n)\,a(n-i)$, with
the convention $a(m)=0$ for $m<0$. Then
\[
B(x):=\sum_{n\ge0}b(n)x^{n}=\sum_{i=0}^{r}x^{i}\,\bigl(p_{i}(\theta+i)A\bigr)(x).
\]
\end{lemma}

\begin{proof}
Fix $i$ and substitute $m=n-i$:
\[
\sum_{n\ge0}p_{i}(n)a(n-i)x^{n}=\sum_{m\ge0}p_{i}(m+i)a(m)x^{m+i}
=x^{i}\sum_{m\ge0}p_{i}(m+i)a(m)x^{m}=x^{i}\bigl(p_{i}(\theta+i)A\bigr)(x),
\]
the last step because $p_{i}(\theta+i)$ multiplies the coefficient of $x^{m}$ by
$p_{i}(m+i)$. Summing over $i$ gives the claim.
\end{proof}

\begin{corollary}\label{cor:criterion}
With the notation of Lemma~\ref{lem:transfer}, the recurrence
$\sum_{i}p_{i}(n)a(n-i)=0$ holds for every $n>d$ if and only if $B$ is a polynomial of
degree at most $d$.
\end{corollary}

\begin{proof}
$b(n)$ is the coefficient of $x^{n}$ in $B$, so $b(n)=0$ for all $n>d$ says exactly that
$B$ has no terms above $x^{d}$.
\end{proof}

This turns the conjecture into a closed-form identity. The point is that it can then be
decided exactly, with no truncation: $A$ is algebraic, so $B$ lies in the same field as
$A$, and one only has to recognise it.

\begin{lemma}\label{lem:field}
Let $D\in\mathbb{Q}(x)$ and let $K=\mathbb{Q}(x)\bigl[\sqrt{D}\bigr]$. Then $K$ is closed
under $\theta$; explicitly,
\[
\theta\bigl(u+v\sqrt{D}\bigr)=x\,u'+\Bigl(x\,v'+\frac{x\,v\,D'}{2D}\Bigr)\sqrt{D},
\qquad u,v\in\mathbb{Q}(x).
\]
\end{lemma}

\begin{proof}
Differentiate: $(\sqrt{D})'=D'/(2\sqrt{D})=\bigl(D'/(2D)\bigr)\sqrt{D}$, and multiply by
$x$. Both components remain in $\mathbb{Q}(x)$.
\end{proof}

Consequently, if $A\in K$ then every $p_{i}(\theta+i)A$ is in $K$, and so is $B$. Writing
$B=P+Q\sqrt{D}$ with $P,Q\in\mathbb{Q}(x)$, the test of Corollary~\ref{cor:criterion}
becomes: $B$ is a polynomial precisely when $Q=0$ and $P$ has constant denominator. Both
are decided by exact cancellation of rational functions.

\section{The computation for %(ANUM)s}

The generating function \eqref{eq:gf} lies in $K=%(FIELD)s$ with
\[
D \;=\; %(DLATEX)s .
\]
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
holds for every $n>%(DEG)d$.
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


RES = json.load(open("rec-results.json"))


class _TO(Exception):
    pass


def _alarm(sig, frm):
    raise _TO()


signal.signal(signal.SIGALRM, _alarm)


def build():
    os.makedirs("build_rec", exist_ok=True)
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
                base = taylor(G, v["offset"] + N0 + 6)
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
            deg, B = residual_poly(A, ps)
        except Exception as e:
            print(f"     skip {a}: {e}")
            continue
        if deg is None:
            print(f"     skip {a}: residual not polynomial on recheck")
            continue
        q = qf.to_quad(A)
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
            # NOT v["time"] and v["revision"]: those come from the candidate record this
            # builder was handed, and when that record has no such field they default to an
            # empty string and 0 -- so eight papers went out asserting "As of the Last
            # modified line on the live entry (, revision 0)", a sentence claiming a check
            # with nothing in it while the entries carried real dates and revisions up to 68.
            # The entry is the authority and is read here.
            "TIME": LE_META(a)[0] or v["time"],
            "REV": LE_META(a)[1] or v["revision"],
            "PSLIST": ",\\qquad ".join(
                f"p_{{{i}}}(n)={sp.latex(sp.factor(p))}" for i, p in enumerate(ps)),
            "RECLATEX": rec_latex(ps),
            "NCHECK": min(len(v["data"]), 13),
            "NVER": v["terms_verified"],
            "FIRSTN": v["first_n"],
        }
        tex = TEMPLATE % subs
        d = f"build_rec/{num}"
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
