# Pending ledger notes

Written by the hourly working routine; folded into LEDGER.md and cleared by the daily
routine. Not a published document.

## 6 September 2026, sixteenth pass — the g.f.-only pool was five times bigger than I measured

61 proofs. Roster 8951 -> 9012.

**The bug was mine and it was the same shape as the one it was fixing.** The previous pass
found that the shared g.f. parser refused `Empirical g.f.:` lines, fixed the parser, and then
built the candidate pool with a NARROW REGEX of its own rather than with the fixed parser.
The pool came out at 49. Built with the parser, it is 130 -- 125 newly reachable. So the pass
that recorded the fifth silent refusal committed a sixth in the same breath. **Build the
candidate list with the same predicate that decides the candidate, or the list is not the
list.**

61 proved across 9 engines (transfer46 24, transfer48 17, transfer52 8, transfer64 5,
transfer14 2, transfer63 2, transfer6/71/9 one each), 0 false. All 61 brute-forced from the
entries' English.

**Third time this session the independent check was the faulty side.** Writing the brute force
for `rows and columns in nondecreasing order`, I read it entrywise -- entries increasing along
each row and down each column. That gives 20 where A184130 publishes 29. The entry means the
ROWS, as tuples, form a nondecreasing sequence, and likewise the columns. The engine had it
right. Three for three this session; the quick check is where the reading gets rushed.

**Two DATA mismatches, both benign.** A195971 and A218836 publish one leading term the model
does not generate (an offset convention), so the shift search finds no alignment and the sweep
skips them. Not a modelling error, and no existing paper is affected.

**Left standing.** 8 g.f.-only entries over the 20000-state cap. 6 entries of the
`nondecreasing ... in the i direction and NONINCREASING ... in the j direction` shape, which
transfer46 does not read -- its parser hardcodes both senses as nondecreasing and its edge test
hardcodes the comparison. 50 more of that family whose statistic pair the parser rejects.

## 6 September 2026, seventeenth pass — a sense the parser could not see, and a budget that rejected good results

23 proofs. Roster 9012 -> 9035.

**`transfer46` read both directions as nondecreasing, in the parser AND in the brute force.**
The family's names run `nondecreasing <f> in the i direction and nondecreasing <g> in the j
direction`, and six entries say NONINCREASING in the j direction. The parser's pattern spelled
both senses out literally, so those six were invisible; had they been visible, the edge test
hardcoded `>` in both directions and would have modelled them wrongly. Both now carry a sense
that travels with its statistic under transposition. Regression over the 220 existing
`transfer46` results: 207 reproduce their data, 0 wrong, 13 skipped for size.

**The sweep was rejecting good results because it asked for too few terms.** `sweep_gfonly.py`
computed how many series coefficients the generating-function argument needs, then fetched that
many model terms and compared them against the entry's DATA. An entry publishing MORE terms
than the coefficient budget was therefore compared against a truncated list and recorded as
`model does not match DATA` --- when the model in fact matched every published term. A250737
matched all 31 of its terms and was thrown out. Fixed by asking for whichever is longer.
**Re-running everything the bug could have touched recovered 19 results.** A false negative
that reads exactly like a real one is worth more scrutiny than a false positive.

**Fourth and fifth times this session the independent check was the faulty side.**
`bf46.py` hardcoded the same sense the parser did, so it disagreed with the model on all five
mixed-sense entries; fixed, all five match. And for A203175 none of four readings I tried
reproduced the data, while the engine matched all 38 terms --- because `preceded by 0 1` means
the two cells to the left, or the two above, read 0 then 1 IN THAT ORDER, a two-step lookback,
not a condition on the immediate predecessors. Implemented independently, it reproduces the
entry exactly.

Five for five this session. The pattern is now unambiguous and belongs in the methodology: the
slow engine, written against the entry with its data as a gate, keeps being right; the quick
check written afterwards keeps being the sloppy one. A check is worth what the care taken over
it is worth, and these were written in a hurry precisely because they were "just" checks.

**New: `src/sync_sources.py`.** The build tree is no longer stored, so each batch's LaTeX
sources are copied into `paper-sources/` by matching PDF content hashes, and the script also
maintains `MISSING.txt`. 8997 of 9035 papers now have their source in the repository, up from
8834; 38 have no surviving build directory.

**Left standing.** 8 g.f.-only entries over the state cap, 3 where the model could not produce
enough terms in the time budget, and 2 whose entry publishes a leading term the model does not
generate. `transfer77`: A233220 and A233221 exhaust memory when built.

## 6 September 2026, eighteenth pass — a table sweep that had been refusing 62 of 71 engines

83 proofs. Roster 9035 -> 9115.

**`sweep_table.py` dispatched per engine by hand and called `<engine>.avals`, which 62 of the
71 engines do not have.** The `AttributeError` was swallowed by a broad `except` and reported
as `model does not match the column`, so every table whose column model came from one of those
engines was rejected as if the mathematics had failed. This is the same failure as the
`transfer7` one already in this ledger and the same fix: go through `uniform`, the shared
interface, instead of re-implementing the dispatch. Rewritten, and all 1330 previously examined
tables reopened and re-examined; 3 tables and 5 columns recovered. Smaller than feared, because
most of these tables state no explicit column recurrence at all.

**What they state instead is `[order N]`, and that is a claim.** 619 tables carry such lines,
1095 of them outside the roster. `sweep_ordline.py` settles them: a column is a fixed-width
array count, hence a walk count on S vertices, hence satisfies a monic recurrence of order at
most S; Berlekamp--Massey on 2S exact terms returns the minimal one; if its order is the stated
one then every recurrence of that order the column satisfies is that same polynomial. **The
sweep had been run at a state cap of 1200, which was refusing most of them.** Re-run at 6000:
proved tables 43 -> 123, recovered lines 55 -> 197, of which **80 tables and 142 lines are
new**. The independent re-check passed 123 of 123 with no problems.

**The cap was not a wall, it was a setting**, and nothing recorded that it had been chosen
rather than reached. Worth a rule: when a sweep reports `state space > cap`, the cap is part of
the result and belongs in the ledger next to it.

**Length now follows content here.** These papers come out at two pages when one column was
recovered and three when several were, which is what it should look like.

**Left standing.** 24 entries of the `nondecreasing ... i direction` family are `(n+1)X(n+1)`,
both sides growing --- the n X n wall, a real obstruction. Of the remaining order-line tables,
those still refused sit above 6000 states.

## 6 September 2026

- **Every comment now carries the date the result was found.** 173 entries had
  none: the date was read out of the LaTeX source and 181 papers have no source
  left. Every paper prints its date under the author, so the paper is now the
  source of record (`engine/src/paperdates.py`) and the source only corroborates.
  Nine papers print a month with no day and are recorded that way rather than
  guessed at.
- **The sixteen papers carrying the suggested-comment appendix are all rebuilt.**
  Reconstructed from the published text, compiled, word-diffed against the
  original, installed only when nothing but the appendix differed.
- **Nine of those sixteen also pointed at another paper** --- "proved in a
  companion note", "treated elsewhere". Each pointer replaced by the thing it
  stood for. No paper now asks its reader to hold a second one.
- **Paper 5342 printed "By Lemma ??"**: compiled once, so its own reference never
  resolved. Recompiled; the diff is "??" to "1", twice.
- **deep-check/PLAN.md**: the thirteen-phase check for when the roster passes
  10,000, written down in advance. `dc_gate.py` holds the trigger; Phases 1 and 2
  are written and pass over all 9115 papers.
- Two of my own checks were wrong before the papers were, which is now six or
  seven times running: the roster is keyed by the number a paper was built under
  and not by its rank (reading it as ranks reported 9079 mismatches that were not
  there), and the papers use T1 ligatures, so a plain search for "Verification"
  reported 9091 papers missing a section every one of them has. Both now have
  code that cannot repeat them: `dc_phase1.py` compares the multiset of
  (A-number, verdict, engine), and every text check goes through `dc_text.py`.

### transfer81 — arrays counted up to renaming, under a subblock condition (36 entries)

A family of 46 Hardin entries that no engine parsed. Each asks two things at once: a
condition on every 2×2 or 3×3 subblock, and "new values introduced in row major order".
The second is not a local condition — whether a value may appear here depends on the whole
prefix — but the prefix enters only through **how many values have been introduced so far**,
so one extra integer in the state carries it exactly. 36 proved; the other 10 carry no
conjecture at all and are not counted.

Four readings pinned against published DATA before the engine was written, one per
predicate shape, each by a program enumerating arrays from the entry's own words.

**The mistake.** The parser treated `L X (n+a)` as the transpose of `(n+a) X L`. It is not:
the conditions are stated about ROWS — "every subblock in a row", "adjacent rows differing",
"row major order" — so transposing rewrites the condition into a different one. Six entries
were reported as "model does not match DATA", which is the only reason it was caught; had
those six been absent the error would have shipped. The fix walks the array along its own
growing direction and keeps the conditions where the entry puts them.

That fix needed one real argument rather than a code change alone. Walking by columns, the
canonical condition read along the walk is *column* major order, not the entry's row major
order. They give the same count: every condition here is a statement about which entries are
equal, so it is invariant under renaming the values, and each rule picks exactly one
representative from each renaming class. Checked, not assumed — an independent brute force
written to the entry's row-major wording reproduces the published terms of A205627.

Thirty of these had already been papered and ranked when the defect turned up. The natural
orientation was not touched by the fix, but "not touched" is a claim about code and the
roster is a claim about mathematics, so all 36 were re-run from scratch through the shipped
engine (`src/reverify81.py`) and every paper rebuilt from that run.

**Cap recorded next to the refusal:** A206173 refused at cap 6000 with "state space > cap",
and settled at cap 400000. Its lumped model has 76 states.

## 7 September 2026 — four new engines, 139 conjectures

The unsettled pool was measured properly for the first time: of 29073 OEIS names known
here, 9124 were settled and **15006 were unsettled and parsed by no engine at all**. Of
those, **604 carry a conjecture in a form the machinery can test** — that number, not
15006, is the real target list. The 604 fall into 268 clause shapes, so the way forward is
engines that each cover several shapes rather than one engine per entry.

Also worth recording as a negative: the largest families of unparsed names — 170 entries of
"binary arrays symmetric under 90 degree rotation with all ones connected only in a 1 2 1
pattern", 408 across the "row sums and column sums" families — carry almost no conjectures
at all. They are large and they are not targets.

### transfer82 — a condition on every subblock (19 entries)

Every subblock summing to a constant; every block having exactly so many ones; no block
having so many ones; each element of a block the sum mod m of two others; no block the
mirror of its neighbour. Four readings pinned against published data first. One entry counts
$1/16$ of the arrays and that factor is carried, not ignored.

**The mistake:** the mirror condition was tested only once two bands of subblocks existed,
so every two-row array came out unconstrained and the model counted all of them. Caught by
the data gate on A183804. The window now tests each constraint as soon as the lines it needs
are present.

### transfer83 — a condition on each element and its neighbours (36 entries)

Counts of equal neighbours in named directions, compared, forbidden or required. Six
readings pinned first. Three consecutive lines decide the condition on the middle one, and
the boundary is honest: a missing neighbour is not a neighbour.

**The mistake:** `"horizontally".rstrip("ly")` is `"horizonta"` --- rstrip removes every
trailing character in the set, not the suffix --- so the whole family using adverbs silently
failed to parse and would simply have been reported as unreachable. The adverb is mapped now.

### transfer84 — no column above the one before it in every row (9 entries)

"In all rows" quantifies over the whole array, so no bounded window decides it. But it is a
conjunction of independent per-row facts: one bit per adjacent column pair, cleared and never
set. The state is that bit mask alone, so entries whose terms run to twenty digits have
models with three to eleven states.

### transfer85 — a value repeated at exactly its own distance (11 entries)

The condition ranges over the whole array but reaches only as far as the value itself, which
the alphabet bounds. Carry that many lines plus one bit per cell for "partner found yet".

The reading needed pinning and the strict reading is wrong: "another element value z"
includes the element itself when z = 0. Strict gives 0, 1, 1, 3 for A209173 where the entry
publishes 1, 2, 5, 12.

**Cap recorded next to the refusal:** A209370 (n X 4 over 1..3) refused at cap 400000 and
again at cap 3000000, the second time by exhausting a 280-second build rather than the cap
itself. Its window is 3 lines of 4 cells with a bit each, which is where the size comes
from. Not settled.

### transfer86 — five more conditions, one engine (16 entries so far)

No two ones adjacent diagonally; the neighbours of any element all different; no more than
so many of any run of consecutive bits set in a row or column; entries increasing by a fixed
set of steps modulo m rightwards and downwards; and row sums nondecreasing with columns
lexicographically nondecreasing.

The first four are local and share a three-line window. The last is not local in either
direction and needs no window at all: carry the previous row's sum, and one flag per adjacent
column pair saying whether the two have agreed in every line so far. A pair that separates
the right way is settled for good; one that separates the wrong way ends the walk; pairs
still tied at the end are equal, which the entry allows. Five readings pinned against
published data first, including the two entries that count a quarter of their arrays.

The remaining candidates in this family are still running at cap 2000000; whatever they come
back as will be recorded next to the cap.

### transfer87 — parities, forbidden differences, distinct differences, neighbour quantifiers (18)

Four more clause shapes. Three are local and share the three-line window. The fourth is not:
"an even number of ones above it" counts a whole column back to the top of the array, which
no window holds --- but only its parity is asked for, so one bit per column carries it, and
the parity to a cell's left is read off the line being placed. Four readings pinned first.

**A parser bug worth recording:** Hardin writes a fixed dimension as a sum, "(3+1) X (n+1)",
meaning width 4. Reading only a bare digit there dropped an entire family, which would have
been reported as unreachable rather than as a bug. Dimensions written as sums are now read.

### The refused pool, re-run at a higher cap

1967 candidates that an engine already parses had been processed and not settled. Re-running
them at cap 2000000 recovered **12 results** so far from engines transfer8, 20, 21, 38, 44,
85 and 86 --- with the run interrupted partway. A cap is a setting, not a wall, for the
fourth time in this project.

### The knight-distance family: measured, not attempted

19 entries, the largest single family left. The reading is pinned: writing $w = d - v$ for
$d$ the knight distance from the corner turns the entry's condition into "$w$ takes values in
$\{0,1,2\}$ and rises by 0 or 1 along every minimum-path knight move", and a direct
enumeration of that reproduces A253112's published 53, 272, 1342 exactly.

What is not built is the digraph. Knight distances depend on the actual board, so the edge
structure has to come from the board rather than from the entry's words. Measured: for
widths 3 to 6 the row profile of distances is periodic with period 4 away from the ends,
which is what a transfer matrix needs; widths 7 and 8 show no period up to 12 in the window
tested. The bottom edge of the board perturbs distances in its last rows and needs a
separate finish. That is the next target, written down rather than quietly skipped.

### The knight-distance chunk (19 entries): reading pinned, model correct, one lemma short

Following the chunk rule, this was taken as the biggest new family. Where it stands:

**The reading is pinned.** Writing $w = d - v$ for $d$ the knight distance from the corner
turns the entry's two conditions into one: $w$ takes values in $\{0,\dots,s\}$ and rises by
$0$ or $1$ along every minimum-path knight move. Direct enumeration of those labellings
reproduces A253112's published 53, 272, 1342.

**The model is correct.** A row-by-row count using each board's own distances reproduces
*every* published term of the fifteen entries of widths 3 to 7 — 26 terms for A253112, 34
for A253417, 22 for A253113. Widths 8 and 9 (four entries) show no period and are refused.

**Two facts about the board were measured.** Knight distances on a strip do not depend on
the board's height at all, except for heights 2, 3 and 4 — so one distance function serves
every board and those three heights are counted on their own boards. And the local structure
the transfer needs repeats with period 4, from row 5 for widths 3 and 4, row 7 for width 5,
row 9 for width 6, row 11 for width 7.

**The mistake.** The first measurement of that offset compared the wrong thing: it checked
the minimum-path edges within rows $i-1, i, i+1$, but the transfer also needs the edges
between rows $i-2$ and $i$, and those settle one row later. The engine built on it matched
the first six published terms of A253112 and undercounted every term after. Caught by the
DATA gate, which compares against the whole published sequence and not a prefix. Fixed; with
the corrected offsets the model matches everything.

**What is still missing, exactly.** The transfer matrix exists only if the structure really
does repeat forever, which is the claim $d(i+4,j) = d(i,j) + 2$ for every column once $i$ is
large. The inequality $\le$ is immediate: the moves $(2,1)$ then $(2,-1)$ drop four rows and
return to the same column. The inequality $\ge$ is not proved, and a finite check over a few
hundred rows is evidence, not proof. So `transfer88` is written, its reading pinned, and
deliberately **not registered**: nothing it certified would be safe to count.

**The proof strategy, written down so it can be executed rather than rediscovered.** Every
move changes the row by at most 2, so $d(i,j) \ge \lceil i/2 \rceil$; and iterating the
two-move drop gives $d(i,j) \le \lceil i/2 \rceil + K$ for a constant $K$ computable from the
first few rows. A shortest path to $(i,j)$ that dipped $k$ rows below would have length at
least $\lceil i/2 \rceil + \lfloor k/2 \rfloor$, so $k \le 2K+1$: **a shortest path never
dips more than a bounded distance below its target.** The distances on rows up to $i$ are
therefore determined by a window of $2K+2$ rows, the strip is invariant under shifting by a
row, and the induction closes once one window is checked to repeat — a finite check. That
turns the measured periodicity into a proof and settles all fifteen.

### transfer89 — the white squares of a board (12 entries)

Only the cells with $i+j$ even carry a value, and the diagonal and antidiagonal neighbours
of such a cell are again such cells, so the white squares form a board of their own and the
entry's condition never refers to anything else: each must have a neighbour holding a
prescribed function of its value, the successor modulo the alphabet or the complement. Three
consecutive lines settle it. The white cells of a line occupy alternate columns and which
ones depends on the parity of the line, so the state carries that parity in the shape of the
line it holds.

Both readings pinned against published data first, including the boundary: a cell at the
edge simply has fewer neighbours, and having none of the right value is a failure rather
than a special case. That is why A230647 begins at zero rather than one.

Also measured and rejected this pass: the commuting-subblock tables (16 entries, the second
largest family). Their conjecture is stated once "for every row and column" rather than
per-column, so it is a claim about infinitely many widths at once, and settling the few
columns whose data is published would not settle what the entry states. Recorded so it is
not measured again.
