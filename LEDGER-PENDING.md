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
