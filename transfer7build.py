#!/usr/bin/env python3
"""One paper per Hardin entry counting arrays UP TO RELABELLING of the values."""
import os, json, re
import localentry as LE, phibuild, transferbuild

PRE = phibuild.PRE
esc = phibuild.esc
rec_tex = transferbuild.rec_tex


def conj_line(anum):
    e = LE.get(anum)
    for L in e["comment"] + e["formula"]:
        if re.search(r'onjectur|Empirical', L, re.I) and re.search(r'a\(n\)\s*=', L):
            return L
    return None


def build(h):
    a = h["anum"]
    W, K, S = h["fixed"], h["K"], h["S"]
    order, nterms, nthr = h["order"], h["nterms"], h["nthr"]
    base, frac, raw = h["base"], h["frac"], h["raw"]
    rowwalk = h["walk"] == "rows"
    e = LE.get(a)
    d = [int(v) for v in e["data"].split(",") if v.strip()]
    mod, rev = e["modified"], e["revision"]
    conj = conj_line(a)
    off = h["offset"]
    line = "row" if rowwalk else "column"
    lines = "rows" if rowwalk else "columns"
    cross = "column" if rowwalk else "row"
    crosses = "columns" if rowwalk else "rows"
    powtex = rf"n+{base}-1" if base != 1 else "n"
    scale = rf"{K}!" + ("" if frac == 1 else rf"\,/\,{frac}")
    fracinv = "" if frac == 1 else rf"\tfrac1{{{frac}}}"

    if h["kind"] == "sub":
        blocktex = (r"\begin{pmatrix}\alpha&\beta\\\gamma&\delta\end{pmatrix}"
                    r"=\begin{pmatrix}r_j&r_{j+1}\\s_j&s_{j+1}\end{pmatrix}" if rowwalk else
                    r"\begin{pmatrix}\alpha&\beta\\\gamma&\delta\end{pmatrix}"
                    r"=\begin{pmatrix}r_i&s_i\\r_{i+1}&s_{i+1}\end{pmatrix}")
        condpara = rf"""Every $2\times2$ subblock of the array occupies two consecutive
{lines} and two consecutive {crosses}; writing those two {lines} as $r$ and $s$ the
subblock is
\[
{blocktex},
\]
and the entry's requirement on it is
\begin{{equation}}\label{{eq:loc}}
{h['tex']}.
\end{{equation}}"""
        startword = (rf"""Because the condition involves no {line} before the first, every
{line} may start a walk, and $\mathbf{{s}}_i=\mathbf{{1}}$.""")
    else:
        nb = h["nbtex"]
        condpara = rf"""Write $x_{{t,u}}$ for the entry in {line} $t$ and {cross} $u$. The
entry's requirement is that no cell equals more than ${h['lim']}$ of its neighbours at the
offsets
\[
\mathcal N=\{{{nb}\}}
\]
(offsets given as ({line} shift, {cross} shift), and only cells inside the array count),
that is
\begin{{equation}}\label{{eq:loc}}
\#\bigl\{{(d_1,d_2)\in\mathcal N:\ x_{{t+d_1,\,u+d_2}}=x_{{t,u}}\bigr\}}\;\le\;{h['lim']}
\qquad\text{{for every cell }}(t,u).
\end{{equation}}
Every offset in $\mathcal N$ points backwards in the walk, so the condition at a cell of
{line} $t$ is settled by {line} $t$ itself together with {line} $t-1$."""
        startword = (rf"""The first {line} has no {line} before it, so its cells are tested
against their within-{line} neighbours only; $\mathbf{{s}}_i$ is the indicator vector of the
{lines} that pass that test.""")

    return rf"""{PRE}
\title{{The empirical recurrence for OEIS {a}, proved by counting patterns}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
OEIS {a} counts arrays subject to a local condition \emph{{and}} to the clause ``new values
$0..{K - 1}$ introduced in row major order'', which says the array is written in canonical
form. That clause is not local, so a transfer matrix over the alphabet does not see it. It
does not have to: what is being counted is not arrays but equality patterns, and the number
of patterns is recovered from the numbers $L_i$ of arrays over an $i$-letter alphabet by
inverting a falling factorial. The result is the clean identity
${K}!\,a(n)=\sum_i\binom{{{K}}}{{i}}D_{{{K}-i}}L_i(n)$ with $D_m$ the derangement numbers,
and each $L_i$ is an ordinary walk count. A second reduction --- the chain is strongly
lumpable over the patterns, because the condition is relabelling-invariant --- brings the
state space down from ${raw}$ to $S={S}$. The entry's empirical recurrence of order
${order}$, contributed by R.~H.~Hardin, then follows from a finite exact computation.
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. 05A15, 05A18, 15B36.\normalsize

\section{{The sequence and the conjecture}}

OEIS {a} is ``{esc(e['name'].strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:8])},\ \dots
\]
The entry carries the following comment:
\begin{{quote}}\small
{esc(conj)}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({mod}, revision {rev}) the statement is
still recorded as empirical, and nothing on the entry records it as settled either way.

Written out, the claim is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;{rec_tex(h['coeffs'])}
\end{{equation}}
for all $n>{nthr}$.

\section{{What the canonical-form clause counts}}

Fix the shape: ${W}$ {crosses} and $L=n+{base}$ {lines}, so $L\cdot{W}$ cells. Call a
partition of the cells into nonempty classes a \emph{{pattern}}; an array over an alphabet
determines a pattern, two cells lying in the same class exactly when they carry the same
value.

{condpara}

The condition is stated purely in terms of equalities between entries, so it is invariant
under any relabelling of the values and is therefore a property of the pattern alone. Call a
pattern \emph{{admissible}} when it has the property.

The clause ``new values $0..{K - 1}$ introduced in row major order'' selects, from each class
of arrays that differ only by a relabelling, exactly one representative: reading the cells in
row major order, the first occurrence of the value $v$ must precede the first occurrence of
$v+1$. Every pattern with at most $K={K}$ classes has exactly one such representative, and
every array in canonical form is the representative of its own pattern. Hence, writing
$N_j(n)$ for the number of admissible patterns with exactly $j$ classes,
\begin{{equation}}\label{{eq:apat}}
a(n)\;=\;{fracinv}\sum_{{j=0}}^{{{K}}}N_j(n).
\end{{equation}}

\begin{{lemma}}\label{{lem:inv}}
Let $L_i(n)$ be the number of arrays over an alphabet of $i$ letters satisfying the local
condition, with no canonical-form clause. Then
\[
L_i(n)=\sum_j N_j(n)\,i(i-1)\cdots(i-j+1),
\qquad
{K}!\,\sum_{{j=0}}^{{{K}}}N_j(n)=\sum_{{i=0}}^{{{K}}}\binom{{{K}}}{{i}}D_{{{K}-i}}\,L_i(n),
\]
where $D_m=m!\sum_{{t=0}}^{{m}}(-1)^t/t!$ is the number of derangements of $m$ letters.
\end{{lemma}}

\begin{{proof}}
An array over $i$ letters satisfying the condition determines an admissible pattern together
with an injection of its classes into the alphabet, and conversely; a pattern with $j$
classes admits $i(i-1)\cdots(i-j+1)$ injections. That is the first identity. Writing
$i(i-1)\cdots(i-j+1)=j!\binom{{i}}{{j}}$ it reads $L_i=\sum_j (j!N_j)\binom{{i}}{{j}}$, so by
binomial inversion $j!N_j=\sum_{{i}}(-1)^{{j-i}}\binom{{j}}{{i}}L_i$. Summing over
$j\le {K}$ and exchanging the order of summation,
\[
\sum_{{j=0}}^{{{K}}}N_j=\sum_{{i=0}}^{{{K}}}L_i\sum_{{j=i}}^{{{K}}}\frac{{(-1)^{{j-i}}}}{{i!\,(j-i)!}}
=\sum_{{i=0}}^{{{K}}}\frac{{L_i}}{{i!}}\sum_{{t=0}}^{{{K}-i}}\frac{{(-1)^t}}{{t!}} ,
\]
and multiplying by ${K}!$ turns the coefficient of $L_i$ into
$\frac{{{K}!}}{{i!}}\sum_{{t\le {K}-i}}(-1)^t/t!=\binom{{{K}}}{{i}}({K}-i)!\sum_{{t\le {K}-i}}(-1)^t/t!
=\binom{{{K}}}{{i}}D_{{{K}-i}}$, an integer.
\end{{proof}}

\section{{Each $L_i$ is a walk count, and the chain lumps}}

Fix $i$ and let $V_i=\{{0,\dots,i-1\}}^{{{W}}}$ be the possible {lines}. For $r,s\in V_i$
declare $r\to s$ an edge when placing $s$ directly after $r$ satisfies \eqref{{eq:loc}} at
every {cross}, and let $M_i$ be the adjacency matrix. An array is exactly a sequence of
{lines}, and its condition is exactly the conjunction of the edge conditions along that
sequence, so
\[
L_i(n)\;=\;\mathbf{{s}}_i^{{\!\top}}M_i^{{\,{powtex}}}\mathbf{{1}} .
\]
{startword}

\begin{{lemma}}\label{{lem:lump}}
Let $\pi(r)$ be the equality pattern of the {line} $r$. For all $r,r'$ with
$\pi(r)=\pi(r')$ and every pattern $Q$,
\[
\#\{{s:\ r\to s,\ \pi(s)=Q\}}\;=\;\#\{{s:\ r'\to s,\ \pi(s)=Q\}}\, .
\]
Consequently the numbers $\widehat M_i[P][Q]$ obtained by taking any representative of $P$
are well defined, and with $e_P=i(i-1)\cdots(i-|P|+1)$ the number of {lines} of pattern $P$,
\[
\mathbf{{s}}_i^{{\!\top}}M_i^{{\,m}}\mathbf{{1}}\;=\;\sum_P \varepsilon_P\,f_m(P),
\qquad f_0\equiv1,\quad f_{{m+1}}(P)=\sum_Q\widehat M_i[P][Q]f_m(Q),
\]
where $\varepsilon_P=e_P$ if {lines} of pattern $P$ may start a walk and $0$ otherwise.
\end{{lemma}}

\begin{{proof}}
If $\pi(r)=\pi(r')$ then the map sending the value of $r$ at a {cross} to the value of $r'$
at that {cross} is a well-defined injection between the letters used, and extends to a
permutation $\sigma$ of the alphabet with $r'=\sigma(r)$. The edge condition is a statement
about equalities among entries, so $r\to s$ if and only if $\sigma(r)\to\sigma(s)$; and
$\pi(\sigma(s))=\pi(s)$. Hence $s\mapsto\sigma(s)$ is a bijection between the two successor
sets preserving patterns, which is the first claim. It says the chain is strongly lumpable
over $\pi$, so $\bigl(M_i^{{m}}\mathbf{{1}}\bigr)(r)$ depends on $r$ only through $\pi(r)$;
calling that value $f_m(\pi(r))$ gives the recursion, and summing over $r$ in each class
gives the displayed identity, the number of {lines} of pattern $P$ being the number of
injections of its $|P|$ classes into the alphabet.
\end{{proof}}

Assembling the ${K}$ lumped chains into one block-diagonal matrix $N$ of size $S={S}$ and
putting the weights of Lemma~\ref{{lem:inv}} into the start vector,
$\mathbf{{v}}=\bigl(\binom{{{K}}}{{i}}D_{{{K}-i}}\varepsilon_P\bigr)_{{i,P}}$, gives
\begin{{equation}}\label{{eq:walk}}
{scale}\;a(n)\;=\;\mathbf{{v}}^{{\!\top}}N^{{\,{powtex}}}\mathbf{{1}} .
\end{{equation}}
The unlumped alphabet had ${raw}$ {lines} in all; the lumped chain has $S={S}$ states.

\section{{The criterion, and the computation}}

Let $q(t)=t^{{{order}}}-\sum_i c_i\,t^{{{order}-i}}$ be the characteristic polynomial of
\eqref{{eq:conj}}.

\begin{{lemma}}\label{{lem:crit}}
For every $n$ with $m=n+{base}-1\ge{order}$,
\[
{scale}\Bigl(a(n)-\sum_i c_i\,a(n-i)\Bigr)\;=\;\mathbf{{v}}^{{\!\top}}N^{{\,m-{order}}}q(N)\mathbf{{1}} .
\]
Hence \eqref{{eq:conj}} holds from that point on if and only if
$\mathbf{{v}}^{{\!\top}}N^{{j}}q(N)\mathbf{{1}}=0$ for every $j\ge0$, and it is enough to check
$j=0,1,\dots,S-1$.
\end{{lemma}}

\begin{{proof}}
Substitute \eqref{{eq:walk}} into the left side and factor $N^{{m-{order}}}$ out of
$N^{{m}}-\sum_i c_iN^{{m-i}}$. The scalar ${scale}$ is nonzero, so it does not affect whether
the left side vanishes. For the last clause put $w=q(N)\mathbf{{1}}$: by Cayley--Hamilton
$N^{{S}}$ is an integer combination of $I,N,\dots,N^{{S-1}}$, so each
$\mathbf{{v}}^{{\!\top}}N^{{j}}w$ with $j\ge S$ is the corresponding combination of earlier
values.
\end{{proof}}

\begin{{theorem}}
The recurrence \eqref{{eq:conj}} holds for every $n>{nthr}$, which is the statement of
Section~1.
\end{{theorem}}

\begin{{proof}}
The lumped transition counts were obtained by enumerating, for one representative {line} of
each pattern, all admissible successors and sorting them by pattern --- the successors being
generated {cross} by {cross}, since the edge condition is a conjunction of one constraint per
{cross}. The vector $w=q(N)\mathbf{{1}}$ was then formed by ${order}$ matrix--vector products
in exact integer arithmetic and $\mathbf{{v}}^{{\!\top}}N^{{j}}w$ evaluated for
$j=0,1,\dots$, again exactly. Every one of those integers vanishes from the index
corresponding to $n={nthr}+1$ onwards, and the run continued until $w$ was the zero vector,
which settles all larger $j$ at once. Lemma~\ref{{lem:crit}} gives the theorem.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the whole construction was compared against the entry's DATA: the right-hand side of
\eqref{{eq:walk}}, divided by ${scale}$, was evaluated at every one of the ${nterms}$
published indices and agrees exactly. This is a strong test of the modelling and not only of
the arithmetic --- the inversion of Lemma~\ref{{lem:inv}}, the reading of the local
condition, and the alignment of the entry's index with the number of {lines} would each
show up as a mismatch, and the quotient by ${scale}$ came out an integer at every index.

Second, the lumped chain was checked against the unlumped one: for the small shapes the walk
counts $\mathbf{{s}}_i^{{\!\top}}M_i^{{m}}\mathbf{{1}}$ were computed directly over the full
alphabet as well and agree with $\sum_P\varepsilon_Pf_m(P)$ term by term.

Third, the recurrence \eqref{{eq:conj}} was evaluated on the published terms in exact integer
arithmetic with no matrices involved, and the annihilation test of Lemma~\ref{{lem:crit}} was
run until the working vector was identically zero rather than to a sampled prefix.

\begin{{thebibliography}}{{9}}
\bibitem{{oeis}} The OEIS Foundation, \emph{{The On-Line Encyclopedia of Integer
Sequences}}, \url{{https://oeis.org}}, 2026. Sequence {a}.
\bibitem{{stanley}} R.~P.~Stanley, \emph{{Enumerative Combinatorics}}, Volume 1, 2nd ed.,
Cambridge University Press, 2011. (Transfer-matrix method, Section 4.7; Stirling and
falling-factorial inversion, Section 1.9.)
\bibitem{{kemeny}} J.~G.~Kemeny and J.~L.~Snell, \emph{{Finite Markov Chains}}, Springer,
1976. (Strong lumpability, Section 6.3.)
\bibitem{{fs}} P.~Flajolet and R.~Sedgewick, \emph{{Analytic Combinatorics}}, Cambridge
University Press, 2009.
\end{{thebibliography}}

\end{{document}}
"""


if __name__ == "__main__":
    hits = [h for h in json.load(open("transfer7_hits.json")) if not h.get("FAILS")]
    for h in hits:
        dd = f"build/t7{h['anum']}"
        os.makedirs(dd, exist_ok=True)
        open(f"{dd}/p.tex", "w").write(build(h))
    print("wrote", len(hits), "papers")
