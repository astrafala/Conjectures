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
