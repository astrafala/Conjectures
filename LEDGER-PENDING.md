
## 8 September 2026 — the deep check closes, and 611 held results are installed

**The check is complete.** Phase 5 was the last phase running and it closed at **3,840 of
3,864 sweep records recomputed from cold, 0 disagreements**. Its 24 refusals are recorded in
DEEP-CHECK.md next to the setting that caused each: 23 over an 8,000,000-state cap, 1 over a
900-second budget. Phase 12's reading half had already closed at 105 of 105, one paper from
every argument family, with no paper's mathematics found wrong.

**611 held results installed**, every one re-checked against the LIVE OEIS first: 611 fetched,
**0 dropped, 0 carrying settlement wording**. The roster goes from 10,054 to **10,665 papers —
10,659 proofs and 6 disproofs over 10,638 entries, 107 arguments.**

Where they came from:

| vein | installed |
| --- | --- |
| unified transfer-matrix sweep | 51 |
| order line, whole sequence | 145 |
| order line, recovered on a tail | 334 |
| T(n,k) table columns and rows | 65 |
| closed form | 16 |

The tail vein is the largest single addition in the project's history and it grew twice in one
day: the pool it had been working was exhausted at 382, a fresh pool of 136 never-tried
order-line entries was built from the clone, and the 191 entries an earlier run had refused at
a cap were re-asked at 60,000,000 states and 30,000 merged states. **The re-ask alone returned
78 proofs.** A cap is a setting, not a wall, and this is the fourth time raising one has
recovered real results.

### A gap in the tail argument, found and closed before any paper was written

The tail papers needed a builder of their own, and writing it exposed something the sweep had
not been checking. The identification argument says: the entry asserts a recurrence of order N
holding from some index on; the tail found here has minimal order exactly N; a minimal
polynomial divides any other the sequence satisfies; both are monic of degree N, so they are
equal. That last step needs the minimal order not to FALL at some later starting point — and
it can, exactly when the minimal polynomial has a root at zero, which is to say when its last
coefficient vanishes. Then a further tail satisfies something shorter and the entry's
recurrence is not pinned down at all.

All 479 tail results were checked: **every one has a nonzero last coefficient**, so the
argument closes for all of them. The builder now states that coefficient in the paper, makes it
the fourth item of the Verification section, and **refuses to write a paper where it is zero**.

### Four mistakes of mine, all in the machinery, none in a paper

* **status.py double-counted Phase 5.** It summed the three shards' lists, which overlap, so
  it reported 3,871 of 3,865 — more than the whole pool — and then "0 left" when 3 remained. It
  now takes the union by A-number and derives the total from the sweep records instead of a
  hard-coded 3,865 (the real pool is 3,864).
* **Three single-writer scripts were each started twice.** rank.py, sync_sources.py and
  paperdates.py all had two copies running at once, and each pair fought over the same
  directory or cache; two died outright. Nothing was lost — rank.py only replaces papers/ at
  the very end — but the pattern is now written once in `engine/src/singleton.py` and all three
  refuse to start a second copy.
* **Whole veins had no installer.** 145 compiled order-line papers were sitting in build/ow
  with nothing to install them, and the table and tail veins had no builder at all;
  `install_vein.py` now does the job for any vein, and `addtexfacts_all.py` reads a paper's
  facts from the stored source instead of from one vein's hits file.
* **paperdates re-read all 10,665 PDFs after every ranking**, because its cache was keyed by
  file path and a ranking moves every paper. It now also keeps a cache keyed by A-number, which
  a ranking does not touch.

### 8 September 2026, later — what is actually left, measured honestly

The check being over, the question is where the next results come from. The clone was
re-measured rather than guessed at.

**37,991 entries carry conjectural wording. 10,582 of them are in the roster. Of the 27,409
that are not, only 5,511 carry a conjecture worth a sweep** — a recurrence, a generating
function, or an order line. The other 21,898 were removed by a new filter,
`engine/src/pooltrim.py`, and it says why: 19,069 have conjectural wording on something that
is not a settleable claim, **1,046 link a published proof**, and 537 say on the entry itself
that the conjecture is settled.

Of the 5,511, an engine reads the name of 1,246 and reads none of the rest. So the wall is
name coverage, not method.

### A family of 229 that I did not write papers for

The largest single cluster of unread names was 229 entries reading "Number of base b circular
n-digit numbers with adjacent digits differing by d or less". The model is exact and easy —
a(0)=1 and a(n) is the trace of the n-th power of the banded 0/1 matrix — and it reproduced
**all 229 entries' published terms with no mismatch**.

**It is still a dead end, and here is why.** Every one of those 229 entries links a 2026 paper
proving exactly the recurrences and generating functions a sweep would have gone after, and
not one of them carries a conjectured recurrence or generating function any more. The
"[Empirical]" line they do carry is a cross-family identity that, for a fixed base, covers only
finitely many n and is checkable from the published data. **Elementary where it is not already
proved by someone else.** Checking that before writing cost minutes; not checking it would have
cost 229 papers that were not mine to write. The pool filter now looks for a proof link, so
this cannot happen quietly again.

### One clause, 91 entries

`transfer17` reads "every 3X3 subblock <predicate>" names and has 510 papers. 37 entries state
the predicate "having rows and columns in lexicographically nondecreasing order", and the
shape, the quantifier and the block size all parsed — only that phrase was missing from the
vocabulary. Adding it, with the three related orderings, made **37 entries readable**, the
model matched the published terms of all 21 tried so far with **0 mismatches** (6 more want a
cap above 400,000), and the existing engine's 400 sampled papers all still parse.

**Correction to my own first count.** I said 91. 91 was how many names matched the phrase
"lexicographically ... order" anywhere, and 54 of those are a different object altogether:
arrays that *indicate a property of the subblocks of some larger array*, which is an image
count and not a walk count. The clause unlocked **37**, not 91. The 54 are kept in
`engine/deep-check/derived-arrays.txt` as the next engine target -- `transfer26` already has
the right machinery (the subset construction for counting images) and would need a parser and a
condition written for this shape.

That is the shape of what is left: not one huge chunk, but a long tail of clusters of 30 to 90
that each need one phrase added to a parser that can already do the mathematics.

### 8 September 2026 — nineteen "disproofs" that were my own bug

The lexicographic-subblock sweep came back with 19 entries whose conjectured closed form it
said was FALSE, against only 7 proved. Nineteen disproofs in one family would have been the
largest single find in the project. **Every one of them was a defect in my own reader.**

A long formula in the OEIS is written across several `%F` lines, each continuing the one
before it:

```
%F A184566 Empirical: a(n) = (1/121645100408832000)*n^19
%F A184566 + (53/3201186852864000)*n^18
```

`localentry.get` returned those as separate formulas, so the sweep was handed
`a(n) = n^19/121645100408832000` — the first term of a degree-19 polynomial and nothing else —
and correctly found that the sequence does not satisfy it. The conjecture it was testing was
not the entry's conjecture. A line whose first character continues an expression is now joined
to the one before it, and re-asking the same 19 returned **16 proved and 0 failures**.

Two things were checked before this was written down, because a false disproof is the most
expensive mistake available here:

* **All 6 disproofs already in the roster are unaffected.** Each rests on a conjecture written
  on a single line — A197230's 295-character recurrence included — so none was ever truncated.
* **No installed paper quotes a truncated conjecture.** Of 10,665 papers, only 7 sit on an
  entry that has a continued line at all, and only one of those quotes a conjecture in its text;
  that quotation is complete.

The rule this confirms, again: a result that would be a triumph deserves more suspicion than
one that is routine. Nineteen disproofs from one small family was not plausible, and it was not
real.

### A second reader defect, found the same way

The lexicographic family refused A184540 with "no readable closed form". Its line is

```
Empirical: a(n) = (84 + 149*n + 36*n^2 + n^3) / 6. Corrected by _Colin Barker_, Apr 12 2018
```

The formula is perfectly readable; the editorial note after it is what made the line
unparsable. The reader already stripped an attribution written after a dash and did not strip
one written as its own sentence. It does now.

**813 entries across the closed-form sweep's records had been marked done and unreadable and
can be read after the fix.** They have been put back for re-asking. Most will refuse again for
some other reason -- no engine reads the name, a state space over the cap -- and that is
expected; the point is that they were never asked the question at all.

Both of today's reader defects were found the same way: by looking at *why* a sweep refused,
rather than at what it proved. A refusal that is really a bug is invisible in a hit count.

## 8 September 2026 — a new engine, and the biggest single family found this month

Going back for big veins rather than small ones, the reservoir was re-measured by CONDITION
rather than by name, and one family dominated everything else:

> Number of n X 4 arrays of the minimum value of corresponding elements and their horizontal or
> vertical neighbors in a random, but sorted with lexicographically nondecreasing rows and
> nonincreasing columns, 0..1 n X 4 array.

**134 entries, and no engine could read a single one of them.** `engine/src/transfer95.py` now
does. **97 are proved.**

Two things make the object different from everything the project had built before.

**It counts an image, not a set of arrays.** What varies is the underlying sorted array; what
is counted is how many *different* filtered arrays come out, so two underlying arrays with the
same image count once and the obvious graph overcounts. The cure is the subset construction:
the filtered row is decided by three consecutive underlying rows, so a pair of rows is a state
of a nondeterministic machine whose output is the filtered array, and the distinct outputs are
the paths of its determinisation.

**One of the domain constraints is not row-local.** "Rows in lexicographically nondecreasing
order" compares consecutive rows. "Columns in lexicographically nonincreasing order" compares
whole columns read downward, left to right, which looks global — but it decomposes: an adjacent
column pair is either still equal in every row so far, or already decided at some earlier row
and never constrained again. One bit per adjacent column pair makes it local.

### Nothing was assumed; the entry settled every question

* The reading was pinned by brute force before a line of the engine was written: for A219498
  the one-row arrays are the nonincreasing 4-bit words, their images are 1111, 1100, 1000 and
  0000, and the entry's a(1) is 4.
* **99 of the 134 reproduce their entry's published terms exactly. 0 mismatch.** The other 35
  are refused at a DFA-state cap derived from 400,000 — recorded as the setting it is.
* 30 entries disagreed at first and every one was written `W X n` rather than `n X W`.
  Transposing the array exchanges the two orderings as well as the offsets, and the engine was
  transposing only the offsets. The data caught it; nothing else would have.
* Two entries name a direction twice — "horizontal, diagonal, diagonal or antidiagonal" — which
  names no set at all. Rather than guess, each candidate repair was run against the entry's own
  terms and exactly one reproduced them. The parse records that the name is defective so a
  paper built from it has to say so.
* A 300-paper regression sample confirms the new engine takes no name away from an existing one.

Two pieces of shared machinery needed widening for an engine whose model is not an adjacency
matrix: `uniform` gained an image-engine branch in `build`, `terms`, `size` and `threshold`, and
`sweep_cf` was reading the state count as `len(b[0])` — true of every engine written until now
and false of this one. It asks `uniform.size` instead.

## 8 September 2026 — pushed to find veins in the thousands, and my own filter was the wall

Asked whether the families I was working were too small, I went back over the measurement
rather than the mathematics, and the measurement was wrong twice.

### My conjecture filter required the hedge word and the formula on the same line

A conjecture is very often written as a block, and then the formulas carry no conjectural word
of their own at all:

```
%F Axxxxxx Conjectures from _Colin Barker_, Apr 12 2018: (Start)
%F Axxxxxx a(n) = 3*a(n-1) - a(n-3).
%F Axxxxxx G.f.: x*(1 + x) / (1 - 3*x + x^3).
%F Axxxxxx (End)
```

`pooltrim.py` required "Conjecture"/"Empirical" and a formula on ONE line, so it dropped every
entry whose only conjecture is a block. **1,648 entries.** It reads the block as a whole now,
and the reservoir of genuinely open unread entries goes from **5,511 to 7,091**.

A second phrasing was missing entirely: "It appears that", "Apparently", "It seems that". 3,743
entries use one of them, and **551 that state a formula or recurrence were in no pool at all**.

### The vein in the thousands was one the project already had the machinery for

Sampling the entries the filter had dropped turned up "Empirical for column k:" over and over.
That is the T(n,k) table-column conjecture — the shape `sweep_table.py` was written for, and
which has 188 papers in the roster already.

**2,101 entries carry one. 372 are in the roster. 1,729 are not — and the sweep had asked
about 11 of them.**

Not because they were hard: because of how the sweep chose what to ask. It walked all 399,027
names in A-number order, skipped anything not beginning "T(n,k)" **without recording the skip**,
and was killed by its timeout long before the interesting A-numbers. Every run re-read the same
early part of the index. In its whole life it had asked about 889 entries.

It now reads an explicit pool built from the clone, records what it skips, and shards four
ways. 1,718 entries that had never been asked are being asked.

**The lesson is the same one as this morning's nineteen false disproofs, from the other side.**
A sweep that reports a small clean number is not evidence that the pool is small. Both times the
number came from my own code deciding what to look at, and both times the way to find it was to
read the refusals rather than the results.

### The table sweep had no clock at all

Pointing it at the real pool was not enough: it still asked about one more entry per
two-minute window. The reason is worth recording because it is a different failure from the
pool one.

`sweep_table.py` had **no per-column time limit of any kind** — the only sweep here without
one. A table states a recurrence for *every* column it has, and the build cost roughly triples
per column: on A205193, column 9 takes 21 seconds and column 12 would take minutes. One table
could therefore consume an entire run, and did.

Three guards, each a setting that is named in the refusal it causes:

* a per-column alarm on the build, the terms and the threshold (`BUDGET`, 30s);
* a **row cap** refusing a column whose board is wider than `ROWCAP` (1,024 rows) before
  anything is built, since an alarm cannot interrupt a build that sits inside one C-level
  call — the columns are tried smallest first and those are the ones that get proved;
* a per-table budget (`ENTRY_BUDGET`, 90s), so no single table can take a whole run.

**43 entries asked per window became 266, and 2 tables proved became 27** (57 column
conjectures). The remaining columns are refused with the cap that refused them, so a later pass
at a higher one can be seen to be worth making.

## 8 September 2026, evening — 235 results installed: the roster reaches 10,900

Every one re-checked against the live OEIS first: **243 fetched, 0 dropped, 0 carrying
settlement wording.** The roster goes from 10,665 to **10,900 — 10,894 proofs and 6 disproofs
over 10,873 entries, 108 arguments.**

| vein | installed |
| --- | --- |
| T(n,k) table columns and rows | 123 |
| min-filter images (the new engine) | 97 |
| order line recovered on a tail | 14 |
| unified transfer-matrix sweep | 1 |

### The min-filter papers needed a builder of their own, and this is why

`cfbuild` writes every closed-form paper in the corpus, and each of its papers says: *the lines
of an array are the vertices of a finite digraph, an array is a walk in it, and a(n) is a walk
count.* For every engine it was written for that sentence is true. **For these it is false.**
These entries count how many DIFFERENT filtered arrays arise, so two underlying arrays with the
same image must be counted once; the walk whose steps are counted lives in the determinisation
of a machine whose output is the filtered array, not in a graph of arrays.

Using the existing builder would have produced 97 papers each describing a construction that
was not the one performed. `engine/src/mfbuild.py` states what was actually done: the image, why
the obvious graph overcounts, the two lemmas that make the domain local and the count a walk,
and — for the two entries whose own name repeats a direction word — a remark saying the name is
defective and that the reading was settled by the entry's published terms rather than chosen.

### One more defect, found while installing

`mkcomments` opened each paper's stored source to pick a comment template, and died on the
first paper whose source is missing. 263 papers have no stored source, and a re-ranking moves
every path. A missing source now only means that paper's abstract cannot be read to choose a
template; it is not a reason to abandon a redraft of ten thousand comments.

## 8 September 2026 — transfer96: the family that was invisible because it has one dimension

Every one of the eighty-odd array engines parses a shape like "n X 4". A name that reads

> Number of length n+3 0..2 arrays with no four elements in a row with pattern abba (possibly
> a=b) and new values 0..2 introduced in 0..2 order.

has no second dimension to find, so **not one of them read a single entry of this family** —
359 of them, and the object is easier than most of what the project already handles. The count
is a walk count on the windows: the same argument as everywhere else, one dimension down.

`engine/src/transfer96.py` reads them. **101 reproduce their entry's published terms exactly,
0 mismatch**, and a 300-paper regression sample confirms it takes no name from an existing
engine.

Four clause types, all local:

* **a forbidden pattern.** "pattern abba" names a shape, not letters: a window matches when
  positions carrying the same pattern letter carry the same value. "(with a!=b)" also requires
  positions carrying different letters to differ; "(possibly a=b)" does not — so "possibly
  a=b" forbids strictly more words, since aaaa matches abba there and not in the strict
  reading.
* **"new values 0..m introduced in 0..m order"** — the first occurrences must be 0, 1, 2, …, so
  a word may use v only once v-1 has appeared. One extra number in the state.
* **"at most one downstep in every 3 consecutive neighbour pairs"** — a sliding window over the
  neighbour PAIRS, so it spans four elements. Two other readings suggested themselves (a global
  bound, and a window of n pairs) and **both disagree with the entry's own terms**: 66, 147,
  294 and 81, 216, 441 against the entry's 66, 168, 441. The data picked the reading.
* **"no consecutive three elements summing to more than S"**.

### An indexing bug the sweep caught before any paper was written

The engine indexes by word LENGTH; the entry indexes by its own n, and a name reading "length
n+4" puts a(1) at length 5. Left as it was, 32 of the 101 came back from the recurrence sweep
as "model does not match DATA" — a model that matches every published term, reported as
wrong, because the shift search window is deliberately only a few steps wide (a wide one can
fit a wrong model). `uniform.terms` now drops the leading terms for this engine, and all 101
align inside the usual window. **The first sweep after the fix returned 25 proofs.**

## 8 September 2026 — cuspdim: a family settled by a formula, not a matrix

51 entries read "Dimension of the space of weight 2n cusp forms for Gamma_0(N)", and nothing
in this repository resembled them: there is no array to count and no transfer matrix to build.
There is instead an exact classical formula, and it settles the conjecture outright.

For even $k\ge4$ (Diamond--Shurman, Theorem 3.5.1),

    dim S_k(Gamma_0(N)) = (k-1)(g-1) + (k/2-1)·e_inf + floor(k/4)·e_2 + floor(k/3)·e_3,

with dim S_2 = g and dim S_0 = 0. Every quantity on the right is elementary integer arithmetic
in N: the index, the two elliptic-point counts, the cusp count, and the genus. With k = 2n the
right-hand side is linear in n apart from floor(n/2) and floor(2n/3), so a(n) is a
**quasi-polynomial of period 6** and a conjectured linear recurrence on such an entry is
decidable outright.

**All 51 reproduce their entry's published terms exactly, 0 mismatch**, and a 400-paper
regression sample confirms the parser takes no name from an existing engine. **46 are proved.**

### And the reason the first sweep proved none of them

The sweep reported "no parsable recurrence" for 16 of the first 16. The conjectures are there;
they are written as blocks:

```
Conjectures from _Colin Barker_, Jun 04 2017: (Start)
a(n) = 3*a(n-1) - a(n-3).
G.f.: x*(1 + x) / (1 - 3*x + x^3).
(End)
```

**Every sweep this project has ever run decided which lines to read with a regular expression
requiring the word "Conjecture" or "Empirical" ON the line.** A block's formula lines carry no
such word, so they were invisible — the same defect found this morning in `pooltrim.py`, where
it had hidden 1,648 entries from the candidate pools, now found one level down, deciding what
to read *inside* an entry already selected.

`engine/src/conjlines.py` returns an entry's conjectural lines with blocks understood, and
`sweep_shard` uses it. On the cusp family the effect was total: 0 proved became 12 in the same
window, then 46 overall.

**Corpus-wide the effect is much smaller, and the honest number is worth stating: of 9,142
entries already swept and not in the roster, 14 have a parsable recurrence only inside a
block.** They have been put back for re-asking. So this defect mattered enormously for one
family and barely at all for the corpus — both facts are true and neither should be quoted
without the other.

## 8 September 2026 — ecarow: cellular automaton rows, and the hardest argument so far

138 entries read "Binary representation of the n-th iteration of the Rule N elementary
cellular automaton starting with a single ON cell", and no engine read any of them. The row at
step n is the light cone, a word of length 2n+1; "binary representation" reads that word as a
DECIMAL number whose digits are its bits, "decimal representation" reads it as a binary number.

**51 of the 138 settle into a shape that makes the conjecture provable:**

    w(n+p) = L + w(n) + R,   L and R fixed, |L| + |R| = 2p.

Given that, the value satisfies an exact linear recurrence: a(n+p) = a(n)·B^|R| +
val(L)·B^(2n+1+|R|) + val(R), which the operator (S^p − B^|R|)(S − B²)(S − 1) annihilates.
**All 51 reproduce their entry's published terms exactly, 0 mismatch**, and a 400-paper
regression sample shows the parser takes no existing name.

The other 87 have genuinely fractal rows and no such shape. They are not settled and are not
counted.

### The shape identity is a proof, not an observation

The automaton is a LOCAL map, so once w(n+p) = L + w(n) + R holds at two consecutive n past
the settling point — which fixes every three-cell window at both boundaries — it holds at every
later n by induction. `certify` reports how far past the settling point the identity was
checked; for the sample entry that is 45 further steps.

### Two errors caught before anything was counted

* **The background leaked into the cone.** Outside the cone the cells never met the initial
  one, so they follow the orbit of the all-zero configuration — which for a rule with
  000 → 1 is not zero. With too little padding that background travels inward at one cell per
  step: rule 175's row came out as 110111111111110 at step 7 instead of 110111111111111. Only
  the tail was wrong, which is exactly the kind of error that survives a check of the first few
  terms. The padding now exceeds the number of steps.
* **Six entries were reported as having their conjecture contradicted, and all six were an
  off-by-one of mine.** My threshold scan started at index `order + 1` instead of `order`, the
  first index at which a recurrence can be evaluated at all. So a recurrence the entry itself
  claims only "for n > 2" was recorded as holding from the start, the sweep then tested index 2,
  found it false, and called the entry's conjecture contradicted. A262779's conjecture is
  correct and its own line says "for n > 2". The scan was fixed in all four new engines, every
  FAILS record they had produced was dropped and re-asked, and **19 proved with 0 failures**.

That is the second time today a batch of apparent disproofs turned out to be my own code. The
rule I am now following without exception: **a disproof is checked by hand against the entry's
own wording before it is recorded as anything at all.**

## 8 September 2026 — the largest vein in the database: a conjecture that needs no model at all

Asked for bulk in the thousands, I stopped writing engines and measured the ceiling instead.
**19,097 entries in the whole OEIS carry a conjectured recurrence or generating function and
link no proof.** That is the number this project is working against.

Then the question that mattered: how many of those can be settled **without a model of any
kind** — no array to count, no transfer matrix, no name to parse?

**3,520 of them carry a generating function the entry itself states as fact.** For those the
conjectured recurrence follows from the stated g.f. by algebra alone: a rational g.f. of
denominator degree d makes the sequence C-finite with that denominator as its characteristic
polynomial, so whether the conjectured recurrence holds is a polynomial identity, decidable
exactly. 2,817 of them are not in the roster.

`sweep_gf.py` was written for exactly this and had 233 papers. It had the same four defects
found in the table sweep this morning, and one of its own:

* it walked all 399,027 names in A-number order;
* it skipped an entry **without recording the skip**, so every run re-read the same early part
  of the index and its timeout meant it never reached the rest;
* it did not shard;
* it required the conjectural word to be ON the line, so a conjecture written as a block was
  invisible;
* and `HITS`/`DONE` were fixed names, so four shards would all have written the same file.

With those fixed and the pool pointed at the 2,817:

| shard | proved in one window |
| --- | --- |
| 0 | 573 |
| 1 | 519 |
| 2 | 526 |
| 3 | 533 |

**2,151 proofs from this vein, and 0 records claiming a conjecture is false** — the sweep only
records a result when the implication holds and never asserts a falsehood, which after two
batches of false disproofs today is the design I want. Held results across all veins:
**2,212**, awaiting the live-OEIS re-check before any of them is counted.

The lesson is now unmistakable and is the same one five times over: **every large vein this
project has found was already reachable by machinery it already had, and was hidden by how a
sweep chose what to look at.** Not one of them was hidden by mathematics.

### The block defect a third time, and this one was destroying finished results

`livenew.py` is the gate every result passes before it is counted: it re-fetches the entry from
the live OEIS and drops anything that no longer carries an unsettled conjecture. It decided
that with a search for "conjectur" or "Empirical" **on the line** — so a conjecture written as
a block was invisible to it too.

The first two times this defect appeared it hid work. Here it **threw finished work away**:
183 proved entries were dropped as "no conjectural line left on the entry" when the conjecture
is plainly on the entry, in a block. A004484's live text reads

```
Conjectures from _Chai Wah Wu_, Apr 05 2021: (Start)
a(n) = a(n-1) + a(n-6) - a(n-7) for n > 14.
```

With blocks understood, the same 1,035 entries re-checked and **0 were dropped**.

There is a second lesson in how long this took to see. The fix was in the file and the drops
kept coming, because a background copy of the checker had been started before the edit and was
still running the old code inside a 1,700-second window. A source fix does not reach a process
that is already running.

## 8 September 2026 — 701 installed from the generating-function vein: the roster reaches 11,601

Every one live-confirmed before a paper was written: `build_gfdef.py` refuses to build for an
entry the live re-check has not returned as still open, so the gate is enforced by the builder
and not only by a report I read.

**The roster goes from 10,900 to 11,601 — 11,595 proofs and 6 disproofs over 11,574 entries.**
The rest of the vein's 2,151 proofs are waiting on the live re-check, which is still running.

**One result withheld.** A164735's live entry links a file by Kauers and Koutschan whose title
reads "Conjectured closed form for a(n), a quasi-polynomial of period 18 and degree 5". The
title says conjectured, and my result concerns the recurrence rather than that closed form, so
it is probably fine — but "probably fine" is not the standard here. One entry, genuinely
ambiguous, and a wrong claim costs far more than a withheld one. Dropped, with the reason
recorded next to it.

### Later the same hour — 11,797, and two flags judged by hand

Another 196 installed from the same vein. **11,797 papers: 11,791 proofs and 6 disproofs over
11,770 entries.**

The live re-check raised two flags and both were read rather than obeyed:

* **A265380 — kept.** The line that flagged it records N. J. A. Sloane *removing* "an
  unjustified claim that Colin Barker's conjectures are correct". That is evidence the
  conjecture is still open, not that it is settled — and a reminder that somebody has already
  asserted this one without proof.
* **A164735 — withheld.** Its linked Kauers–Koutschan file is titled "Conjectured closed form",
  so it is not a proof; but the entry is a known hard one and my result concerns the recurrence
  rather than that closed form. Ambiguous, one entry, and a wrong claim costs more than a
  withheld one.

`sync_sources` re-read and re-hashed all twelve thousand build directories on every run,
several minutes to recover hashes that had not changed. A build directory's PDF is written once
and never touched again, so its hash is now cached against the file's size and modification
time and only genuinely new builds are read.

### 12,012 — and 41 flags that meant the opposite of what my checker read

**12,012 papers: 12,006 proofs and 6 disproofs over 11,985 entries.** Another 215 installed
from the generating-function vein.

The live re-check raised 41 flags at once and every one carried the same line from
N. J. A. Sloane:

> Removed an unjustified claim that _Colin Barker_'s conjectures are correct. Removed a program
> based on a conjecture.

My checker saw "are correct" and flagged the entries as possibly settled. **The line says the
opposite**: somebody asserted these conjectures were correct without justification and Sloane
struck the assertion. Each entry still carries its conjecture — checked directly on three of
them before any were cleared — so all 41 stand open, and I now have proofs for them.
`livenew.py` reads a claim that was REMOVED, WITHDRAWN, RETRACTED or called UNJUSTIFIED as
evidence the conjecture stands, which is what it is.

There is a general point in this. A settlement checker that only pattern-matches words will
read a retraction as a confirmation, because retractions quote the claim they retract. Every
flag it raises has to be read.

## 8 September 2026 — a new vein, and a scan of mine that confidently returned zero

The generating-function vein settles a conjectured recurrence from a g.f. the entry states as
fact. The same argument runs from a **closed form** stated as fact: a formula built from terms
n^k·b^n is annihilated by a known monic integer polynomial, so the sequence satisfies exactly
the recurrences whose characteristic polynomial is a multiple of it, and the conjecture is
decided by one polynomial division with no model of the sequence at all.

Getting to that number took three tries and the middle one is the instructive part.

* **First measurement: 1,190.** Built on `line.startswith('a(n) = ')`, which also matches
  English prose — "a(n) is the number of sublattices of index n in a generic 2-dimensional
  lattice". Wrong.
* **Second measurement: 0 of 8,148 scanned.** I was ready to record the vein as a dead end.
  It was not: `closedform.parse_line` requires a line to begin "Conjecture:" or "Empirical:",
  because that module was written to read *conjectured* closed forms. A formula stated as fact
  carries no such prefix, so asking it whether an entry states one always answered no. **The
  scan was confident, thorough, and meaningless.**
* **Third measurement, with the parser taught to read a bare formula: 189 usable** from the
  8,148 scanned so far, of 19,097 to scan. **12 proved in the first window**, and 30 refused
  because the stated formula does not reproduce the entry's own published terms — a premise
  that cannot be read correctly is a premise I will not use, and nothing is claimed for those.

The pattern I have been reporting all day — a sweep whose refusal is really a defect in what
it asks — turned up this time in code I had written an hour earlier. It is not a legacy
problem. **A clean zero deserves the same suspicion as a surprising success**, and I now check
an instrument on a case I know the answer to before trusting a number it produces.

## 8 September 2026 — the criticism is right, and here is the measurement behind it

Challenged that the proof rate is low and only one easy kind of claim is ever attempted, I
measured the whole database rather than argue.

**32,629 OEIS entries carry a conjecture of a recognisable kind. This project has only ever
attempted one of them.**

| kind of conjecture | entries | attempted |
| --- | ---: | --- |
| linear recurrence / generating function | 15,978 | yes |
| inequality or bound | 5,726 | **no** |
| closed form | 4,943 | partly |
| congruence or divisibility | 4,130 | **no** |
| asymptotic or limit | 3,978 | **no** |
| primality or factorisation | 1,618 | **no** |
| always / never / infinitely many | 541 | **no** |

"Decidable" had quietly come to mean "reduces to linear algebra over Q". So I built the next
class properly.

### Congruences are decidable, by a theorem rather than by arithmetic

If a satisfies a monic integer linear recurrence of order r, the state vector
(a(n),…,a(n+r-1)) mod m evolves under a fixed matrix over Z/mZ. There are m^r states, so the
state must recur: **a mod m is eventually periodic, and the pre-period and period are computed
exactly.** Every claim of the form "a(n) ≡ c (mod m) for n > k", including one restricted to a
residue class of n, is then settled by checking one period past the pre-period — decided, not
sampled, and a failure inside that window is a genuine counterexample.

`engine/src/congruence.py` does this and `sweep_cong.py` applies it, taking the recurrence only
from a line the entry states as fact or from a result already proved here — a congruence proved
from a *conjectured* recurrence would be a conditional result dressed as an unconditional one.

### And the honest size of the vein: 17, not 4,130

The measurement that matters is not how many congruence conjectures exist but how many sit on
sequences the method can reach. Of 4,000 entries sampled, 294 carry a congruence-shaped
conjectural line and **only 4 also carry a recurrence stated as fact**. Of the 11,985 entries
whose recurrence this project has itself proved, **15** carry a congruence conjecture.

**The congruence conjectures in the OEIS overwhelmingly sit on sequences that are not linear
recurrences at all** — primes, divisor functions, digit sequences — where eventual periodicity
does not apply and the claim is genuinely hard. That is a structural limit of the method, not a
lack of effort, and it is worth stating plainly rather than leaving as an unexplained gap.

### The third false disproof of the day, again from my own parser

The sweep's first output was `DISPROVED? A237930`. The entry says

> a(n) == 10 (mod 84) for **odd** n. a(n) == 31 (mod 84) for **even** n > 0.

My parser dropped both qualifiers and tested each congruence at every index, where of course
both fail. With "odd n", "even n" and the "> 0" all read, **both claims are PROVED** — the
sequence mod 84 has pre-period 1 and period 2, so the two residues alternate forever.

Three times today a batch of apparent disproofs has been a defect in how I read the claim, not
in the claim. The mathematics in this project is not the hard part; **reading the sentence
correctly is**, and that is where every error of the day has been.

## 8 September 2026 — the leverage was not in exotic classes, it was in the second conjecture

Pressed on why only one kind of claim ever gets attempted, I built the next two classes
properly and measured them honestly. **Both are structurally out of reach, and it is worth
saying exactly why:**

* **Congruences.** Decidable for a C-finite sequence — the state vector mod m evolves under a
  fixed matrix over a finite state space, so the sequence mod m is eventually periodic with
  computable pre-period and period. Of 4,000 entries sampled, 294 carry a congruence
  conjecture and **4** also carry a usable recurrence. **17 usable in total.**
* **Asymptotics.** Decidable for a C-finite sequence — the growth rate is the dominant root of
  the characteristic polynomial, an exact algebraic number, so a stated limit is compared
  digit for digit rather than estimated. 47 entries carry a ratio-limit conjecture. **0 of
  them has a linear recurrence.**

Both classes live overwhelmingly on sequences that are not C-finite at all — primes, digit
functions, divisor counts — where these methods say nothing. That is a wall in the mathematics,
not a shortage of effort, and the right response is to name it.

### Where the leverage actually was

**11,968 of the 11,985 entries in the roster still carry a conjectural line**, and **6,150 of
those lines are a further recurrence, generating function or closed form** — for a sequence
this project has ALREADY PROVED is C-finite. The premise that is the whole difficulty
elsewhere is, for these, already in hand:

* another recurrence holds exactly when its characteristic polynomial is a multiple of the
  proved one;
* a generating function holds exactly when its denominator's reciprocal is;
* a closed form holds exactly when its own annihilator is.

`engine/src/sweep_second.py`. One shard of four, one window: **362 entries, 581 further
conjectures settled.**

One guard had to be loosened, and the reason matters. A recurrence proved here is proved *past
a threshold*, and an entry's early terms need not satisfy it. Testing from the first term
refused 919 entries whose recurrence is perfectly correct. The premise must now hold from some
index on with at least order+2 confirmations after it — still a real check, and it recovered
158 entries in one window.

### The second-conjecture vein, counted honestly: 885 not 2,461

The sweep reported **2,461 further conjectures settled** across 1,612 entries. Before counting
any of them I checked what they were, and most were not a second result at all.

A generating function whose denominator's reciprocal **is** the characteristic polynomial of
the recurrence already proved for that entry states the same fact in another notation. Of the
first 389 such claims, **386 were exactly that.** They are not a further conjecture settled;
they are the conjecture already settled, restated.

The closed forms are different: an explicit formula for a(n) says something a recurrence does
not, and those are real.

`sweep_second.py` now classifies a generating function as *restating the proved recurrence*
when its denominator carries no more information, and counts only what says something new. On
the same shard: **297 claims with new content, 618 restatements** — and the restatements are
kept in the record under their own name so the distinction is visible rather than discarded.

**The count that would have been reported was 2.8 times the real one.** The standing rule is
never pad the count; this is what enforcing it looks like when the padding is my own.

## 8 September 2026 — exponential generating functions, a class never attempted

An ordinary generating function conjecture is settled by comparing denominators. An
**exponential** one is a different transform, written with exp, sin and cosh rather than as a
ratio of polynomials, and nothing here had ever looked at one. 122 entries conjecture an
e.g.f.; **28 have a recurrence available as a premise, and 11 are proved.**

It is decidable because a C-finite sequence's e.g.f. is a combination of exponentials fixed by
the recurrence's roots. The test expands the conjectured e.g.f., requires it to reproduce every
term the entry publishes, and then requires its own coefficients to satisfy the premise
recurrence — two sequences satisfying the same recurrence and agreeing on `order` consecutive
terms past its threshold agree for ever.

### The fourth false-disproof class of the day, and I created it in the same hour

The first run reported **8 conjectures false**. Every one was mine.

I had just relaxed the premise check to allow a recurrence that holds only past a threshold —
correct in itself — and then seeded the comparison by regenerating the sequence from that
recurrence starting at index 0. The regenerated early terms are not the entry's terms, so eight
e.g.f.s that match their entry exactly came out false. A273790's conjectured e.g.f. gives
1, 6, 31, 80, 161, 282, 451, 676 and the entry publishes 1, 6, 31, 80, 161, 282, 451, 676.

The fix is a rule worth stating on its own: **the entry's published data is the ground truth,
and the recurrence is only what carries a claim beyond it.** A test that compares a conjecture
against regenerated terms rather than against the entry is not testing the conjecture.

Four times today an apparent batch of disproofs has been a defect in how I read or reconstruct
the claim. Not once has it been a false conjecture. **The disproof count stands at 6, all from
earlier work, all re-verified.**
