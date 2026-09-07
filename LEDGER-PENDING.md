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

### denumerant — a lattice count, not a walk count (5 entries)

The first engine here that is not a transfer matrix at all.

A nondecreasing row of $-1$s and $1$s is a block of $-1$s followed by a block of $1$s, so it
is fixed by one number: how many $-1$s it holds. Writing $k_i$ for that, row $i$ sums to
$n-2k_i$ and the entry's condition $\sum_{i,j} i\,x(i,j)=0$ becomes $\sum_i i\,k_i =
nH(H+1)/4$. The arrays vanish; what is left is the lattice points of a box on one hyperplane
— the points of the $n$-th dilate of a fixed rational polytope, hence a quasi-polynomial in
$n$.

That is what makes the recurrence provable rather than observed. A quasi-polynomial of
degree $d$ and period $P$ satisfies the recurrence with characteristic polynomial
$(x^P-1)^{d+1}$; here $d \le H-1$ and $P \mid 2\,\mathrm{lcm}(1,\dots,H)$ by the classical
denumerant, so the order is bounded, and the bound is the certificate. Inclusion–exclusion
over which $k_i$ exceed $n$ turns the count into $2^H$ lookups in one denumerant table, so
thousands of exact terms cost nothing — which is exactly what a bound of 13440 needs.

The reduction was checked against a brute force over the arrays themselves before anything
was built, and the model reproduces every published term of all five.

Two things `uniform` needed for this, both contained: `build` no longer refuses a model
whose first component is not a digraph when the engine supplies its own `terms_p` and
`threshold_p`, and those hooks are now honoured.

**Left, with the reason:** the seven entries that also require $\sum x(i,j)=0$ have two
conditions and need a two-dimensional denumerant; their period bound at $H=12$ runs to tens
of thousands, so the certificate is not affordable there. The idempotent-subblock family (10)
and the bishop's-tour family (6) are $n \times n$ — both sides grow — which is the standing
wall, not a new one.

### A methodology bug: two sweeps sharing one results file

The denumerant sweep reported five proved and the file then held none of them. A second
sweep was still running on the refused pool; each holds the whole hits list in memory and
writes it back whole, so whichever saved last silently dropped everything the other had
proved. Nothing in the output said so — the count was the only trace, and it was right.

Caught by reading the file back rather than trusting the report. `sweep_uni.py` now takes a
lock and refuses to start while another sweep is writing the same file. The five were
re-proved and are in.

### transfer91 — an element and the cells around it, reaching further than one line (21)

Five clause shapes in one engine: no element equal to any knight-move neighbour; a
comparison on how many neighbours an element equals ("more than two", "at least two"); an
element equal to the largest or the smallest of its neighbours; and an element required to
find both $x+1$ and $x-1$ modulo $k$ among a listed set of offsets. Several carry the
row-major canonical condition as well, and one counts half its arrays.

The earlier neighbour engine assumed every cell named lay one line away, which a knight move
does not. Here the window is $2R+1$ lines for $R$ the furthest the condition reaches, the
state carries $2R$, and the last $R$ lines are judged by the end vector.

**A reading the data had to settle.** "Each element equal to at least two neighbors" does not
say which neighbours. The four horizontal and vertical ones give A180752's published
$0,1,1,2$; all eight king-move neighbours give $0,3,9,37$. Pinned before the engine existed.

### The lock earned itself within the hour

Two sweeps from before the lock was added were still running while the transfer91 sweep
finished. They hold a stale copy of the whole results list, so either would have dropped all
21 on its next save. Checked the file immediately, found the 21 present, and stopped the old
processes before they could write. The lock stops new sweeps from starting into that
situation; processes already running when it was added were not covered, which is worth
remembering the next time shared state gets a guard.

### chunks.py now records the cap beside each refusal

The ranking called 676 already-retried entries "the cheapest chunk" and would have sent the
next pass to redo exactly what the last one had just done. The sweep now records, per entry,
the largest cap it was tried at, and the ranking reports the refused pool split by that cap
and names how many have never been tried at the highest one. That is the standing rule about
caps, made mechanical rather than remembered.

## 7 September 2026 --- the straight-line family, and the queue

### transfer92: a global condition that is not global

Six entries (A223056, A223057, A223058, A223382, A223383, A223384) count arrays in which
every horizontally or vertically connected set of equal values lies in a straight line. That
reads as a condition on connected components, which no bounded window decides. It is
equivalent to a condition on single pairs of adjacent rows, in two steps.

A component fails to be straight exactly when it contains a **turn**: a cell with an equal
neighbour beside it and an equal neighbour above or below. (A connected set with both a
horizontal and a vertical join has, along a path between them, two consecutive joins of
different kinds; consecutive joins share a cell, and that cell is a turn.)

Then: whether a cell has an equal neighbour *beside* it is decided by its own row. Writing
$B(r)$ for those positions, the array is admissible iff every consecutive pair $r,s$ has
$r_j \neq s_j$ for all $j \in B(r)\cup B(s)$. The state is one row --- no window, no
deferred judgement, no special last row. $S$ runs from 5 to 26.

The reading was pinned first by a brute force that builds the components with a graph search
and checks each lies in one row or one column, exactly as the entry says. It agrees with the
local rule and with every published term of all seven names in the family.

**A223060 is not settled and is not padding:** its conjecture line does not parse as a
recurrence, so there is nothing to prove. A223055 and A223380 are $n \times n$ --- both sides
grow, the standing wall. A223381 was already settled by the generating-function argument;
left alone.

### The queue was the bottleneck, not the mathematics

`chunks.py` ranks *unreached* families, so it could not see the largest chunk on the board:
**5178 candidates that an engine already parses, that carry a conjecture, and that had never
been processed at all.** The sweep is one process, the container has four cores, and each
heavy entry can eat the whole per-entry budget, so the queue simply never advanced past the
first few hundred names. Two contributing causes: every relaunch of the refused-pool loop
requeued the same 1967 refused entries, and each 1200-second run restarted from the front of
the list.

**`src/sweep_shard.py`** runs a slice of the candidates and writes its own hits, done and
caps files; **`src/merge_shards.py`** folds them back under the sweep lock. Shards never
share a list, so they cannot overwrite each other --- that is the failure the lock exists to
prevent, and giving each shard its own file is the fix, not serialising them. The partition
is `crc32`, not `hash()`: Python randomises string hashing per process, so `hash()` would
partition differently in every shard and entries would be both duplicated and dropped.

`ONLY=<engine>` now also bypasses the done set, because a newly written engine's candidates
were marked done by earlier sweeps that had no engine to offer them; honouring that would
refuse to ask the new question, which is the whole point of the run.

### transfer93: a condition on the multiset of a subblock

Twenty-eight entries ask something of every $h\times w$ subblock that depends only on which
values the block holds and how many times, never on where in the block they sit: how many
distinct values it holds, how many entries equal $1$, whether the two middle order statistics
agree, or what the sorted multiplicity vector is. One predicate on the multiset serves all of
them, and a block spanning $h$ lines is decided by $h$ consecutive lines, so the state is the
$h-1$ lines before the current one.

The medians needed pinning and the data pinned them: for a $2\times2$ block with entries
sorted $v_1\le v_2\le v_3\le v_4$, the lower median is $v_2$ and the upper median $v_3$. An
independent brute force that forms every subblock directly agrees with the model term for
term on the median (both senses), the distinct-value and the ones-count families, and the
model reproduces every published term of all twenty-nine names read.

### A fixed bound on the width is a wall

transfer82 refused any array wider than five columns or over an alphabet larger than four.
Those were numbers in a parser, not facts about the model: `no 2 X 2 block having four 1's`
on `n X 7` binary matrices builds in twenty-two states. The bound is now the state space
measured against the cap the caller gives, and eight more entries follow from that alone
(A181249--A181251, A181258--A181260, A183807, A183841), each checked against a brute force
that enumerates the arrays and forms the blocks directly.

### The bug in ONLY, found by reading the file rather than the count

`ONLY=<engine>` bypasses the done set so a new engine's candidates get asked. It bypassed the
*shard's own* done set as well, so every interrupted rerun started from the front and appended
the same hits again --- 66 records for 30 entries. The merge deduplicates, so nothing wrong
would ever have reached a paper, and nothing in the output said a word about it. Only the
global set is bypassed now.

`ANUMS=<list>` was added for the case a widened parser creates: a handful of named entries
become reachable, and asking about them should not mean re-asking about every candidate the
engine has.

### 142 entries that were waiting on a merge, not on an idea

The 3 X 3 subblock families (A251838--A252700 and their neighbours) are read correctly by
transfer17 and always have been. They were unsettled because the annihilation test runs until
$S$ consecutive residuals vanish, and $S$ here is the number of *pairs* of lines:
$(\alpha+1)^{2W}$, which is 65536 at width 4 over four values and 59049 at width 5 over three.
A test that long on a matrix that size never finishes.

The models are enormously redundant. Merging states with identical futures takes A252060 from
**59049 states to 60**. The merge changes no count --- states with the same future contribute
identically to $\iota^\top M^n\tau$ --- and the unmerged $S$ a paper quotes as its
Cayley--Hamilton bound is still a valid bound, merely a generous one. The pair engines have
lumped before the test for a long time; the plain ones did not, and that one missing line was
the whole obstruction.

Building was the other half. transfer17 tested every candidate line against every block:
$|lines|\cdot(W-2)$ work for each of tens of thousands of pairs. Each block is decided the
moment its last column arrives, and a prefix already ruled out rules out everything extending
it, so the search now grows the next line one column at a time and prunes --- five times
faster at width 4, and it agrees with the old routine edge for edge on the models where the
old one could still be run.

With those two changes **142 entries settled**, every one of them open, every one carrying a
conjecture, none contradicted by its own published data. They were the largest approachable
chunk on the board and nothing about them was hard; they were simply never asked.

The papers quote the entry's own condition rather than describing it in general terms:
`build_new.py` re-parses the name and folds the parse into the sweep record, because the
record does not carry it.

### The same missing line, across the other plain engines

Merging before the annihilation test is not specific to the 3 X 3 families: every engine that
returns `(states, adj)` with all-ones vectors was running the test on the unmerged graph. The
497 candidates those engines had processed and left unsettled were requeued --- a refusal made
under the old test is not a refusal under the new one, the same rule that applies to a cap ---
and **23 more settled**: ten in the clockwise-edge-increase family, seven and two in the
subblock-statistic families, three in the commuting-subblock family, one more elsewhere.

Most of the 497 were never candidates for a proof at all: 110 of the first 150 carry no line
that parses as a recurrence, and about a fifth are over the state cap. That is the honest
shape of the pool, and it is worth writing down so the next pass does not expect more from it.
