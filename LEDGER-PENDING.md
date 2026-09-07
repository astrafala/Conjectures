# Pending ledger notes

Written by the hourly working routine; folded into LEDGER.md and cleared by the daily
routine. Not a published document.

## 7 September 2026 --- two papers withdrawn: somebody else was three days earlier

The local OEIS mirror was two days stale. Refreshed to the 7 September export and every one
of the 9676 roster entries re-checked for settlement wording. **27 entries carry such
wording; 25 of them are about a different statement on the same entry** --- the pattern the
openness checker's own docstring records, and the papers involved already say so in their own
first pages (paper 0007 names Greathouse's 2013 confirmation of the square case and proves
Kaydalov's rectangle case; paper 0005 names Adamczewski on Conjectures B and C and proves A).

**Two are real, and both are withdrawn.**

- **A105872**, paper 9503, dated 25 August 2026.
- **A127361**, paper 9509, dated 25 August 2026.

Both prove R. J. Mathar's conjectured polynomial-coefficient recurrence. The entries now
carry `[Proved in Easwar (2026). - Rohun Easwar, Aug 31 2026]`, and the linked preprint is
arXiv:2608.22053, **submitted 22 August 2026** --- verified on the arXiv abstract page, not
inferred from the identifier. That is three days before the date on my papers. The standing
rule is that a result found after mine stays and one found before mine goes; these were found
before mine, so they go. Roster 9703 -> 9701.

Easwar's preprint is cited by six OEIS entries (A002897, A034015, A094213, A105872, A127361,
A290575); only those two were ever in the roster, so nothing else is affected.

**What this says about the method.** The freshness of the mirror is part of the count. A
two-day-old export cost two papers that should never have been claimed, and would have kept
costing them silently. The check is cheap --- one `git pull` and a scan of 9676 entries in
under a minute --- and belongs at the start of every session, not at the end.

## 7 September 2026 --- the 208 the queue never reached: 76 more

The 799 conjecture-carrying candidates were swept in rounds bounded by wall-clock, and the
round ended before the list did: **208 were left unprocessed rather than refused**, which is
a different thing and had to be checked rather than assumed. It was worth checking --- one of
them, A279576, settles in three seconds from a standing start.

Swept at thirty seconds an entry: **76 proved**, thirty-five of them arrays of permutations
under an offset condition, nineteen on permutation arrays with a fixed displacement, ten more
on the same family, and a tail of four engines. None is contradicted by its own published
data.

**Refusals, with the cap beside them, as the rule requires.** 92 refused with `state space >
cap` at **cap 2000000**; 3 exceeded the thirty-second budget in the annihilation test rather
than in the build, and are worth a longer pass rather than a bigger cap; 30 are not open.

**A cost measured, not guessed.** The heavy end of this pool is real work, not a bug:
A264014 builds 1048576 states in 84 seconds. That is why the pass was run at thirty seconds
and the expensive tail deferred, instead of letting four entries consume the whole budget.

**Settlement re-checked before counting.** `freshcheck.py` over all 9750 roster entries
against the 7 September export: 25 carry settlement wording, the same 25 already examined,
every one about a different statement on the same entry. None of the 76 new entries is among
them.

## 7 September 2026 --- the refused pool, measured properly, and one wall recorded

**`src/whyrefused.py`.** "State space > cap" and "build timed out" come back from the sweep
as the same thing --- a refusal --- and they want opposite responses: a bigger cap, or a
longer budget. Re-running everything at both is how an afternoon disappears. The new script
gives each entry a short fixed slice and records which wall it hit, so the next pass can be
aimed instead of sprayed.

**What it found in the 132 unsettled entries of the last pass:** 30 not open, and of the rest
the largest block is `transfer32` at widths 8 and 9, which the diagnostic reported as
cap-refused --- but the cap was never the binding constraint. The build could not finish at
all.

**`transfer32` rebuilt, and it is a real improvement.** The start weights were built by a
triple loop over rows: at width 9 over two letters that is 1.34e8 iterations, each recomputing
every window statistic. Only the statistics matter, and window $j$ of them depends on the
first row through columns $j$, $j+1$, $j+2$ alone. The row is now grown one column at a time,
prefixes agreeing on their last two entries and on the statistics so far are merged carrying
their count, and the within-row constraints are tested the moment their second column appears
so a doomed prefix dies immediately. Verified against the old loop on random row pairs at two
widths --- every weight agrees exactly --- and the rebuilt model reproduces all 22 published
terms of A253932.

**And it is still not enough. Recording the wall with its numbers.** Width 7 builds in 80
seconds. Width 9 has 512 rows, so the outer loop alone is 262144 row pairs at about 10 ms
each: three quarters of an hour before the state count is even known, and it then exceeds
**cap 2000000** anyway. Three entries were run to completion under a 1500-second budget and
none settled. **The 21 `transfer32` entries at widths 8 and 9 are out of reach by this route**
--- not because of the cap, and not for want of a longer budget, but because the pair loop is
quadratic in a row count that doubles with every column. A different formulation would be
needed, and I do not have one. Written down so it is not measured a third time.

The 34 `transfer22` entries in the same pool are a separate question and untouched: their
builds do finish (A264014 reaches 1048576 states in 84 seconds), so they are a cap-and-budget
matter rather than a structural one.

## 7 September 2026 --- 19 more, and the difference between a cap and a clock

`whyrefused.py` said the `transfer22` entries were refused on the cap. They were not: A264014
builds 1048576 states in 87 seconds, computes its terms in 8 and settles its residual in 10 ---
**106 seconds in total, against a 30-second budget.** The refusal was a clock, not a wall.

Re-run at a 200-second budget over the 106 buildable entries of the refused pool: **19 proved**,
all in the permutation-array family, where a value moves from its home cell by an index change
on a short list and the count becomes a matching problem solved column by column. The remaining
entries of that pass were refused again, and those really are cap-bound.

**The two refusals look identical in the log and want opposite responses.** That is the whole
reason `whyrefused.py` exists, and this pass shows it still reports them wrongly when a build
finishes just past the slice it is given. The diagnostic's own slice is now part of what it
reports.

Settlement re-checked against the 7 September export before counting: 25 entries carry
settlement wording, the same 25 already examined, none of them among the 19.

## 7 September 2026 --- the pair state was never needed: 65 more

The refused pool was swept whole first, and it did not pay: 111 entries processed, one result.
That pool is genuinely cap-bound, not clock-bound, and the ranking was right to leave it. What
paid was asking *why* the largest block in it --- 150 `transfer17` entries --- was over the
cap, and the answer was that the model was built out of the wrong thing.

**The redundancy in a pair-of-lines state is exact, and can be removed before the states
exist.** The vertices were ordered pairs $(r,s)$, so the count was $(\alpha+1)^{2W}$: sixteen
million at width 6 over four values. But for a window $j$, whether a line $t$ is admissible
there depends on $r$ and $s$ only through their own $j$-th windows. Collect for each $j$ the
set of triples $(t_j,t_{j+1},t_{j+2})$ the pair allows, call it $C(r,s)$; then the lines that
may follow $(r,s)$ are exactly those consistent with every $C_j$, and the successor $(s,t)$
carries $C(s,t)$, which does not mention $r$ at all. **Two pairs $(r,s)$, $(r',s)$ with the
same $C$ have the same outgoing lines and the same successors**, so the vertex is $(s,C)$,
with the multiplicity of $r$ as its starting weight. Those multiplicities come from a small
dynamic programme over columns rather than from enumerating $r$.

That is the merge `lumpauto` already performed --- done before the states exist rather than
after, which is the difference between a model that fits and one that cannot be written down.

- A252060: 59049 states to **3140**, 11.7 seconds to under one.
- A252072: 4782969 pairs, **75396** states in 1.2 seconds, all 18 published terms.
- A251946: 16777216 pairs, **465700** states in 11 seconds, all 23 published terms.

Same terms as the pair model wherever the pair model can still be built at all.

**65 proved** in the family, 51 refused at **cap 2000000** even after the merge (the widest
widths over four letters), 0 contradicted by their own data.

**The papers say which digraph the numbers came from.** They state the pair count, then the
identification and why it is exact, then the $S$ it leaves. The 142 papers built earlier today
are untouched and remain correct: they quote the unmerged count, which is a valid
Cayley--Hamilton bound, merely a generous one.

**A pipeline order that matters.** `makecomments_site.py` reported 3958 papers whose source
disagreed with the date the paper prints. Nothing was wrong: `paperdates.py` had not finished,
so the date map was still keyed by the previous ranking and every shifted paper looked like a
disagreement. Run `rank.py`, then `paperdates.py` to completion, then `makecomments_site.py`;
out of order it manufactures thousands of false alarms.

## 7 September 2026 --- the same merge again, on the cell-centred engine: 67 more

`transfer19` indexes its vertices by $(r,s,c)$ --- an ordered pair of lines and the violations
so far --- and the loop filling its edges runs over TRIPLES of lines. **No vertex guard sees a
triple loop**, so an entry could pass the guard and then never finish. That is what had
happened to the wider members of the family, and it is why they sat in the refused pool
looking cap-bound.

Every offset these entries name has $|dj|\le1$, so whether the cell at column $j$ of the middle
line is satisfied depends on the three lines only through their windows at $j-1,j,j+1$. Collect
for each $j$ the indicator over the window of the line below and call it $P(r,s)$: the number
of cells any $t$ violates is read off $P$, so is the number violated at the bottom edge, and
the successor $(s,t)$ carries $P(s,t)$, which does not mention $r$. Two pairs with the same $P$
are indistinguishable, so the vertex is $(s,P,c)$. One column's profile depends only on a pair
of windows, so it is computed once per such pair rather than once per pair of lines.

Checked against the old build on six entries where the old build still runs: identical terms
every time. The old build is kept where it is both small and affordable --- for small models it
gives the tighter state count --- and past either wall the pair-free one is the only one that
returns.

**67 proved, at a 78% strike rate over the entries reached.** A195974 goes from 390625 pair
states to **2473**. Round two of the same sweep found nothing in its first ten, which is where
the vein runs out for now.

**The papers say which digraph the numbers came from,** as they did for `transfer17`: the pair
count, the identification and why it is exact, then the $S$ it leaves.

Settlement re-checked against the 7 September export: 25 entries carry settlement wording, the
same 25 already examined, none among the 67.

**The deep check is 72 papers away** (`dc_gate.py` reports 9928 of 10000).

## 7 September 2026 --- the deep check, made real before it fires

72 papers from the 10,000 trigger, and Phases 3--12 were still prose. Two of them are now
code, and writing them found the usual thing: **the checks were wrong before the papers
were.**

**Phase 0, `dc_phase0.py`** --- freezes the roster to `deep-check/frozen-roster.json`, records
the commit, whether the tree is clean, a SHA-256 of all 21069 tracked files, the Python and
library versions. It refuses to re-freeze without `--refreeze`, because a check that
re-freezes halfway is checking two corpora and reporting one number.

**Phase 3, `dc_phase3.py`** --- every paper re-checked against the live entry: the quoted
conjecture, the "Last modified" line and revision, the terms printed in section 1 against the
entry's current DATA, the paper naming its own A-number, and the settlement scan over the
whole roster.

**Four false-positive classes, all mine, all fixed:**

1. *Terms.* `a(0), . . . , a(7) = 1, 1, 3, ...` contains an ellipsis of its own, so a pattern
   that stopped at the first ellipsis captured the label and none of the terms --- **12 papers
   reported as disagreeing with data they match exactly.** Now the terms are read from the
   line after "begins", after the last `=`.
2. *Dates.* The paper prints `22 July 2026` or `2026-07-22`, the entry prints
   `Jul 22 2026 01:20:48`. **31 papers "edited since they were written"**, none of them edited.
   Now the revision number decides and the day is compared after parsing both forms.
3. *Page numbers.* A quotation running across a page break comes back from the extractor with
   the page number inside it --- `a(n-`, `1`, `40)` --- and A223336 was reported as
   misquoting an entry it quotes exactly. Lines that are nothing but a number are dropped.
4. *One lead-in.* The builders introduce the quotation several ways, and knowing only one of
   them left **280 of the first 400 papers unquotable and unchecked** --- a check that looks
   like a pass because it never ran. All the lead-ins are now known.

**A real distinction the plan did not draw.** Some papers quote the entry as plain text;
others TYPESET it, so `x^3` becomes $x^3$ and `>=` becomes a glyph, and the extracted text
cannot equal the entry character for character. Demanding verbatim there is not a defect in
the paper. Those are now identified and checked on their numbers instead --- every integer of
two digits or more, in order, against the best-matching entry line.

**Where it stands:** trialled over papers 1--400. 0 term mismatches, 0 date defects,
2 entries genuinely edited since their paper (A079144, r71 to r73), **11 quotations still
unresolved** and listed by rank for examination when the phase runs for real. That list is
the phase's output, not its failure.

## 7 September 2026 --- Phase 3 run over the whole corpus, and the pair dropped from a third engine

**Phase 3, all 9928 papers, against the 7 September export: 0 defects.** Every paper names its
own A-number; every term printed in section 1 is a prefix of the entry's current DATA; every
quotation the comparison can adjudicate is exact.

What it also reports, which is the useful part:

* **414 papers typeset their quotation**, so the extracted text cannot equal the entry
  character for character. Those are checked on their numbers --- every integer of two digits
  or more, in order.
* **39 quotations the automated comparison cannot settle**, listed by rank for the reading
  pass. An automated string comparison is not entitled to a verdict on a typeset formula, and
  saying so is more honest than passing them.
* **381 papers whose section 1 quote could not be located at all** --- 3.8% of the corpus, the
  early bespoke papers whose section 1 is laid out individually. That is a coverage gap in the
  check, not a defect in the papers, and it is named rather than hidden.
* **11 entries edited since their paper was written** (A079144 r71 to r73, A262482 r13 to r17,
  and nine that print no Last-modified line at all --- those last were the pattern matching
  some other parenthesis and reading the revision as zero, now fixed).

Four more of my own false-positive classes were removed getting there: a credit line rendered
differently in paper and entry, two more quotation lead-ins, containment tested in only one
direction, and the revision-zero case above.

### transfer9 --- the third engine with a pair state it did not need

Same shape as `transfer17` and `transfer19`: the pair branch fills its edges with a loop over
TRIPLES of lines, which the guard `len(lines)**2 > cap` cannot see. Every offset moves at most
$R$ columns, so the profile $P(a,b)$ of indicators over the window of the line below carries
everything the pair does; the vertex is $(b,P)$, and the starting pairs --- those whose first
line is satisfied with nothing above --- decompose over the same windows.

Identical terms to the old build on all seven entries small enough to run both, with the state
count 2 to 6 times smaller (A188554: 64 to 11; A188519: 1024 to 262). 81 entries requeued.

### 13 more from transfer9, and two things the papers had to be told

The pair-free build settled 13 of the 81 requeued `transfer9` entries; the second round found
nothing in its next 23, which is where that vein ends.

**A paper may not say a false thing about the object its numbers came from.** The general
builder said "take as vertices the admissible configurations of one such window", which stops
being true the moment the model identifies windows that behave alike. Those papers now say so:
*windows that admit exactly the same continuations and lead to the same states are identified,
which changes no count.* `transfer9build` says it in the family's own terms but wants fields
the unified sweep does not record, so these thirteen use the general builder rather than a
builder invoked with the wrong arguments.

**The pipeline order is now a check, not a rule.** `makecomments_site.py` reported 3570 papers
whose source disagreed with the date the paper prints --- for the second time, and for the same
reason: it ran before `paperdates.py` had finished, so the date map was still keyed by the
previous ranking. It now refuses to run when `paper-dates.json` is older than
`papers/index.csv`. A rule that has to be remembered gets remembered late.

## 7 September 2026 --- past 10,000, on a vein that had been invisible

**The sweep had been filtering on a recurrence it could PARSE.** 432 unsettled entries state
only *"Empirical recurrence of order N (see link above)"* --- the recurrence lives in a file the
local copy does not carry --- so every one of them was skipped in silence. Not refused. Never
looked at. **An engine already modelled 414.**

The recurrence does not need to be read. The entry is a fixed-width array count, hence a walk
count on $S$ states, hence satisfies some monic recurrence of order at most $S$;
Berlekamp--Massey on $2S$ exact terms returns the MINIMAL one; and if that order equals the
stated one, any recurrence of that order the sequence satisfies has a characteristic polynomial
that is a multiple of the minimal one and of the same degree, hence equal to it. Where the
stated order is *larger* than the minimal one the uniqueness fails, and those entries are left
alone rather than guessed at.

`src/sweep_ordwhole.py`. **100 proved** at a 42% strike rate over the entries reached, every
recovered recurrence checked against the entry's own published terms before it counted.

**Measuring the whole open pool, since it turned out I had been mining a fifth of it.** Of the
unsettled entries carrying an unsettled conjecture: 1239 state a parsable recurrence (the pool
worked all day), 546 state a closed form, 151 a generating function, and **1286 something
else** --- of which the largest shapes are 554 per-column blocks and these 432 order lines.

### Three errors of my own, all found by looking rather than by being told

1. **A paper described a computation that was not performed.** `ordbuild` said
   "Berlekamp--Massey applied to $2S$ exact terms" with $S=4768$; the run used the merged
   bound, 152. The paper now states both and says which one the computation used. The comment
   said 4768 too, and now says 152.
2. **`build_new.py` read a stale roster and overwrote a hundred papers that had just been
   installed.** `rank-map.json` is only regenerated by `rank.py`, so between an install and the
   next ranking it lags; `paper-engines.json` is current the moment `integrate_rest.py`
   returns. The installed PDFs were the right ones --- checked, six of six --- but the sources
   and therefore the comments described a different paper. It now reads both.
3. The comment template printed *"Its order is the one stated, the order stated here"* where
   the recovered order belongs, because the lookup had no entry for these results.

**Roster 10054 papers over 10027 entries. `dc_gate.py` reports the deep check is DUE.**

## 7 September 2026 --- the deep check, phases 5, 6, 8 and 10, and the repository straightened

**Phase 5 (the mathematics, recomputed from cold)** rebuilds each model in a fresh process
with nothing reused and checks the paper's claim against it: the model still reproduces every
published term, the recurrence still annihilates it, and the threshold comes out where the
paper says. **390 recomputed so far, 0 disagreements.**

Its first finding was a false one of my own making. Some papers' names are now read by a
*newer* engine than built them --- `transfer93` generalises `transfer75`, and `uniform.read`
returns whichever comes first in its list --- and the phase called that a disagreement. Both
engines reproduce every published term of A184404, checked directly, so it is an **overlap**,
not a defect. What the paper claims is what ITS engine computes, so the rebuild now uses that
engine and the overlap is recorded for the duplicate-work audit.

**Phase 6 (the checks, themselves audited).** Of 730 modules, 263 exception handlers record
nothing before continuing. But only 95 modules are on the path a sweep actually takes, and
**only 3 of the silent handlers are among them.** The one that matters is `uniform.read`: a
parser raising on a name it ought to read makes that name unreachable, and the handler hid it.
The raises are now counted and kept --- nothing stops, since one broken parser must not take
down a sweep, but nothing is invisible. Asked over 6000 names there are currently **none**.

Phase 6 also names the 158 modules that match their own patterns against entry text instead of
going through the canonical parser. That is how a candidate pool once came out at 49 instead
of 130.

**Phase 10 (comments): 0 defects over 10022.** Two of its findings were wrong and are fixed:
it called `Sum_{i>=1}` and set braces LaTeX, condemning 54 correctly written comments, and it
read `submission-order.txt` as an index when it is a deliberate first-round queue --- the OEIS
allows three pending submissions at a time --- reporting ten thousand entries as missing from
a file never meant to hold them.

**Phase 8 (wording and logic)** found two more of my own before finding a real one: "the
statement is false for k even", written while delimiting a hypothesis, made a proof read as a
disproof; and a pattern expecting "still recorded as EMPIRICAL" missed "still recorded as an
unproven conjecture", reporting 68 of the first 400 as missing a sentence they all have.

**The real one: 8 of the first 400 papers carry no statement that the entry is still open.**
A061002, A000071, A000139 and five others quote the conjecture with its contributor and date
and then never say the entry is unsettled. That is a required part. The whole-corpus count is
still running; the fix waits, because the plan's stop rule is that defects are collected and
fixed only when the check is finished.

### Organisation

`deep-check/` had become a sixth folder at the root, against the stated layout of documents
plus five folders. The plan and the running report are documents and are now one document at
the root, `DEEP-CHECK.md`; the working data moved to `engine/deep-check/` with its own README
and is reached through `repopaths.DEEPCHECK`. Phase 1 re-run after the move: 8 checks, 0
failures. The root is now exactly documents and `papers/ paper-sources/ comments/ engine/
archive/`.

## 7 September 2026 — six stale filters, one new engine, 86 results found and held

The day's lesson, stated first because it is the whole of it: **almost nothing here was
blocked by mathematics.** Six separate caches and hard-coded lists had stopped matching the
code around them, and each was holding back real work.

1. `sweep_table.py` carried its own list of twelve engines — all of them when it was written,
   twelve of eighty-three now. Every table whose column model needed a later engine was
   reported *"no engine reads it"* and dropped. **434 entries** sat behind it, 385 of them
   stating *"Empirical for column k:"*, which is exactly what that sweep settles.
2. `falsify.py`, the disproof sweep, had the same list. Seventy-two engines' worth of entries
   were never even parsed, so no conjecture of theirs was ever tested for failure.
3. `sweep_tablerow.py` had the list *and* a second bug in the same lines: it called `avals`,
   which most engines do not have, and the `AttributeError` was swallowed and reported as
   *"model does not match the column"* — a model matching the entry perfectly, thrown away.
4. The cached name list the sweeps read was missing **358** order-line candidates, so every
   sweep skipped them silently. The order-line pool is 499 untried, not 168.
5. `uni_cands.json` is iterated *before* `ANUMS` is applied, so entries a newly written engine
   reads — which cannot be in a cache built before it existed — were filtered out to nothing
   and the run reported processing zero of them.
6. `sweep_cf.py` wrote to fixed file names, so aiming it at a different pool silently reused
   the old run's `done` set and did nothing.

**A claim of mine was wrong and is corrected in place.** The *"2,098 entries blocked at a
state cap of 2,000,000"* figure counted the keys of `shard_caps_*.json`, which recorded the cap
of every entry a sweep **attempted**, not of the ones it refused. A sample of 70 re-run with
the reason counter read came back **60 with no parsable recurrence, 7 already settled, 3
refused for size**. The pool is overwhelmingly entries with nothing to prove. Reading all
1,411: **1,395 carry no unsettled conjecture at all.** Dead, and closed. The sweep now records
a cap only where a refusal for size happens, and `dc_englists.py` is the enforcing code for the
engine-list rule, run by Phase 11.

**The whole remaining pool, mapped.** Of every name an engine reads with no paper — 5,621
entries: 4,053 carry nothing to settle, **841 state a recurrence**, **671 state only an
order**, 56 something else. So 1,568 live candidates, not the 1,010 Phase 7 counted.

**transfer94**, a new engine, 37 entries no engine read: monotone height arrays, values rising
by 0 or 1 with every step, pinned to a corner distance. Reading each row relative to its own
index makes every condition local. Two of my own errors are recorded in the file — a state
bound derived for city-block distance applied to king-move too, and an accepting condition
using the tall-array distance for every `n`. All 37 reproduce their published data exactly.

**86 results found and held**, not installed: the check's rule is that the corpus stays frozen
until it finishes. Recurrence sweep 19, order-line 19, table columns 43, table rows 10, closed
forms 3.

**Independence**, the weakness Phase 11 named: 90 of 104 argument families had never been
checked by anything but the program that produced them. Three brute forces that share no
engine code now exist — `indepcell.py` (**197 of 197**, complete), `indep2x2.py` and
`indepadj.py` (1,300+ confirmed between them). **Nothing disagrees.** The one disagreement that
did appear was the checker's fault: a name reading *"a(n) is half the number of ..."* whose
divisor pattern was anchored at the start of the name, so the brute force came back at exactly
double.

**Defects found and recorded**: 8 papers printing *"As of the Last modified line on the live
entry (, revision 0)"* — a check asserted with nothing in it, which Phase 3 had been *skipping*
as a false alarm; 100 order-line papers quoting a term count from the unmerged bound while
saying they used the merged one; 263 papers with no stored source, 100 from a build-directory
collision now fixed.

**A 7.2 MB truncated zip** was found tracked under a scrambled name, holding duplicate PDFs.
Removed; the ignore rules now catch archives by kind rather than by the one name that was
listed.

**README** gained an *Authorship, priority and reuse* section: sole authorship, the dated
record in four independent places, and that CC BY 4.0 permits reuse only with credit.

### Standing rule added: never stop

Written into `METHODOLOGY.md` as section 7a. **The work does not stop, and there is no state
of this project in which waiting is the right thing to do.** A sweep that empties its pool is
pointed at the next one; when every pool an engine can read is exhausted, the next work is a
new engine, chosen by clustering the names no engine reads and taking the largest cluster;
when a check finishes it is re-run, because the corpus has grown since; and a wall is re-tested
whenever the thing that caused it changes. Idle is a defect.

That last clause is not a slogan. Every wall re-tested on 7 September 2026 turned out to be a
stale filter rather than mathematics — seven of them in one day, hiding between forty and four
hundred and thirty-four entries each.

### The 92 held results re-checked before counting

Every pending result was re-read against the OEIS clone (at commit `bc2cd37f64`, 7 September
2026 03:04) looking for wording that would mean someone else has settled it. **None carries
any.** The clone is roughly nineteen hours old at the time of the check and a `git pull`
brought nothing newer; that age is stated rather than described as "live", because a two-day
stale clone has already cost this project two withdrawn papers once.
