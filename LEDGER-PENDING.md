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

Checking the three by hand is what found the real fault. Two rested on `gf-conjecture` papers
for the active-cell count of a two-dimensional automaton — the class withdrawn on 13 September
because that count has no proved generating function, so the degree bound the argument needs
does not exist. That pass took five and left four. Each of the four names the same S=24
`ca2dcount` model and the same transfer-matrix argument, a strip of consecutive rows taken as
the state of a finite automaton, which is what a fixed-width array count licenses and what an
automaton growing in every direction does not. **Withdrawn: A270934, A273334, A273447,
A273781.**

The third, A277560, turned out to be sound and **is installed**. It rests on a `ca2d` model of
the automaton's x-axis — a finite row at each stage, a real automaton, a real degree bound —
which is a different object from the active-cell count, and the distinction is the whole of it.
All 80 remaining `gf-conjecture` papers on this family rest on a `ca2d` axis model and **none is
at risk**; no roster paper anywhere still rests on a `ca2dcount` model. The 13 September pass
was complete on its own terms, and what it missed was four papers whose records had been pruned.

**Roster 13,768 → 13,764 → 13,765.** Net for the night: **one result added, four withdrawn**, and
the machine doing the verification it had been prevented from doing. The honest number in the
batch is 1, not 138.

The method error is worth more than either count. The first query for "does this project model
this sequence" looked for a `coeffs` key; a generating-function record has no `coeffs`, it has
`degnum` and `degden`, so the query reported "nothing models these twelve" about twelve entries
whose records read `engine: ca2d, S: 8` in plain sight. Ask what shape a record has before
asking whether it exists. And an absent record is not an absent proof: the four withdrawn have
no surviving record of any kind, and what settled them was reading the paper, which names its
own model in its abstract.
