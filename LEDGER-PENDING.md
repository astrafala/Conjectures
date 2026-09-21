# Pending batch notes

Batch notes are appended here by the hourly working routine and folded into `LEDGER.md` by the
daily one. Everything written up to and including 20 September 2026 has been folded; this file
holds no unfolded notes.

## 20 September 2026 (later) — the transfer21 vein read out in full

`uniform.build` now dispatches `transfer21` to `transfer17.build_pairfree`, verified on 243
shapes with zero mismatches. The whole capped `transfer21` population has since been asked, and
the reading is complete:

| | |
|---:|---|
| 78 | capped off-roster `transfer21` entries |
| **5** | proved and installed |
| 73 | asked again and still over the cap |
| 0 | left unasked |

Fifteen of the 78 carried a conjecture and all fifteen were refused a priori by
`transfer17.build`'s `(alpha+1)^(2W) > cap` test and by nothing else. **Five of those fifteen
now build and prove**; the other ten exceed the cap for real, not a priori. At `W=7` over
alphabet `0..2` the pair test demands `3^14 = 4,782,969` against a cap of two million, and the
pair-free build returns the same sequence in 663,553 states — so the a-priori refusal was
wrong about five entries and right about ten.

That is the honest shape of it. The swap was worth making and is permanent, and it bought five
results rather than fifteen.

## 21 September 2026 — the rotation was spinning, and a withdrawal was short by four

**The machine.** Sixty-eight Python processes on four cores, and thirteen of the veins driving
them had nothing left to ask. A sweep that examines no entries prints an empty result dict and
exits, and every runner loop relaunched it immediately: five minutes after a container restart
wiped `/tmp`, the runner logs held about twenty-five thousand lines, almost all of them that
dict. Phase 5 — 1,904 entries of real work outstanding — wrote nothing for the fifty-five
minutes before the restart. Stopping the read-out runners for four minutes was the whole
experiment: its three shard states were written again at 02:04, 02:05 and 02:07.

A round that finds work takes minutes, so a round that returns in seconds found nothing. That
test reads the clock and needs nothing from the sweep, so it covers every script the runners
call. Twenty-eight runners now break out on a short round; `forever.sh` sleeps instead, because
it must not stop. **68 processes → 17, 23 of 30 runners stopped themselves**, and Phase 5 has
the machine. Breaking out is not retirement — `restart_all.sh` brings everything back an hour
later, which is when a changed engine could have reopened a vein.

**The results.** `merge_sharded.py` reported 419 second-conjecture results, and the installer
was reading a different file that stopped at 203 on 15 September. The gap looked like 138.

| | |
|---:|---|
| 138 | settled and not papered |
| 42 | premise not on the roster, and no record of it anywhere in the project |
| 93 | already withdrawn, correctly kept out |
| **3** | actually new |
| **0** | installed |

None of the three was installed, because checking them by hand is what found the real fault.
Two rested on `gf-conjecture` papers for the active-cell count of a two-dimensional automaton —
the class withdrawn on 13 September because that count has no proved generating function. That
pass took five and left four. All four have every formula line inside one `Conjectures from
Colin Barker: (Start)` block, no model anywhere in the project, and build numbers interleaved
with the five withdrawn. **Withdrawn: A270934, A273334, A273447, A273781. Roster 13,768 →
13,764.**

Eighty more `gf-conjecture` papers on that family are unresolved and are written up in STATE.md:
none of the 224 x-axis and diagonal entries states its generating function as fact, but the
`ca2d` vein does model the axis, so those may be sound where the active-cell counts cannot be.
That is a pass of its own, not a line in a batch note. The third new result, A277560, is one of
the eighty, which is why it was held too.

Net for the night: **no results added, four withdrawn, and the machine doing the verification it
had been prevented from doing.** The one honest number in the batch is 3, not 138.
