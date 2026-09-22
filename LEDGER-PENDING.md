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

### defect 66 — the machine was too busy to notice it had nothing to do

Defect 65's loop closing on itself. All 33 runners started at once, each with 2–6 shards:
**92 python processes and 42 `sweep_shard` instances on four cores**, load average 56, about
**0.04 cores each**.

Nothing finishes at that ratio. Every wall-clock budget is worth a fortieth of itself, which is
defect 64. And the part that makes it self-sustaining: **the idle backoff cannot fire either.**
A runner declares its vein read out only when a round returns in under 60 seconds, and under
that load an empty round cannot start four interpreters that fast. No marker, so `restart_all`
restarts it, so the load stays up, so no marker.

`restart_all.sh` now starts at most `MAXSTART` (default 8) runners per firing, rotating the
start point through `/tmp/restart_all.offset` so each runner gets its turn across wake-ups
instead of all of them fighting on every one. Runners already up are not counted against the
cap — it caps new work, not total work — and the read-out hold applies first. `start()` returns
0 only when it actually launched: returning 0 for a hold would make a firing that held eight
read-out runners believe it had started eight and stop looking, the opposite of the point.

Verified live: two firings at `MAXSTART=2` started exactly two each, honoured three read-out
holds and printed their ages, advanced the offset, and took the container from **load 56 with
92 python jobs to load 42 with 61**.

**Three defects, one loop.** 66 kept the machine too busy to back off; that kept 65's restarts
coming; that made 64's wall-clock budgets record the load rather than the entry; and that fed
`uniall_tmo.json`, which the whole project reads to decide what to work on next. None of the
three is visible from inside its own layer, and all three were found by asking why a file
defect 62 had just created was still empty.

## 22 September 2026 — A196074, and the false cap row that was hiding it

The third entry of this shape today, and the one that says most about the refusal files.

**A196074**, "Number of nX4 0..4 arrays with each element x equal to the number its horizontal
and vertical neighbors equal to 0,3,2,1,4 for x=0,1,2,3,4", offset 1, 30 DATA terms, 200-term
b-file. Its order-37 empirical line first asserts at n = 38 and **fails at all 163 indices the
b-file can test**, first at n = 38 where it exceeds a(38) = 299,231,374,661,523 by 393. As with
A269637 and A236647, the entry's own published terms settle it and no model is needed.

**The correction, and it is proved.** The least order that fits is **43**, integral, and its
first 37 coefficients are exactly the published ones — the tail
`+274*a(n-38) +112*a(n-39) +84*a(n-40) -56*a(n-41) +8*a(n-42) -8*a(n-43)` dropped. Run through
the project's own annihilation test, the order-43 line is **certified from threshold 42** and
the published order-37 line returns **no threshold at all**: there is no index beyond which it
holds.

The model was not taken on trust. An independent enumeration written from the entry's wording,
sharing no code with the engine, gives 0, 0, 1, 8, 39, 60, 111 — the entry's first seven terms;
and the engine's model reproduces all 30 DATA terms and all 200 b-file terms.

Paper at rank 1256. `src/verify_a196074.py` re-derives every claim and passes.

### Why this entry was sitting unasked

**A196074 carried a row in `uniall_caps.json` at a cap of 2,000,000.** It builds in **3.8
seconds at 1,461 reachable states**, which merge to **58**. IDEAS.md §T names it explicitly as
one of the entries "in the pool because the BUILD refuses them, not the parser" — that
sentence was written from the cap file and the cap file was wrong.

So the audit that made `uniall_caps.json` honest this morning (defect 61) did not just correct
a number. One of the rows it was wrong about was hiding a disproof, and the entry had been
carrying the wrong label long enough to be quoted in a planning document as evidence for where
the engine work should go.

Three disproofs today, all the same truncation shape — A269637 (10 published, 13 true),
A236647 (34, 38) and A196074 (37, 43) — and in every one the published coefficients are the
true recurrence's first coefficients, term for term.

## 22 September 2026 — A222434: a fourth disproof, and the variant where the RANGE is the thing

With the container no longer thrashing, `bsweep` jumped from ~9,378 to **10,375 of 10,632** in
minutes — which is its own comment on defects 64–66 — and surfaced one new unpapered
DISPROVED row.

**A222434**, "Number of binary arrays indicating the locations of trailing edge maxima of a
random length-n 0..4 array extended with zeros and convolved with 1,1,1", offset 1, 38 DATA
terms, 210-term b-file. Its order-25 empirical line first asserts at n = 26 and **fails at all
185 indices the b-file can test** — and **thirteen of those failures are visible in the DATA
alone**, first at n = 26 where a(26) = 194,714 and the line gives 194,711.

The `edgemark` engine builds the model instantly at **62 states**, reproducing all 210 b-file
terms. Through the project's own annihilation test:

* the published order-25 line is certified **for no n at all** — there is no index beyond which
  it holds;
* the same line with **one term appended, `-a(n-26)`**, is certified from **threshold 54**.

**And the range is the point.** The corrected line still fails at eight indices below 55 —
n = 29, 35, 38, 41, 45, 48, 51, 54 — and holds at all 156 from 55 to 210. So this is *not* the
published line with a term dropped in transcription, the way the other three are: it is a
different statement, true only eventually. A reader who appended `-a(n-26)` and tested from
n = 27 would conclude the correction was false as well.

Paper at rank 1393. `src/verify_a222434.py` re-derives every claim and passes.

### Four in one day, and the shape they share

| entry | published | true | what is missing |
|---|---:|---:|---|
| A269637 | 10 | 13 | last three terms |
| A236647 | 34 | 38 | last four terms |
| A196074 | 37 | 43 | last six terms |
| A222434 | 25 | 26 | one term **and a range** |

In all four the published coefficients are the true recurrence's first coefficients term for
term. Three are pure truncations; A222434 is the variant where the missing range does as much
work as the missing term, and it is worth keeping separate for exactly that reason.

Worth stating plainly about how they were found: none needed a new idea. Two came from a scan
built in an hour (`tableorder.py`), two from `bsweep` reading b-files it has been reading for
weeks. What changed today was that the refusal files stopped lying (defect 61) and the machine
stopped strangling itself (defects 64–66).

## 22 September 2026 — bsweep is finished: 10,632 of 10,632

Every held conjecture, tested against every term of every published b-file. **2,426,440 terms**,
median 210 per entry, up to 20,001.

      10,616  holds on all b-file terms
           5  DISPROVED
          10  no b-file
           1  b-file disagrees with its own DATA (A193641, already examined)

Most of the last 1,250 entries went through in the hour after defects 64–66 were fixed, which
is the clearest evidence of what the oversubscription was costing: the sweep had sat at ~9,300
for weeks.

The five DISPROVED: **A076217** and **A197230** papered earlier, **A196074** and **A222434**
papered today, **A210247** not open (defect 63 — the entry refutes itself one line below).

**Four false recurrences in 10,632 conjectures.** That is the honest yield and it is worth
saying why it is low: Hardin's empirical lines are almost all *true*. They are fitted to enough
terms to be trustworthy, and the ones that fail are precisely the ones fitted at an order their
sample could not support — which is why all four share one signature, the published
coefficients being the true recurrence's first coefficients term for term.

The vein is read out at the current b-file lengths. It reopens when the OEIS publishes longer
b-files, or when a new engine puts new entries in the pool — not before.

## 22 September 2026 — the cap pool is 645, not 2,759, and the recovery it promised is null

`uniall_caps.json` went 2,759 → 1,755 this morning when the settled rows were retired
(defect 61). The next question was whether the **BUILDS** rows — entries that build fine at the
cap they were "refused" at — are a recovered pool. A196074 was one and turned out to be a
disproof, so the expectation was reasonable.

**It is not a pool.** Of the first 32 BUILDS rows audited, all 32 are `done`, none settled, none
papered — and **none of them carries a conjecture at all.** Ten were run through the sweep's
full sequence by hand: every one builds, every model matches the entry's DATA exactly, and
every one reports *no parsable recurrence*. A183965's entire content beyond its name is
"Column 3 of A183971", and A183971 has no formula lines either, so the conjecture is not
hiding on the parent table the way `tableorder.py` taught me to check. There is nothing on
these entries to prove.

Measured over the whole file rather than the sample:

      1,754  cap rows, already-settled ones removed
        645  carry a parsable conjecture
      1,109  carry none

So **the capped pool is 645**, not 2,759 — under a quarter of the figure that has been quoted
in planning all week, after two independent corrections to the same file in one day. The 1,109
were put in the pool by a name-shape scan, the sweep finished them correctly as "no parsable
recurrence", and their cap rows are leftovers from a generation that hit the cap during the
BUILD, before ever reaching the recurrence check. Auditing them answers a question nobody has.

`capwhy` now takes `ONLY=<list>` and `capwhyrun.sh` points it at the 645 with a 180-second
budget, which cuts the audit by 63% and loses nothing. It is also in `restart_all`'s rotation
now, so it is governed by the same MAXJOBS guard as every other runner rather than being
launched by hand on top of a loaded machine.

**A196074 remains the one that paid** — and the honest reading is that it paid because it
carried a conjecture, not because its cap row was wrong. The wrong cap row is what kept it
out of view; the conjecture is what made it worth finding.

### defect 67 — capping starts is not capping what runs

`restart_all` capped the runners STARTED per firing at 8 (defect 66). Each runner spawns 2–6
shards and the firings come every minute or two, so it climbed straight back to **74 python
jobs on 4 cores**. The quantity that matters is what is already running, so that is what is
checked now: above `MAXJOBS` (default 24, six per core) a firing starts nothing and lets the
machine drain. Verified: it now reports *"holding all starts: 68 python jobs already running"*
instead of adding eight more.

## 22 September 2026 — a census of the whole pool, and the two defects it found

Three pool figures quoted in planning this week were wrong, so rather than correct them one at
a time `src/poolcensus.py` classifies **every entry the unified sweep has ever considered**,
once, from the files as they stand. **16,998 entries:**

      11,110  settled
       4,736  no conjecture to settle
         643  refused: cap
         396  asked, unsettled, NO refusal recorded
          68  refused: budget
          32  refused: shard death
          10  no engine reads the name
           3  refused: memory

The fourth line is the one nobody had counted: an entry that carries a conjecture, has an
engine, was asked, was not settled, and has **no refusal row anywhere explaining why**. Six of
the first six put through the sweep's own sequence by hand returned a finite threshold —
proofs. Following that found two defects.

### defect 68 — every TAG'd runner wrote its results where nothing read them

`merge_shards` globs `shard{TAG}_kind_*.json`, and with `TAG` unset the literal underscore
matches **only the untagged files**. Every tagged runner — np, np2, cap, cap2, rcap, rcap2,
gal, gal2, gal5, cg, oom, res, t17c, tmo — has been writing hits and refusals to disk that
nothing ever merged, because nothing runs the merger with their tag.

**468 cap rows for those 396 entries were sitting in `shardnp2_caps_*` and `shardnp_caps_*`.**
That is why the census called them unexplained: the record existed, under a tag nobody merges.
**Four HITS were unmerged as well** — four proved results invisible to every builder.

An unset tag now means every tag. The first such merge folded in 4 hits, 796 newly processed
entries, and retired 234 stale refusal rows.

### defect 69 — a cap refusal was filed as an answer

The cap was the only refusal with **no skip and no re-ask**. So a shard re-asked, every round,
entries it had already refused at its own cap — waste — and, far worse, the refusal path
marked them `done`. `done` is global and permanent. `np2run` asks at a cap of **2,000,000**;
the entries it refuses were thereby excluded from **every** runner at **every** cap, for ever.
`done` meant "this shard is finished with it" and was read everywhere as "answered".

A cap row is now the record and carries its setting, so a runner with a larger cap can tell an
unanswered entry from a finished one, and a new skip stops a shard re-asking below its own
recorded cap.

**2,265 entries freed from `done`, 1,110 of them carrying a conjecture.**

And they are not hard. **21 of 25 build at the main sweep's own cap of 2,000,000**, at state
counts of 5, 20, 40, 80, …, 2560 — the cap rows were written by engines that have since
changed and never retracted. Of 40 put through the sweep's complete sequence by hand,
**29 proved outright**.

**The pattern, for the fourth time today:** a refusal recorded once and never re-checked, read
back as a fact about the mathematics. Defect 61 was settled work in the cap file; 64 was the
load in the budget file; 68 is a record nobody merged; 69 is a refusal filed as an answer. None
of them is about conjectures at all.

### Correcting the freed-pool estimate: a sorted prefix is not a sample

The note above said 29 of 40 of the freed entries proved outright. **That number is wrong**, and
the way it was got is worth writing down because it is an easy mistake to repeat.

It came from `un[:40]` — the first forty entries in *sorted* order. Sorted by A-number, the head
of that list is all A163xxx/A166xxx/A183xxx `conn2` and `transfer6` entries, with state spaces
of 13, 16, 36, 43, 139. They prove instantly. They are also nothing like the rest of the list.

Drawn properly, with `random.sample`:

| population | sample | PROVED | build refused | other |
|---|---:|---:|---:|---|
| 742 freed, no other refusal row | 40 | **0** | 37 | 3 timed out |
| 396 unexplained | 40 | **0** | 33 | 7 not open |

So the cap rows on the wider pool are **largely honest**: those entries really are too big, even
at a cap of 8,000,000. The recovery is the small easy cluster at the head of the list — a few
dozen entries, not the hundreds the prefix implied.

That does not undo defects 68 and 69. An entry refused at a cap of 2,000,000 should not be
excluded from a runner with a cap of 8,000,000, and a tagged runner's results should not be
written where nothing reads them; both were real and both are fixed. What is corrected is only
the estimate of what they unlock, and the exact figure is now being measured entry by entry
over all 396 rather than sampled.

**The lesson is the one this project keeps relearning, turned on myself:** I spent the morning
finding refusal files that were never re-checked, and then quoted a headline number from the
first forty rows of a sorted list without checking that they were representative. Measure the
population, not its prefix.
