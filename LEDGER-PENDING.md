## 13 September 2026 — `latpoly` installed: 126 papers, and the roster reaches 11,901

The Ehrhart engine described in the 12–13 September section is installed. 441 names in the
clone are read and every one checked reproduces the entry's published data exactly; 132 were
proved, 126 survive the corrected bound, and those are in the roster as
`lattice-quasipolynomial`. All 177 held results passed the live OEIS re-check before any was
counted.

Six were dropped rather than installed: five whose model no longer builds inside the compute
limits once the bound was corrected, and one whose re-verification did not finish in the time
given. A withheld result costs nothing.

The 461 papers whose model is not a walk were rebuilt a second time. The first rebuild was
correct in its mathematics and wrong in one detail: it stamped each paper with the day its
prose was rewritten rather than the day its result was obtained. The original dates were
recovered from git, keyed by A-number through the previous ranking, and every one of those
papers prints its own date again.

Roster: 11,901 papers = 11,895 proofs + 6 disproofs, over 11,874 entries, 120 distinct
arguments. `stamps/MANIFEST-2026-09-13a.tsv` is stamped.

## 13 September 2026 — six closed forms, from the same model

Of the 441 names `latpoly` reads, 167 carry no parsable conjectured RECURRENCE. Most of that is
real emptiness: **154 carry no conjectural line at all**, so there is nothing on them to settle.
Twelve carry an empirical CLOSED FORM instead — a polynomial in `n` — and one an order-92
recurrence kept in a link.

The closed forms need no new mathematics. The model gives `a(n)` exactly with a derived monic
annihilator `A` of order `S`; a polynomial of degree `d` is annihilated by `(z-1)^(d+1)`; so the
difference is annihilated by `A(z)(z-1)^(d+1)` and `S + d + 1` consecutive agreements settle it.
Six were proved this way and are installed as `lattice-closed-form`; the other six build too
slowly under the present limits and are recorded, not counted.

Roster: 11,907 papers = 11,901 proofs + 6 disproofs, over 11,880 entries, 121 distinct
arguments. `stamps/MANIFEST-2026-09-13b.tsv` is stamped.

## 13 September 2026 — `ecacount`: five ON/OFF cell counts, and a null generalisation

87 entries name the ON or OFF cell count of an elementary cellular automaton, all with a
parsable conjectured recurrence, and no engine read one of them: `ecarow` wanted the word
"representation" on the line. Counting the ON cells of its own certified row identity
`w(n+p) = L + w(n) + R` gives `on(n+p) = on(n) + ones(L) + ones(R)` at once, and the width
`2n+1` handles OFF and the running totals. **Five proved** — that is every rule in the family
the end-insertion certificate reaches, 3 of the 30 distinct rules.

Said plainly: the obvious generalisation is null. Growth by inserting a fixed block at a fixed
offset inside the row certifies **none** of the other 27 rules, at any period up to 16 and any
settling point up to 27. What those need is a certificate at the level of the count rather
than the row, and that is the same obstacle as the 82 two-dimensional automata with no growth
certificate.

## 13 September 2026 — a pair per residue class, and 125 more papers

`ecarow` derives `w(n+p) = L + w(n) + R` for the row of an elementary automaton and verifies it
over every available step. It asked for ONE pair serving every `n` past the settling point, and
that is too rigid. Rule 1 alternates between `1^k 000 1^k` and `0^k 1 0^k`: the identity holds
with `L = R = "11"` on the odd `n` and `"00"` on the even, and no single pair serves both, so
the engine reported no shape at all. `ca2d` has allowed a pair per residue class of `n` since
its bound was corrected — the one-dimensional engine never did.

Two families come in on that one change.

**`ecacount`, ON and OFF cell counts.** 87 entries name the ON or OFF cell count of a named
rule from a single ON cell, or the running total, and every one carries a parsable conjectured
recurrence. No engine read any of them: the row engine wanted the word "representation" on the
line. Counting the ON cells of the row identity gives `on(n+p) = on(n) + ones(L_r) + ones(R_r)`
at once, and the width `2n+1` handles OFF and the totals. With one pair the certificate reached
5 of the 87; per class it reaches 70, and **69 are proved**.

**`ecarow` itself.** 180 entries it reads sat outside the roster. Per class, 100 of them get a
certificate and **56 are proved** — the other 44 carry no parsable recurrence. For the value the
bound is `ca2d`'s: the distinct roots `B^|R_r|`, `B^(|L_r|+|R_r|)` and 1 across the classes,
pulled back to `S^p`, plus the pre-period.

Said plainly, the generalisation that failed: growth by inserting a fixed block at a fixed
offset INSIDE the row certifies none of the 27 rules the end-insertion form misses, at any
period up to 16 and settling point up to 27. What is left needs a certificate at the level of
the count rather than the row.

Roster: 12,032 papers = 12,026 proofs + 6 disproofs, over 12,005 entries, 122 distinct
arguments. `stamps/MANIFEST-2026-09-13c.tsv` is stamped.
