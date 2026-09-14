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

## 14 September 2026 — the threshold was not the bottleneck; the machine was

Last turn ended by saying the cost in `transfer3` had "moved to the annihilation test". That
was inferred from wall-clock, not measured, and it was **wrong**. Two findings, one real and
one a correction.

**Real: `transfer3`'s threshold was never lumped.** `uniform.threshold` sent it to
`T2.threshold` with the RAW state count, and that test runs until S+1 consecutive residuals
vanish — up to 3S+order+8 matrix-vector products on S states. Every other engine of this shape
is lumped first; `transfer3` was simply never added to that branch. The merge factor is not
marginal:

    A234225   78,125 states -> 17   (4,596x)     threshold 0s
    A234562   78,125 states -> 16   (4,883x)
    A234226  390,625 states -> 17   (22,978x)    build 135s, lump 4s, threshold 0s

Checked against the unlumped test on 576 threshold calls across widths 2..5, alphabets 1..3,
c = 0..3, both senses of the adjacency clause and random coefficient sets: **identical every
time**. The fix is correct and is kept. It is also, honestly, not what was blocking anything.

**The correction: `annihilation timed out` is 1 case in 122 in the pool sample and 0 in both
engine sweeps.** The threshold was never the binding constraint. What was slow was the
machine. `restart_all.sh` brings back about thirty background workers and the load average was
**35 on four cores**, so every targeted run today was getting roughly an eighth of one core.
With the standing sweeps paused the same sweep asked 100 names in two minutes where it had
managed 125 in twenty.

That is now STATE.md defect 21, and it is the more useful of the two: **a measurement taken
through thirty competing processes is not a measurement.** Every "this build is stuck"
judgement today was made through that fog, and one of them became a written conclusion that
was simply false.

With the machine to itself the sweep found **12 more** `transfer35` results before the
container restarted under it: A186879, A188103, A188104, A190029-A190032, A206340-A206342,
A207147, A207148. All twelve survived the restart because the sweep writes after every entry,
and all twelve were kept by the live re-check.

One more, `A224581` from `transfer23`, came in before the sweep's own time limit stopped it.

Roster: 12,966 -> 12,979 papers over 12,952 entries.

A number worth writing down while restarting the standing sweeps: `restart_all.sh` brings back
**71 python processes on 4 cores**. That is not a criticism of the sweeps, which do find things
and are the project's background discovery, but it is the reason a foreground measurement taken
alongside them means nothing, and it is worth someone deciding deliberately whether
seventeen-fold oversubscription is the right setting rather than inheriting it.

## 14 September 2026 — the coordination sequences: the graphs are rebuilt, and nothing is proved yet

The single biggest cluster in the pool is 378 entries reading "Coordination sequence Gal.u.t.v
where Gal.u.t.v denotes the coordination sequence for a vertex of type v in tiling number t in
the Galebach list of u-uniform tilings". Nothing had ever been attempted on them, for the good
reason that the tilings were missing: the local oeisdata mirror keeps the auxiliary file
`a250120.html` only as a git-LFS pointer, 132 bytes of metadata.

Fetched from oeis.org, it turns out to carry all 1,248 tilings in a notation that determines
each one completely — `Gal.1.1.1: A: 6^3; A 60; A 60; A 60`, meaning vertex type A sits in a
6.6.6 corner and along each of its three edges one reaches a type-A vertex whose frame is
rotated 60 degrees, a primed angle meaning the neighbour's frame is also reflected.

`src/galtile.py` turns that into a graph with no geometry input. The configuration fixes the
angles between a vertex's own edges (between edge j and edge j+1 sits a regular q-gon
contributing 180 - 360/q); the notation fixes each neighbour's frame; edges are unit length.
Only multiples of 15 degrees occur, so a position is a Z-combination of 24th roots of unity,
and working in Z[zeta_24] = Z^8 modulo x^8 - x^4 + 1 makes vertex identity EXACT. That is not
fastidiousness. A coordination sequence counts vertices at a distance; a floating-point
near-miss would merge or split vertices and give a plausible wrong answer that matched the
first several terms.

**Validated on the file's own answer key: 6,536 of 6,536 coordination sequences reproduced
exactly, 0 mismatches, 0 errors, 71 seconds.** And 6,070 OEIS entries name a Galebach vertex,
not 378 — the 378 is only what sits in the pool.

The shape of the answer is now pinned too. The counts are eventually quasi-linear with a
period, so the annihilator is (z^p - 1)^2 and no Ehrhart argument is needed:

    A310007  Gal.4.31.1   a(n+2p) - 2a(n+p) + a(n) = 0 from n = 3,   p = 8
    A310025  Gal.4.31.2   the same, p = 8 from n = 3
    A310018  Gal.4.34.1   the same, p = 42 from n = 11

and A310018's conjectured recurrence a(n) = a(n-6) + a(n-7) - a(n-13) has characteristic
polynomial exactly (z^6 - 1)(z^7 - 1), period lcm(6,7) = 42. They agree.

**Zero results are claimed from this.** Those p and n0 are MEASURED over 201 terms, which is
the `transfer88` situation exactly: a finite check of an infinite claim is evidence, not a
proof. What would make them theorems is the certificate — d(v + lambda) = d(v) + c(lambda)
outside a bounded region, verified by the two Bellman conditions on a rank-2 lattice instead
of a strip, with p and n0 falling out of the lattice rather than out of a scan. `kdcert` is
the template and it was written and validated three days' work ago. Until that is done this
vein has a validated graph, a pinned shape, and nothing to install — which is a good place to
stop for the turn and a bad place to claim anything from.
