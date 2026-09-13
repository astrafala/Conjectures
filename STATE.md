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

13. **a fix applied to one builder and not to its twin.** `qpbuild` was written because
    `unibuild` called every model a walk on a digraph; `gfonlybuild` says the same thing and
    was left alone for another 219 papers. When a defect is found in one place, ask which
    other place has the same code.

14. **writing a rebuild to the derived copy rather than the authority.** `rank.py` deletes
    `papers/` and rebuilds it from `papers-old-numbering/`. Two rebuild scripts wrote only to
    the ranked path, so their corrections would have been thrown away by the next ranking,
    silently, with each paper reverting to the text it was rewritten to fix.

10. **taking a line with no conjectural word on it to be a statement of fact.** It is not.
    A `Conjectures from X: (Start) ... (End)' block holds bare formula lines and none of them
    says "conjecture". This cost 1,353 installed papers, withdrawn on 8 September 2026: they
    proved a conjectured recurrence from a generating function on the same entry and inside
    the same block, which is the same conjecture in another notation. **A premise may only be
    taken from `factlines.facts(e)`** — never from a word test on the line.

## Where things stand

* **11,240 papers installed** over 11,213 entries (counts are re-derived by
  `src/sync_counts.py`, never typed by hand). 8 September 2026: 1,353 were withdrawn and 581
  installed, from 12,012 before.
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

## Installing a batch

`newlist.py` → `livenew.py` (live re-check) → the vein's builder → `install_vein.py` →
`rank.py` → `makeindex.py` → `sync_sources.py` → `sync_counts.py` → `addtexfacts_all.py` →
`mkcomments.py` → `paperdates.py` → `makecomments_site.py` → commit and push to
`claude/code-setup-guidance-xit8fk`.

`rank.py`, `sync_sources.py` and `paperdates.py` refuse to run twice at once. Never start a
second copy.
