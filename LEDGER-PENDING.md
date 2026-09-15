# Pending batch notes

## 15 September 2026 — ten more, and an eighth self-inflicted disproof

**10 papers; roster 13,718 → 13,728 over 13,325 entries; 163 → 164 arguments.**

Nine from the rebuilt name-readable pool (§AE), which is now in the standing rotation as
`np2run.sh` and had reached 623 of its 1,727 entries. One new argument below.

### The pending-result scan, and what most of it was

189 A-numbers sat in `*_hits*.json` files without a paper. Read one by one: 19 had been
withdrawn, 18 are no longer open, and most of the rest are not results at all —
`brack_hits.json`, `residual_hits.json`, `extr_hits.json` and others are CENSUS files whose
records carry no proof, and they match the `*_hits*` glob only by their names. Of the genuinely
proved and uninstalled, `known_hits.json` holds 7 and `uni_hits.json` 2, and **eight of those
nine entries are marked settled on the live OEIS** — each names the person who proved it, two of
them in 2026 arXiv preprints. Correctly withheld, and worth saying plainly: that file's "PROVED"
means this project's machinery closed it, not that the conjecture was open.

The ninth, **A034267**, was open and is a real result.

### `hypergeometric-ratio` (new argument, `src/hyperrec.py`)

A034267 states `a(n) = binomial(2n, n+1)(n^2+n+1)/(n+2)` as a fact and conjectures a second-order
P-recursive recurrence. The closed form is hypergeometric — `a(n)/a(n-1)` is a rational function
of n — so the sequence satisfies an exact FIRST-order recurrence, and the conjectured one is
settled by reducing it with that ratio. The reduction is identically zero in `Q(n)`: an identity,
not an agreement of terms. **No generating function is needed**, which is the point, because 228
entries in the P-recursive pool state none at all.

Measured over the whole 989-entry pool it is **one entry**, and the first measurement said zero
for a reason worth keeping: `closedform.parse_line` refuses `binomial(...)` outright, so a census
built on it cannot see the shape that makes this argument work. `hyperrec` has its own narrow
reader — binomials, factorials, powers, rational functions, nothing else.

### The eighth self-inflicted disproof

A060774 states `a(n) = 6*binomial(3n,n) - 6*binomial(2n,n)`, which gives 0 at n = 0 where the
entry has 1 — the empty path — and matches every term after it. Demanding agreement from the
offset made that "the stated closed form does not generate the DATA", an accusation against a
correct entry. A closed form is routinely stated for n past the first index or two; what is
required is agreement from SOME index on, with enough terms after it to mean anything, and the
conjecture is then proved from that index. A060774 now refuses honestly and for a different
reason: a SUM of two hypergeometric terms has no rational ratio.

**Eight for eight.** Every apparent disproof this project has produced has been my reader.

## 15 September 2026 — the table-column pool rebuilt: 296 new candidates, no results

`deep-check/tabpool.txt` held 1,729 entries; rebuilt from the clone on the same criterion (an
entry stating a per-column recurrence, off the roster) it is 1,851, so **296 were never asked**.
Swept: **zero results**, and the refusals are worth more than the zero.

| | |
|---:|---|
| 181 | the name is not a `T(n,k)` table |
| 108 | no explicit column recurrence |
| 5 | nothing proved on this table |
| 2 | not open |

Two defects found on the way, both fixed:

**The 276 that vanished without a counter.** `sweep_table` skipped every name not beginning
`T(n,k)` and recorded nothing — defect 3, the one STATE.md has carried since the beginning. The
skip is now counted, which is how the 181 above is known at all.

**The layout wrapper.** The corpus writes the same table a dozen ways — "Triangle read by rows:
T(n,k) is ...", "Array read by descending antidiagonals: A(n, k) = ...", "Triangular array read
by rows: ..." — and the wrapper says how the table is LAID OUT, which matters to the reader of
the data and not at all to the name of column k. `tablecol.PREFIX` strips it, and 115 of the 296
became rewritable. None proved, but the widening applies to the standing pool too.

The 108 "no explicit column recurrence" are honest: they state a **generating function** for
column k (`G.f. for column k: (1-x)^2*x^k/(...)`) rather than a recurrence, which is a different
argument — `gfrec` per column, with the conjecture still to be found. Noted, not built.
