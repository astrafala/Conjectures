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

## 22 September 2026 — a new scan: tables that name an order their own column entries contradict

A269637's disproof was corroborated by something that cost nothing. Its parent table A269640
prints, in one block, the full recurrence for its short columns and a **placeholder naming only
the order** for its long ones — `k=5: [order 13]` — while A269637, which *is* column 5,
publishes an order-10 line. Two statements on the OEIS about the same recurrence, disagreeing,
and the disagreement visible without computing anything.

So: **scan the whole clone for that shape.** `src/tableorder.py` reads every
`%F <table> k=<j>: ...` block, every `Column j of <table>` / `Row n of <table>` comment, and
compares the order the table names against the order the member entry's own line has.

**The measurement: 399,027 files, 2,111 tables with per-column blocks, 22,866 column/row
members, 6,430 pairs where both sides say something about the same recurrence.**

**Exactly two disagreements in the whole OEIS.** And both are real:

| | table says | entry says | truth | dropped |
|---|---:|---:|---:|---|
| A269637 (k=5 of A269640) | 13 | 10 | **13** | last 3 terms |
| A236647 (k=2 of A236651) | 38 | 34 | **38** | last 4 terms |

In both the table is right, the column entry's line is the correct recurrence truncated, and
the published coefficients are the true line's first ones term for term. Two for two.

### A236647, the second one

"Number of (n+1)X(2+1) 0..2 arrays colored with the maximum plus the upper median minus the
lower median minus the minimum of every 2X2 subblock", offset 1, 16 DATA terms — but a
**b-file of 210**. Order 34 first asserts at n = 35, so the b-file tests it 176 times and it
**fails all 176**, first at n = 35 short by 145,084,608. Again no model is needed for the
disproof: the entry's own published terms do it.

The wording had to be pinned down and then checked rather than assumed. Hardin's "colored with
X of every 2X2 subblock" means the 2X2 subblocks are **properly coloured** by
χ = max + upper median − lower median − min: horizontally and vertically adjacent subblocks get
different χ. Brute force over all 3^(3(n+1)) arrays gives 484, 4500, 41980 for n = 1,2,3 — the
entry's first three terms — and the same rule at width 2 reproduces A236646, the k=1 column.

A 224-state transfer model (last row, colours of the subblock row just completed) reproduces
all 16 DATA terms and all 210 b-file terms. The recurrence that holds has **order 38**, integral,
first 34 coefficients exactly the published ones, tail
`+1733120*a(n-35) +12956032*a(n-36) +5889024*a(n-37) -243712*a(n-38)`.

The proof is an annihilation that does **not** vanish, and that is the interesting part:
1ᵀp(M)u = 114,688 ≠ 0, so the order-38 line fails at n = 39 — while 1ᵀMᵐ(M·p(M)u) = 0 for every
m ≤ 224 and hence for all m, so it holds for every n ≥ 40. **The table said "for n>39" and that
is exactly the exception the matrix produces.** Every order 1..37 fitted on the tail fails
there, so 34 is not merely incomplete — no order-34 recurrence exists.

Paper installed at rank 1278 (A269637 is now 1620). `src/verify_a236647.py` re-derives every
claim and passes.

### What the scan refused, which is the more useful half

The first run also reported 839 pairs as ABSENT — a table naming an order for a column entry
that carried no recurrence at all. **That number is now 0**, and the correction is the familiar
one: those entries *do* carry the conjecture, in prose. When the line is long the entry writes
`Empirical recurrence of order 26 (see link above)` instead of the coefficients, and a parser
that only reads lines containing `a(n-` counts them as carrying nothing. 839 "new conjectures"
were my own parser.

Two other corrections came out of the same scan and are worth keeping:

* **Six false hits from the table's stride.** A263913's columns alternate with zeros, so its
  lines are written in a(n-2), a(n-4), … and its column entries count (2n+2)X(k+2) arrays —
  one term per two table rows. All four of its columns looked like contradictions of *exactly*
  a factor of two. Dividing by the stride unconditionally then turned fourteen agreeing pairs
  into disagreements, because a short column can have only even lags without the block being in
  double units. Both directions are the defect-59 lesson: **report a contradiction only when no
  reasonable reading agrees.**
* **521 pairs silently dropped** because only `[order N]` was matched. The placeholder is also
  written `[linear recurrence of order N]` (423), `[same order N]` (79) and
  `[same linear recurrence of order N]` (19) — and one of the dropped lines was in the very
  block carrying the second disproof.

**The honest verdict on the vein: it is exhausted, and it was worth running.** 6,430 pairs, two
hits, both papers. There is no third.

### The same scan found the table sweep's pool was built from one wording

`tabpool.txt` held 1,729 tables and was assembled by matching the block header
`Empirical for column k:`. Scanning for the **`k=<j>:` lines themselves** finds **1,983**
column tables, and 431 row tables against a row pool of 444. The entries do not all use that
header — A200785 writes `Empirical formulas for columns:` — and a pool built from one wording
is a pool that silently drops the rest.

**379 tables carrying 1,535 column conjectures and 98 carrying 388 row ones had never been
asked about.** Merged into `deep-check/tabpool.txt` (1,729 → 2,108) and
`deep-check/rowpool.txt` (444 → 542), written by rename because a running shard reads them at
startup, and `tabrun.sh` restarted on the wider pool.

Not a result — a queue. But 1,923 conjectures the machinery was structurally unable to see,
found by a scan built for something else entirely, which is the usual way.

The blind spot this looked for and did **not** find is worth stating too: only **one** table
line printed in full belongs to a column entry that carries no formula of its own. Where a
column entry exists, it repeats the table's line essentially always. The gap was never
table-states-it-and-entry-does-not; it was tables whose columns have no entry at all.

## 22 September 2026 — measured: which engine deserves an on-the-fly quotient

2,759 entries are refused at the **cap** — the largest single block of unasked work, and
IDEAS.md §T named the lever a week ago: every engine builds the whole reachable set and only
then merges, so the cap is hit during *exploration* and `lumpauto` runs too late to help.
`transfer17` got a Myhill–Nerode quotient of its own (`build_lineset`); nothing else did.

Before writing that again, measure whether it pays. `src/lumpgain.py` takes entries an engine
has actually built, rebuilds them, lumps, and reports the ratio — with `uniform.lumpable()`
factored out of `threshold`, which already knew the per-engine shape but knew it only inline,
so nothing could ask "what would this model merge to".

| engine | capped | median lump ratio | |
|---|---:|---:|---|
| transfer17 | 332 | 3.50× | already quotients (`build_lineset`) |
| transfer40 | 201 | 7.00× | |
| transfer19 | 169 | 2.36× | |
| transfer9 | 114 | 3.00× | |
| transfer21 | 103 | **16.37×** | reaches `transfer17.build_pairfree` |
| transfer20 | 103 | **30.38×** | untouched |

**transfer20 and transfer21 are the targets** — 206 capped entries between them at 30× and 16×.
And the number that decides it is not the median but the trend: the ratio **grows with the
width**, which is to say it grows exactly where the cap bites. A184545/46/47 go 12.95×, 21.80×,
37.89× as the width rises; A185459…A185464 go 1.60× to 3.86×. An engine whose redundancy is
flat would not be worth the surgery; these are not flat.

Read the medians as medians: 4 builds each, and one 40× outlier says nothing about the 103
entries behind it. The trend is the evidence, not the maximum.

## 22 September 2026 — defect 61: 36 percent of the "refused at the cap" file was finished work

`uniall_caps.json` held **2,759** rows. Cross-referenced against the files sitting next to it:

* **997 were already HITS of the very sweep that wrote them**; 1,004 were papered by some engine
* **0 were unasked** — every one had been asked, and `sweep_shard` re-asks them every round
* 1,762 were done-and-not-a-hit, which is the real remaining pool

So more than a third of the refusal file was finished work, and every measurement built on it —
which engine deserves attention, how much a raised cap would open, what a list is askable
against — was inflated by that much.

`merge_shards.py` already carried the fix, **for `oom` alone**, under a comment naming
`uniall_caps.json` as exactly the thing it existed to stop. Written once, applied to one file of
four. And the version extended to `caps` still did nothing, because `CAPS` was dumped *above*
the pruning block: the run deleted 1,004 rows from a dict nothing wrote again, and printed that
it had retired them. A fix that reports success and changes no file is worse than no fix.

All four files now pruned against `roster | hits`, dump moved below the prune. **2,759 → 1,755.**

### What it changed

An hour earlier I measured which engine deserves an on-the-fly quotient and concluded
**transfer20** — highest lump ratio at 30.38x, 103 entries refused at the cap. After the prune
transfer20 has **18**. Eighty-five percent of the entries I was about to do engine surgery for
were already settled.

| engine | capped before | after | lump ratio |
|---|---:|---:|---:|
| transfer40 | 201 | **198** | 7.00x |
| transfer17 | 332 | 98 | 3.50x (already quotients) |
| transfer34 | 94 | **87** | 10.67x |
| transfer9 | 114 | 83 | 3.00x |
| transfer21 | 103 | 71 | 16.37x |
| transfer20 | 103 | 18 | 30.38x |

**transfer40 is the target** — it barely moved, so its refusals are real — with transfer34
second on ratio times count.

`src/capwhy.py` is the auditor. Its first 58 rebuilds found **42 BUILDS and 16 TIMEOUT, not one
honest CAP**; the BUILDS rows build in a median of **2.5 seconds** at the cap they were
"refused" at. Every one of them was already done, which is what led to the count above.

**The habit says read what a sweep refuses. It also has to say: check that the refusal is still
true.** A refusal file is a claim with a date on it, and nothing here was re-reading the date.

## 22 September 2026 — defect 62: three phases, one number, and what the sweep is actually refusing

Having made `uniall_caps.json` honest, the obvious next question is what the refusals now say.
The live sweep's own tally, this generation:

      385  out of budget on an earlier pass
       64  out of memory
       44  a shard died holding this entry 3 times or more
        9  state space > cap
        6  build timed out
        1  engine returned no model

**Nine cap refusals against 385 clock refusals.** So the on-the-fly quotient — the lever
IDEAS.md §T named and I spent this morning measuring targets for — is aimed at nine entries.
Twice in one day I aimed at the cap and the cap was not what was holding anything.

But "out of budget" is not one problem. `sweep_shard` distinguishes **three** timeouts in its
own counters — `build timed out`, `terms timed out`, `annihilation timed out` — and writes the
**same** `tmo[a] = BUDGET` for all three. The file whose entire purpose is keeping refusals
apart (defects 48, 49, 53 went to that trouble) throws away the distinction that decides what
to speed up: exploring a state space, iterating the matrix, or the annihilation test. These are
three different fixes and one number.

The phase was never unavailable — `inflight` writes it for the death marker. It was simply not
kept. Now written to `uniall_tmophase.json`, beside `uniall_tmo.json` rather than inside it so
every reader expecting an int still works, folded by `merge_shards` and pruned with the rest.
Sweeps restarted, since a source fix does not reach a running process.

**Defect 48 one level down.** That one separated the cap from the clock from the memory; this
one separates the clock from itself. The next firing can read which phase the 385 are losing
to, and that is the first time that question has had an answer on disk.

## 22 September 2026 — defect 63: the openness test could not read a refutation

`bsweep` reached 9,333 of 10,632 and surfaced two unpapered DISPROVED candidates. One is real.
The other is the more useful finding.

**A210247 is not open.** "Conjecture: a(n) = -a(n-28)" does fail — at n = 606 and twice more in
2,000 terms — and the entry says so on the line immediately below:

> That is not quite true: the first counterexample is n=578, where a(578)=a(578+28)=-1.
> — *Robert Israel*, Sep 05 2018

`livenew` called it open, twice over: none of the PROOF words appears in Israel's line, and the
co-occurrence test asks the same line to say "conjecture" or "recurrence", which rules out a
refutation referring to its claim **by position** — how most of them are written. (My checker
and Israel agree exactly: he names the index the relation reads from, 578; the sweep names the
index it is asserted at, 578 + 28 = 606.)

One build away from papering a disproof the entry already records, and the binding rule
"check every apparent disproof by hand against the entry's own wording" would **not** have
caught it, because the wording to check is the conjecture, and the conjecture really is there.

`REFUTED` now matches *is false / is not true / not quite true / fails at / fails for /
counterexample / disproved / refuted / is incorrect / does not hold / breaks down at*, read
without the co-occurrence requirement. **Audited across all 13,391 papered entries: one hit,
and it is a false positive** — A114584's example line about Motzkin paths, the definition at
work. No papered result is compromised, and REFUTED is now read only where settlements are
actually recorded: not in examples, not in programs.

Worth recording separately: wiring it in as `or REFUTED.search(l)` inside the existing
comprehension silently un-guarded the other branch, since `A or B and not N` binds as
`A or (B and not N)`. That is defect 56's 41 entries reintroduced by an `or`. Both branches
carry the guard now.

### A196074 is real, and it is the truncation shape a third time

"Number of nX4 0..4 arrays with each element x equal to the number its horizontal and vertical
neighbors equal to 0,3,2,1,4", offset 1, 30 DATA terms, **200-term b-file**. Its order-37
empirical line first asserts at n = 38 and **fails at all 163 indices the b-file can test**,
first at n = 38 by 393. No model needed, as with A269637 and A236647.

Fitting from the b-file, the least order that holds is **43**, integral, verified on 157 terms —
and **its first 37 coefficients are exactly the published ones**, with
`+274*a(n-38) +112*a(n-39) +84*a(n-40) -56*a(n-41) +8*a(n-42) -8*a(n-43)` dropped. Live: still
open, revision 9, Oct 2025.

Not yet papered, deliberately. The A197230 precedent is that solving for the correction only
*proposes* it; what makes it a theorem is annihilation against a model. A196074 is column 4 of
A196078 and is read by `transfer19`, which **refuses it at the cap** — it is one of the entries
in the refused pool. So the paper waits on a model, and the disproof is complete without one.

bsweep's own record for it reads `[38, 78, 41, 200]`, which looks like "fails 38–78 then holds".
That is the defect-58 cap at 40 collected failures doing its job — the record is correctly
marked capped, and the truth is that it fails at every one of the 163.

## 22 September 2026 — defects 64 and 65: the machine was the bottleneck, and I was making it worse

Defect 62 made `sweep_shard` record which phase exhausts the budget. The file never appeared.
The reason is the first finding: **an entry already in `uniall_tmo.json` at this budget or more
is skipped before it is ever asked again**, so the 427 rows there will never record a phase
unless something re-asks them deliberately. `src/phasewhy.py` does exactly that — it replays
the sweep's own sequence (build → size → terms → annihilation) at the row's own budget and
reports where the clock runs out.

Looking for why nothing had re-timed-out, the machine answered instead.

### defect 64 — a wall-clock budget records the load, not the entry

**Measured on this container: load average 46 on 4 cores, 31 runnable processes, and a sweep
shard receiving 0.53 cores.** So a BUDGET of 600 wall-seconds is **318 CPU-seconds** — and the
row it writes excludes that entry from every future round at 600 or less. Load was being
written into the refusal file and read back as difficulty.

It also explains, quietly, the ledger's own repeated observation that *every budget raise
produced a result and every cap raise produced nothing*. Part of what a raise bought was
undoing the oversubscription.

`sweep_shard` now records `time.process_time()` across each phase — CPU-seconds, a property of
the entry — instead of the wall budget. The skip still compares this runner's wall BUDGET
against the stored CPU figure, which errs towards re-asking; that is the right direction for a
file that had been permanently excluding work it never fairly tried. The 427 legacy rows are
wall values and over-state.

### defect 65 — and the load was self-inflicted, once per turn

Every runner stops itself when a round finds nothing. That is defect 44 and it is correct.
Then `restart_all.sh` relaunches it, because *is it running?* was the only test — and
`restart_all.sh` runs on **every wake-up**. With 33 runners that is 33 read-out veins brought
back once a turn, each spawning 2–6 shards. That is the load average of 46. That is defect 64.

A runner that stops because its vein is read out now writes `/tmp/<name>.readout`, and
`restart_all` leaves it alone for an hour. A runner that **crashed** writes no marker and comes
back immediately — the distinction defect 52 went to the trouble of making, since the two look
identical from outside. An hour matches the firing rhythm: long enough to stop the churn, short
enough that a changed engine, a raised budget or a widened pool is picked up next time.
Applied to all 34 runners; the read-out helper was tested against a fresh marker, a stale one
and a missing one.

**The shape worth remembering: two mechanisms each correct on its own, wired so that one
silently undid the other every turn, with the damage surfacing two layers away in a refusal
file — as difficulty that was really arithmetic about who got the CPU.**
