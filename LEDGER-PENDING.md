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
