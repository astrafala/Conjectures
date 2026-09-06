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
