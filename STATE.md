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

1. a pool built from a stale snapshot (seven times, 40–1,718 entries each)
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

## Where things stand

* **12,624 papers installed** over 12,597 entries and 145 distinct arguments, as of the
  evening of 13 September 2026 (counts are re-derived by `src/sync_counts.py`, never typed by
  hand). 8 September: 1,353 withdrawn. 13 September: 184 withdrawn for the two-dimensional
  certificate, and 377 installed across seven new veins.
* **The generating-function-as-fact vein is null**, not 2,151. Asked correctly it proves 2.
  Everything held under it has been purged, and `WITHDRAWN.md` records what was taken back.
* Held: 85 generating-function results being re-derived under the corrected automaton bound,
  plus whatever the standing sweeps are finding now.
* `sweep_shard` with `TAG=np` over `deep-check/namepool.txt`: 1,446 entries with a readable
  conjecture AND a readable name that the cached candidate list had never heard of. 1,017
  asked, about 190 proved. **811 are refused with `state space > cap` at CAP = 2,000,000**
  (`deep-check/capped.txt`); a trial at 6,000,000 built two models in five minutes and proved
  neither, and re-asking them at the standing cap was **killed by the kernel for memory** --
  `uniform.build` allocates toward the cap before it can refuse. Do not brute-force them; they
  are marked done deliberately. The 429 still unasked are worth asking.
* **Every engine's degree bound S must be derived, not assumed.** `ca2dcount` set S = 24 from
  nothing and could certify nothing; it now refuses. `ca2d`'s bound was the one-dimensional
  figure and was too small; it is computed from the certificate's roots.
* **19,097 OEIS entries carry a conjectured recurrence with no linked proof.** 32,629 carry a
  conjecture of any recognised kind. That is the ceiling this project works against.

## When you create a new sharded sweep

Add its shard files to `.gitignore` **at the moment you create it**, and add its stem to
`merge_sharded.py`. Six workers rewriting their own progress file every few seconds leave the
tree dirty between every commit, and the merge is what keeps the tracked pair complete. This
has been caught by the stop hook four separate times.

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
