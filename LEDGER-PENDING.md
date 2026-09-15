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
proof. What would make them theorems is a certificate, and the obvious one does not work. The first
version of the plan — claim d(v + lambda) = d(v) + c(lambda) outside a bounded region and
verify it the way `kdcert` verifies the knight distance — is **false**, and measuring it took
ten minutes where believing it would have cost a turn:

    Gal.1.1 (honeycomb)   d(v + lambda) - d(v) takes the values -2, 0, +2
    Gal.1.2 (4.8.8)       -3, -1, +1, +3
    Gal.4.31              seventeen distinct values from -9 to +9

Of course it does. The knight strip had ONE unbounded direction, so a single translation claim
closed the induction. A tiling is unbounded in two, d is asymptotically a polyhedral norm, and
the difference along a fixed lambda is +|lambda| out one side and -|lambda| out the other.
`kdcert` is the right idea and the wrong claim, and the handoff note that said otherwise has
been corrected in IDEAS section U before it could cost anything.

The true structure is piecewise affine over finitely many cones, with the same two Bellman
conditions checked region by region — affine inequalities, each decided once per cone. That is
finite and rigorous, and the work is fitting the cones, which is the limit shape of the graph
metric. It is worth saying plainly that "coordination sequences of crystals are of
quasi-polynomial type" is a 2021 research theorem and not a lemma; a per-tiling certificate is
much easier than the general result, but this is still the largest piece of mathematics the
project has taken on, and it should be started with that expectation.

Until it is done this vein has a validated graph, a pinned shape, and nothing to install.

## 14 September 2026 — the sweep that kept "running out of time" was being OOM-killed

`sweep_engine` over transfer35/transfer23/transfer6/transfer21/transfer3 had been stopping
without its summary line, at the same entry every time. Three handoff notes in a row recorded
the same inference — "cut off by its own time limit, so there are more results in these
engines" — and it was an inference, never a measurement.

It was being killed by the kernel: `Memory cgroup out of memory: Killed process (python3)
total-vm:14086164kB, anon-rss:13927820kB`. A state-space cap is a promise about the number of
STATES, and `uniform.build` allocates toward it before it can count them, so one entry past
A210331 takes 14 GB and the process dies with its tally and its place in the list.

`sweep_engine` now sets `RLIMIT_AS` (`MEMGB`, default 6 GB) at start. That turns the runaway
allocation into a `MemoryError`, which the per-entry `except Exception` already treats as
"build failed" — the entry is skipped and the sweep goes on. Verified in isolation that the
limit does raise a catchable `MemoryError` rather than killing the interpreter.

**The first complete run of that sweep:**

    788 asked: 682 no parsable recurrence, 88 state space > cap, 18 not open, 0 PROVED

So those four engines are exhausted, and this is the first time that has actually been
established rather than assumed. The three notes claiming more were left behind by a process
that could not report its own death. STATE.md defect 22: **a sweep that is killed is not a
sweep that found nothing** — when a long run ends without its summary line, find out whether
it was killed before believing anything about what it did not find.

## 14 September 2026 — a fit that checked itself, caught one term before it mattered

The coordination-sequence pipeline was built end to end this turn: the tiling as a graph, the
translation lattice, d as a max of affine pieces per class, and an Ehrhart count with the
period and the onset derived rather than scanned. It reproduced breadth-first search on every
tiling tried, and the derived period matched the conjectured recurrences' own.

It is wrong, and the way it is wrong is worth writing down.

`galhull` fits d on a patch and then checks the fit ON THAT SAME PATCH. A cone whose region
lies entirely outside the patch cannot show up as a leftover, so the fit certifies itself. On
**A310102** (Gal.4.16.1) the fitted form agrees with breadth-first search for 29 terms and
diverges at the 30th — one step past the radius it was fitted on:

    engine  ... 90, 93, 96, 94, 103, 118, ...
    data    ... 90, 93, 96, 99, 102, 119, ...

The Ehrhart half is sound and that was checked separately: the closed form and a direct lattice
count of the fitted region agree at every radius. The region is what is wrong.

Two consequences, both stated plainly:

  * **the "723 of 1,248 tilings are exact" figure is not what it says.** It counts tilings
    where a patch-sized fit failed to contradict itself, which is weaker and very likely an
    overcount. The "296 pool entries reachable" that followed from it is not a number to plan
    with;
  * `src/galcoord.py` is written and is **NOT IN SERVICE**. `build` returns None for
    everything, with the reason in the file.

What makes it a proof is the check deferred twice already: verify the closed form over the
WHOLE lattice by the two Bellman conditions, with the edges written as (class, class, lattice
offset). Both sides are convex piecewise-linear, so each condition becomes finitely many
"affine <= affine on a polyhedral cone" tests, each an exact rational LP in two variables.

The good news is that it was caught by the ordinary discipline — comparing the model against
the entry's own published data, which is the check that exists precisely for this — and caught
at 29 terms rather than after a batch of papers. The bad news is that I had already written
"the mathematics is done for the 723 exact tilings" into IDEAS, and it was not.

## 14 September 2026 — the certificate that passed its own tests and was still wrong

Wrote `src/galcert.py`, the whole-lattice Bellman check that IDEAS U.4a said was the missing
piece. It passed every test put to it: accepts the honeycomb, 4.8.8 and the triangular tiling;
refuses Gal.4.16, the tiling whose patch fit agreed with breadth-first search for 29 terms and
diverged at the 30th; and refuses any tiling whose plane constants are perturbed by one in
either direction. That is a real negative control and it did its job.

**A310511 is accepted and diverges at the 35th term.** Two gaps, both in the half that handles
points outside the breakpoint radius:

  * `_cone_points` finds a cone by walking out along its plane's gradient, and when that fails
    it returns None and the cone is skipped without comment. A check that silently skips what
    it cannot find is defect 8 in new clothes;
  * three affinely independent points settle an affine statement on a cone. Condition (c) is
    "SOME edge attains equality", and the attaining edge can change from point to point. Three
    points do not settle a disjunction.

So `galcoord` is back to IN_SERVICE = False. That is twice in two turns that this vein's
machinery has looked finished and not been, and both times the thing that caught it was the
same: comparing the model against the entry's own published data. It is worth being explicit
that the sampling shortcut was chosen to avoid writing a 2-D arrangement, and the arrangement
is what the next attempt should write — sort planes by gradient angle, take the region where
each is the maximum as the cone between its ties with its neighbours, and decide
"affine <= affine on a cone" from the apex and the two generator directions. Nothing sampled.

One real gain, and it stands: **counting is exact and settled.** `galehr.count` agrees with
brute-force enumeration at every radius tried, and `galcoord.ball` now uses it always. An
earlier version used the Ehrhart closed form wherever the derived onset said it applied, and
that was wrong on entries the certificate accepted -- `galehr.onset` can come out too small,
the quasi-polynomial is then fitted inside the transient, and its own verification passes
because the transient is locally smooth. A310393 drifted from t = 12 that way. Four entries
that had been recorded as "model mismatch" were nothing of the kind once the count was made
exact.

Roster unchanged. Nothing installed from this vein, which is the correct outcome.

## 14 September 2026 — the growing-alphabet pool measured, and it is 96 per cent one refusal

Having taken `galcoord` out of service twice, the question was whether this vein deserves
another turn at all, so the alternatives were measured rather than guessed at.

**The fixed-length growing-alphabet shape** (`0..n` or `-n..n` in the name), re-measured on the
whole clone because IDEAS section L's figures date from before the roster grew by 350:

    names of that shape                                  6,947
    open, not in roster, with a parsable conjecture        282
      of those, read by NO engine                          139
      of those, read by an engine and still unproved       143

The 139 unread are a **long tail**, not a cluster: the largest single name shape is 6 entries,
then a run of 4s and 3s. IDEAS section L's "31 N-bead necklaces" is 6 once the open-and-parsable
filter is applied. There is no parser here that pays for itself.

The 143 that ARE read were asked one by one, and the answer is almost perfectly uniform:

    state space > cap    124
    PROVABLE               3
    annihilation timed out 2

    behind the cap refusals: latpoly 98, transfer22 16, ordpoly 10

**96 per cent of them refuse at the cap in `latpoly`.** That is not a nested loop or an
enumeration that could have been a construction — the alphabet grows with n, so the arrangement
`latpoly` works over grows with it too. Defect 20's question ("is the build testing candidates
it could have constructed?") has an answer here and the answer is no.

The three that were provable are installed: **A248538** (latpoly), **A263594** and **A263751**
(permdisp), all kept by the live re-check. Roster 12,979 -> 12,982.

So the honest position on what is left in the pool: the coordination sequences are 378 entries
behind a certificate that has now failed twice; the growing-alphabet block is 282 entries of
which 124 are structurally past the cap and 139 are a fragmented tail. Neither is a vein with a
cheap opening. That is worth knowing before another turn is spent looking for one.

## 14 September 2026 — section P opened, and the first thing in it was circbase one dimension up

IDEAS section P asks the question that found the circular-base vein: how many entries carry a
conjecture of a shape no parser here can even read as a claim? Measured across the whole clone:

    entries outside the roster with a conjectural line       25,298
      of those, a line naming another A-number                8,202
      of those, open and with no parsable recurrence          6,163

Bucketed by the shape of the line, the head is not what the project can use — 1,500-odd are
Simon Plouffe's 2025 conjectures of the form `Sum_{k>=0} A0xxxxx(k)/exp(k*Pi) = <constant>`,
which are analytic identities and not this machinery's business. But eighteen entries carry

    [Empirical] a(base+1,n,diff) = a(base,n,diff) + F(n,diff) for base >= 2.diff.(n-1)

on **n X n arrays with entries in 1..base whose orthogonally adjacent entries differ by at most
diff** — which is exactly the identity `circbase` proves for circular digit strings, one
dimension up, and the same four lines settle it:

  1. T(b+1,d,n) - T(b,d,n) counts the admissible arrays over 1..b+1 that USE the value b+1.
  2. Every admissible array has max - min <= 2d(n-1): the grid graph on n X n cells with
     orthogonal adjacency has diameter 2(n-1) — along a row then along a column — and the
     entry changes by at most d per step.
  3. An array using b+1 has maximum b+1, so all its entries lie in [b+1-2d(n-1), b+1]; when
     b >= 2d(n-1) that window sits inside 1..b+1 and the alphabet constraint imposes nothing.
     The count is then the number of admissible arrays over Z with maximum 0, free of b.

**The entry's own threshold is exactly the diameter bound**, and it is sharp: checked at the
threshold and one above it the identity holds, and below it it fails — at base 5, diff 3, n 3
the difference is 964,755 where F(3,3) is 1,253,329.

One reading detail decided it. The line names its reference as `A063496(diff+1)`, and those
sequences do not share an offset — A063496 has offset 1, A068744 offset 0. The index is
POSITIONAL, the (diff+1)-th term as listed. Both readings agree at n = 2 and only the positional
one is right at n = 3, where F(3,2) = 87,825 is the third term of A068744 while A068744(3) under
its own offset is 1,253,329. Getting that backwards would have made eighteen papers cite the
wrong number.

**18 proved and installed**, A125530 through A125547, all kept by the live re-check, 0 refused.
Roster 12,982 -> **13,000** papers over 12,973 entries, 157 arguments.

Worth saying plainly: for most of these entries the threshold leaves only n = 1 at their own
alphabet size, so the identity is not a statement about their published terms. It is a
statement about the family, each entry carries it, and it is the family statement that is
proved — the same footing `circbase`'s 223 stand on. Each paper says so in as many words.

## 14 September 2026 — 66 more from section P, the reading pinned and the proof refused

The bucket that produced the 18 grid-base results has another 66 entries in it: "a(n) is the
number of letters in the n-th iterate of the mapping 00->001, 1->000, starting with 00".

The rule is now pinned, against the entries' own published data rather than assumed: scan left
to right, take the longest left-hand side that matches, copy any character that matches
nothing. `00->001, 1->000` then gives 2, 3, 6, 10, 17, 29, 51, 90, 160, 282, 499 and
`00->001, 1->011` gives 2, 3, 6, 13, 29, 65, 146, 328, 737, 1656, 3721, which are A285665 and
A286062 term for term.

The model is refused, and the reason is the useful part. The obvious state is (unit being
rewritten, characters pending before it) -- finite, because the left-hand sides are bounded --
and measured over nine levels the map (unit, carry) -> (emitted units, carry-out) is a
FUNCTION: eight states, not one disagreement. That is the check that would normally be run and
it passes.

Asking instead whether the CHILDREN are determined fails it: the same parent pair emits
children with different carries depending on what came before, 198 disagreements over eleven
levels on A285665 and 15 on A289131 -- and 0 on A286062, which is precisely how a partial check
misleads. A child's carry belongs to the NEXT level's parse rather than to the buffer position
it came out of, and it chains across parent boundaries; putting the next level's carry into the
state only introduces the level after that.

So the object is an HD0L system rather than a substitution, its length sequence is C-finite for
reasons that need the theory, and `src/morphlen.py` is left with `IN_SERVICE = False`. Three
unsound certificates in one day would be carelessness; the reading is done and recorded, and 66
entries are waiting for someone with the HD0L length theorem rather than more state.

## 14 September 2026 — cusp-form dimensions: three claims lost to a mashed line

Three new results, all `cusp-form-dimension`:

| entry | N | claim proved |
|---|---|---|
| A063110 | 42 | `a(n) = 2*a(n-1) - a(n-2)` for n > 3 |
| A063126 | 58 | `a(n) = a(n-1) + a(n-2) - a(n-3)` for n > 4 |
| A063157 | 89 | `a(n) = a(n-1) + a(n-2) - a(n-3)` for n > 4 |

All three were in `deep-check/cusp.txt` and had been swept. Every one was refused with
"no parsable recurrence", because the entry writes three claims on ONE line:

    Conjecture: a(n) = 16*n-12 for n>1. a(n) = 2*a(n-1)-a(n-2) for n>3. G.f.: x*(5+10*x+x^2)/(1-x)^2.

`ratrec.parse_rec` is handed the whole line and sees none of the three. `conjlines.claims`
now splits a line into its sentences and offers each alone; the three sweeps that build a
recurrence list read it. In each case the last nonzero residual sits at exactly the index the
entry itself claims, so the stated bound is tight and not merely sufficient.

Measured before changing anything: sentence-splitting rescues **17 entries pool-wide**, of
which **3 have a name an engine reads** — these three. The defect is real and it is also
small; `conjlines` was already splitting `(Start)…(End)` blocks correctly, which is where the
bulk of it was.

### Nulls recorded the same day

- **Inhomogeneous recurrences with a constant term** (`a(n) = a(n-6) + 14`). These differ
  once into a homogeneous recurrence of order max(i)+1, so they are free to support. Pool-wide
  there are **3 entries** whose only readable claim has this shape and **none** has a name an
  engine reads. Not a vein. (Two more sit on A063081 and A063168 as a *second* conjecture by a
  different author on an entry already on the roster.)
- **Shift identities** (`Conjecture: a(n) = A######(n+k)`). **26 pool-wide**; both sides
  already on the roster in exactly **one** case (A063148 = A063128, where both sides carry the
  same proved g.f., so the identity is immediate and elementary). Not a vein either.
- The deeper `relscan` tail past the top-25 shapes is pointer lines ("See A###### for a
  similar conjecture") and one-off claims relating two independently-defined sequences. No
  second gridbase-shaped family in it.

## 14 September 2026 — a generating function lost to a square bracket

`gfrec.ATTR` strips an attribution written `- _Name_, date` and nothing else. The older OEIS
house style puts it in square brackets:

    Empirical g.f.: x*(x^5+5*x^4+...) / ((x-1)^2*(x+1)*(x^2+x+1)). [_Colin Barker_, Feb 07 2013]

so the bracket reached sympy and the whole line was refused. **82 entries pool-wide** carry a
conjectured generating function written this way and nothing had ever read one of them; 5 have
a name an engine reads and are not on the roster. All five proved:

| entry | engine | claim |
|---|---|---|
| A063129 | cuspdim | `x*(x^5+5x^4+16x^3+21x^2+15x+4)/((x-1)^2(x+1)(x^2+x+1))` |
| A187588 | boardwalk | `2x^3(53+130x+34x^2-15x^3)/(1-x)^3` |
| A207021 | transfer48 | `13x(1+8x-7x^2+2x^3)/(1-x)^5` |
| A207022 | transfer48 | `18x(1+13x-5x^2+2x^3)/(1-x)^5` |
| A207023 | transfer48 | `25x(1+19x-14x^2+7x^3-2x^4)/(1-x)^6` |

`sweep_gfonly` also gained a `GFONLY` override: a reader that has just been widened has to be
able to ask about entries the narrower reader already marked done, or the widening is
invisible and the sweep reports the same refusals for ever.

## 14 September 2026 — the refusal census

One pass over the whole clone, classifying every open entry outside the roster that states a
conjecture by WHICH reader refuses it:

| count | |
|---:|---|
| 360,774 | no conjectural line |
| 16,368 | neither name nor claim read |
| 12,976 | on the roster |
| 4,976 | not open |
| 2,211 | **claim read, name NOT read** — an engine is missing |
| 1,164 | both read — sweep territory |
| 558 | **name read, claim NOT read** — a *reader* is missing |

The 558 is the cheap bucket: the engine already exists and the model already works, and only
the wording of the claim defeats the parsers. Bucketed by shape, it is dominated by two:

- **192** `Empirical recurrence of order k (see link above)` — the recurrence is not in the
  entry at all, it is in a linked a-file. The local clone has those files, but as **Git LFS
  pointers**, so opening one yields `version https://git-lfs.github.com/spec/v1` and settles
  nothing. Fetched from oeis.org they parse with `ratrec.parse_rec` unchanged.
- **36** `Empirical polynomial of degree d (see link above)` — same, one level down.

Orders run 37 to 96, on engines that already exist (transfer20 21, transfer56 16,
transfer22 15, transfer57 14, transfer9 13, window 11, ...).

## 14 September 2026 — the conjecture that is not in the entry

**23 results**, first of a vein of 228 candidates.

192 entries outside the roster state their conjecture as

    Empirical recurrence of order 42 (see link above).

and 36 more as `Empirical polynomial of degree 26 (see link above)`. The statement itself is
in a linked a-file. Every reader in this repository looks only at the entry's own text, so all
228 were refused with "no parsable recurrence" — and **every one of them has a name an engine
here already reads**. Not a missing engine: a missing fetch.

The local clone does carry these files, at `oeisdata/files/A279/a279654.txt`. They are **Git
LFS pointers**:

    version https://git-lfs.github.com/spec/v1
    oid sha256:dda0b1751a5304cc44ea590739d4db64f5dea0a9dbc1056ded6dd060

so opening the clone's copy settles nothing, and — worse — looks like a file that is simply
not a recurrence. All 228 fetched once into `afiles/`. `ratrec.parse_rec` reads the fetched
line unchanged, at order 96 as readily as at order 2.

Installed so far: 4 by `sweep_linkrec` (orders 91, 95, 98, …) and 19 by `sweep_cf` through
the linked polynomial (degrees to 31). The sweeps continue; the models are large — one is a
digraph on 114,688 vertices — so this is hours of arithmetic, not minutes.

One refusal is deliberate: the entry's sentence states an ORDER and the linked file states a
recurrence, and those are two statements. If the file's order is not the entry's order the
pair is **refused**, not reconciled.

### The same day's other stale filter

`polyclosed_cands.json`, the closed-form sweep's pool, held 137 entries chosen by hand on
1 September. 274 entries whose only readable claim is a closed form `closedform` reads
outright, and whose name an engine already reads, were not in it — 5 were. Ninth stale filter
found in this project, and they all hide the same way: the sweep runs, reports a small clean
number, and is never asked about the rest. Pool rebuilt from the clone at 406;
`cfpoolrun.sh` is in `restart_all.sh`.

## 14 September 2026 — the closed-form pool, rebuilt

**88 results**, every one `walk-closed-form`, from the 274 entries the stale pool had never
been offered. Degrees run to 19 and the engines are the ones already here (transfer14 mostly,
then transfer52, lexsub, …). All 88 re-checked against the live OEIS.

The bug that had been hiding inside the sweep itself: `sweep_cf` sized its term list as
`off + len(DATA) + order + 12`, from the number of terms the ENTRY publishes. The agreement
test runs at `order` consecutive indices above the annihilation threshold, and the threshold is
a property of the model, not of the entry. An entry with 17 published terms and a degree-30
polynomial asked for index 131 of a list of 61; the IndexError was caught and recorded as
"closed form evaluation failed", 13 times out of 36. The threshold is taken first now and the
list sized from it.

## 14 September 2026 — the Galebach certificate, decided rather than sampled

No results yet; the part that was unsound is now sound, and it is not the part that blocks.

`galcert` decided the two Bellman conditions by sampling three points per cone. Wrong twice:
`_cone_points` could not tell whether its three points lay in the cone (it returned `None` and
the cone was skipped in silence), and condition (c) is a **disjunction** — three points may
each have a different predecessor while no single one serves the whole cone. It certified
A310511, which diverges from its model at term 35.

`galpoly.py` does exact integer region arithmetic in the plane: vertices, recession rays,
emptiness, "affine ≥ 0 on a region", and subtraction of one region from another. Validated
against brute force on 1,494 random regions, no false claim. Only lattice points matter, so a
violated constraint is written `≤ -1` and there is no strict inequality in the file.

`galcert2.py` uses it: the region where affine piece *i* is the maximum is a polyhedron, so (b)
is an affine inequality on it, and (c) says that polyhedron is **covered** by the neighbours'
equality regions — decided by subtracting them one at a time. Results:

| | galcert | galcert2 |
|---|---|---|
| A310511 (diverges at term 35) | certifies | **refuses** |
| A310102 (diverges at term 30) | refuses | refuses |
| Gal.1.1.1 honeycomb | certifies | **certifies** |
| Gal.1.2.1 | — | **certifies** |

`galfit.py` is now the one place that turns (tiling, vertex) into planes and edges, and it
makes a check `galhull` does not: the fit is made on the inner patch and **validated on the
whole patch, rim included**. `galhull.pieces` reports "no leftovers" when its max reaches every
point it was *given*, and its supports were only ever validated against those same points — at
radius 110 one fit had no leftovers and still exceeded the true distance by one at 35 rim
points. The rim check says so in half a second instead of leaving it to the certificate.

What blocks the vein now is the FIT, not the certificate — and that is a better place to be.

## 14 September 2026 — running total for the day

Roster **13,000 → 13,276 papers over 13,249 entries**, and 157 → **159 arguments**.
276 results:

| | |
|---:|---|
| 144 | the closed-form pool, rebuilt from the clone after the hand-made one went stale |
| 82 | the recurrence or polynomial the entry defers to a linked a-file |
| 5 | generating functions lost to an attribution in square brackets |
| 3 | cusp-form dimensions, from splitting a line that carried three claims |
| 17 | Galebach coordination sequences — a new argument |
| 5 | a claim that names a degree and no coefficients — a second new argument |
| 20 | conjectured P-recursive recurrences, from an algebraic generating function |

Every one re-checked against the live OEIS. All the sweeps are still running.

## 14 September 2026 — the Galebach coordination sequences: 2 results, and a thin vein measured

A **158th argument**, `tiling-coordination`. The first two results on the family that has been
open since the tilings were rebuilt:

| entry | tiling | claim proved |
|---|---|---|
| A315405 | Gal.3.15.3 | `a(n) = 3a(n-1) - 4a(n-2) + 3a(n-3) - a(n-4)` for n > 4 |
| A315418 | Gal.3.21.3 | `a(n) = a(n-1) + a(n-5) - a(n-6)` for n > 6 |

In both the last nonzero residual sits at exactly the index the entry claims, so the stated
bound is tight. The chain: `galtile` rebuilds the tiling exactly in `Z[ζ24]`; `gallat` finds
the translation lattice **in the caller's own embedding** and verifies each generator is a
graph automorphism; `galfit` fits the distance per orbit as a max of affine pieces and
validates it on the patch **rim**; `galcert2` proves it IS the distance by deciding the two
Bellman conditions on regions via `galpoly`'s exact integer polyhedron arithmetic; `galehr`
counts the ball exactly and derives the Ehrhart period and onset.

### And the honest measurement: the vein is about 2%, not 379

Over 98 of the 379 entries scanned:

| | |
|---:|---|
| 72 | the fit fails on the patch **rim** |
| 12 | the distance is not a max of affine pieces even on the inner patch |
| 7 | fit timed out |
| 4 | the certificate refuses (the fit is exact on the patch and wrong off it) |
| 2 | **certified** |

The rim failures were measured for direction, which is the thing that decides whether a bigger
patch would help: of 17 sampled, **13 have the fit EXCEEDING the true distance** (by up to 5)
and only one is exact. A support fitted inside that exceeds `d` outside means `d` is not
convex, and then **no** max of affine pieces equals it and no radius fixes that. Refining to a
sublattice of index up to 4 did not help on the case tested.

So: the max-of-affines premise reaches a small minority of these tilings, and for the rest the
model would have to be piecewise affine on a subdivision that is not convex. `galcert2` would
verify such a D unchanged — it never uses convexity, only that the pieces are polyhedra — so
the open problem is producing the subdivision, not certifying it. The sweep (`galrun.sh`) is in
`restart_all.sh` and will grind the remaining 281 entries at its own pace.

One off-by-one worth recording: `galcoord.terms` documented these entries as offset 1 and
`threshold` believed it. They are offset 0 — all 379 of them. On A315405 that reported the
recurrence failing at n = 5 when it fails at n = 4, which is the difference between
contradicting the entry's stated range and confirming it. And `S` was returned as the period
q when the annihilator is `(z^q - 1)^2` of degree 2q, which would have put a run half the
length it needs behind the theorem.

## 14 September 2026 — the claim that names a degree and no coefficients

A **159th argument**, `polynomial-degree`. Seven entries in the pool say only

    Empirical: a(n) is a polynomial of degree 26 for n>13

and nothing here read them: there is no formula, so `ratrec` and `closedform` both decline. But
the claim is decidable by machinery already present, because it is two linear recurrences:

* `a` agrees with a polynomial of degree at most `d` on `n ≥ N` **iff** the (d+1)-st finite
  difference vanishes there — that is, `(z−1)^(d+1)` annihilates `a` from `N+d+1` on;
* the degree is exactly `d` **iff** `(z−1)^d` does not annihilate the tail.

So the entry's "for n>k" predicts a threshold of precisely `k+d+1`. That prediction is what is
tested, and it is what makes the reading of the English defensible rather than assumed:

| entry | degree | claimed | threshold | k+d+1 |
|---|---|---|---|---|
| A201350 | 31 | n > 10 | 42 | 42 |
| A201351 | 63 | n > 22 | 86 | 86 |

Both tight, both installed, both live-checked. `(z−1)^d` refuses on each, so the degree is
exactly the one claimed and not smaller. The sweep is still grinding the remaining five —
degrees 127 and 80 are large enough that the annihilation test is minutes, not seconds.

`degbuild` writes these papers rather than `unibuild`, because the theorem is **not** a
recurrence: printing `(z−1)^(d+1)` as "the conjectured recurrence" would state something the
entry does not say.

## 14 September 2026 — the conjectured P-recursive recurrences: a large claim pool, a small proof pool

**459 open entries** conjecture a recurrence with polynomial coefficients in n,
`sum_i p_i(n) a(n-i) = 0`. `ratrec` reads constant coefficients only, so not one was ever asked
about — larger than the linked-a-file vein by claim count. `precrec` reads **380** of them.

But the claim being readable is not the same as the claim being provable, and the measurement
is blunt: of the 380, **24 have a generating function the entry states as FACT and that is
explicitly algebraic** — the only route `holonomic` can take, where the claim becomes

    B(x) = sum_i x^i (p_i(theta+i) A)(x),  theta = x d/dx,

an element of an algebraic function field, zero exactly when the recurrence holds for every n
and a polynomial of degree d exactly when it holds for every n > d. An identity of functions,
not a check of terms.

Every other refusal — 155 of the first 158 asked — says the same thing: **no factual algebraic
generating function**. The reader is not the limit here; the proof route is. The 88 entries
with a binomial or `Sum_` formula are `zeilb`'s territory (creative telescoping) and the rest
would need the closure properties of holonomic functions, built from the entry's definition
rather than read off it. Both are real work, and this is the first vein today where the
obstacle is mathematics rather than instrumentation.

### An error found in an entry, not a conjecture disproved

A116388 states, as fact and not as a conjecture,

    G.f.: 2*x/(sqrt(1-2*x-3*x^2)*(sqrt(1-2*x-3*x^2) -1 +2*x +3*x^2)).

That series begins 2, 0, 10, 12, 62, … The entry's published terms are 1, 1, 4, 10, 29, … and
the expression in the entry's own NAME, `1/((1+x*(1-M(x)))*sqrt(1-2*x-3*x^2))` with M the
Motzkin g.f., reproduces them exactly. Checked by hand; the two expressions differ by a
nonzero algebraic function. So the `G.f.` line is wrong.

This is an error in a formula stated as fact — **not** a disproof of a conjecture, and it is
not counted as a result. It is recorded because the sweep's guard is what caught it: the stated
generating function is checked against the entry's own terms *before* it is allowed to be the
premise of a proof. Without that check the sweep would have proved a recurrence from a false
premise and never known. `algf` now prefers the name's expression when the formula section has
none, for the same reason.

## 14 September 2026 — the telescoping machinery was run once in August and never given a runner

`zeil_run`, `zeilb_run` and `hyp_run` implement creative telescoping with the boundary
correction, Ore right-division, and the hypergeometric-value conversion. They have produced
11 installed results. Their result files are dated **29–30 August** and there is no runner for
any of them in `restart_all.sh`: the machinery was run once, by hand, and nothing has asked it
anything in over two weeks.

Reading what those August runs refused, across 761 recorded verdicts:

| | |
|---:|---|
| 542 | no usable hypergeometric sum formula |
| 65 | summand does not vanish outside the stated range |
| 28 | boundary correction not computable for this range |
| 21 | **PROVED** |
| 19 | no telescoper found up to the order tried |
| 19 | **skipped: the conjecture line would not parse** |
| 16 | timeout |

The 19 parse skips are **stale**. Every one reads `Conjectured to be D-finite with
recurrence: ...` or `Conjecture: D-finite with recurrence ...`, and `prove_rec.parse_conj`
handles all of them today — it was fixed at some point after that run and nobody re-asked.
`zeilbrun.sh` is now in `restart_all.sh`, writing shards 3–5 so `harvest.py`'s existing
`zeilb-[0-9].json` glob picks the results up and the August files' own done sets do not
suppress the re-ask. 309 candidates.

### Three results held back for the right reason

The August runs proved 14 distinct entries; 11 are installed and **3 are not** — A010845,
A160906, A183204. Each looked like a free result sitting uninstalled, which is the shape of
the gfonly vein that had 241 results held and invisible. They are not. All three are flagged
**not open**, and the entries themselves say why:

* A010845 — "Mathar's recurrence above follows easily from this" (an e.g.f. differential equation);
* A160906 — "R. J. Mathar's conjecture verified using differential equation …";
* A183204 — "The conjectured D-finite recurrence can be proved by Zeilberger's algorithm."

Someone else settled each of them on the entry. Verified by hand that the summand reproduces
every published term and the recurrence holds on the data — the mathematics is fine; the
conjectures are simply not open, so they are not results. `openness` did its job.

## 15 September 2026 — the reader defects behind a "null", and continued fractions

**11 new papers, roster 13,280 → 13,291 over 13,264 entries. One null withdrawn as mine.**

### The null that was mine (IDEAS §Z, corrected in place)

§Z recorded, as a measured fact, that all 40 entries of the `(s(0), s(1), ..., s(n))` lattice-
path family "carry no readable claim of any kind, because nobody conjectures a linear recurrence
on a Motzkin number". That was measured with readers that could not read a P-recursive
recurrence — the exact shape a Motzkin-like sequence takes. Re-measured: **16 of the 41 carry a
readable claim, every one P-recursive.** The family looked empty because of the reader.

What the re-measurement found instead is a real refusal: of the 14 off the roster, 13 state no
generating function at all — a claim with nothing to prove it against — and closing those needs
the g.f. derived from the walk, which is a new argument, not a better reader.

### Five defects in `algf`, each one entry's refusal blamed on the entry

Found by asking why the fourteenth of those, A026110, was refused:

1. `with M the g.f. of the Motzkin numbers (A001006)` — the citation regex could not cross the
   opening parenthesis before the A-number. One character.
2. The clause splitter recognised `where` but not `with`, so the clause stayed in the body.
3. `G.f.=...` — the separator can be `=`, not only `:`, and `O.g.f.` is the same line as `G.f.`.
   A171853's body began with an equals sign and could not be parsed at all.
4. `[...]` and `{...}` are GROUPING in this corpus. sympy read A171853's denominator as a list.
5. An entry may state its g.f. at a different index origin from its own offset (A026110 is
   three below). The shift is not guessed: it is the one reproducing the whole published run.

And one **soundness** gap, which is the more important of the two kinds: `CONJ` caught
"conjectural" and "empirical" but not **"seems to be"**, so A075045's openly hedged g.f. would
have been used as a premise the moment the clause parser could read it. Proving one conjecture
from another is not a proof. Now caught.

Regression over the whole 375-entry P-recursive pool, old reader against new: **10 gained, 0
lost, 0 changed.** Three entries became slow rather than instantly refused; the implicit-clause
degree is now capped at 2, which costs no result (`holonomic.quadratic` refuses degree 3
anyway) and removes the hang.

### Papers installed

| | |
|---:|---|
| 7 | P-recursive, unlocked by the `algf` fixes — A026110, A026122, A026125, A026126, A026270, A026672, A228178 |
| 2 | P-recursive, from the earlier SLOW pass — A054109, A103138 |
| 2 | P-recursive, g.f. read as a periodic continued fraction — A152601, A292461 |

### Continued fractions (IDEAS §AC) — machinery kept, vein small

`algf.OUT` rejects any line containing the words "continued fraction", written when nothing
could read one. 1,509 entries state their g.f. that way. A periodic continued fraction is a
composition of Möbius maps whose tail is a fixed point, hence **algebraic of degree exactly 2,
always** — the field `holonomic.quadratic` already decides in. `src/cfrac.py`, no new solver.

The yield was **two results**, and the 1,509 should not be quoted as a vein: 1,015 are level-
indexed and genuinely not algebraic, 88 not open, 435 carry no conjecture, and 35 of the
remaining 42 were already on the roster. Seven entries were actually at stake. The size of a
grep is not the size of a vein.

### Defect recorded (the fifth of its kind)

A084261's continued fraction drifts `x^2, x^2, 2x^2, 2x^2, 3x^2, ...`. Read with two repeats as
evidence of a period, it produced a g.f. that failed the data check, and the sweep recorded
"the stated g.f. does not generate the DATA" — an accusation against the entry for a defect of
mine. Caught and reverted before it counted. Two repeats now suffice only when the period starts
at the top; three are required once a prefix is allowed.

### Telescoping

`zeilbrun.sh` merged: 175 records, 6 PROVED, **0 new** — all six are on entries already on the
roster except A010845, which the entry itself records as following from its own ODE. Correctly
withheld.

### Two more reader fixes, both measured, both null (IDEAS §AD)

`algf.from_name` could not read the standard trailing phrase "**in powers of x**" (1,552 names
carry it). Fixed; of the 756 with an x or z variable, **744 carry no readable claim**. Zero
candidates. `gfrec.parse_gf` — the reader behind the project's largest pool — accepted only a
g.f. with every `*` written out, refusing `1/(1-2x-x^2)`, `O.g.f.`, `G.f.=`, bracket grouping
and `z`. Fixed; measured corpus-wide rather than over the pool (**the pool was built by a
filter using that reader, so a regression over it is blind by construction**): 5 newly readable,
of which three state the g.f. inside a conjectural block, one is marked proved, and one says in
its own text that the g.f. implies the recurrence. **Zero results.**

Both fixes are correct and stay. Neither is a vein. The yield of a reader fix is not the size of
the refusal — it is the overlap between the refusal and the entries that state a claim.

### Rebuilding the pools (IDEAS §AE) — 21 more papers

**21 further papers; roster 13,291 → 13,312 over 13,285 entries.** Every candidate pool in
`deep-check/` is a snapshot made on the day it was written and nothing rebuilds them. Rebuilt
four from the clone:

| pool | held | corpus-wide | never asked | off roster | proved |
|---|---:|---:|---:|---:|---:|
| P-recursive | 380 | 989 | 609 | 123 | **3** |
| closed form | 416 | 728 | 564 | 564 | **18** |
| linked a-file | 192 | 888 | 696 | 35 | 0 |
| polynomial degree | 7 | 8 | 1 | 0 | 0 |

The closed-form 18 are all R. H. Hardin board-and-array counts with an empirical polynomial;
none failed. The three P-recursive are A239204, A141344 and A186338 — the last of these reads
its generating function as a periodic continued fraction, so `cfrac` paid a third result.

Degree was not stale: that phrasing occurs 8 times in the whole database. linkrec was not stale
either — the sweep needs an engine for the NAME, and 30 of its 35 new candidates have none — but
it did hide a defect of mine: it reads only CACHED a-files and reports an uncached one as
"a-file absent". All 35 were on oeis.org; fetched and re-run, and the refusal became honest.

### A new argument and a sixth self-inflicted disproof (IDEAS §AF)

**4 more papers; roster 13,315 over 13,288 entries; 159 → 160 arguments.**

`window-image-alphabet` (new, `src/window.py`): entries counting the arrays obtainable as the
windowed MAXIMA of a length-k array over `{0..n}`. Every engine here models a fixed alphabet
with n as the length; these invert it — the length is constant and the ALPHABET grows. The
greedy witness `a_i = min{b_j : window j covers i}` is exact and uses only b's own values, so
membership in the image depends solely on b's order type, and the count is
`sum_m A_m * C(n+1, m)` with `A_m` the achievable order types on m values. Exact, no fitting.
**A228462 and A228463.**

The median variants are NOT settled and are left refused: a median witness can need a value
strictly between two entries of b, and whether an integer sits there is a fact about the GAPS,
which the order type does not record. Four entries whose published terms my formula happened to
reproduce are therefore withheld — matching 30 terms is the standard of evidence the conjecture
already has.

Also **A171853**, P-recursive, readable after the algf fixes.

**The sixth self-inflicted disproof.** A118447's `.../8R^5` means division by `8R^5`; read left
to right it multiplies by `R^5`, and the sweep recorded "the stated g.f. does not generate the
DATA" against a correct entry. Fixed (`_denominator_run`), record deleted, regression over the
989-entry pool: 988 unchanged, 0 lost, A118447 the only difference. Six for six: every apparent
disproof this project has produced has been my reader, never a false conjecture.

### The premise reader, and three big greps worth five papers (IDEAS §AG)

**5 more papers; roster 13,320 over 13,293 entries; 161 arguments.** A056328, A056329, A082975
(new `gf-identity`: the entry asserts one generating function and conjectures another, and they
are the same rational function); A208995, A250883 (`gf-conjecture`, from the rebuilt pool).

**A soundness hole, found and closed with nothing installed behind it.** `algf` tested for a
conjectural word ON THE LINE, so a generating function inside a `Conjectures: (Start)` block read
as fact — proving the entry's recurrence from it would be proving a conjecture from itself.
`factlines.facts` exists for exactly this and records 1,336 papers once withdrawn for it.
Audited first: of the 36 entries with an installed `holonomic` paper, 33 took the premise from a
fact line and 3 from the NAME. **None affected.** Both readers now take premises only from
`factlines.facts`; regression over the 989-entry pool: 989 unchanged, nothing lost.

**The 2,211 "engine missing" bucket needs engines.** 2,204 of them assert no generating function
at all. The census's conclusion was right and my objection to it was wrong.

**Three large greps, five papers.** 1,509 continued-fraction g.f.s, 3,593 `Empirical g.f.` lines
(against the 131 `equate`'s filter could see — defect 2 again, in a vein with four papers), and
2,211 claim-readable entries. Every filter defect was real; the populations behind them were not.

### A vein with no builder, and two papers stopped by hand (IDEAS §AH)

**6 more papers; roster 13,326 over 13,299 entries; 162 arguments.** `sweep_recgf` — a
conjectured generating function proved from a recurrence the entry states as fact — had six
proved records and **no builder at all**. `src/rgbuild.py`, `src/build_recgf.py`, engine
`recurrence-to-gf`: A162698, A007388, A121138, A063219, A083178, A065261.

Applying the §AG.3 filter lesson to that vein's pool found ten never-asked entries; three
proved, and **two of the three would have been unsound**:

    A020745  a(n) = 2*a(n-1) - a(n-2) + a(n-3) - a(n-4)
             (holds at least up to n = 1000 but is not known to hold in general)
    A153368  Heuristically, a(n) = +6*a(n-2) -9*a(n-4) +2*a(n-6).

Neither carries a conjectural word and `factlines` read both as premises. A formula qualified by
a finite range is not a fact and neither is a heuristic one. Both now rejected, along with
"probably" (130 in the clone), "presumably" (71), "checked/verified up to n = ...".
**Audited: zero installed papers rest on a line the widened test rejects.** Caught by reading
the three results by hand before installing them, which is the rule that keeps paying.

### The second-conjecture vein, audited before installing (IDEAS §AI)

**No papers installed from it yet, deliberately.** `sweep_second` holds 244 proved records and
has no builder — `install_vein` skips an entry already on the roster, and a second paper on the
same entry is what this vein produces. Before writing that plumbing the argument was read, and
it did not close:

for another RECURRENCE, `q | p` is the whole proof; for a **closed form** it is not. `q | p`
shows `a` and `f` satisfy the same recurrence and says nothing about which solution each is. The
window check — agreement at D consecutive indices, past where `a` provably satisfies `p` — was
missing. Added. Re-asking all 244: **one is refused by it outright**, and the other 243 were
being asserted on an argument that did not close.

Also: `PROVED`, the premise store, read a hand-written list of eleven hits files; it now reads
all of them. 44 entries still drop because their proof is a generating function rather than a
recurrence and so carries no coefficients — deriving the premise from a proved g.f.'s
denominator is the next widening and is not yet done.

**My own defect:** the rebuilt closed-form results were written to `cfnew_hits.json`, a filename
that already existed, destroying sixteen records. Recovered from git and merged. Noticed only
because `PROVED` reads that file.

Sweeping the 1,460 roster entries added since the pool was built gives 21 further settled
conjectures, all of which pass the new window check. They are held, not installed, until the
builder exists.

### The rebuilt name-readable pool starts paying (IDEAS §AE)

**16 more papers; roster 13,342 over 13,315 entries.** The first 439 of the rebuilt 1,727
name-readable candidates give 16 proofs and no failures; the sweep is still running on the rest.

One more glob defect on the way: every TAGGED run of `sweep_shard` writes
`shard<TAG>_hits_<i>.json`, and `newlist.py` globbed `shard_hits_*.json`, which matches only the
untagged run. A sweep over a rebuilt pool was invisible to the installer for the sake of one
pattern — the same shape as the eleven stale filters, in the file names rather than in a pool.
The pattern is now `shard*_hits*.json`, which covers every tag at once.

### The second-conjecture vein installed: 235 papers (IDEAS §AI)

**235 papers; roster 13,577 over 13,315 entries; 163 arguments.** These are SECOND papers on
entries that already carry one, and they are second RESULTS because each settles a different
conjecture — 234 closed forms and one further recurrence, none of them a restatement of the
proved recurrence in other notation (those are identified by the sweep and excluded; there were
145 of them).

Three pieces of plumbing that did not exist:

* `src/sndbuild.py` and `src/build_second.py` — the vein had 244 proved records and no builder.
* `install_vein.py` gained `ALLOW_SECOND`, an explicit per-run opt-in that lets a second paper
  onto an entry already on the roster, and only when the record NAMES the conjecture it settles.
  262 entries now carry more than one paper, up from 27.
* the engine `second-conjecture` in `rank.py`'s TIER.

Every one of the 235 passes the window check added this round (§AI.1), and every one was
re-confirmed against the live OEIS before installation. The paper states the window explicitly:
for a closed form, `q | p` plus agreement at D consecutive indices past the point where the
sequence provably satisfies `p`.
