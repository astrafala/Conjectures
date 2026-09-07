# Pending ledger notes

Written by the hourly working routine; folded into LEDGER.md and cleared by the daily
routine. Not a published document.

## 7 September 2026 --- two papers withdrawn: somebody else was three days earlier

The local OEIS mirror was two days stale. Refreshed to the 7 September export and every one
of the 9676 roster entries re-checked for settlement wording. **27 entries carry such
wording; 25 of them are about a different statement on the same entry** --- the pattern the
openness checker's own docstring records, and the papers involved already say so in their own
first pages (paper 0007 names Greathouse's 2013 confirmation of the square case and proves
Kaydalov's rectangle case; paper 0005 names Adamczewski on Conjectures B and C and proves A).

**Two are real, and both are withdrawn.**

- **A105872**, paper 9503, dated 25 August 2026.
- **A127361**, paper 9509, dated 25 August 2026.

Both prove R. J. Mathar's conjectured polynomial-coefficient recurrence. The entries now
carry `[Proved in Easwar (2026). - Rohun Easwar, Aug 31 2026]`, and the linked preprint is
arXiv:2608.22053, **submitted 22 August 2026** --- verified on the arXiv abstract page, not
inferred from the identifier. That is three days before the date on my papers. The standing
rule is that a result found after mine stays and one found before mine goes; these were found
before mine, so they go. Roster 9703 -> 9701.

Easwar's preprint is cited by six OEIS entries (A002897, A034015, A094213, A105872, A127361,
A290575); only those two were ever in the roster, so nothing else is affected.

**What this says about the method.** The freshness of the mirror is part of the count. A
two-day-old export cost two papers that should never have been claimed, and would have kept
costing them silently. The check is cheap --- one `git pull` and a scan of 9676 entries in
under a minute --- and belongs at the start of every session, not at the end.

## 7 September 2026 --- the 208 the queue never reached: 76 more

The 799 conjecture-carrying candidates were swept in rounds bounded by wall-clock, and the
round ended before the list did: **208 were left unprocessed rather than refused**, which is
a different thing and had to be checked rather than assumed. It was worth checking --- one of
them, A279576, settles in three seconds from a standing start.

Swept at thirty seconds an entry: **76 proved**, thirty-five of them arrays of permutations
under an offset condition, nineteen on permutation arrays with a fixed displacement, ten more
on the same family, and a tail of four engines. None is contradicted by its own published
data.

**Refusals, with the cap beside them, as the rule requires.** 92 refused with `state space >
cap` at **cap 2000000**; 3 exceeded the thirty-second budget in the annihilation test rather
than in the build, and are worth a longer pass rather than a bigger cap; 30 are not open.

**A cost measured, not guessed.** The heavy end of this pool is real work, not a bug:
A264014 builds 1048576 states in 84 seconds. That is why the pass was run at thirty seconds
and the expensive tail deferred, instead of letting four entries consume the whole budget.

**Settlement re-checked before counting.** `freshcheck.py` over all 9750 roster entries
against the 7 September export: 25 carry settlement wording, the same 25 already examined,
every one about a different statement on the same entry. None of the 76 new entries is among
them.

## 7 September 2026 --- the refused pool, measured properly, and one wall recorded

**`src/whyrefused.py`.** "State space > cap" and "build timed out" come back from the sweep
as the same thing --- a refusal --- and they want opposite responses: a bigger cap, or a
longer budget. Re-running everything at both is how an afternoon disappears. The new script
gives each entry a short fixed slice and records which wall it hit, so the next pass can be
aimed instead of sprayed.

**What it found in the 132 unsettled entries of the last pass:** 30 not open, and of the rest
the largest block is `transfer32` at widths 8 and 9, which the diagnostic reported as
cap-refused --- but the cap was never the binding constraint. The build could not finish at
all.

**`transfer32` rebuilt, and it is a real improvement.** The start weights were built by a
triple loop over rows: at width 9 over two letters that is 1.34e8 iterations, each recomputing
every window statistic. Only the statistics matter, and window $j$ of them depends on the
first row through columns $j$, $j+1$, $j+2$ alone. The row is now grown one column at a time,
prefixes agreeing on their last two entries and on the statistics so far are merged carrying
their count, and the within-row constraints are tested the moment their second column appears
so a doomed prefix dies immediately. Verified against the old loop on random row pairs at two
widths --- every weight agrees exactly --- and the rebuilt model reproduces all 22 published
terms of A253932.

**And it is still not enough. Recording the wall with its numbers.** Width 7 builds in 80
seconds. Width 9 has 512 rows, so the outer loop alone is 262144 row pairs at about 10 ms
each: three quarters of an hour before the state count is even known, and it then exceeds
**cap 2000000** anyway. Three entries were run to completion under a 1500-second budget and
none settled. **The 21 `transfer32` entries at widths 8 and 9 are out of reach by this route**
--- not because of the cap, and not for want of a longer budget, but because the pair loop is
quadratic in a row count that doubles with every column. A different formulation would be
needed, and I do not have one. Written down so it is not measured a third time.

The 34 `transfer22` entries in the same pool are a separate question and untouched: their
builds do finish (A264014 reaches 1048576 states in 84 seconds), so they are a cap-and-budget
matter rather than a structural one.

## 7 September 2026 --- 19 more, and the difference between a cap and a clock

`whyrefused.py` said the `transfer22` entries were refused on the cap. They were not: A264014
builds 1048576 states in 87 seconds, computes its terms in 8 and settles its residual in 10 ---
**106 seconds in total, against a 30-second budget.** The refusal was a clock, not a wall.

Re-run at a 200-second budget over the 106 buildable entries of the refused pool: **19 proved**,
all in the permutation-array family, where a value moves from its home cell by an index change
on a short list and the count becomes a matching problem solved column by column. The remaining
entries of that pass were refused again, and those really are cap-bound.

**The two refusals look identical in the log and want opposite responses.** That is the whole
reason `whyrefused.py` exists, and this pass shows it still reports them wrongly when a build
finishes just past the slice it is given. The diagnostic's own slice is now part of what it
reports.

Settlement re-checked against the 7 September export before counting: 25 entries carry
settlement wording, the same 25 already examined, none of them among the 19.
