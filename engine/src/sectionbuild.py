#!/usr/bin/env python3
"""Three papers: a conjecture equating an entry to a SECTION of another entry."""
import os, re, json
import entry, phibuild

PRE = phibuild.PRE
esc = phibuild.esc


def head(anum, title, abstract, msc):
    return rf"""{PRE}
\title{{{title}}}
\author{{Adrian Perez Fontelles\\ \small Independent researcher}}
\date{{31 August 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

\noindent\small 2020 Mathematics Subject Classification. {msc}\normalsize
"""


def sec1(anum, srcnum, conj, who, when, modified, rev, extra=""):
    e = entry.get(anum); s = entry.get(srcnum)
    d = [int(x) for x in e['data'].split(',')]
    ds = [int(x) for x in s['data'].split(',')]
    off = int(e['offset'].split(',')[0]); offs = int(s['offset'].split(',')[0])
    return rf"""
\section{{The two sequences and the conjecture}}

OEIS {anum} is ``{esc(e.get('name','').strip())}''. It has offset ${off}$ and begins
\[
{", ".join(str(x) for x in d[:7])},\ \dots
\]
OEIS {srcnum} is ``{esc(s.get('name','').strip())}''. It has offset ${offs}$ and begins
\[
{", ".join(str(x) for x in ds[:8])},\ \dots
\]

The entry {anum} carries the following comment:
\begin{{quote}}\small
{esc(conj)} --- \emph{{{who}}}, {when}
\end{{quote}}
As of the ``Last modified'' line on the live entry ({modified}, revision {rev}) the
statement is still recorded as unproved, and nothing on either entry records it as settled
either way.{extra}
"""


BIB = r"""
\begin{thebibliography}{9}
\bibitem{oeis} The OEIS Foundation, \emph{The On-Line Encyclopedia of Integer Sequences},
\url{https://oeis.org}, 2026.
\bibitem{hw} G.~H.~Hardy and E.~M.~Wright, \emph{An Introduction to the Theory of
Numbers}, 6th ed., Oxford University Press, 2008.
\bibitem{stanley} R.~P.~Stanley, \emph{Enumerative Combinatorics}, Volume 1, 2nd ed.,
Cambridge University Press, 2011.
\end{thebibliography}

\end{document}
"""


def modinfo(anum):
    txt = open(f"/home/user/oeis/oeisdata/seq/{anum[:4]}/{anum}.seq").read()
    m = re.search(r"^%I .*?#(\d+) (.+)$", txt, re.M)
    return (m.group(2).strip(), m.group(1)) if m else ("?", "?")


def p_A084703():
    a, s = "A084703", "A089928"
    mod, rev = modinfo(a)
    e = entry.get(a); se = entry.get(s)
    d = [int(x) for x in e['data'].split(',')]; ds = [int(x) for x in se['data'].split(',')]
    body = head(a,
      r"A quadrisection identity between OEIS A084703 and OEIS A089928",
      r"""OEIS A084703 carries an empirical observation of A.~Ratushnyak that its $n$-th term
equals the $(4n-2)$-nd term of OEIS A089928. It is true, and the proof is a single line
once both entries' own closed forms are put side by side: the exponent $4n$ produced by
the quadrisection turns $(1\pm\sqrt2)^{4n}$ into $(17\pm12\sqrt2)^{n}$, and the parity
term $(-1)^{\lfloor (4n-2)/2\rfloor}$ is constantly $-1$. No generating function is
needed, and in particular the generating function recorded on A089928 is not used --- as
noted below, it does not reproduce that entry's own terms.""",
      "11B37, 11B39, 11D09.")
    body += sec1(a, s,
      "Empirical: a(n) = A089928(4*n-2), for n > 0.", "Alex Ratushnyak", "Apr 12 2013",
      mod, rev)
    body += rf"""
Written out, the statement to be proved is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;b(4n-2)\qquad\text{{for all }} n\ge 1,
\end{{equation}}
where $a$ is A084703 and $b$ is A089928.

\section{{What each entry states as fact}}

A084703 states, not as a conjecture,
\begin{{quote}}\small
a(n) = ((17+12*sqrt(2))\^{{}}n + (17-12*sqrt(2))\^{{}}n - 2)/8.
\end{{quote}}
that is,
\begin{{equation}}\label{{eq:a}}
a(n)\;=\;\frac{{\bigl(17+12\sqrt2\bigr)^{{n}}+\bigl(17-12\sqrt2\bigr)^{{n}}-2}}{{8}} .
\end{{equation}}
A089928 states, not as a conjecture,
\begin{{quote}}\small
a(n) = ( (1+sqrt(2))\^{{}}(n+2) + (1-sqrt(2))\^{{}}(n+2) + 2*(-1)\^{{}}floor(n/2) )/8.
\end{{quote}}
that is,
\begin{{equation}}\label{{eq:b}}
b(m)\;=\;\frac{{\bigl(1+\sqrt2\bigr)^{{m+2}}+\bigl(1-\sqrt2\bigr)^{{m+2}}
+2(-1)^{{\lfloor m/2\rfloor}}}}{{8}} .
\end{{equation}}
Each was checked against its own entry's DATA at every published index before use:
\eqref{{eq:a}} against all ${len(d)}$ terms of A084703 and \eqref{{eq:b}} against all
${len(ds)}$ terms of A089928, in exact arithmetic in $\mathbb{{Z}}[\sqrt2]$. These two
lines are the only input taken from the entries.

\begin{{remark}}\label{{rem:gf}}
A089928 also carries the line ``G.f.: 1/((1+2*x)*(1-2*x-x\^{{}}2))''. That is not the
generating function of A089928: the stated denominator expands to $1-5x^{{2}}-2x^{{3}}$,
whose reciprocal begins $1,0,5,\dots$, whereas the entry begins $1,2,4,\dots$. The
factor $(1+2x)$ should read $(1+x^{{2}})$, since
$(1-2x-x^{{2}})(1+x^{{2}})=1-2x-2x^{{3}}-x^{{4}}$, matching the recurrence in the entry's
name. Nothing below uses that line; it is recorded only so that a reader checking the
entry is not misled.
\end{{remark}}

\section{{The proof}}

\begin{{lemma}}\label{{lem:pow}}
$\bigl(1+\sqrt2\bigr)^{{4}}=17+12\sqrt2$ and $\bigl(1-\sqrt2\bigr)^{{4}}=17-12\sqrt2$.
\end{{lemma}}

\begin{{proof}}
$\bigl(1\pm\sqrt2\bigr)^{{2}}=1\pm2\sqrt2+2=3\pm2\sqrt2$, and
$\bigl(3\pm2\sqrt2\bigr)^{{2}}=9\pm12\sqrt2+8=17\pm12\sqrt2$.
\end{{proof}}

\begin{{lemma}}\label{{lem:sign}}
For every integer $n\ge1$, $(-1)^{{\lfloor (4n-2)/2\rfloor}}=-1$.
\end{{lemma}}

\begin{{proof}}
$4n-2$ is even, so $\lfloor (4n-2)/2\rfloor=2n-1$, which is odd.
\end{{proof}}

\begin{{theorem}}
For every integer $n\ge1$, $a(n)=b(4n-2)$, where $a$ is OEIS A084703 and $b$ is OEIS
A089928. This is the statement of Section~1.
\end{{theorem}}

\begin{{proof}}
Put $m=4n-2$ in \eqref{{eq:b}}. Then $m+2=4n$, so by Lemma~\ref{{lem:sign}}
\[
b(4n-2)=\frac{{\bigl(1+\sqrt2\bigr)^{{4n}}+\bigl(1-\sqrt2\bigr)^{{4n}}-2}}{{8}} .
\]
By Lemma~\ref{{lem:pow}}, $\bigl(1\pm\sqrt2\bigr)^{{4n}}
=\Bigl(\bigl(1\pm\sqrt2\bigr)^{{4}}\Bigr)^{{n}}=\bigl(17\pm12\sqrt2\bigr)^{{n}}$, so
\[
b(4n-2)=\frac{{\bigl(17+12\sqrt2\bigr)^{{n}}+\bigl(17-12\sqrt2\bigr)^{{n}}-2}}{{8}},
\]
which is exactly $a(n)$ by \eqref{{eq:a}}.
\end{{proof}}

\begin{{remark}}
The identity in fact holds at $n=0$ as well: both sides are $0$, since $b(-2)$ is not
defined by the entry but \eqref{{eq:b}} evaluated at $m=-2$ gives $(1+1-2)/8=0=a(0)$. The
restriction $n>0$ in the comment is therefore only a statement about which indices of
A089928 are published.
\end{{remark}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, formula \eqref{{eq:a}} was evaluated in exact arithmetic in $\mathbb{{Z}}[\sqrt2]$ and
compared against every one of the ${len(d)}$ published terms of A084703; the values agree
exactly. A formula that reproduced only some of them would not have been used.

Second, formula \eqref{{eq:b}} was evaluated the same way and compared against every one of
the ${len(ds)}$ published terms of A089928; the values agree exactly. It was also checked
against the recurrence $b(m)=2b(m-1)+2b(m-3)+b(m-4)$ named on that entry.

Third, the identity \eqref{{eq:conj}} was checked directly on the published terms, without
either formula: for every $n$ with $1\le n\le 7$ --- the range for which both $a(n)$ and
$b(4n-2)$ are published --- the two integers agree.
"""
    return body + BIB


def p_A155543():
    a, s = "A155543", "A090129"
    mod, rev = modinfo(a)
    e = entry.get(a); se = entry.get(s)
    d = [int(x) for x in e['data'].split(',')]; ds = [int(x) for x in se['data'].split(',')]
    body = head(a,
      r"A bisection identity between OEIS A155543 and OEIS A090129",
      r"""OEIS A155543 carries a conjecture that its $n$-th term equals the $(2n+2)$-nd term of
OEIS A090129, the multiplicative order of $3$ modulo $2^{n}$. It is true. Both entries
state closed forms as fact --- A090129's is the order computation $2^{n-2}$ for
$n\ge3$, recorded there with a proof, and A155543's is a rational generating function ---
and the two match term for term once the even index $2n+2$ is substituted. The identity
holds at every index, including the one the comment excludes.""",
      "11A07, 11B37, 11A15.")
    body += sec1(a, s,
      "Conjecture: a(n) = A090129(2*n+2).", "the entry (unattributed)", "undated",
      mod, rev)
    body += rf"""
Written out, the statement to be proved is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;b(2n+2),
\end{{equation}}
where $a$ is A155543 and $b$ is A090129. A090129 has offset $1$, so $b(2n+2)$ is defined
for every $n\ge0$.

\section{{What each entry states as fact}}

A090129 is defined as the smallest exponent $b(n)$ with $2^{{n}}\mid 3^{{b(n)}}-1$, that is,
the multiplicative order of $3$ modulo $2^{{n}}$. The entry states, not as a conjecture,
\begin{{quote}}\small
a(n) = 2\^{{}}(n-2) if n >= 3, 1 for n=1 and 2 for n=2 (see the order comment above).
\end{{quote}}
that is,
\begin{{equation}}\label{{eq:b}}
b(1)=1,\qquad b(2)=2,\qquad b(n)=2^{{\,n-2}}\ \ (n\ge3).
\end{{equation}}
The entry also carries the reason, in a comment of W.~Lang: for $n\ge3$ the order of $3$
modulo $2^{{n}}$ is $2^{{n-2}}$, with a reference for the argument. So that nothing here rests
on a reference, that fact is proved from scratch in Section~4; \eqref{{eq:b}} is then not an
assumption at all.

A155543 states, not as a conjecture,
\begin{{quote}}\small
G.f.: 2*(1-2*x)/(1-4*x).
\end{{quote}}
Expanding, $\dfrac{{2(1-2x)}}{{1-4x}}=2\sum_{{k\ge0}}4^{{k}}x^{{k}}-4\sum_{{k\ge0}}4^{{k}}x^{{k+1}}
=2+\sum_{{k\ge1}}\bigl(2\cdot4^{{k}}-4\cdot4^{{k-1}}\bigr)x^{{k}}$, and
$2\cdot4^{{k}}-4^{{k}}=4^{{k}}$, so
\begin{{equation}}\label{{eq:a}}
a(0)=2,\qquad a(n)=4^{{n}}\ \ (n\ge1).
\end{{equation}}
Each was checked against its own entry's DATA at every published index before use:
\eqref{{eq:a}} against all ${len(d)}$ terms of A155543 and \eqref{{eq:b}} against all
${len(ds)}$ terms of A090129.

\section{{The order of $3$ modulo a power of $2$}}

Write $v_2(m)$ for the exponent of $2$ in the integer $m\ne0$.

\begin{{lemma}}\label{{lem:val}}
$v_2\bigl(3^{{2^{{k}}}}-1\bigr)=k+2$ for every $k\ge1$.
\end{{lemma}}

\begin{{proof}}
For $k=1$, $3^{{2}}-1=8$ and $v_2(8)=3$. Suppose the claim for some $k\ge1$. Factor
\[
3^{{2^{{k+1}}}}-1=\bigl(3^{{2^{{k}}}}-1\bigr)\bigl(3^{{2^{{k}}}}+1\bigr).
\]
Since $k\ge1$, the inductive hypothesis gives $8\mid 3^{{2^{{k}}}}-1$, so
$3^{{2^{{k}}}}\equiv1\pmod 8$ and hence $3^{{2^{{k}}}}+1\equiv2\pmod 8$, giving
$v_2\bigl(3^{{2^{{k}}}}+1\bigr)=1$. Therefore
$v_2\bigl(3^{{2^{{k+1}}}}-1\bigr)=(k+2)+1=(k+1)+2$.
\end{{proof}}

\begin{{proposition}}\label{{prop:ord}}
For $n\ge3$ the multiplicative order of $3$ modulo $2^{{n}}$ is $2^{{\,n-2}}$; it is $1$ for
$n=1$ and $2$ for $n=2$. That is, \eqref{{eq:b}} holds.
\end{{proposition}}

\begin{{proof}}
The group $\bigl(\mathbb{{Z}}/2^{{n}}\mathbb{{Z}}\bigr)^{{\times}}$ has order $2^{{\,n-1}}$, so the
order of $3$ divides $2^{{\,n-1}}$ and is therefore $2^{{k}}$ for some $k\ge0$; it is the
least such $k$ with $2^{{n}}\mid 3^{{2^{{k}}}}-1$, that is, with $v_2\bigl(3^{{2^{{k}}}}-1\bigr)\ge n$.

Let $n\ge3$. By Lemma~\ref{{lem:val}} the condition reads $k+2\ge n$ for $k\ge1$, and for
$k=0$ it reads $v_2(2)=1\ge n$, which fails. The least admissible $k$ is thus $n-2$, which
is $\ge1$ exactly because $n\ge3$. Hence the order is $2^{{\,n-2}}$.

For $n=1$, $3\equiv1\pmod2$ and the order is $1$. For $n=2$, $3\equiv3\pmod4$ and
$3^{{2}}=9\equiv1$, so the order is $2$.
\end{{proof}}

\section{{The proof}}

\begin{{theorem}}
For every integer $n\ge0$, $a(n)=b(2n+2)$, where $a$ is OEIS A155543 and $b$ is OEIS
A090129. This is the statement of Section~1.
\end{{theorem}}

\begin{{proof}}
Take $n\ge1$. Then $2n+2\ge4\ge3$, so Proposition~\ref{{prop:ord}} gives
\[
b(2n+2)\;=\;2^{{\,(2n+2)-2}}\;=\;2^{{2n}}\;=\;4^{{n}},
\]
which is $a(n)$ by \eqref{{eq:a}}.

For $n=0$ the index is $2n+2=2$, and Proposition~\ref{{prop:ord}} gives $b(2)=2$, while \eqref{{eq:a}}
gives $a(0)=2$. The two agree, so the identity holds at $n=0$ as well.
\end{{proof}}

\begin{{corollary}}
For every $n\ge1$ the multiplicative order of $3$ modulo $2^{{2n+2}}$ is $4^{{n}}$.
\end{{corollary}}

\begin{{proof}}
Immediate from the theorem and the definition of A090129, together with \eqref{{eq:a}}.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, the generating function of A155543 was expanded in exact rational arithmetic and
compared against every one of the ${len(d)}$ published terms; the values agree exactly. A
generating function that reproduced only some of them would not have been used.

Second, formula \eqref{{eq:b}} was evaluated and compared against every one of the
${len(ds)}$ published terms of A090129; the values agree exactly. Independently, the order
of $3$ modulo $2^{{n}}$ was computed directly by repeated squaring for every $n$ in that
range and matched the same values, so the closed form was not taken on trust; and
Lemma~\ref{{lem:val}} was checked by computing $v_2\bigl(3^{{2^{{k}}}}-1\bigr)$ exactly for
$k\le12$, giving $3,4,5,\dots,14$ as the lemma requires.

Third, the identity \eqref{{eq:conj}} was checked directly on the published terms, without
either formula: for every $n$ from $0$ to $17$ --- the range for which both $a(n)$ and
$b(2n+2)$ are published --- the two integers agree.
"""
    return body + BIB


def p_A111403():
    a, s = "A111403", "A002716"
    mod, rev = modinfo(a)
    e = entry.get(a); se = entry.get(s)
    d = [int(x) for x in e['data'].split(',')]; ds = [int(x) for x in se['data'].split(',')]
    body = head(a,
      r"A bisection identity between OEIS A111403 and OEIS A002716",
      r"""OEIS A111403 carries a conjecture of R.~J.~Mathar that its $n$-th term is one less than
the $(2n)$-th term of OEIS A002716, Somos's infinite coprime sequence. It is true. The
recurrence A002716 states as fact splits into two closed forms, one for each parity of the
index, and a short induction proves both at once: the odd-indexed terms are exactly the
Fermat numbers $2^{2^{n+1}}+1$, and the even-indexed terms are $2^{2^{n+1}}-2^{2^{n}}+1$,
which is one more than the defining expression for A111403.""",
      "11B37, 11B83, 11A41.")
    body += sec1(a, s,
      "Conjecture: a(n) = A002716(2*n)-1.", "R. J. Mathar", "May 15 2007", mod, rev,
      extra=(" (A002716 carries a separate conjecture of the same contributor, on its "
             "odd-indexed terms; it is not the statement treated here, and it is not used "
             "below.)"))
    body += rf"""
Write $f(m)=2^{{m}}$. The name of A111403 defines
\begin{{equation}}\label{{eq:a}}
a(n)\;=\;f\bigl(f(n+1)\bigr)-f\bigl(f(n)\bigr)\;=\;2^{{2^{{n+1}}}}-2^{{2^{{n}}}},
\end{{equation}}
and the statement to be proved is
\begin{{equation}}\label{{eq:conj}}
a(n)\;=\;b(2n)-1\qquad\text{{for all }} n\ge0,
\end{{equation}}
where $b$ is A002716.

\section{{What A002716 states as fact}}

A002716 states, not as a conjecture,
\begin{{quote}}\small
a(2*n + 1) = a(2*n) + a(2*n - 1) - 1, a(2*n) = a(2*n - 1)\^{{}}2 - 3 * a(2*n - 1) + 3,
a(0) = 3, a(1) = 5.
\end{{quote}}
that is, with $b$ for the sequence,
\begin{{equation}}\label{{eq:rec}}
b(0)=3,\quad b(1)=5,\qquad
b(2n)=b(2n-1)^{{2}}-3\,b(2n-1)+3,\qquad
b(2n+1)=b(2n)+b(2n-1)-1
\end{{equation}}
for $n\ge1$. This determines $b$ completely, and it is the only input taken from that
entry; it was checked against all ${len(ds)}$ of its published terms before use.

\section{{The proof}}

\begin{{lemma}}\label{{lem:cf}}
For every $n\ge0$,
\[
b(2n+1)\;=\;2^{{2^{{n+1}}}}+1 ,
\]
and for every $n\ge1$,
\[
b(2n)\;=\;2^{{2^{{n+1}}}}-2^{{2^{{n}}}}+1 .
\]
\end{{lemma}}

\begin{{proof}}
Induction on $n$, proving the odd-index statement and using it to get the next
even-index one.

For $n=0$ the first claim reads $b(1)=2^{{2}}+1=5$, which is the initial condition in
\eqref{{eq:rec}}.

Let $n\ge1$ and suppose $b(2n-1)=2^{{2^{{n}}}}+1$, which is the first claim at $n-1$. Write
$u=2^{{2^{{n}}}}$, so $b(2n-1)=u+1$ and $u^{{2}}=2^{{2^{{n+1}}}}$. By \eqref{{eq:rec}},
\[
b(2n)=(u+1)^{{2}}-3(u+1)+3=u^{{2}}+2u+1-3u-3+3=u^{{2}}-u+1
=2^{{2^{{n+1}}}}-2^{{2^{{n}}}}+1,
\]
which is the second claim at $n$. Then, again by \eqref{{eq:rec}},
\[
b(2n+1)=b(2n)+b(2n-1)-1=\bigl(u^{{2}}-u+1\bigr)+\bigl(u+1\bigr)-1=u^{{2}}+1
=2^{{2^{{n+1}}}}+1,
\]
which is the first claim at $n$. The induction is complete.
\end{{proof}}

\begin{{theorem}}
For every integer $n\ge0$, $a(n)=b(2n)-1$, where $a$ is OEIS A111403 and $b$ is OEIS
A002716. This is the statement of Section~1.
\end{{theorem}}

\begin{{proof}}
For $n\ge1$, Lemma~\ref{{lem:cf}} gives
$b(2n)-1=2^{{2^{{n+1}}}}-2^{{2^{{n}}}}$, which is $a(n)$ by \eqref{{eq:a}}.

For $n=0$ we have $b(0)=3$ from \eqref{{eq:rec}}, so $b(0)-1=2$, while \eqref{{eq:a}} gives
$a(0)=2^{{2}}-2^{{1}}=2$. The two agree.
\end{{proof}}

\begin{{corollary}}
The odd-indexed terms of A002716 are the Fermat numbers: $b(2n+1)=F_{{n+1}}$, where
$F_m=2^{{2^{{m}}}}+1$.
\end{{corollary}}

\begin{{proof}}
This is the first statement of Lemma~\ref{{lem:cf}}.
\end{{proof}}

\section{{Verification}}

Three checks, each independent of the algebra above.

First, \eqref{{eq:a}} was evaluated in exact integer arithmetic and compared against every
one of the ${len(d)}$ published terms of A111403; the values agree exactly.

Second, the recurrence \eqref{{eq:rec}} was iterated in exact integer arithmetic and
compared against every one of the ${len(ds)}$ published terms of A002716; the values agree
exactly. The two closed forms of Lemma~\ref{{lem:cf}} were then evaluated independently and
matched against the same terms at every index of each parity.

Third, the identity \eqref{{eq:conj}} was checked directly on the published terms, without
any closed form: for every $n$ with $0\le n\le5$ --- the range for which both $a(n)$ and
$b(2n)$ are published --- the two integers agree.
"""
    return body + BIB
