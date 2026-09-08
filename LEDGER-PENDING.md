
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
vocabulary. Adding it, with the three related orderings, made **91 entries readable**, the
model matched the published terms of all 21 tried so far with **0 mismatches** (6 more want a
cap above 400,000), and the existing engine's 400 sampled papers all still parse. The
closed-form sweep has already returned **18 proofs from the first 22** of them.

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
