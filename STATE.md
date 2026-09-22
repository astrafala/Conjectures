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

## The container restarts on no schedule at all — sometimes every eleven minutes

Measured on 20 September: four restarts between 16:00 and 20:00 UTC, each landing near the top
of the hour, which is where the old heading's "about once an hour" came from. **21 September
disproved the regularity**: restarts at 01:58, 03:48, 03:59 and 04:27 — a 110-minute gap
followed by an 11-minute one and a 28-minute one. A restart wipes `/tmp` and every process in
it.

**Nothing may be planned around the interval.** Two consequences, both paid for tonight:

* a budget longer than the shortest gap cannot be relied on to complete. `t17big.sh` allows
  2,400 seconds per entry, and an 11-minute container will never finish one — it will re-ask
  the same entry for ever, making no progress and recording nothing. That is not a reason to
  cut the budget (the work genuinely takes that long) but it is a reason to expect the large
  shapes to be settled only in a long generation, and to say so rather than read the silence as
  a refusal.
* anything that accumulates must persist after every step, not at the end. Two attempts at the
  `transfer21` verification were lost whole this way before `t21check.py` was written to record
  each entry as it goes; `sweep_shard` and `dc_phase5` already save per entry.

And a restart is not a refusal — see defect 47, which is what a restart used to be recorded as.

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

### The 13 September withdrawal was short by four, and the eighty it did not touch are sound

The three genuinely new second conjectures rested on A270934, A273334 and A277560. The first two
are `gf-conjecture` papers on the active-cell count of a two-dimensional automaton — the exact
class withdrawn on 13 September for "the active-cell count of a two-dimensional automaton has no
proved generating function, so the degree bound the argument needs does not exist". That pass
took five and left four: **A270934, A273334, A273447, A273781**, the last two being partial sums
of the same quantity. Checked one at a time against their own entries, all four are
indistinguishable from the five:

* every formula line sits inside one `Conjectures from _Colin Barker_: (Start)` block, so the
  generating function the argument consumes is the conjecture itself in another notation;
* each paper names the same S=24 `ca2dcount` model and the same transfer-matrix argument — a
  strip of consecutive rows taken as the state of a finite automaton — which is what a
  fixed-width array count licenses and what an automaton growing in every direction does not
  (`build/gfoA270934/p.tex` says it in the abstract: "counts arrays of a fixed width under a
  local condition", which A270934 is not);
* they were built in the same run — builds 11677, 11680, 11682, 11684 against the withdrawn
  11676, 11678, 11679, 11681, 11683.

Withdrawn. **Roster 13,768 → 13,764.** Nothing was installed on their second conjectures.

**The other eighty are sound, and asking properly is what showed it.** 84 roster papers carried
engine `gf-conjecture` on this automaton family, and all 84 rest on a generating function the
entry states only inside a conjecture block — of 224 x-axis and diagonal papers checked, **not
one** states a g.f. as fact. That looked like the same defect at twenty times the size. It is
not, and the distinction is the model, not the entry's wording:

| model the paper is built on | what it licenses | papers |
|---|---|---:|
| `ca2dcount` — the active-cell COUNT | nothing: no bounded strip exists, so no degree bound | 0 on the roster |
| `ca2d` — the x-axis or diagonal at stage n | a finite row, a real automaton, a real degree bound | 80 |

Every one of the 80 rests on a `ca2d` axis model. **Zero are at risk**, and no roster paper
anywhere still rests on a `ca2dcount` model — the 13 September pass was complete on its own
terms, and what it missed was four papers with no surviving record at all.

**Two method errors of mine, worth more than the result.** The first query for "does this
project model the sequence" looked for a `coeffs` key. A generating-function record does not
have one — it carries `degnum` and `degden` — so the query answered "nothing models these 12"
about twelve entries whose records say `engine: ca2d, S: 8` in plain sight. **Ask what shape the
record actually has before asking whether it exists.** And the four withdrawn have no surviving
record of either kind, which says only that theirs were pruned: an absent record is not evidence
of an absent proof, and the thing that settled it was reading the paper, which names its model
in its own abstract.

**A277560 is one of the 80, so its premise holds and its second conjecture is installable.**

**A corollary, and it is the reason the log is the right diagnostic.** After the backoff stopped
`precrun.sh`, its own `prec_done*.json` said 486 of its 989 entries were still unasked — which
would make the stop a bug. It is not: `sweep_prec` line 107 is
`if a in done or a in roster or <not my shard>: continue`, a bare `continue` with no note and no
`done.add`, so all 486 are entries that already have a paper and are skipped, unrecorded, on
every pass for ever. **A done file measures what a sweep finished, not what it has left**, because
a refusal that costs nothing is never written down — the same shape as defect 40, where a
timeout was recorded as a settlement. Checked: 486 of 486 are on the roster, 0 genuinely
unasked. The empty result dict in the log is the only statement either way that is actually
true.

### defect 46 — a zero produced by a swallowed exception is not a measurement

Twice in one night, and the second time within an hour of writing up the first:

* the query "does this project model this sequence" looked for a `coeffs` key. A
  generating-function record has no `coeffs`; it carries `degnum` and `degden`. The query
  reported **0 models for 12 entries** whose records read `engine: ca2d, S: 8` in plain sight,
  and that zero was one step from withdrawing eighty sound papers.
* the query "how many capped `transfer17` entries carry a conjecture" called
  `conjlines.recs(e)`. There is no such function — it is `conjlines.claims` — and the call sat
  inside `try: ... except Exception: pass`, so every one of the 118 raised `AttributeError` and
  the answer came back **0 of 118**. IDEAS AP.3 had recorded 82 six days earlier. Asked
  correctly: **80**.

A zero is the cheapest wrong answer to produce and the most expensive to act on, because it
reads as a finished search. Two habits, and neither costs anything:

1. **Never wrap a probe in a bare `except Exception: pass`.** The except is there for the entry
   that genuinely cannot be read; it silently absorbs a typo in the function name just as
   willingly. Catch what the data can do, let a `NameError` or an `AttributeError` out.
2. **Before believing a zero, make the same query return a non-zero on a case you already
   know.** Either query above would have failed that test in one line.

The same shape as defect 38, where a harness returned its own `TypeError` as the compared value
and 99 entries "matched". A measurement that cannot fail is not a measurement.

### The capped `transfer17` population, and defect 46 a third time

IDEAS AP.5 listed `transfer17` among the engines worth a merged build with a parenthesis: "82 —
it already has `build_pairfree`, so the question there is why those 82 still cap". Asked:

* 118 off-roster capped `transfer17` entries, **80** of them carrying a parsable conjectured
  recurrence (AP.3 said 82; the roster has grown since);
* eight of eight **cap at 2,000,000**, taking 12–30 seconds each. The time-to-cap scaling with
  the cap is the tell: this is construction reaching the limit, not the a-priori
  `(alpha+1)^(2W) > cap` refusal, which is instant and which `build_pairfree` does not have;
* **79 of the 80 had only ever been asked at 2,000,000.** Not because anything judged that the
  right cap for them — because it is the cap every sweep happened to use;
* **A204606 (alpha=2, W=9) builds at 8,000,000**, in about seven minutes and 1.8 GB.

`t17run.sh` asks all 80 at 8,000,000. This is the standing habit again: the population was
refused by a number in a shell script, not by mathematics, and nothing had re-asked it.

**Defect 46 a third time, in one night.** The probe that found A204606 printed
`TypeError: object of type 'int' has no len()` after 428 seconds, because the reporting line
called `len(b[3])` where `b[3]` is already the state count. The build had SUCCEEDED. The first
two instances swallowed a query; this one swallowed the answer, which is worse — a failed query
returns a suspicious zero, and this returned a plausible-looking error that reads as "the build
did not work". **Widen the rule: a probe must not be able to turn a result into an error
message.** Print the raw object before formatting it, or format inside its own `try`.

### A further exact quotient for `transfer17`

Reading `build_pairfree` to answer the question above turned up a merge it misses. Its state is
`(s, C)` — the current row, and the tuple of `K` window masks the pair (previous row, `s`)
imposes — and its loop is

    for t in follows(C):
        row.append(sid((t, constraint(s, t))))

`C` decides which `t` are legal. The successor uses `s` and `t` only: **`constraint` never looks
at `C`**. So two states `(s, C1)` and `(s, C2)` with `follows(C1) == follows(C2)` have the same
outgoing labels and, label by label, literally the same successor. They are indistinguishable,
and merging them is exact. Many distinct mask tuples admit the same set of lines, and that
saving is invisible while the key is the mask tuple.

`transfer17.build_lineset` does it. Verified against `build_pairfree` on 96 shapes — both walks,
alpha 1 and 2, W 3 to 5, four predicates, two thresholds — **0 mismatches, none skipped**, and
**44 of the 96 have different state counts**, which is what shows the comparison ran rather than
comparing an object with itself (defect 38). 32.6% fewer states in total, and the reduction
grows with `W`, which is where the capped entries are: `alpha=2 W=5 sum<=2` goes 1152 → 386.

**Not dispatched from `uniform.build` yet, deliberately.** That one line touches every
`transfer17` entry on the roster, and the missing number is build TIME on entries that already
succeed. A third fewer states bought at triple the time is a regression wearing an improvement's
clothes. The engine stands on its verification; the dispatch waits for that measurement.

### The in-flight recovery cannot tell a kill from a refusal

The marker from defect 39 worked exactly as designed within minutes of the `transfer17` vein
starting: restarting its three shards to pick up a source change left

    previous shard died on A204606 in phase build at MEMGB=5.0

in each log, which is the whole point — an entry that killed its shard is named instead of
vanishing. But the recovery block then does `done.add(a)` and writes the entry into the shard's
out-of-memory file, and **those three shards died because I killed them**, not because the
machine refused anything. A204606 is the entry that had just been PROVED to build at 8,000,000.

So a deliberate restart retires whatever each shard happened to be inside, as an out-of-memory
that never happened. Retracted by hand here (three `done` files, three `oom` files). The general
rule is the one this project keeps relearning in new costumes: **a refusal recorded for a reason
about the machine must carry an expiry, and "the engine changed" is the natural one** — which is
already the defect-34 rule and already implemented for Phase 5's skips via the engine stamp.
`sweep_shard`'s oom file has no such stamp. Until it does, after killing a runner on purpose,
check its `oom` file and its `done` files for whatever was in flight.

### Never start a runner by hand; `restart_all.sh` is the only safe way to start one

Within twenty minutes of the `transfer17` vein opening there were **two `t17run.sh` shells
running at once**, six `sweep_shard` processes on TAG `t17c`, two of them writing each of
`shardt17c_hits_0/1/2.json`. That is the precise failure `restart_all.sh`'s `running()` guard
exists to prevent, and the comment at the top of `sweep_shard.py` records what it costs: two
writers on one hits file destroy each other's results.

The cause was not the guard. It was that I started the runner myself —
`nohup /bin/sh /tmp/t17run.sh &` — after `restart_all.sh` had already started one, and a manual
start consults no guard at all. Nothing detected it; I found it only by reading `ps` for an
unrelated reason, and by then two generations had been running for seven minutes.

**The rule: to start a runner, run `restart_all.sh`.** It starts only what is not already
running, it refreshes the `/tmp` copy while doing so, and it is the single place that knows
what "already running" means. Adding a runner to its list and calling it is one line and cannot
produce a second generation. Starting one by hand is never necessary and has no safe form.

Nothing was lost this time: `atomicjson` kept every file parseable, `shardt17c_hits_1.json`
still held the vein's first proof (A251842), and the two `done` files had not diverged. That is
luck, not design — the same luck the `forever.sh` header already records from the time its loop
reached 470 copies of one sweep.

### defect 47 — a container restart was being recorded as a refusal, once per restart

The in-flight marker (defect 39) names the entry a shard died inside, and the recovery block
then retires that entry: `oom[anum] = MEMGB` and `done.add(anum)`. That is right when the entry
killed the shard and wrong when something else did — and the commonest something else is the
container restarting, which kills every shard exactly as the OOM killer does.

It restarted **twice in eleven minutes** on 21 September, after a 110-minute stretch, so the
cadence is irregular and cannot be planned around. Every restart retired one entry per shard as
an out-of-memory that never happened. `t17big.sh` asks the 25 entries at alpha=3 W=9, tens of
minutes each: left alone, the restarts would have retired its entire list without a single
genuine refusal, and the list would have read as "this shape is beyond the machine" when
nothing of the sort had been shown.

**The distinction is free.** `/proc/uptime` only increases within one boot, so a marker whose
recorded uptime is GREATER than the machine's current uptime was written before a reboot. The
marker now carries `boot`, and on recovery:

* marker's uptime > current uptime → the restart killed it. Clear the marker, record nothing,
  let the entry be selected again on this pass.
* otherwise → as before: name it, record the memory, mark it done, so the next shard does not
  walk into the same wall for ever.

Both branches were tested with planted markers before this was trusted — a recovery path only
runs after a crash, which is exactly the kind of code that goes untested until it matters. The
reboot branch recorded nothing and marked nothing done; the death branch recorded both.

**And the first version of it was wrong, in two ways, both caught in production within an
hour.**

It stamped UPTIME and asked whether the marker's number was larger than the current one,
reasoning that uptime only increases within a boot. True, and still wrong: a marker written 10
seconds into the previous boot, read 20 seconds into the new one, carries the SMALLER number and
reads as a genuine death. A252303 and A252147 were killed by the 05:47 restart and retired as
refusals by exactly that. **The stable quantity is BOOT TIME — `time.time()` minus uptime —
which is constant within a boot and needs no reasoning about which number is bigger.** Two of
the three shards did classify their restarts correctly, which is what makes this kind of bug
expensive: it works most of the time.

The second way was worse and is defect 46 for the fourth time, in code written while documenting
defect 46. The `import time` was never added, `time.time()` raised `NameError` inside `_boot()`,
and `except Exception: return -1` turned that into a sentinel — so `_boot()` returned -1 for
every call, `abs(-1 - anything) > 5` held always, and every marker read as a container restart,
genuine deaths included. The test caught it only because it asserted the DEATH branch as well as
the reboot branch. **A guard clause that returns a sentinel on `Exception` will hide the bug you
just introduced.** It catches `OSError` now, which is the only failure reading `/proc` that is
data rather than a mistake.

One transition artifact, benign and worth knowing: a marker written by the uptime version
carries a small number, and the boot-time version compares it against a Unix timestamp, so every
such marker reads as a container restart. That is the SAFE direction — the entry is re-asked
rather than retired — and it clears itself as soon as each shard writes a new marker. **If this
stamp is ever changed again, check which way an unrecognised value falls.** A format change that
defaults to "genuine refusal" would retire an entry per shard, silently.

This also retires the hand-rule written a few hours earlier ("after killing a runner, check its
oom and done files for whatever was in flight") for the restart case, though not for a
deliberate `kill`, which leaves uptime unchanged and is still indistinguishable from a real
refusal.

### The transfer17 vein, first read: five proofs and a memory wall

14 of the 55 small-shape entries asked, and the shape of the answer is already clear:

| | |
|---:|---|
| 5 | proved and installed |
| 7 | exceeded MEMGB=5 at cap 8,000,000 |
| 1 | state space over 8,000,000 even merged |

The seven are W=7 and W=8 — genuine machine refusals under the current settings, not container
restarts (defect 47's stamp distinguishes them now), and they are in `uniall_oom.json` at 5.0,
so they stay re-askable at a limit chosen for them. Raising that limit is a real trade rather
than a free win: three shards at 5 GB already claim 15 GB on a 15 GB machine, so more memory
means fewer shards, and the vein is currently reading faster than it is refusing.

The 25 large-shape entries (alpha=3, W=9, 262,144 rows) are on `t17big.sh` at 7 GB with a
2,400-second budget, and two of them are already recorded at 7.0. Given restarts as close
together as eleven minutes, that budget cannot be relied on to complete — expect those to be
settled only in a long generation, and do not read their silence as a refusal.

### defect 48 — a merge deletes the progress an ANUMS runner depends on

`merge_shards.py` folds a tagged run's `done` set into `uniall_done.json` and then **deletes**
`shard<TAG>_done_*.json`. `sweep_shard` honours the global set only when no list is given —
`if a in done or (not (ONLY or ANUMS) and a in GDONE)` — and that bypass is deliberate: the
point of an ANUMS list is to re-ask what the global set calls finished.

Together they mean **an `ANUMS_FILE` runner starts its list from the beginning after every
merge.** Observed directly: `TAG=t17c python3 src/merge_shards.py` folded three new proofs and
left the vein reading `asked 0/55`.

The proofs are safe — they are on the roster now and the roster check skips them — so what the
runner actually re-asks is the entries that already **failed**, spending a 900-second budget
each time on a wall it has already hit. That is defect 44 in a new place: work that cannot
produce anything, repeated because nothing remembers it was done.

`sweep_shard` now reads `uniall_oom.json` and skips an entry whose recorded limit is at least
this shard's `MEMGB`. Re-asking at the same memory cannot succeed; the state space did not
shrink because a file was deleted. **The skip releases as soon as `MEMGB` exceeds the recorded
limit**, so raising memory re-opens the entry automatically — that is the defect-34 rule with a
bigger machine as the expiry instead of a changed engine. Both directions were tested against a
real row: A251843, recorded at 5.0, is skipped at `MEMGB=5` and asked again at `MEMGB=9`.

What is still not remembered is a `state space > cap` refusal, which `uniall_caps.json` records
but which nothing consults on the ANUMS path. That one is cheap to re-ask — the cap is checked
during construction rather than after — so it is left alone for now, and named here so it is
not rediscovered as a surprise.

### defect 49 — every build timeout in this project has been recorded as a cap refusal

`uniform.build` ends with

    except MemoryError:
        # NOT `return None'. The callers read None as "the state space exceeded the cap", and
        # an out-of-memory is a different fact ...
        raise
    except Exception:
        return None

The comment is exactly right and the clause below it undoes the argument. Every sweep raises
its alarm as `class Timeout(Exception)`, the alarm fires **inside** `uniform.build`, and that
last clause catches it and returns `None` — which every caller reads as "the state space
exceeded the cap". **A timeout is a different fact by precisely the same argument as an
out-of-memory, and it has been silently filed as a cap since the day the alarm was added.**

Measured, not inferred. A252147 at `alpha=3, W=9`, asked with `BUDGET=2` and a cap of 10^12 —
a cap nothing can exceed:

| | before | after |
|---|---|---|
| why | `state space > cap` | `build timed out` |
| named | nothing | `uniall_tmo.json: {A252147: 2}` |

This is the mechanism behind two things already written down here. `uniall_caps.json` holds
2,311 off-roster entries and an unknown share of them never touched the cap at all. And
`residue.txt` — the 33 entries `uniall_done.json` called finished with no record anywhere of
what finished them (defect 40) — is what this looks like from the far end: the clock ended them,
the cap took the blame, and the cap's own list was written under a different name.

**The fix is the exception's base class.** `Timeout` now derives from `BaseException` in all 19
sweeps that define one, so no `except Exception` anywhere can absorb it — the idiom Python
itself uses for `KeyboardInterrupt`, and for the same reason: a control-flow signal is not an
error the callee may handle. A bare `except:` would still swallow it, so do not write one in a
build path.

Alongside it, a timeout is now NAMED. `sweep_shard` writes `shard<TAG>_tmo_<i>.json` holding
the largest budget each entry has failed under, `merge_shards.py` folds those into
`uniall_tmo.json` and retires rows for entries since proved, exactly as it does for
out-of-memory. Three separate files for three separate facts — the cap, the container, the
clock — because the whole history of this project's refusal lists is one of them wearing
another's name.

### A budget longer than a container generation is not a budget

Defect 47 makes a shard re-ask the entry a container restart killed, rather than retiring it as
a refusal. That is correct and it is not progress. With `BUDGET=900` against restarts as close
as eleven minutes apart, all three `t17c` shards sat in a loop on A252318, A252421 and A252146 —
starting the same entry every generation, being killed, and starting it again — while **35
entries of that list had never been asked at 8,000,000 at all.** `uniall_caps.json` still
recorded 2,000,000 for them, which is what gave them away: a stale cap is not a current refusal,
and reading one as the other made the vein look read out when a third of it was untouched.

`t17big.sh` was worse: `BUDGET=2400` is longer than this container has ever lived, so it could
not complete an entry under any circumstances. It produced nothing at all in two hours.

**Budgets are now 420s and 900s.** The reason this is a fix rather than a retreat is defect 49:
a build that runs out of budget is NAMED in `uniall_tmo.json` with the budget it failed under,
where before it was counted anonymously in the why file and, worse, attributed to the cap. A
shortened budget now converts entries this machine cannot reach into **a list to re-ask on a
quieter one**, which is the opposite of the silence they were.

**The rule: a budget must be shorter than the shortest container generation you have seen, or
it is a guarantee of being killed mid-work rather than a limit on it.** Check `uptime` against
the budget before trusting a runner that reports nothing.

### `checkclaim.py` — the by-hand check, done mechanically

The binding rule is to check every apparent proof against the entry's own wording. By eye that
is slow and it degrades: eleven results were checked that way in one night, and the eleventh got
the same attention as the first only by luck.

`src/checkclaim.py` does the textual half mechanically. For every held, un-installed hit
carrying `coeffs` it parses the entry's own formula line and compares the coefficient set lag by
lag, and the threshold the entry states against both the claimed and the computed one. A record
that disagrees is printed loudly and withheld; a record whose entry has no parsable recurrence
line is ALSO withheld and named, because the absence of a line is not evidence the claim is
wrong, only that this tool cannot speak to it.

**It does not replace the reading.** Whether a parsed line is the entry's conjecture at all, and
whether the conjecture says what the paper claims it says, still needs a human pass — that is
the part that caught the `ca2dcount` family. What this removes is the part where a coefficient
is misread on the eleventh check of a long night.

Validated before use, per defect 46: run against the whole held set it printed
`0 verified, 0 DISAGREE, 0 withheld`, which is exactly what a broken check prints. Run against
the eleven results already installed it re-verified **11 of 11 with 0 disagreements**, so the
zero was an empty input. **A checker that has not been shown to return non-zero on a case you
know is not a checker.**

### Changing a sweep's shard count orphans its in-flight markers

Cutting `t17run.sh` from three shards to two left `shardt17c_inflight_2.json` behind, naming
A252190 at the old `MEMGB=5` and an old boot stamp. Nothing reads it — shard 2 no longer runs —
so it sits there for ever, and every later inspection reads it as a shard at work on an entry
that nothing is touching. Harmless to the data, actively misleading to the reader, which is the
same failure as every refusal list this project has had to retract.

**The entry itself is not orphaned.** The partition is `crc32(anum) % NSHARD`, recomputed on
every run, so lowering `NSHARD` reassigns every entry among the shards that remain: A252190 went
from shard 2 of 3 to shard 0 of 2 and is still unsettled and still in the list. **Delete the
markers above the new shard count when changing it**, and do not assume an entry was lost with
its shard.

A related misreading, worth naming because it cost a minute twice tonight: `ps` showed
`sweep_shard.py 8000000 0 3` after the change and I read it as t17run still running three
shards. It was `readable.sh`, which also uses an 8,000,000 cap. **The cap is not an identifier.**
Match a runner's shards by the runner's own `ANUMS_FILE` or by parentage, never by the cap.

### defect 48, the half that was missing — and the tag that is invisible

`sweep_shard` learned to skip an entry the MACHINE had refused (`uniall_oom.json`), but not one
the CLOCK had refused, because `uniall_tmo.json` did not exist when that guard was written. So:
`merge_shards` deletes the per-shard done file, the timeout rows are folded into
`uniall_tmo.json`, nothing consults it, and **every generation re-asks the same entries and
spends the whole budget rediscovering the same timeout.** Both `t17c` shards had been looping on
A252112 and A251948 for hours, recording correctly and advancing not at all.

Measured before fixing: A252112 asked alone with the runner's own settings reported
`build timed out` and wrote `{"A252112": 420}`. The machinery was right; nothing read what it
wrote. `sweep_shard` now skips an entry whose recorded budget is at least its own `BUDGET`, and
releases it the moment `BUDGET` is larger — the memory rule, for the clock. Both directions
tested: skipped at 420, asked again at 900.

**The tag that is invisible.** Chasing this, 54 timeout rows appeared to vanish between two
commands. They had not: they were in the UNTAGGED shard files, `shard_tmo_0.json` and friends,
and the command that listed the tags rendered the empty tag as an empty string, so the output
read as `" t17c "` and I read it as "only t17c". **`TAG=` is a real tag and it is the one the
biggest runners use.** When folding or auditing by tag, run the empty one explicitly — the
untagged fold turned 2 recorded timeouts into 59, and 116 out-of-memory rows.

The scale is the point. `uniall_tmo.json` now holds **59 entries the clock refused** at budgets
of 90, 150 and 420 seconds — a population that before defect 49 would have been recorded as
exceeding the cap, and that a longer budget on a quieter machine can simply have.

### BUDGET is a per-PHASE limit, so an entry can cost three times it

`sweep_shard` sets `signal.alarm(BUDGET)` three times for each entry — once around the build,
once around the terms, once around the threshold. **`BUDGET` therefore bounds a phase, not an
entry, and an entry's worst case is `3 * BUDGET`.**

This is not a detail. `tmorun.sh` was given `BUDGET=900` on the reasoning that fifteen minutes
fits comfortably inside a container generation. Its real worst case was forty-five minutes, most
of a generation, and in its first hour it recorded **nothing at all**: each shard began one
entry and the restart killed it before the entry finished. The runner looked broken and was
merely mis-budgeted.

The arithmetic to do before setting a budget is `3 * BUDGET` against the SHORTEST container
generation seen, not `BUDGET` against the average. By that rule the earlier changes were
luckier than they were reasoned: `t17run`'s 420 is really up to 21 minutes per entry.
`tmorun` is 300 now — a 15-minute worst case, about four entries per shard per generation, and
still more than three times the ninety seconds most of its list was refused at.

### A recovery message marks where a generation BEGAN, not what it did

`tmorun.sh` looked stuck: its shard-0 log held two lines across two container generations, both
`previous shard on A183358 was killed by a container restart, re-asking`, and A183358 was
recorded at 150 rather than at the runner's 300. I read that as a loop and started building a
case that `SIGALRM` was not being delivered inside long C-level calls — a genuine limit of the
budget mechanism, which would have gone into this file as a fact.

**It was wrong, and measuring it is what showed that.** Asked directly with a 60-second alarm,
A183358 raised at exactly 60 seconds: the signal is delivered. Watched live, the shard moved
A183358 → A183359 after its 300 seconds and wrote `{"A183358": 300}`. Nothing was stuck. The
vein has since re-asked four of its 62 at the higher budget and recorded each honestly.

**A container-restart recovery line says only where a generation started.** It is written at
startup, about the PREVIOUS generation's death; it carries no information about the entries the
generation then processed, because those are recorded silently in the shard files and swept away
by the next `merge_shards`. Two such lines in a log are two generations, not a loop. To tell a
loop from progress, read the in-flight marker twice a minute apart, or read the refusal lists
for the budget the entry was last refused at — never the log alone.

The near-miss is the lesson. A plausible mechanism, a symptom that fits it, and a file that
would have carried it for ever — with the measurement that refutes it costing sixty seconds.

### defect 50 — the outer `timeout` lies where a container restart tells the truth

`BUDGET` is per PHASE. `sweep_shard` arms `signal.alarm(BUDGET)` separately for the build, for
the terms and for the threshold, so a single entry's worst case is `3 * BUDGET`. Every runner
also wraps the shard in a shell `timeout`. Nobody had compared the two numbers.

`oomrun.sh` ran `BUDGET=1500` inside `timeout 2400` — an outer clock shorter than two of the
three phases it was supposed to contain. An entry slow in the build could not reach a recorded
outcome at all. What happened instead is worse than silence: `timeout` killed the interpreter
with the in-flight marker still on disk, the boot stamp unchanged, and the next round read that
marker and wrote the entry down as having died at `MEMGB=11`.

**A200556, A201092, A202126 and A202127 were recorded as out-of-memory refusals at 11 GB when
what refused them was a shell timeout.** They have been withdrawn from `shardoom_oom_0.json`
and put back in the list. This is defect 49's shape one layer further out: the per-phase alarm
was taught to say `timed out` instead of `too big`, and then an outer clock that nothing had
counted in said `out of memory` on its behalf.

**A container restart is not this problem, and the difference is the whole point.** A restart
changes the boot stamp, the marker reads as a death that was not the entry's, and the round
re-asks — defect 47's machinery, working. Only a killer that leaves the boot stamp intact can
be mistaken for the entry, and the outer `timeout` is the only such killer. So the fix is to
put it out of reach rather than to shorten the budget: the container is then the sole external
killer, and that one is already handled honestly.

Five runners had `timeout < 3 * BUDGET`; four were preventive and one had already done the
damage. `oomrun` 2400 → 5400, `resrun` 2400 → 6000, `t21run` 1700 → 3000, `caprun` and
`rcaprun` 1700 → 2100. The check is one line and belongs before any budget change:

    for f in src/*.sh; do B=$(grep -oE 'BUDGET=[0-9]+' $f|head -1|cut -d= -f2); \
      T=$(grep -oE 'timeout [0-9]+' $f|head -1|cut -d' ' -f2); ...  # T must exceed 3*B

I also killed the live shard by hand while fixing this, and that leaves the same lying marker.
Deleting the marker for the entry I interrupted (A203295) is not tidying up: a death I caused
must not be recorded as a refusal the entry earned.

**A number in a comment is not a setting.** Verifying the patch with
`grep -oE 'timeout [0-9]+' /tmp/oomrun.sh | head -1` returned `timeout 2400` — from the prose
in which I had just explained the bug. The same mistake as reading a cap out of `ps` and
calling it an identifier. Anchor on the command line (`^\s+timeout [0-9]+ python3`), not on the
first occurrence of the digits.

### the idle veins are the measurement

`rcaprun`, `resrun` and `t21run` had all stopped on the idle backoff, each reporting only
`out of memory on an earlier pass, at this limit or more` — 17, 4 and 0 entries skipped. They
are not out of work; they are asking at 5 and 6 GB for entries already refused at 5 and 6 GB.
That population has exactly one open route, which is `oomrun` at 11 GB, and its list had been
left at the 41 entries `uniall_oom.json` held when it was written. The file now holds 138, all
off-roster, all unsettled, none ever asked above 7 GB. Regenerating the list from the refusal
file rather than from memory is the whole of today's unblocking.

### defect 51 — the guard against a wrong recurrence read nothing for 36% of the results

`sweep_shard` has exactly one empirical check on a result it is about to keep: recompute each
published term from the recurrence and refuse the hit if any disagrees. It runs at indices
satisfying both `off + k > nthr` and `k >= order`.

A183618 has order 30 and fourteen published terms. There is no such index. **The guard tested
nothing and printed exactly what it prints when a result passes** — which is nothing.

It is not one entry. **2,132 of 5,987 held results have a DATA field shorter than the order of
the recurrence proved for them**, so every one of those passed a guard that read zero terms.
The distribution is not a tail either: the modal number of terms tested is 0, and the next most
common values are 11–19.

**This does not make them wrong, and the reason matters.** The model is matched term-for-term
against the whole DATA field before any recurrence is derived (`tv[s:s+len(d)] == d`, and a
mismatch is recorded as `model does not match DATA`), and the recurrence comes from the
transfer matrix by annihilation rather than from fitting terms. So what was uncovered is the
independent check on the annihilation step alone — the only step with no second witness.

For Hardin's entries that witness is free and was sitting on disk. DATA stops at fourteen terms
where the b-file runs to a hundred or more, and `bcache/` already held 3,377 of them. With no
network at all: **1,560 proved recurrences tested at 289,903 b-file indices, orders up to 99,
zero failures.** Of the results whose own guard had read nothing, 886 are now verified on
151,921 indices. A183618 holds at all 87 of its testable indices, with all 30 coefficients
identical to the entry's own `Empirical:` line.

Zero failures across 1,560 recurrences is the strongest evidence this project has that the
engines are right. It is also the first evidence of that kind, which is the uncomfortable half:
36% of the results had nothing behind them but the engine's own arithmetic, and the check that
would have caught a wrong annihilation had been silently inert since the beginning.

**A cache-only pass writes `no cached b-file`, which is a fact about this machine.** Left in
the state file it made `FETCH=1` a no-op — 4,426 results recorded as unreachable by a pass that
was not allowed to reach them, then skipped by the run whose whole job was to. A resume must
discard the conclusions the new run is able to overturn.

### an out-of-memory row can be a statement about the clock

A183618's row in `uniall_oom.json` said 6 GB refused it. Asked alone: **364 seconds, peak RSS
0.07 GB.** Seventy megabytes. Nothing about that entry was ever a memory problem. What refused
it was every budget it had been asked under, all shorter than 364 seconds.

The file is written from two places and only one is honest. `uniform.build` raising MemoryError
against the shard's `RLIMIT_AS` is a fact about the entry. The in-flight marker is not: the
shard died recording nothing, the boot stamp said the container had not restarted, so the next
round wrote the entry down as having died at `MEMGB`. A shard the cgroup killed while
twenty-eight runners shared 15 GB has learned nothing about whichever entry it happened to be
holding when the kernel chose it.

The cost is not bookkeeping. `sweep_shard` skips when `MEMGB <= GOOM[a]`, so a row recorded at
6 GB locks that entry out of every runner at 6 GB or less, for ever. `rcaprun`, `resrun` and
`t21run` were all idle tonight reporting nothing but `out of memory on an earlier pass, at this
limit or more` — declining to ask entries that may need seventy megabytes and six minutes.
`src/oomtruth.py` measures each row alone and records the two numbers that decide which file it
belongs in. The population is also growing faster than it is read: 138 rows at the start of
tonight, 197 after the merges.

### defect 52 — a crash and an empty vein were the same event

The idle backoff added for defect 44 stops a runner when a round comes back in under a minute,
on the reasoning that a round doing real work takes minutes. It is right about that. What it
cannot see is WHY the round was short.

**`bsweep.py` has been dead since 31 August.** `conjlines` was refactored to `lines()` and
`claims()`, `is_recurrence` went away, and the one call to it was never updated. The sweep
raises `AttributeError` on its first entry, every time. Its results file has sat at 3,376 of a
10,632-entry queue for three weeks looking exactly like a half-read backlog, and nothing said
otherwise — a crash in under a second and an exhausted vein print the same thing, which is
nothing. The moment it was put behind an idle backoff, the backoff would have announced the
queue read out.

The exit code tells them apart and costs nothing: 0 is a clean round, 124 is `timeout` doing
its job, anything else is a crash and must never be read as an empty vein. All 33 runners now
check it.

**`wait` with no operands is specified to return zero, always.** So the first version of this
fix was inert in the 22 runners that launch more than one shard — the check was there, it ran,
and it could not fail. Each backgrounded shard's pid is collected now and waited on in turn.
Verified by construction rather than by reading: two children exiting 0 and 3 under the new
block report 3.

`forever.sh` is deliberately left out. It runs six sequential sweeps a round and must never
stop, so where the others break it sleeps; a crash there costs one 300-second sleep and is
retried, which is already right.

**The rot was three layers deep, and each layer hid the next.** Fixing `is_recurrence` exposed
`'list' object has no attribute 'get'` — 3,376 stored results are in an older `["ok", {...}]`
shape the current readers do not understand. The wrapper tag is `"ok"` for all 3,376 and
carries nothing, so unwrapping loses nothing. With both fixed, bsweep checked 101 entries in a
180-second slice: 3,540 of 10,632, and alive for the first time in three weeks.

**The lesson is the standing one, pointed at the sweeps themselves.** Read what a sweep
refuses. This sweep refused everything, and the refusal was indistinguishable from success.

### defect 53 — one death wrote a permanent exclusion, and the file could not say from where

`uniall_oom.json` was written from two places that produce the same key and the same value:

* `uniform.build` raising `MemoryError` against the shard's `RLIMIT_AS`. That is the entry's
  own appetite and it is a fact about the entry.
* the in-flight marker, read by the next round after a shard vanished. That is the machine's
  state at that moment — the cgroup choosing this process while a hundred and twenty others
  shared fifteen gigabytes, or an outer clock killing it (defect 50) — and it says nothing
  certain about the entry at all.

`sweep_shard` skips when `MEMGB <= GOOM[a]`, so either one made a **permanent exclusion from
every runner at that limit or below**, from a single event.

**Measured, and the measurement is what forced this.** Of the first seven rows, six are not
memory facts: A183618 builds in 391s at 0.07 GB; A183913 in 34s at 0.06 GB; A183921 is refused
by the CAP before memory is ever in question; A183358, A184472 and A183359 run out of clock,
the last with **9.33 GB free** — three times what its row claimed it wanted, available and
unused. Only A185885's SIGKILL is arguably about memory, and it died with about five gigabytes
free out of fifteen, so even that is the machine's choice rather than a footprint.

The list was also growing three times faster than it could be measured — 138 rows at 21:00,
207 at 22:25, 222 at 22:45, against `oomtruth` managing about five an hour. Brute force was
never going to settle it.

**So the two facts are separated instead.** `MemoryError` still writes `uniall_oom.json` and
still excludes. A shard dying writes `uniall_died.json`, a COUNT, and costs the entry a chance
rather than its place in the queue; only `DIEDMAX` deaths across separate generations — three —
are treated as the entry reliably killing whatever asks it. That still stops a shard walking
into the same wall for ever, which is what the original behaviour was for.

All 222 rows were migrated to one death each, because nothing in the file could be told from
anything else in it. This is safe in one direction that matters: **an entry that really does
raise `MemoryError` writes itself straight back into `uniall_oom.json` on the first re-ask**,
since that handler is untouched. The file sorts itself out within a generation.

Verified rather than assumed: A184472, previously excluded from every runner at 6 GB or below,
is now asked and comes back `build timed out` at BUDGET=90 — the honest answer, and one a
longer clock can change. 146 of the 222 have no clock row either and are open to every runner.

**The definition-order trap caught me again while writing this.** `died = json.load(open(DIED))`
went in forty lines above `DIED = ...`, which is the same `NameError`-on-first-statement that
made twenty `oomrun` rounds die silently. Checked by character offset rather than by reading.

### the defect-53 migration answered its own question in one generation

The migration was built so that the record would correct itself: `MemoryError` still writes
`uniall_oom.json`, so an entry that genuinely wants more memory re-establishes its own row the
first time it is asked again, while an entry that was only ever a dead shard does not. One
generation later, every one of the 222 migrated rows has been re-asked and classified.

| what the row turned out to be | count |
|---|---:|
| genuine `MemoryError`, row re-established by the untouched handler | **106** |
| refused by the CAP | 93 |
| refused by the CLOCK | 21 |
| asked, no verdict recorded | 2 |

**116 of 222 — 52% — were not memory facts at all**, and not one of them is merely unexamined:
every single one came back with a different verdict. They had been excluded from every runner
at their recorded limit or below, permanently, on no evidence.

The two halves matter separately. **The honest handler works**: 106 rows returned at once, at
5, 6, 7, 9 and 11 GB, so nothing real was lost by emptying the file. **The marker path was
writing fiction**: 114 of the remaining 116 are cap or clock refusals — both reachable by
changing a setting, neither needing a bigger machine.

This is the standing habit paying out exactly as it usually does. The vein was not hidden by
mathematics. It was hidden by a sweep recording two different facts in one file under the name
of the more discouraging one.

### defect 54 — two runners spent weeks asking at the cap that had already refused their lists

A refusal is only meaningful next to the cap it was made at. That rule is written into
`sweep_shard`'s own comments, and both cap runners broke it.

`caprun.sh` reads `deep-check/realcap2.txt` — 734 entries, **727 of which carry a row in
`uniall_caps.json` saying they were refused at 2,000,000 or more** — and asked at exactly
2,000,000. `rcaprun.sh` reads `realcap.txt`, 255 entries, **all 255 refused at 2,000,000 or
more**, and asked at exactly 2,000,000. Re-asking at the cap that already refused is not a
question; it is the same answer again, and neither runner could have produced a result.

It printed as work. Both looped, both wrote refusal rows, both looked busy.

Raised to 8,000,000, which is measured rather than guessed: that is a genuinely new question
for **375 of realcap2's 603 open entries and 242 of realcap's 243**. The lists were regenerated
at the same time, dropping what has since been proved, what is now a real memory refusal, and
what 8,000,000 has already refused — 734 → 375 and 255 → 242.

The memory was deliberately not raised with the cap. Three shards at `MEMGB=5` already reach
the whole container if they all peak; an entry whose state space needs more than that at the
new cap raises `MemoryError` and is recorded honestly, which is information rather than a loss.

**This is the third stale refusal list tonight** — `oomlist.txt` at 41 rows when the file held
138, `realcap2.txt` and `realcap.txt` here. A list generated from a refusal file is a snapshot,
and every one of them was being treated as though it were a query.

### defect 55 — the hourly merge kills the runners it is merging for

Every unified file is read by seventy shards at startup and written by `merge_shards`. The
writes were plain `json.dump(open(f, 'w'))`, which truncates first and writes second. A shard
starting during a merge reads a half-written file and dies with `JSONDecodeError` before its
first entry.

Nineteen such deaths sit in tonight's runner logs — `uniall_done.json` torn at char 3,646,799,
`uniall_hits.json` at 3,203,111, across `cap_run`, `oom_run`, `res_run`, `t21_run`, both
`t17c` shards and both `tmo` shards. Each one cost a whole round.

**They were invisible until defect 52.** A shard that dies at line 89 comes back in under a
second, and the idle backoff read that as the vein being read out. So the merge — which runs
every hour, on the hour, against every runner at once — has been stopping runners and reporting
it as exhaustion. Two defects that each hid the other: the crash looked like an empty vein, and
the empty vein explained away the crash.

`merge_shards` and `merge_sharded` both write through `atomicjson` now, six files and two. A
reader sees the old file or the new one.

**Third instance of the same defect tonight**, after `dc_phase5.save()` and `bsweep`. The rule
is worth stating once: *any file a long-running process reads at startup must be written by
rename, not by truncate.* `atomicjson` has existed in this project since two shard files were
destroyed that way, and the writers that predate it were never converted.

### defect 54 again, twice more — and the check that finds it in one line

`tmorun.sh` reads `deep-check/tmolist.txt` and asked at `BUDGET=300`. **39 of its 62 entries
carry a `uniall_tmo.json` row saying the clock refused them at 300 seconds or more.** The vein
whose entire subject is the clock was re-asking at a budget already known to be too short.
Raised to 500, at which all 62 are a new question — the worst row is 420 — and not higher,
because `BUDGET` is per phase and `3 * 500 = 1500` must stay under the outer `timeout 1700`
(defect 50).

`realcap2.txt` had a second kind of dead weight. With the cap fixed, `caprun`'s dominant
refusal became `not open` — 41 in one round — which is `openness.status` saying the entry's
conjecture is already settled and there is nothing to prove. **117 of its 375 entries.**
Dropped; 258 remain.

**Four stale lists in one night** — `oomlist` (41 rows against a file of 138), `realcap2` and
`realcap` (asked at the cap that had refused them), `tmolist` (asked at the budget that had
refused it). The check is one line and belongs before trusting any runner list:

    for each entry on the list: is it already in the refusal file AT OR ABOVE the setting
    this runner uses? and is its conjecture still open?

Run over all five lists, only `realcap2` had entries with nothing to prove; `realcap`,
`tmolist`, `oomlist` and `t17small` are all fully open. So this is not a general rot in the
lists — it is specifically that **a list generated from a refusal file is a snapshot, and the
setting it was generated for is part of the snapshot.** Neither half is carried in the filename.

### the transfer21 switch: what the precondition actually says, and a figure I had invented

`t21check` is finished: **160 of 160 candidates. 110 comparable, ZERO mismatches, ZERO lost,
19 opened by the merge, and 80 of the 110 agree while the state space genuinely SHRANK** —
median 2.13×, maximum 81×. That last number is the one that matters: an agreement between two
builders that produce identical state counts proves little, and an earlier harness on this very
vein reported 99 of 99 agreeing having compared its own `TypeError` with itself (defect 38).
Eighty cases where the quotient collapsed states and the terms came out the same is the
evidence that the quotient is exact.

**I had been carrying a precondition that does not exist.** Every handoff note I wrote said
"do not switch until the sample approaches the 243 shapes this vein was held to". The 243 is
real, but it belongs to a *different* comparison: `uniform.py` records `build_pairfree` being
accepted against the PAIR build on "99 entries and 144 of the parameter grid". `t21check`
compares `build_lineset` against `build_pairfree` — the next link in the chain, with its own
sample. Repeating a number from one verification as the bar for another is how a figure becomes
folklore, and I did it to myself three times in one night.

The precondition that IS written down is AP.7: *"nothing will [dispatch to it] until a
comparison that can actually run comes back clean."* That is met — and it can fail, which is
the point of the `lost` bucket and of the `both_refused` fix that stopped the harness recording
a lineset failure as agreement.

What the earlier standard does have, and mine did not, is the **grid** — shapes no entry
happens to use. `src/t21grid.py` supplies it: every distinct body form among the 160 candidates
crossed with width 3..6 and K 2..4, terms compared through `uniform.terms` so the scaling
denominator is handled as production handles it, and a builder that raises reported with its
exception type rather than counted as agreement.

### a sweep has THREE refusals, and a list is only new against all three

The one-line check written down earlier tonight — *is this entry already in the refusal file at
or above the setting this runner uses?* — has a plural in it that I dropped the first time I
applied it to a list I had built myself.

`t17small.txt` was rebuilt as the 57 `transfer17` entries that are capped, unsettled and carry
an open conjecture. I checked them against the CAP and against memory, found 36 below the
runner's 8,000,000, and said 36 were a new question. The runner immediately reported **32 skips
of "out of budget on an earlier pass"**: 31 of the 57 carry a `uniall_tmo.json` row of exactly
420, which is `t17run`'s own budget. **Only 16 were askable at all.**

The three refusal files exist precisely because they are three different facts — that is the
whole of defects 48, 49 and 53 — and a list is new only against `uniall_caps`, `uniall_tmo` AND
`uniall_oom`, each compared to the corresponding runner setting. Checking one and announcing a
number is how a list looks fixed while being mostly unaskable.

`t17run` is at `BUDGET=550` now: nothing on the list is budget-skipped (the worst row is 500),
36 become askable, and the remaining 21 are refused by the cap and need a bigger one rather
than a longer clock. 550 and not more because the budget is per phase and `3 * 550 = 1650` has
to stay under the outer `timeout 1700`.

The runner's own counters are what caught this. Reading them is the standing habit working on
my own work rather than on somebody else's sweep.

### `src/listcheck.py` — the stale-list check, done mechanically

Five stale lists were found by hand in one night, and the fifth was one I had built myself
twenty minutes after writing the check down. That is the signature of a check that needs to be
a program rather than a habit, exactly as `checkclaim.py` is for the by-hand claim comparison.

`listcheck.py` parses each runner's own settings out of its script — cap from the
`sweep_shard.py <cap>` argument, `BUDGET`, `MEMGB` — and reports, for its list, how many
entries each refusal file already refuses **at or above that runner's own setting**, plus how
many are already proved. What survives all four is the number of questions the runner can
actually ask.

It paid immediately. **`t21run` was asking NOTHING**: 5 rows, 1 proved and 4 refused at its own
cap. **`resrun` was asking 5 of 33** — 20 refused at the 2,000,000 it was asking at. Both are
the defect-54 shape that had already been found four times by hand and was still sitting in two
more runners.

Fixed by measurement rather than by guess: `t21run` and `resrun` to `CAP=8,000,000`, and
`t21cap.txt` rebuilt from the whole `transfer21` candidate pool rather than the stale 5 — 160
candidates, 123 unsettled, **60 carrying an open conjecture, 52 askable at the new setting**.
`resrun` goes 5 → 25. Re-run of the checker confirms 52 of 52 and 25 of 33.

The remaining honest reading across all seven runners: `caprun` 220 of 258, `rcaprun` 214 of
242, `oomrun` 90 of 222, `t17run` 36 of 57, `tmorun` 46 of 62. Those were already asking real
questions; the two that were not are now.

### a job started by hand is in no list, and does not come back

`restart_all.sh`'s own comment says it: *"every runner belongs here: a container restart wipes
/tmp, and a sweep that is not in this list simply never comes back — which is how two veins sat
idle for a whole day earlier in this project."*

`bproved` was started by hand with `nohup`. It stopped at **3,060 of 5,987** when its process
ended and nothing restarted it, because a hand-started job is not in any list. Its log's last
lines are ordinary successes — it did not fail, it just stopped existing. 2,927 held results
were left unchecked with no sign that anything was wrong.

It is a round of `bsweeprun.sh` now, first of the three, so the fetching slot holds all of
`bproved`, `bsweep` and `provedsweep` in sequence. The wait-for-bproved loop that runner used
to carry is gone — there is nothing to wait for once all three are rounds of one runner, and
that loop was itself a symptom of one fetcher living outside the rotation.

The rule generalises past sweeps: **anything expected to still be running an hour from now
belongs in `restart_all.sh`.** A `nohup` in a terminal is a one-shot, whatever it is doing.

### defect 56 — a cap row only means something if the engine's build reads the cap

`sweep_shard` reads `None` from a build as *state space > cap* and writes a row into
`uniall_caps.json`. That inference is sound for an engine that compares its state count against
the cap. For nineteen of them it is not, and the criterion is mechanical rather than a
judgement: **does the engine's `build` read `cap` at all?**

* `transfer6.build(p)` and `transfer7.build(p)` do not even take the parameter.
* `latpoly.build(p, cap=200000)` takes it and never uses it. It has **seven** `return None`
  sites, every one a "this reading does not apply" test.
* `ca2dcount.build` is an unconditional refusal on principle (the section above).

**607 of the 2,367 off-roster unsettled cap rows — 26% — belong to such engines**, and every
one of them looked like an entry reachable by raising a number. Removed: `uniall_caps.json`
3,366 → 2,759, and the off-roster unsettled pool 2,367 → 1,760. `uniform.NO_SIZE_REFUSAL`
carries the nineteen with the criterion written next to them, and `sweep_shard` records
*engine returned no model (its build has no cap)* instead. Verified on A183914, A183921 and
A183929: recorded under the new reason with an empty caps file.

**This is the fourth mechanism to pollute that one file.** Defect 49 put timeouts in it.
Defects 36, 39 and 41 put out-of-memory in it. The section above put refusal-by-design in it.
This one is subtler than all three, because it is not about anything the machine did — it is
about what the engine *means* by `None`, and `uniform.build` flattens every meaning into one.

The rule to carry: **`None` is not a fact.** Before reading a `None` as any particular refusal,
check what the function that produced it is able to refuse for. Every one of the four pollutions
came from skipping that check, and each cost a population that looked reachable and was not.

### the root of all four: `uniform.build`'s `except Exception: return None`

Four mechanisms polluted `uniall_caps.json` and every one of them passed through a single
clause. `uniform.build` catches every exception and returns `None`, and every caller reads
`None` as *state space > cap*. So an engine that is BROKEN is indistinguishable from an engine
that declined, and both are indistinguishable from a model that is genuinely too big.

It is also the root of tonight's worst self-inflicted bug. Pointing the transfer21 dispatch at
`M[en].build_lineset` asked the module for a function it does not have; the `AttributeError`
landed in that clause; **every transfer21 build returned `None` in 0.0 seconds and was written
down as a cap refusal.** It was caught only because two of my own measurements disagreed about
A204282 — `t21check` built it at S=21,607 under a 200,000 cap while the sweep refused it at
forty times that.

`uniform.LAST_ERROR` now records what the clause swallowed, cleared on entry to `build`. The
contract is unchanged — thirty callers still read `None`, and changing that under the running
sweeps is not a surgical change — but the caller that matters can now name the fact.
`sweep_shard` checks it first, before the no-cap test and before the cap row, and records
`ENGINE RAISED: <type>: <message>` while printing it.

**Both paths verified, and the raise path took some doing.** `uniform.build('transfer17',
{'nonsense': True}, 1000)` returns `None` and sets `LAST_ERROR` to `KeyError: 'fixed'`. The
decline path is end-to-end: two `latpoly` entries record *engine returned no model* with an
empty caps file, so a clean `None` is not mistaken for an error.

The raise path could not be exercised by production data — **275 completed builds across a
400-entry sample of the candidate pool, and not one engine raised**, which is the reassuring
answer and also a dead end for testing. So it was contrived deliberately: `uniform.build` was
wrapped to raise the exact `AttributeError` tonight's wrong dispatch produced, and
**`sweep_shard.py` was then executed unmodified**. A183914 and A183921 print

    A183914 ENGINE RAISED AttributeError: module 'transfer21' has no attribute 'build_lineset'

record that reason in the why file, and write **no caps row**. The instrumentation would have
named tonight's bug on its first entry instead of after forty thousand states of disagreement
between two of my own measurements.

### defect 57 — `sweep_shard`'s first skip is the roster, and it is silent

`sweep_shard` begins each entry with `if a in roster or a in GHITS: continue`. No counter, no
log line. A list made entirely of entries that already carry an installed paper therefore asks
nothing at all, while every refusal file reports the list as clear and the round returns `{}`.

**`t21run` sat at "52 of 52 askable" and an empty result dict for an hour.** I had rebuilt its
list from the full transfer21 candidate pool filtered on `uniall_hits`, and all 52 were on the
roster — an entry can carry several conjectures, so a paper on one leaves the A-number on the
roster while `uniall_hits` says nothing about the others.

**`listcheck.py` had the identical gap**, which is the part worth recording: the tool written to
catch lists that ask nothing was itself filtering on `uniall_hits` and not on `paper-engines`,
so it confirmed the wrong number. It now folds the roster into its skip set and reports
`ASKS NOTHING` for that runner. The other six are barely affected — 4, 6, 5, 3 and 2 roster
entries between them.

**With the roster filter the transfer21 vein is read out.** 160 candidates: 37 already hits, 89
on the roster, 71 neither — and only **eight** of the 71 carry an open conjecture. All eight are
refused by a cap of 8,000,000, three also by memory at 6 GB, and a cap of 32,000,000 was
measured not to open this family. Nothing there is reachable by a setting. `t21run` is retired.

The `build_lineset` switch was still right — verified on 268 shapes, and it produced A204282 and
A204480, models the pair-free build refuses outright. It read the vein out rather than opening
it further.

**The general lesson is the one I keep relearning in new clothes.** A skip that increments no
counter is invisible to every check built on counters, and I have now twice built a check that
omitted a filter the sweep actually applies: first the clock, among the three refusal files, and
now the roster. The rule: **enumerate the skips from `sweep_shard`'s source, not from memory.**


### correction — `tmorun` did produce a result, and the clock is the current ceiling

I repeated, including into LEDGER.md, that the runners whose lists and settings were fixed
overnight had produced nothing. **That is false for `tmorun`.** A253494 was on its list at the
time it was proved (git history confirms it; the entry is absent from the current file only
because the roster strip removed it once papered). Its `PROVED: 1` for this generation is that
entry, so the raise from `BUDGET=300` to 500 — made after finding that **39 of its 62 entries
carried a `uniall_tmo` row of exactly 300** — is what produced it.

The claim stands for `caprun`, `rcaprun` and `resrun`, which have still produced nothing, and
`t21run` was asking nothing at all (defect 57).

**And the current ceiling is the clock, not the cap.** Across all six runners the dominant
refusal this generation is *out of budget on an earlier pass* — 19, 4, 3, 15 and 28 of the
entries each asked. Every one of those rows was written at a budget the runner has since raised
past once already, which is the shape that has paid twice now: `tmorun` 300 → 500 gave A253494,
and `t17run` 420 → 550 gave A252102, A252128 and A252145.

### a `why` file that outlives its merge is not evidence

`merge_shards` consumes and deletes a shard's hits, done, caps, oom, tmo and died files on every
run, so each of those always describes the **current** generation. The `why` file was not in
that list. It accumulated counters indefinitely and outlived the results it described.

This morning a `tmo` shard read `{"PROVED": 1}` at the newly raised budget. It was tempting to
call that a result of the raise. The file was dated **06:07 — five hours earlier** — and the
hit was A253494, already merged, installed and papered. The raised budget had been running for
one minute and had produced nothing yet.

Nothing in the codebase reads `shard*_why_*.json`; the only reader is a person looking at what a
vein is refusing **right now**, which is this project's central habit. A counter that cannot be
dated is no use for that, so the merge clears it with the rest.

**The general form**, since this is the second time the same shape has cost me: a file that
survives the operation that resets its siblings will eventually be read as current. Either it is
cleared with them or every reading of it has to carry a date, and the first is cheaper.

### a shared slot with a fixed order is a priority list nobody chose

`bsweeprun` runs three fetching sweeps in one round, because `bfile.fetch` is single-process and
two downloaders would double the request rate at OEIS. The order was `bproved`, `bsweep`,
`provedsweep` — and the last of those **had not run since 01:43, ten hours earlier**, while
`bsweep` advanced from 4,453 to 5,109 in the same period.

Nothing was broken. `bproved` could take its full 2,000 seconds and `bsweep` its slice, so the
third only got a turn when a whole round completed, and a container restart resets the loop to
the top. A queue whose last entry waits on two others finishing is not a rotation; it is a
priority order arrived at by accident.

`provedsweep` goes first now, being the one behind — 5,958 of 13,387 roster entries against
`bsweep`'s 5,109 of 10,632 — and `bproved` is finished, so it returns at once and costs the
round nothing.

**The general form:** when several jobs share a serialised slot, the order is a scheduling
decision whether or not anyone made it. Check which of them is furthest behind, not which one
was written first.

### defects 68 and 69 — a refusal nobody merged, and a refusal filed as an answer

`src/poolcensus.py` classifies every entry the unified sweep has ever considered, once, from
the files rather than from memory. **16,998 entries:**

      11,110  settled
       4,736  no conjecture to settle
         643  refused: cap
         396  asked, unsettled, NO refusal recorded
          68  refused: budget
          32  refused: shard death
          10  no engine reads the name
           3  refused: memory

The 396 is the bucket nobody had counted, and following it found two defects.

**Defect 68 — `merge_shards` only ever merged the untagged files.** Its globs are
`shard{TAG}_kind_*.json`, and with `TAG` unset the literal underscore matches only
`shard_hits_*.json`. Every TAG'd runner — np, np2, cap, cap2, rcap, rcap2, gal, gal2, gal5,
cg, oom, res, t17c, tmo — wrote its hits and refusals where nothing read them, because nothing
runs the merger with their tag. **468 cap rows for those 396 entries were sitting in
`shardnp2_caps_*` and `shardnp_caps_*`**, which is exactly why the census called them
"no refusal recorded": the record existed, under a tag nobody merges. **Four HITS were
unmerged too.** An unset tag now means every tag; merging folded in 4 hits, 796 newly
processed entries, and retired 234 stale rows.

**Defect 69 — a cap refusal marked the entry `done`.** It was the only refusal with no skip
and no re-ask. Two consequences. A shard re-asked, every round, entries it had already refused
at its own cap. And worse: `np2run` asks at a cap of 2,000,000 and records the refusal — then
marks it `done`, and `done` is global and permanent, so the entry is excluded from **every**
runner at **every** cap for ever. `done` meant "this shard is finished with it" and was read
as "answered".

A cap row is now the record, carrying its setting, so a runner with a larger cap can tell an
unanswered entry from a finished one; and a new skip stops a shard re-asking below its own
recorded cap.

**2,265 entries freed, 1,110 of them carrying a conjecture, 1,001 still open.**

**How much of that is recoverable — corrected.** The first estimate here said "29 of 40 proved
outright", and that number came from `un[:40]` — the first forty in *sorted* order, which are
all A163xxx/A166xxx/A183xxx `conn2` and `transfer6` entries with state spaces of 13 to 139. A
sorted prefix is not a sample, and the estimate it gave was wrong.

Random samples of 40, drawn properly:

  * from the 742 freed entries with no other refusal row: **0 proved**, 37 refused at the
    build even at a cap of 8,000,000, 3 timed out;
  * from the 396 unexplained: **0 proved**, 33 refused at the build, 7 not open.

So **the cap rows on the wider pool are largely honest** — those entries really are too big —
and the recovery is the small, easy cluster at the head of the list, not hundreds of results.
`freedrun.sh` is working the list and the exact count is being measured entry by entry rather
than sampled.

The structural fixes stand on their own: an entry refused at one cap should not be excluded
from a runner with a larger one, whatever the yield turns out to be.

### defect 67 — capping starts is not capping what runs; and the cap pool is 645, not 2,759

`restart_all` capped the runners *started* per firing at 8 (defect 66). Each spawns 2–6 shards
and the firings come every minute or two, so it climbed back to **74 python jobs on 4 cores**.
What matters is what is already running: above `MAXJOBS` (default 24, six per core) a firing
now starts nothing and lets the machine drain.

And the capped pool shrank again. Of the 1,754 unsettled cap rows, **1,109 carry no conjecture
at all** — no formula line, and none on the parent table either. Ten were run through the
sweep's whole sequence by hand: all build, all match the DATA, all report *no parsable
recurrence*. **The capped pool is 645.** Under a quarter of the number quoted in planning all
week, after two independent corrections to the same file in one day.

The BUILDS rows are therefore **not** a recovered pool of results. A196074 paid because it
carried a conjecture, not because its cap row was wrong — the wrong row is what hid it, the
conjecture is what made it worth finding.

### bsweep is COMPLETE: every held conjecture against every published b-file term

**10,632 of 10,632 checked, 2,426,440 b-file terms, median 210 per entry and up to 20,001.**
The vein is read out.

      10,616  holds on all b-file terms
           5  DISPROVED
          10  no b-file
           1  b-file disagrees with its own DATA (A193641, already examined)

The five: **A076217** and **A197230** papered earlier, **A196074** and **A222434** papered
today, and **A210247**, which is not open — the entry records its own refutation on the line
below the conjecture (defect 63).

**Four false recurrences in 10,632, and that is the honest yield.** It is low *because*
Hardin's empirical lines are almost all true: they are fitted to enough terms to be
trustworthy, and the ones that fail are the ones fitted at an order their sample could not
support. Every one of the four has the same signature — the published coefficients are the
true recurrence's first coefficients, term for term.

### defect 66 — the machine was too busy to notice it had nothing to do

Defect 65's feedback loop closing on itself. Starting all 33 runners at once, each with 2–6
shards, put **92 python processes and 42 `sweep_shard` instances on four cores** — load average
56, about 0.04 cores each.

At that point nothing finishes, every wall-clock budget is worth a fortieth of itself
(defect 64), and — the part that makes it self-sustaining — **the idle backoff cannot fire
either.** A runner declares its vein read out only when a round returns in under 60 seconds,
and under that load an empty round cannot start four interpreters that fast. So no marker is
written, so `restart_all` restarts it, so the load stays up.

`restart_all.sh` now starts at most `MAXSTART` (default 8) runners per firing, with a rotating
start point kept in `/tmp/restart_all.offset`, so every runner gets its turn across successive
wake-ups instead of all of them fighting on every one. Runners already up are not counted
against the cap — it is a cap on new work, not on total work — and the read-out hold applies
first. `start()` returns 0 only when it actually launched, or a firing that held eight read-out
runners would think it had started eight.

Verified live: two firings at `MAXSTART=2` started exactly two each, honoured three read-out
holds with their ages, advanced the offset, and took the container from **load 56 / 92 python
jobs to load 42 / 61**.

**Three defects, one loop.** 66 kept the machine too busy to back off, which kept 65's restarts
coming, which made 64's wall-clock budgets record the load instead of the entry — and that fed
a refusal file the whole project reads to decide what to work on next.

### defect 64 — a budget measured in wall-clock seconds records the load, not the entry

`uniall_tmophase.json` was supposed to answer "which phase is the out-of-budget pool losing
to". It does not exist, and the reason is the finding: an entry already in `uniall_tmo.json`
at this budget or more is **skipped before it is ever asked again**, so the 427 rows sitting
there will never record a phase unless something re-asks them on purpose
(`src/phasewhy.py` does).

Looking for why nothing had re-timed-out, the machine answered instead. **Measured: load
average 46 on 4 cores, 31 runnable processes, a sweep shard receiving 0.53 cores.** A BUDGET
of 600 wall-seconds is 318 CPU-seconds at that load, and the row it writes excludes the entry
from every future round at 600 or less. **Load was being written into the refusal file and
read back as the entry's difficulty.**

It also quietly explains the ledger's own observation that *every budget raise produced a
result and every cap raise produced nothing*: part of what a raise bought was simply undoing
the oversubscription.

`sweep_shard` now records `time.process_time()` across each phase — CPU-seconds, a property
of the entry — instead of the wall budget. The skip still compares this runner's wall BUDGET
against the stored CPU figure, which errs towards re-asking, and that is the right direction
for a file that had been permanently excluding work it never fairly tried. The 427 legacy
rows are wall values and over-state; they will be re-asked as budgets rise.

### defect 65 — the idle backoff and the restarter were fighting, and the restarter won

Every runner stops itself when a round finds nothing (defect 44, and it is right). Then
`restart_all.sh` relaunches it, because "is it running?" was the only test — and
`restart_all.sh` is called on **every wake-up**. With 33 runners that is 33 read-out veins
brought back to life once a turn, which is where the load average of 46 came from, which is
where defect 64 came from.

A runner that stops because its vein was read out now writes `/tmp/<name>.readout` and
`restart_all` leaves it alone for an hour. A runner that **crashed** writes no marker and is
restarted at once — the distinction defect 52 exists to make, and the two look identical from
outside. An hour matches the wake-up rhythm: long enough to stop the churn, short enough that
a changed engine, a raised budget or a widened pool is picked up next firing.

**The shape to remember: two mechanisms that were each right, wired so that one silently
undid the other every turn, and the damage showed up two layers away in a refusal file.**

### defect 63 — the openness test could not read a refutation, and nearly cost a wrong claim

`bsweep` flagged **A210247** as a disproof: "Conjecture: a(n) = -a(n-28)" fails at n = 606 and
twice more in 2,000 terms. True — and the entry says so itself, on the line immediately below:

> That is not quite true: the first counterexample is n=578, where a(578)=a(578+28)=-1.
> — *Robert Israel*, Sep 05 2018

`livenew` called it **open**, twice over. None of the PROOF words appears in Israel's line, and
the co-occurrence test — which asks the same line to say "conjecture" or "recurrence" — rules
out a refutation that refers to its claim **by position**, which is how most of them are
written. (My checker and Israel agree exactly, incidentally: he names the index the relation
reads from, 578, and the sweep names the index it is asserted at, 578 + 28 = 606.)

This came within one build of papering a disproof the entry already records — the precise
credibility cost the binding rules exist to prevent, and it would not have been caught by
"check every apparent disproof by hand against the entry's own wording", because the wording I
would have checked is the conjecture, which really is there.

`REFUTED` now matches *is false, is not true, not quite true, fails at, fails for,
counterexample, disproved, refuted, is incorrect, does not hold, breaks down at* — read
**without** the co-occurrence requirement, since those phrases are about a claim wherever they
appear, and a false positive drops a result rather than publishing a wrong one.

**Audited against the whole roster: 1 hit in 13,391 papered entries, and it is a false
positive** — A114584's example line, "the only counterexamples among the 9 Motzkin paths of
length 4 are HUHD and UHDH", which is the definition at work. So no papered result is
compromised, and `REFUTED` is now read only where a settlement is actually recorded: not in
example lines, not in programs.

One thing to watch: adding `or REFUTED.search(l)` into the existing list comprehension silently
un-guarded the other branch, because `A or B and not N` binds as `A or (B and not N)` — that
is defect 56's 41 entries, reintroduced by an `or`. Both branches carry the guard now.

### defect 62 — three phases, one number: which budget was exhausted was never recorded

`sweep_shard` names three separate timeouts — `build timed out`, `terms timed out`,
`annihilation timed out` — and all three write the **same** `tmo[a] = BUDGET`. So
`uniall_tmo.json`, the file that exists to keep refusals apart, collapses the one distinction
that decides what to fix.

It matters right now. The live sweep's own tally this generation:

      385  out of budget on an earlier pass
       64  out of memory
       44  a shard died holding this entry 3 times or more
        9  state space > cap

**Nine cap refusals against 385 clock refusals.** Every hour spent on an on-the-fly quotient to
raise the cap is aimed at nine entries. But "out of budget" is three different problems —
exploring a state space (raise the cap, write the quotient), iterating the matrix (speed up
`terms`), or the annihilation test (lump harder) — and nothing on disk said which. The phase
was already known: `inflight` writes it for the death marker. It was simply not kept.

Now kept, in `uniall_tmophase.json` beside `uniall_tmo.json` so every reader expecting an int
still works. The sweeps were restarted, because a source fix does not reach a running process.

**This is defect 48 one level down.** That one separated the cap from the clock from the
memory. This one separates the clock from itself.

### defect 61 — a refusal file that is never retracted, and the retraction that was written once

`uniall_caps.json` held **2,759** rows. **997 of them were already HITS of the very sweep that
wrote them**, and 1,004 were papered by some engine. **None of the 2,759 was unasked.** So
thirty-six percent of the file called "refused at the cap" was finished work, and every
measurement built on it was inflated by that much.

`merge_shards.py` already had the fix — for `oom` alone, under a comment naming
`uniall_caps.json` as the thing it existed to stop. Written once, applied to one of four
files. Worse, the version extended to `caps` still did nothing, because `CAPS` was dumped
*above* the pruning: the run deleted 1,004 rows from a dict nothing wrote again and printed
that it had retired them.

Now all four files (`caps`, `oom`, `tmo`, `died`) are pruned against `roster | hits`, and the
dump sits below the prune. **2,759 → 1,755.**

**What it changed, which is the point.** Targeting the on-the-fly quotient by cap count:

| engine | before | after | lump ratio |
|---|---:|---:|---:|
| transfer40 | 201 | **198** | 7.00x |
| transfer17 | 332 | 98 | 3.50x (already quotients) |
| transfer34 | 94 | 87 | 10.67x |
| transfer9 | 114 | 83 | 3.00x |
| transfer21 | 103 | 71 | 16.37x |
| **transfer20** | **103** | **18** | 30.38x |

`transfer20` was the target an hour earlier — highest lump ratio, 103 capped entries. **Eighty-
five percent of those entries were already settled.** The engine with the most honest cap rows
is `transfer40`, which barely moved: 201 → 198, so its refusals are real.

Read a refusal file as a claim that needs re-checking, not as a fact. This one had been
inflating every judgement made from it for weeks, and the audit that caught it
(`src/capwhy.py`) was three lines of cross-referencing against files sitting next to it.

### the tableorder scan — a vein opened, measured and closed in one sitting

A269637's parent table named the right order where the column entry's own line was wrong. That
shape is checkable across the whole OEIS with no arithmetic, and `src/tableorder.py` does it:
6,430 table/column pairs that both say something about the same recurrence, **two
disagreements, both disproofs** (A269637 → order 13, A236647 → order 38; in each the published
line is the true one truncated, and the table is right). Papered at ranks 1620 and 1278.
The vein is **exhausted**; see IDEAS.md §A9 for the three ways the scan was wrong first, all of
them a parser or a reading rather than a false conjecture.

### defect 60 — a re-ranking silently destroyed the LaTeX source of 104 papers

Installing one paper and running the ranking chain cost 104 sources. `paper-sources/` went
from 13,183 files to 13,079 and nothing said so: `sync_sources.py` reported "381 dropped as
belonging to another paper", which reads like tidying and was a deletion.

**The mechanism.** `sync_sources` matches a paper to its source through the build directory
that compiled it, by PDF hash. For **714 papers no build directory survives** — `engine/build/`
is regenerable working state and is not stored — so for those the ONLY copy of the source is
the file sitting under that paper's rank. A rank is a position in an ordering re-derived every
time the roster changes: inserting one paper at rank 1619 shifted all 12,174 papers after it by
one. For a shifted paper with no build directory, `sync_sources` looked under its NEW rank,
found the previous occupant's source there, correctly judged that it named a different paper —
and deleted it, never looking one name away at the paper's own source.

So the loss was proportional to the shift, and every ranking took another bite. It is not
something this session introduced; it would have fired on the next daily fold just the same.

**The fix.** The slot id (`was`) is stable across rankings, so the previous rank-map says
exactly where each source went. `rank.py` now copies `rank-map.json` to `rank-map-prev.json`
before overwriting it, and `sync_sources.py` carries a source across by `was` when no build
directory survives — reading everything it must carry BEFORE it writes or deletes anything,
since the destinations overlap the old locations. A carried source must still name the paper
it lands under, the same test the final check applies.

All 104 were recovered from git by `was`, each verified to name its own paper, and
`src/test_sync_sources.py` is the regression test: it builds a four-paper repository, inserts a
paper at rank 2, and checks every source survives. It fails against the old code (three sources
lost) and passes against the new.

**The general lesson, which is the one worth keeping.** A count that only ever goes up is not
a check. `sync_sources` printed five numbers every run and not one of them was "sources before"
against "sources after". The deletion was loud in the filesystem and invisible in the output.

### defect 58 — the disproof sweep discarded a conjecture for failing too thoroughly

`bsweep.check` filters boundary effects: *a recurrence with polynomial coefficients is asserted
for large n, so failing at a few small indices is the boundary, not a counterexample.* It
implements that by requiring the LAST failure to sit in the upper half of the tested range.

The failure list is capped at 41 entries. So a recurrence that fails at **every** index from its
first assertion onward has `fails[-1]` barely past its start — far below the midpoint — and is
thrown away. **The more comprehensively a conjecture fails, the more certainly it was
discarded.**

**A197230 is the proof that this is not hypothetical.** Its order-22 line fails at n=23 by 134
and at every index after. The b-file's a(23) is 1327965802062332, exactly the value this
project's own disproof computed, and the annihilator applied there gives 134 rather than 0. The
entry was **already disproved by hand and papered as ledger 1392** — and `bsweep` reported it as
*holding on all 200 b-file terms*, `fails = [23..63]`, last 63, midpoint 111, discarded.

Fixed by recording whether the 41-cap was hit: forty-one consecutive failures beginning at the
index the entry itself nominates is not a boundary, and `start_index` already honours the
entry's own *"for n > k"*. A197230 now reports correctly.

**What this opens is not yet known, and must not be claimed.** Re-asking the 5,736 entries
`bsweep` recorded as holding is turning up candidates at roughly five per thousand — but every
one of them fails from a *small* index (3, 4, 5, 6), which is precisely the case the guard was
written to suppress. They are candidates, not disproofs, until each is checked by hand against
the entry's own wording. Four times in one day a batch of "disproofs" was a defect in my own
reading, and this is exactly the shape that produced those.

### a long-running process overwrites the file you just corrected

I patched `provedsweep.py`, re-queued A193641, watched it come back correct — and an hour later
it was wrong again. The live `provedsweep` inside `bsweeprun` had started **before** the patch.
It held the old code and the old verdict in memory, and wrote its whole state back over my
corrected file.

Nothing detected this, because the file was valid JSON containing a plausible answer. I then
said in a commit message that both entries resolved correctly, which was **not true of the file
on disk at the time** — the code was fixed, the record was not.

The rule that follows is the one already written for runner scripts, extended: **a source fix
does not reach a running process, and a running process will undo a data fix.** Stop the process
before correcting data it owns. `restart_all.sh` exists for the first half; the second half has
no guard but the discipline.

**With the runner stopped and the patched code run, all three resolve**, and one is a real gain:

| entry | before | after |
|---|---|---|
| A193641 | *b-file disagrees with DATA* | holds on all b-file terms |
| A286772 | *CONTRADICTS A PROVED PAPER* | other lines fail; not the claim this paper proved |
| A197230 | *DISPROOF PAPER BUT THE CONJECTURE HOLDS* | **disproof confirmed: the entry fails, as its paper says** |

A197230 is the payoff of defect 58. This project disproved it by hand and papered it as ledger
1392; the sweep had been contradicting that, and now the b-file confirms it independently.
`disproof confirmed` goes 2 → 3, and **no entry on the roster contradicts the claim its paper
proved.**

### defect 59 — the evaluator's `n` and the entry's `n` are not always the same

Defect 58's fix re-admitted nine conjectures the boundary guard had been discarding. Checking
each by hand against its entry's own wording, as the binding rule requires, **six were my error
and not the entry's.**

With polynomial coefficients, everything turns on what `n` means. A165968 has offset 1 and
R. J. Mathar's line `a(n) +2*(-n+1)*a(n-1) +2*(-n+2)*a(n-2)=0`. Evaluated with `n` as the array
INDEX the residuals are 0, 0, 0, 0, 0, 0 — exact. Evaluated with `n` including the offset they
are −2, −6, −24, −156, −1344. A026377, A080244 and A221701 are identical in shape: **zero
failures under one reading, every term failing under the other.**

`bsweep` evaluated one convention and would have reported four false disproofs. That is the
fifth time in this project that a batch of "disproofs" was a defect in my own reading, and the
rule that catches it caught it again.

Both readings are tried now, and a failure is recorded only where **both** fail. For constant
coefficients the two are identical, so A197230 — the genuine case all of this was found through
— still reports failing from n=23.

Two more of the nine are the entry's own typo rather than a false claim: **A168494 states
`a(n-2)` twice with no `a(n-1)`, and A202020 states `a(n-4)` twice with no `a(n-3)`.** Both fail
under either reading because the line as published cannot be right. That is the same class as
A286772's lost "even" and "odd", already recorded in the ledger.

**What survives the hand-check: one candidate, not nine — and it is now a paper.**

* **A026672 was a tenth instance of defect 59, in my own correction.** The sentence that stood
  here said it "fails under both readings". It fails under three of the four: `n = index`,
  `n = index + offset`, and nothing else. Under **`n = index + 1`** — equivalently
  `n = index + offset - 1`, since the offset is 2 — Mathar's relation holds at **all 19**
  indices its 22 published terms can test, with no failures. Not a disproof. The entry also
  carries a g.f. stated as fact (`x*C(x)^4/(1-x*C(x)^3)`, Deléham), so it is a **proof**
  candidate for the ordinary residual test, and belongs in that queue rather than this one.
* **A269637 is genuinely false** and is now roster slot 14978. Constant coefficients, so the
  convention is irrelevant; it fails at all ten of the indices its own published DATA can test,
  first at n = 11 (published 199677806, line 199034092). The true minimal order is 13 and the
  published ten coefficients are its first ten — the A197230 truncation shape again. See the
  batch note in `LEDGER-PENDING.md` and `engine/src/verify_a269637.py`.
* **A236647 is untestable**: order 34 against sixteen published terms. Closed, not refuted.

**The lesson repeats.** Nine candidates became one. Eight were my reading, and one of those
eight was in the very paragraph correcting the other seven. A checker that ignores a stated
range or a stated index convention does not find false conjectures; it manufactures them.
