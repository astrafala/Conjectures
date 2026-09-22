# Pending batch notes

Batch notes are appended here by the hourly working routine and folded into `LEDGER.md` by the
daily one.

## 22 September 2026 (morning) — A253494, and an honest note on how small the claim is

**A253494**, `transfer31`, S=48,293, roster 13,791 → 13,792. Its conjecture is
`a(n) = 6a(n-1) - 11a(n-2) + 6a(n-3) for n>6` — characteristic roots 1, 2 and 3 — and the entry
carries two other `Empirical:` lines saying the same thing a different way, a closed form
`49*3^(n-1) + 5322*2^(n-1) + 38777` and Colin Barker's generating function with denominator
`(1-x)(1-2x)(1-3x)`.

**Said plainly: this is a small claim.** An order-3 recurrence whose roots are 1, 2, 3 is about
as simple a linear structure as this vein produces, and the entry's own closed form makes that
visible to anyone reading it. The work is still real — a proof has to show the count satisfies
the recurrence, which is what the 48,293-state transfer matrix does, and the entry says
"Empirical" three times — but nobody should read it as a surprising structure.

Its DATA guard read **16** terms, so this one has an empirical check of its own and did not need
the b-file fallback.

## 22 September 2026 — correction: the clock runner DID produce a result

I said several times, and it went into LEDGER.md's 21–22 September section as
*"the re-settinged cap and clock runners have produced nothing at all"*, that none of the
runners whose lists and settings were fixed overnight had yielded anything.

**That is wrong for `tmorun`.** A253494 was on `deep-check/tmolist.txt` — it is absent from the
current file only because the roster strip removed it once it was papered, and git history
confirms it was there at the time. The runner's `PROVED: 1` for this generation is that entry.

So the budget raise paid. `tmorun` asked at `BUDGET=300` against a list where **39 of its 62
entries carried a `uniall_tmo` row of exactly 300** — the vein whose whole subject is the clock,
re-asking at a budget already known to be too short. Raised to 500, it proved A253494.

The claim stands for the others: `caprun`, `rcaprun` and `resrun` have still produced nothing,
and `t21run` turned out to be asking nothing at all (defect 57) and is retired. **The next daily
fold should amend the 21–22 September section accordingly** — the sentence as written is false.

What the veins are refusing now, which is the more useful half: across all six runners the
dominant reason this generation is *out of budget on an earlier pass* — 19, 4, 3, 15 and 28 of
their asked entries respectively. **The clock, not the cap, is what is holding the remaining
pool**, and every one of those rows was written at a budget the runner has already raised past
once.

## 22 September 2026 — the clock is the ceiling, and the budgets are doubled

Measured across all six runners: the dominant refusal this generation is **out of budget on an
earlier pass** — 19, 4, 3, 15 and 28 entries respectively. Not the cap.

That matches which settings have actually paid. **Every budget raise has produced a result and
every cap raise has produced nothing:** `tmorun` 300 → 500 gave A253494, `t17run` 420 → 550 gave
A252102, A252128 and A252145; `caprun`, `rcaprun` and `resrun` all went to CAP=8,000,000 and
have yielded nothing at all, and a measured test showed a cap of 32,000,000 does not open the
`transfer35` family either.

The raise that fits inside the old outer timeout is **8 percent** — 600 → 651, 550 → 566 — which
will not convert an entry that has already exhausted its budget. The two raises that worked were
67 and 31 percent. So the timeouts rise with the budgets:

| runner | BUDGET | outer timeout | 3×BUDGET |
|---|---:|---:|---:|
| `tmorun` | 500 → **1000** | 1700 → **3300** | 3000 |
| `t17run` | 550 → **1100** | 1700 → **3400** | 3300 |

Both kept under the per-phase rule — `3 * BUDGET` must stay below the outer timeout or an entry
is killed with its marker on disk and written down as something it is not (defect 50).

`caprun` and `rcaprun` are left alone deliberately: their lists are built from **cap** refusals,
not clock ones, so a longer clock is not the thing they are short of. Only 14 and 7 of their
entries are clock-blocked at all.

Askable after the change: `tmorun` 50 of 60, `t17run` 36 of 54.

## 22 September 2026 — A269637: a false recurrence that the entry's own data refutes ten times

The last surviving candidate from the defect-58 rescan, checked by hand, and it is real.

**A269637**, "Number of length-n 0..5 arrays with no repeated value differing from the previous
repeated value by other than plus two or minus 1.", offset 1, carries one formula line, an
**Empirical recurrence of order 10**. The entry publishes **20** terms. With offset 1 and order
10 the line asserts something at each of n = 11, …, 20 — and **it fails at all ten**. At n = 11
the entry prints 199677806 and its own line gives 199034092, short by 643714; the gap grows by a
factor of between 5.5 and 6 at each index after that.

That much needs no model at all. Ten multiply-adds on the twenty integers the entry prints, and
the disproof is done. This is the first disproof here that is visible from the entry alone.

**The correction.** A 42-state transfer model — state = (last entry, last repeated value, or
"none yet") — reproduces all 20 DATA terms and all 210 b-file terms, and its first seven values
were confirmed by brute-force enumeration over all 6^n tuples. Solving from its terms, the least
order admitting a constant-coefficient recurrence is **13**, integral, and its **first ten
coefficients are exactly the published ones**. The published line is the correct recurrence with
`+583350*a(n-11) +364874*a(n-12) +80630*a(n-13)` dropped. Proved by annihilation: p(M)u is the
**zero vector** of Z^42, so the order-13 line holds for every n ≥ 14 outright — the usual
Cayley–Hamilton appeal is not even needed (it was run anyway, and vanishes for every m < 42).

This is the **A197230 shape a second time**: correct as far as it goes, truncated. What is new is
that here the truncation is visible from the entry alone — and the entry's **parent table A269640
already names the order of this column as 13**, printing "k=5: [order 13]" where it prints the
full line for k = 1, 2, 3. Two places on the OEIS disagree about this recurrence and one of them
is right.

Live re-check: revision 4, unchanged since Mar 02 2016, still empirical, nothing recording it as
settled or corrected.

**The rest of the family is clean**, and that is worth saying because a defect in a Hardin table
usually means a defect in a column-family. A269635 (k=3, order 7), A269636 (k=4, order 7),
A269638 (k=6, order 14) and A269639 (k=7, order 16) all hold at every index their DATA can test.
A269643 and A269644 disagree with their data at two indices apiece, and **both are false alarms**:
each line states "for n>9" / "for n>10" and the disagreements are inside the excluded range —
the A208046 lesson, and the checker that flagged them was mine, ignoring the stated range.
A269637 is the only member of the family whose line is false.

Paper installed at roster slot 14978 (DISPROOF, engine `disproof`, order 13, degree 42).
`src/verify_a269637.py` re-derives every claim in it from scratch and passes.

**One result**, not four: one entry, one conjecture.

### The same defect one layer up: A026672

The paragraph recording defect 59 — the one written to correct seven false disproofs caused by
the index convention — contained an eighth. It said A026672 "fails under both readings". There
are four readings, not two. Mathar's relation on A026672 (offset 2, 22 terms) fails under
`n = index` and under `n = index + offset`; under **`n = index + 1`** it holds at **all 19**
indices the published data can test, with no failures at all. Not a disproof.

It is now a **proof** candidate instead: the entry carries `G.f.: x*C(x)^4/(1-x*C(x)^3)` stated
as fact, so the conjectured P-recursive relation is exactly what the standard residual test
settles. Queued there.

Nine candidates from the defect-58 rescan became one. **Eight were my reading**, and one of the
eight was inside the paragraph correcting the other seven. A checker that ignores a stated range
or a stated index convention does not find false conjectures — it manufactures them, and it will
keep doing so one level at a time until the check is written to try every reading and call a
conjecture false only when none holds.

A236647 is closed as **untestable**, not refuted: order 34 against sixteen published terms.

## 22 September 2026 — defect 60: installing one paper destroyed the source of 104 others

Installing the A269637 disproof meant running the ranking chain, and the chain quietly deleted
**104 LaTeX sources**. `paper-sources/` went 13,183 → 13,079. The line that did it read
"381 dropped as belonging to another paper", which sounds like tidying.

`sync_sources.py` matches a paper to its source by hashing the PDF against the build directory
that compiled it. **For 714 papers no build directory survives** — the build tree is working
state and is not stored — so for those the only copy of the source is the file under that
paper's rank. Inserting one paper at rank 1619 shifted the 12,174 papers after it by one rank.
For a shifted paper with no build directory the script looked under its new rank, found the
previous occupant's source, rightly judged it named a different paper, and deleted it —
without ever looking one name away at the paper's own source, which was sitting right there.

Proportional to the shift, and fired on every ranking. Not introduced today; the next daily
fold would have taken the same bite.

Fixed by the one stable key there is: the slot id `was`. `rank.py` now keeps the ranking it
replaces as `rank-map-prev.json`, and `sync_sources.py` carries a source across by `was`
whenever no build directory survives — reading everything it must carry before writing or
deleting anything, because the destinations overlap the old locations. A carried source must
still name the paper it lands under.

All 104 recovered from git by `was`, each verified to name its own paper.
`engine/src/test_sync_sources.py` is the regression test: four papers, one inserted at rank 2,
every source must survive. It fails against the old code and passes against the new.

**The lesson.** A count that only goes up is not a check. `sync_sources` printed five numbers
every run and none of them was sources-before against sources-after. The deletion was loud in
the filesystem and invisible in the output.
