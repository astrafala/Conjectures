# Read this first. Everything crucial, in one page.

## RULE 1 — NEVER STOP

**Every turn MUST end by scheduling the next one.** Before finishing any reply, call
`send_later` with `delay_minutes: 1` and a message telling yourself to continue. That is what
makes the work self-sustaining: the container suspends background jobs between turns, so
without a scheduled wake-up the project simply pauses until someone prompts it.

Stop scheduling only when you are certain no further conjecture can be settled by any means —
and that has never once been true. Every time this project looked exhausted, the next
measurement found thousands more. If IDEAS.md is empty, the job is to fill it, not to stop.

Never stop finding more. Finish an idea and start the next one in the same breath, without
being asked and without reporting-and-halting. When the ideas run out, think outside the box:
look for new veins, look at kinds of conjecture never attempted, re-measure what was called
dead. There is always another angle. **Rule 1 outranks everything else in this file.**


If context was lost, this file plus `IDEAS.md` is enough to carry on without asking anything.

## The job

Find open OEIS conjectures and prove or disprove them. **Never stop.** Finish an idea, start
the next from `IDEAS.md` without waiting to be asked. Target bulk — hundreds and thousands, not
tens. Mildly harder classes are wanted, not avoided.

## Binding rules

* **Never pad the count.** Two results are distinct when they are on different entries, or the
  entry names them as different conjectures. A g.f. whose denominator IS a recurrence already
  proved for that entry is the same conjecture restated — not a second result.
* **Re-check every result against the LIVE OEIS before counting it** (`src/livenew.py`).
* **Say plainly when something is null, elementary, or probably already known.** A withheld
  result costs nothing; a wrong one costs credibility.
* **Check every apparent disproof by hand against the entry's own wording before recording it.**
  Four times in one day a batch of "disproofs" was a defect in my own reading. Never once a
  false conjecture.
* One PDF per result. Author "Adrian Perez Fontelles, Independent researcher". §1 quotes the
  conjecture verbatim with contributor and date, and states it is still open as of the entry's
  Last-modified line. A Verification section. References. A paper is as long as its result
  needs — no padding, no truncation.
* **NO ZIP ARCHIVES.** Papers in `papers/`, sources in `paper-sources/`, comments in
  `comments/` with the date each result was found, all code and working data under `engine/`.
* Batch notes go to `LEDGER-PENDING.md`; a daily routine folds them into `LEDGER.md`.
* Nothing is ever posted to the OEIS. That is the user's to do.

## The habit that has found every large vein

**Read what a sweep REFUSES, not what it proves.** A sweep reporting a small clean number is
not evidence that the pool is small. Every large vein so far was reachable by machinery already
built and hidden by how a sweep chose what to look at — never by mathematics.

Recurring defects, all found this way:

1. a pool built from a stale snapshot (**eleven times now**, 40–1,718 entries each). On
   15 September this stopped being found one at a time and became a deliberate pass: rebuild
   every sweep's pool from the clone and diff. `deep-check/prec.txt` held 380 where the clone
   has **989**; `cfpool_cands.json` held 416 where it has **728**. Those two paid 21 papers
   between them. Two others (degree, linkrec) were NOT stale, and why is worth knowing —
   degree's phrasing occurs 8 times in the whole database, and linkrec's pool was correctly
   filtered by ENGINE coverage rather than frozen. **Before running any sweep again, rebuild
   its pool and diff.** IDEAS §AE.
2. requiring the conjectural word ON the line, so block conjectures are invisible — found in
   the pool filter, in every sweep, and in the live re-check, where it was destroying results
3. skipping an entry without recording the skip, so every run re-reads the same early index
4. no clock, so one slow entry eats the whole run
5. a formula split across continuation lines, read truncated
6. a threshold scan starting one index late
7. a claim's qualifier dropped ("for odd n")
8. **an instrument that cannot see what it is asked about returns a confident zero** — test any
   instrument on a case whose answer is known before trusting its number
9. comparing a conjecture against regenerated terms instead of the entry's own data — the
   entry's published data is the ground truth; the recurrence only carries a claim beyond it
11. **a derived bound that forgets the degenerate case.** `latpoly`'s period bound is right
    for every cell of the arrangement that has a ray, and the origin is a cell with none: it
    contributes the constant series 1, whose numerator over the common denominator has degree
    exactly S rather than below it. The bound was one short, and the guard that extrapolates
    past the computed terms is what caught it, on A189327. Test a derived bound by asking the
    model for terms it did not supply.
12. **a certificate verified where the induction that would carry it does not exist.**
    `ecarow` may check `w(n+p) = L_r + w(n) + R_r` over the stages it ran and call it proved,
    because a row of a ONE-dimensional automaton is a function of the row before it. `ca2d`
    copied the sentence one dimension up, where the axis is not a function of the axis before
    it, and 272 results stood on an identity nobody had shown persists. 184 papers withdrawn
    on 13 September. Before a verified identity is used past the range it was verified on,
    name the induction that carries it and check that the model actually supports it.

18. **a shelved engine is not a dead engine, and the shelf note says what would unshelve
    it.** `transfer88` was finished weeks ago and deliberately left unregistered because its
    transfer matrix rested on `d(i+4,j) = d(i,j)+2`, which had only been CHECKED over a few
    hundred rows. The note in its docstring named the obstruction precisely, and that is what
    made it a half-hour job to remove: the Bellman conditions turn a guessed distance field
    into a proved one, and because a knight move spans at most two rows, finitely many rows
    settle every row. Twenty-one entries. **Re-read the engines that refused themselves.**
    A second lesson sits beside it: the old engine refused widths 8 and up as "showing no
    period", which was a limit of its measurement and not of the board. A refusal written
    from a measurement expires when the measurement is replaced by a theorem.

19. **a construction that works is not a construction that has been looked at.**
    `transfer88` refused A253117 at the state-space cap, which reads like a mathematical
    limit and was not one: it carried the ROW INDEX in the vertex for every row above the
    periodic region, multiplying the vertex set by 2C-3. Walking those rows once with weights
    and summing them away took width 7 from 11,458 states to 3,421 and width 8 from refused
    to 7,657. **Before believing a cap, look at what is in the state.** And when the model
    changes, the paper changes with it: iota stopped being an incidence vector, and the
    exponent stopped being the one the offset and the shift give -- `a(n) = iota^T M^(n-k)
    tau` is right only while the matrix carries the object from the very start.

20. **an engine that enumerates what it could generate.** Two builds in one day refused
    entries for cost, and neither cost was necessary. `transfer3` compared every row with
    every other row when the block condition is LINEAR and the successors can be solved for
    (six billion comparisons to twelve seconds, 30 entries). `transfer35` walked all
    A^(K*W) K-tuples of rows when the condition is local across columns and the valid tuples
    can be grown a column at a time (7,625,597,484,987 tuples to 29,303 valid ones, four
    seconds, 18 entries). **Ask of every build: is it testing candidates it could have
    constructed?** And test the rewrite against the old build on every parameter set the old
    one can still do -- both of these were verified identical as labelled graphs before they
    were used for anything.

21. **thirty standing sweeps on four cores, and every measurement taken through them.**
    `restart_all.sh` brings back about thirty background workers. They are useful, but the
    load average sat at **35 on 4 cores**, so a targeted sweep run alongside them gets about
    an eighth of one core. Every "stuck" build today was that: a run that asked 125 names in
    twenty minutes asked 100 in two once the standing sweeps were paused. Worse, it produced a
    WRONG DIAGNOSIS -- slow wall-clock was read as "the cost has moved to the annihilation
    test", and the measurement says otherwise: `annihilation timed out` is 1 case in 122 in
    the pool and 0 in both engine sweeps. **Pause the standing sweeps before timing anything,
    and restart them after.** Stop them by killing the runner shells in /tmp first, or they
    respawn their workers.

22. **a sweep that is killed is not a sweep that found nothing.** `sweep_engine` died twice
    at the same entry with no message and no tally: the kernel OOM-killed it at 13.9 GB,
    because a state-space cap is a promise about the number of STATES and `uniform.build`
    allocates toward it before it can count them. Three separate handoff notes said "there
    are more results in these engines, the sweep was cut off by its own time limit" -- and
    that was inferred from a truncated run, not measured. `sweep_engine` now sets
    RLIMIT_AS (MEMGB, default 6), which turns the runaway into a MemoryError that the
    per-entry handler already treats as "build failed", so the entry is skipped and the sweep
    continues. On the first complete run the answer was a clean null. **When a long run ends
    without its summary line, find out whether it was killed before believing anything about
    what it did not find.**

13. **a fix applied to one builder and not to its twin.** `qpbuild` was written because
    `unibuild` called every model a walk on a digraph; `gfonlybuild` says the same thing and
    was left alone for another 219 papers. When a defect is found in one place, ask which
    other place has the same code.

14. **writing a rebuild to the derived copy rather than the authority.** `rank.py` deletes
    `papers/` and rebuilds it from `papers-old-numbering/`. Two rebuild scripts wrote only to
    the ranked path, so their corrections would have been thrown away by the next ranking,
    silently, with each paper reverting to the text it was rewritten to fix.

15. **the standing sweep still testing for the conjectural word ON the line.** Defect 2 was
    fixed in the pool filter, in `pooltrim`, and in the live re-check, and never in
    `sweep_uni` -- which is the sweep every recent vein runs through. It hid almost nothing
    there only because the candidate list it reads had already been filtered properly; asked
    of every name instead, the same test refused 170 entries out of 205. When a defect is
    found, the question is not only which other file has the same code but which file was
    protected by an accident rather than by a fix.

16. **a rebuilt paper keeping the date the cache remembers.** `paperdates` keys its cache by
    A-number and verdict, which is what makes it survive a re-ranking, and it therefore never
    re-read a paper that had been recompiled: 99 papers rewritten on 13 September went on
    reporting the date of the text they had replaced. The entry now carries the PDF's size
    and a paper whose size changed is read again.

17. **installing a batch with the wrong installer.** `install_vein.py` takes the engine label
    as an ARGUMENT and applies it to every record in the list it is given, so pointing it at
    `uniall_hits.json` labelled 192 results with one vein's name -- and, worse, checked the
    withdrawal set under that name, so 60 results from the WITHDRAWN `ca2d` argument were
    installed. `integrate_rest.py` is the installer for that file: it reads each hit's own
    engine. Caught and reverted within the minute, but only because the count was wrong.

10. **taking a line with no conjectural word on it to be a statement of fact.** It is not.
    A `Conjectures from X: (Start) ... (End)' block holds bare formula lines and none of them
    says "conjecture". This cost 1,353 installed papers, withdrawn on 8 September 2026: they
    proved a conjectured recurrence from a generating function on the same entry and inside
    the same block, which is the same conjecture in another notation. **A premise may only be
    taken from `factlines.facts(e)`** — never from a word test on the line.

23. **a claim the entry does not contain is still a claim.** 192 entries say only `Empirical
    recurrence of order 42 (see link above)` and 36 say `Empirical polynomial of degree 26`;
    the statement is in a linked a-file. Every reader here looks at the entry's own text, so
    all 228 were refused with "no parsable recurrence" -- and every one has a name an engine
    already reads. The local clone *does* carry those files, as **Git LFS pointers**: opening
    one yields `version https://git-lfs.github.com/spec/v1` and looks like a file that simply
    is not a recurrence. Fetched from oeis.org they parse with `ratrec.parse_rec` unchanged.
    **When a refusal says a claim is unreadable, look at what the entry is pointing AT.**

24. **a fit checked where it was fitted certifies nothing, and a certificate that samples
    is not a certificate.** Three separate failures of the same shape, all in the Galebach
    chain. `galhull` fits the distance on a patch and reports "no leftovers" when its max
    reaches every point it was GIVEN -- and its supports were only validated against those
    same points; at radius 110 one such fit exceeded the true distance by one at 35 rim
    points. `galcert` then checked the whole-lattice conditions by sampling three points per
    cone: it could not tell whether the three lay in the cone (it returned None and the cone
    was skipped in silence), and condition (c) is a DISJUNCTION, which three points cannot
    settle. It certified A310511, which diverges at term 35. And `gallat.lattice` accepted a
    translation on the strength of signatures alone, in an embedding that was not the
    caller's: on Gal.4.142 the vector it returned is not a symmetry at 140 of 700 inner
    vertices. **Validate a fit on points it was not fitted on; decide a region condition on
    the region, not on samples of it; and check that a claimed symmetry is one.**

25. **a per-step alarm longer than the runner's own timeout is not a timeout.** `sweep_degree`
    sat 27 minutes on one degree-127 claim: its annihilation alarm was `8*BUDGET` = 3,200s
    inside a `timeout 1700`, so the runner killed the process first, the entry was never marked
    done, and every restart began on the same one. The same arithmetic was in `sweep_linkrec`
    (2,400s inside `timeout 1700`) and latent in `sweep_gfonly`. All three now take `ALARMCAP`
    (default 900) and use `min(BUDGET*k, ALARMCAP)`. **When you raise a BUDGET, check what the
    longest alarm derived from it becomes and compare it to the runner's timeout.** And when a
    sweep is stuck, do not silently mark the entry done -- let the fixed sweep time out and
    RECORD the reason, or the next person re-derives it from nothing.

## Where things stand

* **13,739 papers installed** over 13,335 entries and **165 distinct arguments**, as of the
  morning of 15 September 2026. 235 were withdrawn that day and 109 of those reinstated once the
  duplicate test was corrected (defect 29); 122 stay withdrawn as genuine duplicates. The 15 September round: 11 from six notation defects in
  `algf` (IDEAS §Z, §AC), 21 from rebuilding two candidate pools (§AE), 2 from a new argument
  for windowed maxima over a growing alphabet (§AF), 2 from reading a g.f. stated as a periodic
  continued fraction (`src/cfrac.py`, §AC). Two reader widenings were measured and are **null**
  and stay null (§AD): `from_name`'s "in powers of x", and `gfrec`'s implicit multiplication on
  the largest pool in the project. A reader fix pays only where the refusal OVERLAPS entries
  that state a claim.
* **Six apparent disproofs, six defects of mine, zero false conjectures.** The newest is
  A118447: `.../8R^5` means division by `8R^5`, and reading it left to right multiplies by
  `R^5`. The sweep recorded "the stated g.f. does not generate the DATA" against an entry whose
  own published terms the correct reading reproduces exactly. **A "the entry is wrong" verdict
  is a claim about the reader until it has been checked by hand.**
* Earlier count, kept for the record: 12,624 papers over 12,597 entries and 145 arguments on the
  evening of 13 September 2026. (Counts are re-derived by `src/sync_counts.py`, never typed by
  hand). 8 September: 1,353 withdrawn. 13 September: 184 withdrawn for the two-dimensional
  certificate, and 377 installed across seven new veins.
* **The generating-function-as-fact vein is null**, not 2,151. Asked correctly it proves 2.
  Everything held under it has been purged, and `WITHDRAWN.md` records what was taken back.
* Held: 85 generating-function results being re-derived under the corrected automaton bound,
  plus whatever the standing sweeps are finding now.
* `sweep_shard` with `TAG=np` over `deep-check/namepool.txt`: that pool is now exhausted and
  rebuilt (§AE, `namepool2.txt`, 1,727 entries). **`deep-check/capped.txt`, the 811 refused as
  `state space > cap`, is a STALE REFUSAL** -- asked one entry per process under a hard
  address-space limit, 23 of the first 30 build fine with 3 to 28 states against a cap of two
  million. The engines changed and the list did not. It is being re-asked by `src/caprun.sh`,
  one shard at 1.5 GB, and has proved nothing yet.
  The old note said "do not brute-force them", and the memory half of it is still true: even
  under `RLIMIT_AS`, four shards plus the standing runners exceed the container and the kernel
  picks victims. One shard at a time.
* **Every engine's degree bound S must be derived, not assumed.** `ca2dcount` set S = 24 from
  nothing and could certify nothing; it now refuses. `ca2d`'s bound was the one-dimensional
  figure and was too small; it is computed from the certificate's roots.
* **19,097 OEIS entries carry a conjectured recurrence with no linked proof.** 32,629 carry a
  conjecture of any recognised kind. That is the ceiling this project works against.

### defect 26 — a juxtaposed product after a division sign is the whole denominator

`(R-1)^2(R+1)(R+3)/8R^5` means division by `8R^5`. Writing the multiplication signs in left to
right gives `.../8*R**5`, which multiplies. This produced the sixth self-inflicted disproof
(above). `algf._denominator_run` parenthesises a juxtaposed run following `/`; only
juxtaposition with NO space is absorbed, so an explicit `*` keeps its usual meaning and
`x/2 - 1` is untouched. Regression over the rebuilt 989-entry pool: 988 unchanged, nothing
lost, and the one entry that motivated it the only difference.

### defect 27 — a sweep that reads only a CACHE reports a missing fetch as an entry's fault

`sweep_linkrec` reads a-files from `afiles/` and never fetches. Thirty-five new candidates were
all refused as "a-file absent or unparsed"; all thirty-five are on oeis.org and fetched without
trouble. A sweep whose premise lives outside the clone must say whether it looked.

### defect 28 — an order-type argument is not automatically gap-blind

`window` counts the image of a sliding-window statistic by classifying candidates by ORDER TYPE.
That is exact for max and min, whose greedy witness uses only the candidate's own values. It is
NOT exact for the median, whose witness can need a value strictly BETWEEN two of them: whether an
integer sits in that open interval is a fact about the gaps, which the order type does not
record. The four median entries whose published terms the (wrong) formula happened to reproduce
are withheld. **Reproducing thirty published terms is the standard of evidence the conjecture
already has; it is not a proof.**

### defect 29 — a vein that writes a SECOND paper must read the first one

`sweep_second` settles a further conjecture on an entry already proved. It excluded a generating
function that restates the proved recurrence in other notation and did not exclude a claim
IDENTICAL to the one the entry's existing paper was built from. 235 papers were installed and
all 235 withdrawn the same day: the second result was the first stated again.

The test that matters is with the PAPER, whose TeX is in `paper-sources/` and which quotes the
conjecture it settles — **and with the entry's OTHER papers, never with this vein's own.** Both
attempts got that wrong in opposite directions. The first compared against the lines other hits
files record and caught only 118, because it can only see a duplicate when the entry's paper came
from a vein that stored the line it used. The second compared against every paper on the entry,
including the second-conjecture paper that states the very claim being tested, so every record
was a duplicate of itself and all 235 were withdrawn. Re-run correctly: 122 genuine duplicates,
4 uncheckable, **109 withdrawn for nothing** and since reinstated. The vein settles at 376.

**A test that rejects more is not thereby a better test**, and the loose one hid the wrong one:
a test that says "duplicate" about everything agrees with the truth wherever the truth is
"duplicate".

And 368 installed papers have no stored source, so the comparison cannot run on them at all.
Refuse, do not assume: assuming would put the first result back as a second one for every one.

### defect 30 — a new hits file must have a name nothing else has

Installing the rebuilt closed-form pool, its results were written to `cfnew_hits.json`, a
filename that already existed, destroying sixteen records. It was noticed only because
`sweep_second` reads that file to find proved recurrences. Recovered from git and merged. The
glob that will later find a new hits file will find the collision too.

### defect 31 — a measurement that reports only at the end can be lost whole

The first census of the 2,211 printed its counts after the last entry, ran into its
ninety-minute timeout and produced nothing at all from ninety minutes of CPU. Write results
incrementally, to one file per shard, from the first entry.

### defect 32 — a directory that GitHub will not finish listing

`engine/src` reached 913 tracked files against GitHub's 1,000-entry listing cap. 525 of its 882
Python files were referenced by no import, no runner and no document — one-off scripts from past
rounds — and are now in `engine/attic/`, which leaves `src/` at 470. Nothing was deleted and
`git mv` kept the history.

**Two static scans were wrong before one was right**, and both mistakes are the same kind:

* `^\s*(?:import|from)\s+([a-z_0-9]+)` captures only the FIRST name of
  `import entry, phispec, phitex, phimeta`, so `phitex` looked unreferenced;
* `uniform.py` imports its 133 engines through `importlib.import_module(e)` over a list, which
  no import-statement scan sees at all.

82 files had to be brought back. The check that finally settled it reads every file's imports
with `ast` and resolves each name against `src/` or an installed package — and it must NOT be
done by importing, because a sweep module RUNS when imported and an import-based smoke test
starts the whole engine.

`engine/` itself is the largest tracked directory. It is tracked on purpose -- a container
restart wipes it, so a sweep's state only survives in git -- and every script opens those files
by bare name from `cwd=engine`, in 105 source files and with names assembled at run time, so
moving them is a real refactor and not a `git mv`.

Measured rather than assumed: **all 682 root JSON files are read by some current code path**, so
the directory cannot be thinned by deleting dead data. What it can be thinned of is SCRATCH:
**92 of the 101 files added on 15 September were one-off runs** -- a rebuilt pool asked once, an
experiment, a measurement -- whose every proved record was already in the canonical file beside
them. Untracked, taking the root from 716 to 624, and `engine/scratch/` is now in `.gitignore`
for the next one. **Only a STANDING sweep's state belongs in git.**

That buys the room; it does not remove the limit. What the limit actually costs is that
github.com truncates a directory LISTING at 1,000 entries — a browsing cosmetic, not a broken
clone — so the invasive move is not worth doing ahead of need. Watch the count; the growth is
almost entirely scratch, and scratch is now ignored.

### defect 33 — a pool built by the reader you are measuring cannot measure it

Three times now a widening has been regression-tested against a pool that the OLD reader built,
which by construction cannot contain an entry the old reader refused:

* `gfrec`'s implicit multiplication, measured over `deep-check/gfdef.txt` — 12 gained there, 5
  over the clone, and the pool number meant nothing;
* `closedform`'s `=`-chain, measured over `cfnew_cands.json` — 0 gained there, 12 over the clone;
* and the first census of the 2,211, which used `algf`'s own line-level conjectural test to
  decide what counted as a fact.

**Measure a reader widening against the CLONE, never against a pool.** The regression over the
pool is still worth running -- it is what proves nothing was LOST -- but it cannot say what was
gained.

### defect 34 — a REFUSAL list goes stale exactly like a candidate pool

Eleven candidate pools were rebuilt because a pool is a claim about the database made on the day
it was written (defect 1). A list of REFUSALS is the same kind of claim and was never treated as
one. `deep-check/capped.txt` records 811 entries as too big for the engines of the day; most of
them now build in milliseconds.

**Re-ask a refusal list when the thing that refused has changed.** The refusals worth re-asking
are the ones whose reason is about the MACHINE -- a cap, a budget, a timeout -- rather than about
the mathematics; "no engine reads the name" only changes when an engine is added, and the sweep
already re-asks that. And record the reason: a sweep that marks an entry done without saying why
leaves nothing to re-ask.

### defect 35 — a second copy of a filter is a second chance to get it wrong

`transfer40.build_merged` is `transfer17.build_pairfree`'s trick in another engine: merge the
predecessor rows into their effect on the future before the states exist, so a build that
refuses on `A^(K*W) > 8*cap` refuses only on `A^((K-1)*W)`. The merge itself is exact. What was
not exact was the seed filter copied alongside it: `build`'s `selfok` tests `kind == 'none'`
for equality and `kind == 'maxdiff'` for exceeding the bound, and the copy tested equality for
EVERY kind. For `maxdiff` that is wrong twice -- equal neighbouring sums differ by 0 and are
always allowed, while a pair over the bound is what has to go -- so the counts came out both
above and below the original's, 11 of the first 25 entries wrong.

The two errors pulling opposite ways is what made it hard to see: a single dropped filter would
have made every count larger, which reads as a missing condition. Both directions reads as a
broken merge, which is where I looked first and where nothing was wrong.

**When a new build is meant to count what an old build counts, test it against the old build
over the PARAMETER SPACE, not over the entries that happen to exist.** The entry-driven check
reached only `K=2` and three of the four kinds; the shapes that were never asked are the shapes
a copied filter can be wrong in. And the signal, when it came, was in the parameters and not in
the mathematics: every mismatch was `kind=maxdiff` with `nb > 1`, and every `maxdiff` entry with
`nb = 1` -- where the horizontal filter is vacuous -- agreed. A defect that sorts cleanly by a
parameter is a defect in the code that reads that parameter.

### defect 36 — a measurement that reports the machine's ceiling as the model's

The merged `transfer40` build loosens the a-priori refusal from `A^(K*W)` to `A^((K-1)*W)`, and
that opens 42 off-roster entries the bound had been refusing. Loosening a refusal is not
building a model, so the question that matters is how many of the 42 actually produce an
automaton under the standing cap of 2,000,000. The first run at that question printed `refused
at build` for the first ten and I was ready to write up that the merge is exact, verified, and
buys nothing.

It was run under a 1.5 GB address-space limit, and it printed `refused at build` for every
entry that did not hand back an automaton -- including the ones that raised `MemoryError`. Of
those first ten, A185806 was the 1.5 GB and not the cap. And the conclusion the ten supported
was wrong: A185863 builds at S=698048, comfortably inside a cap of two million.

**An out-of-memory and an over-the-cap are different facts and a measurement must never print
them as one word.** The limit exists so that one oversized shape fails instead of the whole run
-- that part was right, and `caprun.sh` sets 1.5 GB for a good reason. The error was letting the
limit's verdict wear the cap's name. A run whose whole purpose is to measure a threshold must
report anything that is not that threshold separately, or it measures the container.

The correction mattered less than what the corrected measurement then found, which is that the
whole question was aimed at the wrong population: 40 of the 42 entries the merged bound opens
carry no conjecture at all (IDEAS section AP). The cap was never what was stopping them.

**A refusal list counts entries, not opportunities.** `sweep_shard` writes `state space > cap`
against any entry whose NAME an engine parses, and one of its two cap points fires before the
recurrence is looked for at all. Of 2,311 off-roster capped entries, 1,056 carry a parsable
conjecture and 1,255 carry none -- and for `transfer40` it is 3 of 199. Before spending a round
on a population a sweep refused, ask of it the question the sweep asks last.

## When you create a new sharded sweep

Add its shard files to `.gitignore` **at the moment you create it**, and add its stem to
`merge_sharded.py`. Six workers rewriting their own progress file every few seconds leave the
tree dirty between every commit, and the merge is what keeps the tracked pair complete. This
has been caught by the stop hook four separate times.

## When the rotation is starving the vein that is producing

`restart_all.sh` starts every runner, and that is right: a sweep missing from it simply never
comes back after a container restart, which is how two veins sat idle for a day. But it starts
them all whether or not they have work, and on 20 September that cost real throughput:

* `merge_sharded.py` reported **0 new hits and 0 newly asked** on all eighteen stems;
* load average was **60** on four cores, with about twenty-five runners up;
* the two runners that were producing -- `rcaprun.sh` and the rewritten `caprun.sh`, between
  them responsible for three of that day's six installs -- had managed **8 entries** between
  them in half an hour.

Stopping the starved runners for one window gave the capped re-ask a full core immediately. The
next `restart_all.sh` brings them all back, which is the correct default; this is a note that
the trade-off exists and what it looked like when measured, not an argument for a smaller
rotation. **A runner with nothing left to do still takes its share of the CPU away from the
sweeps that do have work** -- the same sentence `restart_all.sh` already uses about the two
runners it dropped when their phases finished. It applies to more than two.

Before reaching for it, check: a stem reporting 0 newly asked is not necessarily finished, only
that it processed nothing since the last merge -- which under a load of 60 is what starvation
looks like too.

**Read defect 44 before trusting the paragraph above.** It called this a trade-off between
runners and declined to argue for a smaller rotation. Measured properly a day later it was not a
trade-off at all: thirteen of those runners had nothing to do and were relaunching themselves
thousands of times a minute to find that out. The diagnostic that settles it is the runner's own
log -- a sweep that examined nothing prints an empty result dict -- not the load average.

## Every session, first three commands

```
cd /home/user/Conjectures/engine && sh src/restart_all.sh     # brings every sweep back
python3 src/merge_sharded.py                                  # fold shard progress in
python3 src/status.py                                         # one line, where everything is
```

Background jobs only get CPU while a foreground command runs, so keep a useful foreground
command going. A source fix does NOT reach a process already running — restart it.

## Two merge scripts, and they do different things

`merge_shards.py` folds a sharded run into `uniall_hits.json`, which is what `build_new.py`
reads and therefore the only path to a paper. `merge_sharded.py` folds a sweep's own shards
into that sweep's own merged file. A TAG'd run of `sweep_shard` writes `shard<TAG>_hits_*.json`,
and whichever script runs first consumes them -- so results merged by `merge_sharded` land in
`shard<TAG>_hits.json` and reach nothing. Fold that file into `uniall_hits.json` by hand when
it happens; 21 results sat there this morning.

## Two installers, and they are not interchangeable

`integrate_rest.py` installs from `uniall_hits.json` and reads each hit's OWN engine, mapping it
through `integrate_rest_names.ENGNAME`. `install_vein.py` takes the engine label as an ARGUMENT
and stamps it on every record in whatever file it is given -- which is right for a vein with its
own hits file and catastrophic for the unified one: pointed at `uniall_hits.json` it labelled
192 results with one vein's name and, because it checks the withdrawal set under that name,
installed 60 results from the WITHDRAWN `ca2d` argument. See defect 17.

## Registering a new engine — every place, in order

Eight engines were written on 13 September and this list was reconstructed from memory each
time. It is six files:

1. `src/<engine>.py` with `parse_name`, `build(p, cap)`, `terms(b, N)`, `threshold(b, coeffs, order)`
2. `src/uniform.py` — add the name to the FRONT of `ENG` (it is a priority list) and to `IMAGE`
3. `src/integrate_rest_names.py` — the ENGNAME label the roster stores
4. `src/rank.py` — a TIER for that label (the file has ONE dict; check you did not add it twice)
5. the builder: a `WINDOW` entry in `src/unibuild.py` for a walk model, or a `SHORT` entry plus
   a `_model` branch in `src/qpbuild.py` and a `SPECIAL` entry in `src/build_new.py` for one
   that is not a walk
6. `src/build_new.py` `ENRICH` if the paper needs a field only `parse_name` knows (a divisor)

Then `sweep_engine.py <engine>`, `newlist.py`, `livenew.py`, `build_new.py <engine>`,
`integrate_rest.py`, and the ranking chain.

A vein with its OWN hits file (a claim that is not a recurrence) skips 2, 5 and 6, adds its file
to `newlist.py`'s glob list, and installs with `install_vein.py <prefix> <file> <label>`.

An engine whose model is exact only past some size supplies `terms_p` and `threshold_p`
alongside `terms`/`threshold`; `uniform` calls those instead, so the exceptional sizes are
counted on their own objects and the certified bound is raised to cover them. `transfer88` and
`denumerant` do this.

## A new engine is invisible until the candidate cache is rebuilt

`sweep_uni` reads `uni_cands.json`, and rebuilding it costs a quarter of an hour. `sweep_engine.py`
asks named engines about every name with no cache in between:

```
BUDGET=900 CAP=400000 python3 src/sweep_engine.py <engine> [<engine> ...]
```

Its results go into `uniall_hits.json` like the standing sweep's, so the rest of the pipeline is
unchanged. Rebuild `uni_cands.json` with `src/mkcands.py` when convenient, not before sweeping.

## Installing a batch

`newlist.py` → `livenew.py` (live re-check) → the vein's builder → `install_vein.py` →
`rank.py` → `makeindex.py` → `sync_sources.py` → `sync_counts.py` → `addtexfacts_all.py` →
`mkcomments.py` → `paperdates.py` → `makecomments_site.py` → commit and push to
`claude/code-setup-guidance-xit8fk`.

`rank.py`, `sync_sources.py` and `paperdates.py` refuse to run twice at once. Never start a
second copy.

### defect 37 — a maintenance script moved to `attic/` is a routine that fails silently

The daily ledger routine runs `python3 src/ledger_table.py`, which rebuilds the ledger's RESULTS
HELD table from `rank-map.json`. The `engine/src` split (defect 32) moved that script to
`attic/`, and every daily firing since has ended that step with `can't open file` — a line in a
log nobody was reading, because the routine's other steps kept working. The table had drifted
**25 rows**, which is precisely the failure its own docstring records it was written to prevent:
"it drifted to 456 rows once because it was appended to instead of rebuilt".

The script is back in `src/`. But the lesson is not about one file. **A tidy-up that moves a
file moves every path that names it, and the paths inside a scheduled routine are not in the
repository to be grepped.** When a script is relocated, the routines that call it must be
re-read, or the relocation silently turns a maintenance step into a no-op. Nothing fails loudly;
the thing just stops being done.

`attic/` is for code that is finished with. A script a routine calls every day is not.

### defect 38 — a comparison that cannot run must fail, never pass

The check that was to verify `transfer21.build_pairfree` against `transfer21.build` reported
**99 of 99 entries identical**. It had compared nothing. Its helper was

    def seq(b, p):
        try:
            return tuple(transfer21.terms(p, b, NT))
        except Exception as exc:
            return ('ERR', str(exc)[:50])

and `transfer21.terms` IS `transfer19.terms`, whose signature is `(adj, start, end, N)`. Called
as `(p, b, N)` it raises `TypeError` on every shape. Both sides therefore returned **the same
error tuple**, compared equal, and every shape was counted as agreeing. The louder the failure,
the cleaner the result looked.

**An exception must never be returned as the value being compared.** A harness that turns its
own breakage into a comparable object reports perfect agreement exactly when it is testing
nothing, and the report is indistinguishable from a real one. Let it raise, count it as a
failure of the comparison, and print it.

The second half is the same shape: the grid version of the check swallowed the `TypeError` in
an `except ... continue` with no print, so it produced no output at all and read as slow
progress on a hard problem. **A branch that gives up on an item must say so.** Silence is the
one thing a measurement must never mean.

Use `uniform.terms(en, p, b, N)` for this, not the engine's own `terms`: it is the entry point
the sweep uses, it knows which engines carry a scaling denominator, and getting the comparison
to go through the same door as production is most of what makes it worth running.

### defect 39 — catching an out-of-memory is not enough if the handler allocates

Defect 36 fixed `uniform.build` flattening `MemoryError` into `None`, and `sweep_shard` now
counts an out-of-memory as its own outcome instead of writing the entry into `uniall_caps.json`.
That was one phase of three.

A186012's re-ask at 7 GB died like this: the BUILD succeeded — `S=900096`, comfortably under the
cap of 2,000,000 — and the `MemoryError` came out of `lumpauto.lump` inside `uniform.threshold`,
two phases later, where the handler recorded it as **`terms timed out`**. Then `save()` raised
`MemoryError` in its turn, because the address space was still exhausted and writing a file
allocates. The shard died having written **no file at all**: no hits, no done, no caps, no oom,
no record that A186012 had ever been asked.

So: the build is not the only phase that can exhaust the limit, and a phase counter that names
a timeout is as wrong about an out-of-memory as a cap counter is. Every phase now catches
`MemoryError` separately. And the recovery path itself must not allocate — the automaton is
dropped and `gc.collect()` run *before* the save, and it must be the loop's own name `b` that
goes: handing the object to `save()` and deleting the parameter there frees nothing, because the
caller still holds the reference that matters.

**A failure the recorder cannot survive is a failure that leaves no trace at all**, which is
worse than the wrong label — the wrong label at least says an entry was asked.

### defect 40 — a timeout recorded as a settlement is a refusal with no label at all

`uniall_caps.json` at least says an entry was declined. `uniall_done.json` does not. `sweep_shard`
records a build timeout, a terms timeout, an annihilation timeout, a build failure and a terms
failure exactly as it records a genuine settlement — `done.add(a)`, plus a counter in `res` that
lives only as long as the process and is written to `shard<TAG>_why_<i>.json`, which is
overwritten from scratch by the next process. So an entry that merely ran out of `BUDGET` is
marked done **forever**, and nothing anywhere distinguishes it from an entry the sweep actually
decided.

Measured: of 3,579 entries marked done and off-roster, 3,546 are legitimately finished — capped,
a hit, carrying no parsable conjecture, not open, or belonging to a withdrawn engine. The
residue is **33**. That is small and should be reported as small. But two of the first three of
them proved on being re-asked at `BUDGET=1800` instead of the usual 40–600: **A221621**
(`permrow`, S=720) and **A244181** (`transfer96`, S=4676, order 30). Two in three is the densest
yield of the day.

The general form, and it is the same as defect 34 one level down: **a list of what has been
DONE is a refusal list too, if anything that is not a decision can put an entry on it.** The caps
file was three different refusals wearing one label (IDEAS AP); the done file is a refusal
wearing none. When you next add a `continue` to a sweep loop, ask what the entry's row will say
afterwards, and whether a later reader could tell that row from a settled one.

What a sweep writes down when it gives up is the only thing standing between "not proved" and
"not asked".

**And the measurement bears that out from the other side.** `sweep_ordwhole` is the one sweep
that records a per-entry reason -- `note(k, a)` writes `why[a] = k` beside the counter -- and
`sweep_linkrec` does the same with `whyent`. Every entry those two named as a timeout was found
and re-asked later: of the 20 such entries in the whole repository, **16 are proved and
installed** and the other 4 carry no parsable conjecture. Nothing sat lost.

`sweep_shard`, which recorded only a counter, lost 33. So the two behaviours can be compared
directly, and the difference is not hygiene: it is the difference between an entry that gets
asked again and one that does not exist as far as any later run can tell. Eleven sweeps in this
repository mark an entry done on a timeout; two of them write down which entry, and those two
are the two with nothing to recover.

Copy `note()`. It is four lines.

### defect 41 — a refusal list that is never retracted becomes the thing it replaced

`uniall_oom.json` was added this round so that an entry the CONTAINER refused would stop being
recorded in `uniall_caps.json` as a model too big for the cap. Within hours it had the same
fault as the file it was meant to improve on: **six of its first thirty rows were entries that
had since been proved and installed.** An entry that ran out of memory on one pass and built on
the next was still listed as one the machine cannot do.

A refusal list needs a way OUT as well as a way in. `sweep_shard` now drops the row when the
entry proves, and `merge_shards` prunes anything the roster has settled on every fold and
deletes the file when it empties. Neither is clever; both were simply absent, which is why
`uniall_caps.json` accumulated three kinds of wrong for months without anyone reading it back.

**The general rule: every row a sweep writes about an entry needs the condition under which it
is removed, decided at the moment the row is invented.** A row with no retirement condition is
not a record, it is a rumour — and it will be read later by something that cannot tell the
difference.

That is three files now with the same shape: `uniall_caps.json` (wrote the wrong reason),
`uniall_done.json` (wrote no reason), `uniall_oom.json` (wrote the right reason and never took
it back).

## The container restarts about once an hour

Measured on 20 September: four restarts between 16:00 and 20:00 UTC, each landing near the top
of the hour, each reading `up 0 min` on the next check. A restart wipes `/tmp` and every process
in it.

This is why `restart_all.sh` is the shape it is, and it is worth stating plainly because two
hours were lost today misreading its consequences:

* **A runner that vanished is much more likely to have been restarted away than killed.** Both
  times the out-of-memory sweep disappeared, the container had restarted; I diagnosed the
  kernel's OOM killer, lowered a memory limit on that reasoning, and was wrong twice.
  Check `uptime` FIRST when a background job is missing.
* **Quiescing the rotation removes your own recovery.** `restart_all.sh` is what brings a runner
  back, so stopping it to free memory for one experiment means the next restart ends that
  experiment silently. A quiesced machine needs its own way back.
* **No sweep gets more than about an hour of wall time.** An experiment that needs several hours
  of one process does not fit this container and should be designed around, not simply started
  and hoped for. Entries whose single build takes 20 minutes get three or four attempts a day at
  best, which is why `uniall_oom.json` is read at 3 of 41 after an afternoon on it.

### defect 42 — a runner switched off on the belief that it had finished

`restart_all.sh` carried the line *"p5last.sh and p12run.sh were dropped once Phases 5 and 12
finished: a runner with nothing left to do still takes its share of the CPU away from the sweeps
that do have work."* The reasoning is right and the premise was false for one of the two.

**Phase 5 had not finished.** It is the deep check that rebuilds each model in a fresh process
and re-verifies, against no cached verdict, that the model reproduces every published term, that
the stated recurrence annihilates it at the stated threshold, and that the threshold is exact.
Its `ok` count has stood at **3,847 since 8 September**. Its total is derived — every non-FAILS
hit in `uniall_hits.json` carrying coeffs and an engine — so it GROWS with every sweep: 5,942
this morning, 5,971 tonight. The status line has read `left 2,100` all day and nobody, including
me for sixteen hours, read it as a number that was supposed to go down.

So 2,100 results have never had their mathematics recomputed from cold. That is not a search for
new results; it is whether the ones already counted are right, which matters more than any vein.
Back in the rotation as `p5run.sh`.

**The shape is the day's, one level up.** A refusal list nobody re-reads goes stale (defect 34);
a done-list that cannot distinguish a timeout from an answer hides work (40); a refusal list
never retracted becomes a rumour (41). This is the same error applied to a PROCESS rather than a
file: something was recorded as finished, and the machinery that would have shown otherwise was
precisely the thing switched off. **Before retiring a runner, read the counter it feeds — and
check whether that counter's denominator can grow.**

### defect 43 — a skip in a verification is not a pass, and its skip list goes stale like any other

Phase 5 rebuilds each model from cold and re-verifies the paper's claim against no cached
verdict. When it cannot rebuild — over the cap, timed out, raised — it records a SKIP. Two
things follow that nobody had put together:

**A skip is subtracted from `left`.** `status.py` computes `left = tot - ok - bad - sk`, so a
result whose mathematics was never re-checked reads as resolved. The line said `skip 32` all day
and the 32 were not verified, not verified-and-fine.

**And the skip list is permanent.** A comment in `dc_phase5.skip` records a real bug — a skipped
entry was retried and recounted on every round, so "179 rebuild over the cap" was 179 skip
EVENTS, not 179 entries — and the fix was a `seen` set. Correct for the counting, and it turned
the skip list into an exclusion nothing revisits.

So the 31 entries recorded as "rebuild over the cap" were recorded **on 8 September**, by the
engines of that date. Four of them are results installed TODAY, and all four were rebuilt by hand
at `P5CAP=8,000,000`:

| | | |
|---|---|---:|
| A185863 | `transfer40` | S = 698,048 |
| A186955 | `transfer40` | S = 173,934 |
| A184710 | `latpoly` | S = 353 |
| A185900 | `transfer19` | S = 4,088 |

Every one builds without difficulty. **A184710 needs 353 states against a cap of eight
million** — it was never within four orders of magnitude of the limit it was recorded as
exceeding. What could not build the `transfer40` pair was that engine's unmerged construction,
replaced this morning; what could not build the others was whatever stood on 8 September. **The check was the faulty side, exactly as its own docstring warns it usually is.**

46 machine-reason skips cleared, from all three shards, so they are asked again by the engines
that exist now. `skip 32` became `skip 0`.

**The rule, which is defect 34 in its fourth costume today: a refusal recorded for a reason
about the MACHINE must carry an expiry, and the natural expiry is "the engine changed".** Caps,
timeouts, out-of-memory and rebuild failures are all statements about the day they were made.
Only a refusal about the MATHEMATICS — no conjecture in the entry, not open, engine withdrawn —
is safe to keep forever.

### defect 44 — a runner loop with no backoff turns a read-out vein into a spin

The section "When the rotation is starving the vein that is producing" recorded, on 20
September, a load average of 60 on four cores and the two producing runners managing eight
entries in half an hour. It read that as a trade-off between runners and closed by saying it was
"not an argument for a smaller rotation". That reading was wrong, and the measurement that shows
it was available the whole time: **the logs.**

A container restart at 02:00 on 21 September wiped `/tmp`. Five minutes later:

| log | lines | of which the empty result dict |
|---|---:|---:|
| `/tmp/snd_0.log` | 1568 | 1431 |
| `/tmp/tab_0.log` | 1289 | 958 |
| `/tmp/mfcf_0.log` | 750 | 738 |
| `/tmp/eca_0.log` | 959 | 435 |
| `/tmp/np2_0.log` | 178 | 170 |

`sweep_shard` ends with `print(dict(res))`, and `res` is a `Counter`, so `{}` means it examined
**no entries at all** — every candidate was already in this shard's own `done` file. Thirteen
veins were in that state and every one of their runner loops relaunched immediately on exit.
About twenty-five thousand no-op launches in five minutes, each a fresh interpreter parsing
`uni_cands.json`, `uniall_done.json` (11,660), `uniall_hits.json` (5,971) and
`paper-engines.json` (13,364) in order to discover it had nothing to do.

Sixty-eight Python processes were doing this on four cores. The cost fell on the one job with
real work left: `deep-check/phase5-[012].json` were last written at **01:05** and the container
restarted at **02:00** — three Phase 5 shards, fifty-five minutes, not one entry finished.
Stopping the read-out runners for four minutes was the whole experiment: the three shard states
were written again at 02:04, 02:05 and 02:07.

**The fix is the clock, not the bookkeeping.** A round that finds work takes minutes — `BUDGET`
alone is 90 seconds or more — so a round that returns in seconds found nothing. That test needs
nothing from the sweep, which is why it covers `sweep_gf`, `sweep_table`, `ordtails`,
`sweep_cf`, `zeilb_run` and the rest and not just `sweep_shard`. Twenty-eight runners now break
out of their loop on a round under a minute; `forever.sh` sleeps 300 instead, because it must
not stop and is the only thing that rebuilds the pools from the clone. Measured after:
**68 processes → 17, and 23 of 30 runners stopped themselves.**

Breaking out is not retirement. `restart_all.sh` relaunches everything an hour later, which is
exactly when a changed engine could have reopened a vein — that is how the `transfer21` swap
reopened 78 capped entries and bought five results the day before.

Two smaller things fell out of it:

* `restart_all.sh` copied a runner into `/tmp` only when `/tmp/<name>.sh` did not exist, so an
  **edited runner did not take effect until the next container restart**. The copy now happens
  inside the not-running guard, which refreshes the text and still never rewrites a script under
  a live `/bin/sh` — that shell reads its script lazily by byte offset and would resume at
  whatever landed there.
* `dc_phase5.py` now writes `deep-check/phase5-inflight-<shard>.json` naming the entry and phase
  **before** the work starts, as `sweep_shard` does (defect 39). Its absence was itself the
  clue: the running shards had started at 01:59:19 and the edited source was written at
  01:59:57, so they were executing the old code. **A source fix does not reach a running
  process** — after editing anything a runner imports, restart the runner.

The marker earned itself in its first minute. All three shards were inside `rebuild` on
A204406, A203739 and A204416 — three of the 29 entries installed on 20 September, which is the
newest-first ordering working as intended and also why the `ok` count moves slowly: newest-first
is most-expensive-first, because today's installs came from the capped list and are large by
construction.

Two more came out of watching the fix land, and both are about the same thing — a change that
looks local is not:

* **A new file beside an existing glob is a change to every reader of that glob.** The marker
  was first called `phase5-inflight-<shard>.json`, and `status.py` and `dc_phase5._summary`
  both glob `phase5-*.json` for the shard states. `status.py` died on `KeyError: 'ok'` within a
  minute, and `_summary` — which is how one shard learns what the other two have settled —
  would have read the marker as a fourth shard. It is `p5-inflight-<shard>.json` now.
* **`restart_all.sh`'s guard matched a substring.** `ps -eo args | grep -q "[/]tmp/$1"` counts
  any process whose command line merely MENTIONS the path, so a shell that happened to contain
  the words `/tmp/p5run.sh` made the guard report p5run.sh as already running, and
  `restart_all.sh` silently skipped the one runner the machine had just been cleared for. A
  skipped runner and a healthy one print exactly the same nothing. The guard is anchored to
  `^(/bin/)?sh /tmp/<name>( |$)` now, which is the form `start()` actually launches, and both
  directions were checked — a running name is seen, an absent one is not.

And `dc_phase5.save()` was writing with `json.dump(open(OUT, 'w'))`, which truncates the file
for the whole of the write. It runs after every entry, so a reader arriving inside that window
sees a half-written object; the file was well-formed a second later. It uses `atomicjson` now,
like every other progress file in the project. A torn read of a progress file is worse than a
crash, because it reads as data loss.

### defect 45 — a withdrawal blocks the argument, and not the arguments resting on it

`merge_sharded.py` reported `snd: 175 new hits (419 total)` and none of them were visible to the
installer. Two separate reasons, and the second is the one that matters.

**The file name.** `build_second.py` read `snd_all_hits.json`, which stopped at 203 records on
15 September; `merge_sharded.py` has written the merged file as `snd_hits.json` since the vein
was sharded, and it holds 419. The installer and the merge disagreed about a name, so 138
settled results sat held. `newlist.py` does not list either file, so `status.py` never counted
them either. Both now read `snd_hits.json`.

**What the 138 turned out to be.** Nothing like 138 results:

| | |
|---:|---|
| 138 | settled and not papered |
| 42 | premise entry not on the roster at all |
| 93 | already WITHDRAWN as second-conjecture papers, correctly kept out by `withdrawnset` |
| **3** | actually new |
| **0** | installed |

The 93 are `withdrawnset` working exactly as designed, and the honest reading of "138 held
results" is 3. Counting the file would have padded the roster by 135.

**The 42 are the defect.** Every one carries `premise_kind: "proved in this project"`, and
there is no `coeffs` record anywhere in the project that supports any of them — not in any
`*_hits*.json`, not in `uniall_hits.json`, not in `ordtails.json`. Six are named in
WITHDRAWN.md, under `gf-conjecture`. `withdrawnset.blocked(a, 'second-conjecture')` returns
False for all six, and it is right to: **a withdrawal blocks the ARGUMENT, not the entry**, which
is correct for a second engine settling the same entry independently and exactly wrong for an
argument that takes the withdrawn one as its premise. `sweep_second` copied the premise's
coefficients into its hit and kept no reference to where they came from, so when the premise was
withdrawn nothing connected the two. A copied fact cannot be re-checked; a named one can, so a
hit now records `premise_from` (file and engine) and `premise_on_roster` beside it, and
`build_second` refuses any entry that is not on the roster. An entry on the roster is the one
condition checkable at build time that cannot go stale in silence.

`livenew.py` also needed fixing to check these at all. Its state file is a cache — an entry
already in `kept` is skipped and never re-fetched — and every second-conjecture target is on the
roster already, so all 96 were "confirmed" from the day their FIRST paper was installed. A
verdict about the first conjecture says nothing about whether the second line is still
unsettled. `LIVEOUT` now points the check at a state file of its own; re-run that way, all 96
came back kept, 0 dropped, 0 flagged, on a genuine fetch.

### The 13 September withdrawal was short by four, and eighty more are unresolved

The three genuinely new second conjectures rested on A270934, A273334 and A277560. The first two
are `gf-conjecture` papers on the active-cell count of a two-dimensional automaton — the exact
class withdrawn on 13 September for "the active-cell count of a two-dimensional automaton has no
proved generating function, so the degree bound the argument needs does not exist". That pass
took five and left four: **A270934, A273334, A273447, A273781**, the last two being partial sums
of the same quantity. Checked one at a time against their own entries, all four are
indistinguishable from the five:

* every formula line sits inside one `Conjectures from _Colin Barker_: (Start)` block, so the
  generating function the argument consumes is the conjecture itself in another notation;
* no `coeffs` record for them exists in any hits file, so nothing in this project models them;
* they were built in the same run — builds 11677, 11680, 11682, 11684 against the withdrawn
  11676, 11678, 11679, 11681, 11683.

Withdrawn. **Roster 13,768 → 13,764.** Nothing was installed on their second conjectures.

**What is left open, and it is not small.** 84 roster papers carry engine `gf-conjecture` on
this automaton family, and all 84 rest on a generating function the entry states only inside a
conjecture block — 224 x-axis and diagonal-representation papers under the two engines were
checked and **not one** states a g.f. as fact. The four withdrawn tonight are the ones where the
class was already settled. The other 80 are a different question, because the `ca2d` vein
(engine `automaton-axis`, 144 papers on the same family) builds an actual model of the axis, and
an x-axis entry with a real ca2d proof is not in the position the active-cell counts are in. It
may be sound, it may be a duplicate of the ca2d paper, or it may be the same defect at
twenty times the size. **A277560 is one of the 80, which is why its second conjecture was not
installed either.** This wants its own pass, entry by entry, asking of each: is there a model
for this sequence anywhere in the project, or is the generating function the argument consumes
the very thing being conjectured?
