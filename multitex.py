#!/usr/bin/env python3
"""The multiquadratic variant of the recurrence paper.

When the generating function needs several independent square roots, the single-radical
lemma stated in the base template is not the lemma the computation actually uses. This
swaps in the general statement: theta is diagonal in the basis of square-root products,
so no basis mixing occurs and the polynomiality test reads off componentwise.
"""

ABSTRACT_OLD = r"""Since $A$ lies in a quadratic extension of
$\mathbb{Q}(x)$, which is closed under $\theta$, the residual $B$ can be computed in
closed form."""
ABSTRACT_NEW = r"""Since $A$ lies in a multiquadratic extension of
$\mathbb{Q}(x)$, which is closed under $\theta$, the residual $B$ can be computed in
closed form."""

LEMMA_OLD = r"""\begin{lemma}\label{lem:field}
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
are decided by exact cancellation of rational functions."""

LEMMA_NEW = r"""\begin{lemma}\label{lem:field}
Let $D_{1},\dots,D_{k}\in\mathbb{Q}(x)$ and let
$K=\mathbb{Q}(x)\bigl[\sqrt{D_{1}},\dots,\sqrt{D_{k}}\bigr]$. For a subset
$S\subseteq\{1,\dots,k\}$ write $e_{S}=\prod_{i\in S}\sqrt{D_{i}}$, so that the $e_{S}$
span $K$ over $\mathbb{Q}(x)$. Then $K$ is closed under $\theta$, and $\theta$ is diagonal
in this spanning set:
\[
\theta\bigl(c\,e_{S}\bigr)=\Bigl(x\,c'+c\sum_{i\in S}\frac{x\,D_{i}'}{2D_{i}}\Bigr)e_{S},
\qquad c\in\mathbb{Q}(x).
\]
\end{lemma}

\begin{proof}
For each $i$, $(\sqrt{D_{i}})'=D_{i}'/(2\sqrt{D_{i}})=\bigl(D_{i}'/(2D_{i})\bigr)\sqrt{D_{i}}$.
Applying the Leibniz rule to the product $e_{S}=\prod_{i\in S}\sqrt{D_{i}}$ therefore
returns $e_{S}$ itself multiplied by $\sum_{i\in S}D_{i}'/(2D_{i})$, a rational function.
Differentiating $c\,e_{S}$ and multiplying by $x$ gives the stated formula. No basis
element other than $e_{S}$ occurs, which is the diagonality claim.
\end{proof}

Consequently, if $A\in K$ then every $p_{i}(\theta+i)A$ is in $K$, and so is $B$. Writing
$B=\sum_{S}c_{S}\,e_{S}$ with $c_{S}\in\mathbb{Q}(x)$, the test of
Corollary~\ref{cor:criterion} becomes: $B$ is a polynomial precisely when $c_{S}=0$ for
every $S\neq\emptyset$ and $c_{\emptyset}$ has constant denominator. Both are decided by
exact cancellation of rational functions."""

FIELD_OLD = r"""The generating function \eqref{eq:gf} lies in $K=%(FIELD)s$ with
\[
D \;=\; %(DLATEX)s .
\]
Applying Lemma~\ref{lem:transfer} to the coefficient polynomials of Section~1 and reducing
in $K$ by Lemma~\ref{lem:field}, the $\sqrt{D}$ component of $B$ cancels identically and
the rational part collapses to"""

FIELD_NEW = r"""The generating function \eqref{eq:gf} lies in $K=%(FIELD)s$ with
\[
%(DLIST)s .
\]
Applying Lemma~\ref{lem:transfer} to the coefficient polynomials of Section~1 and reducing
in $K$ by Lemma~\ref{lem:field}, every component $c_{S}$ of $B$ with $S\neq\emptyset$
cancels identically and the remaining rational part collapses to"""


def adapt(template):
    """Return the multiquadratic version of the single-radical template."""
    out = template
    for old, new in ((ABSTRACT_OLD, ABSTRACT_NEW), (LEMMA_OLD, LEMMA_NEW),
                     (FIELD_OLD, FIELD_NEW)):
        if old not in out:
            raise ValueError("template block not found:\n" + old[:60])
        out = out.replace(old, new, 1)
    return out
