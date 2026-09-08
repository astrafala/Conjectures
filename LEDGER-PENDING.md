
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
