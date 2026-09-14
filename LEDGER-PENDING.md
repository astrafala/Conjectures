# Pending batch notes

## 14 September 2026 — four more, and a stale-hit scare that was my own misreading

`transfer35` finished four entries the earlier run had not reached: **A188099, A188100,
A188101, A188102**, all kept by the live re-check. Roster 12,954 -> 12,958.

The rest of this note is a correction, because I got the diagnosis wrong twice before getting
it right, and the wrong version is the one worth writing down.

Sixty uninstalled hits were sitting in `uniall_hits.json`, all labelled `ca2d` — the argument
withdrawn on 13 September. **First reading, wrong:** a standing sweep is burning three of four
cores producing results that `withdrawnset` blocks at install. I started making
`ca2d.threshold` refuse outright and pulled `ca2drun.sh` out of `restart_all.sh`.

**Second reading, also wrong, and this one nearly did damage.** Clearing the `ca2d` records
out of the hits file dropped 272, not 60 — because 144 roster papers still carry the
`automaton-axis` label. Dropping their hit records would have destroyed the authority behind
installed work, which is defect 14 in another costume. Restored from git before anything else
touched it.

**What is actually true.** The withdrawal note says it plainly: *only the rules whose whole
configuration is exactly periodic in time keep a proof*, and `ca2d.build` already enforces
exactly that — it refuses unless `ca2dgrid.timeperiod(rule)` succeeds. So the engine is sound,
the 144 retained papers rest on a stated induction, and the 60 blocked hits are STALE RECORDS
written before that guard existed. Asked of today's engine, all sixty are refused:
`timeperiod` is `None` for every one of their rules. The sweep is not producing them; nothing
was being wasted; the blanket refusal I had started writing would have killed a working engine.

So the fix is the narrow one: drop the 60 stale records, keep the 212 that back installed
papers, change no code. The uninstalled-hits list goes from 63 to 4 and becomes a usable signal
again — which is the whole point, since every one of those 60 had to be read to learn that
every one of them was dead.

Two things to keep:

* **A withdrawal list is a fact about the engine that existed when it was written.** Before
  concluding a blocked result is a waste, ask the CURRENT engine. Here the answer confirmed
  the block; it might not always.
* **Never edit `uniall_hits.json` while a sweep is running.** The first cleanup was silently
  undone: `sweep_engine` holds the list in memory and rewrites it whole, so it restored the
  sixty and an `integrate_rest` reading mid-write died on a JSON decode error. Stop the sweep,
  then edit. And stop it with `ps -eo pid,args | awk '$2=="python3" && $3=="src/X.py"'` —
  `pgrep -f` matches the agent's own wrapper shell and kills the command instead.

## 14 September 2026 — where the cap-refusal vein stops, said plainly

IDEAS.md section T proposed one change reaching four engines: merge states on the fly, since
the cap is hit during exploration and `lumpauto` runs after. Having now looked at all four,
**that is not what two of them needed, and the other two already do it.** The honest tally:

* `transfer3` — a nested loop over every pair of rows, where the condition is linear and the
  successors can be solved for. Fixed. **30 results.**
* `transfer35` — enumerated all A^(K*W) tuples where the condition is local across columns and
  the valid tuples can be grown one column at a time. Fixed. **22 results.**
* `transfer17` — **already** grows each pair's successors by column, with a comment saying so
  and why. What is left is the vertex set itself, all (alpha+1)^(2W) ordered pairs of lines,
  and that is not padding: a pair of lines carries no condition of its own, since the block
  spans three. The four pool entries checked are at 268,435,456 pairs (width 7, 0..3) and
  4,294,967,296 (width 8) — too large to enumerate, let alone trim. Those refusals are real.
* `transfer19` — **already** falls back to `build_pairfree`, which "applies its own cap to the
  states it actually reaches", and its guard already covers the triple loop the vertex count
  does not see.

So the section-T idea was half right. It found two builds that were testing what they could
have constructed, which is now STATE.md defect 20 and 52 results; it was wrong that the other
two were waiting for the same fix. Neither is a merge-on-the-fly problem, and writing a
partition refinement over the frontier would have bought nothing on either.

What would move `transfer17` is a different model, not a faster build of this one: the
condition on a 3 X 3 block is itself local along the fixed dimension, so the admissible column
triples are recognised by an automaton scanning that dimension, and the pair of full columns is
more state than the condition can see. Turning that into a transfer matrix needs a subset
construction, which is exponential in the wrong place. Recorded as an idea, not as a plan.

Raising `transfer3`'s cap from 400,000 to 2,500,000 reached **8 more** of its 13 remaining
refusals — A234680, A234736, A234821, A235097, A235185, A235196, A235237, A235278, all kept by
the live re-check. The build is fast now, so the cost has moved to the annihilation test on a
model with hundreds of thousands of states, and that is what the sweep's own time limit spends
itself on. The cap was never the binding constraint once the build stopped being quadratic.

Roster: 12,958 -> 12,966 papers over 12,939 entries.
