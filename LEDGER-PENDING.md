# Pending batch notes

Batch notes are appended here by the hourly working routine and folded into `LEDGER.md` by the
daily one.

## 21 September 2026 (continuing) — the transfer17 vein, tenth result

**A252404**, S=17,865, an **order-84 recurrence with 28 coefficients**, stated on the entry for
`n>87` against 21 published terms — the claim begins four times further out than the data
reaches, so nothing but a model could settle it. Coefficients identical to the entry's own line,
threshold on the entry equal to both the claimed and the computed one, kept by a fresh live OEIS
fetch. **Roster 13,774 → 13,775.**

Ten results now from a population that was refused by a number in a shell script.

The vein's refusals so far, which matter as much as its proofs: ten entries at `W=7..8` exceed
`MEMGB=5`, and `uniall_tmo.json` is still absent — **not one entry of this vein has run out of
budget.** They refuse at the cap or at memory, quickly. Defect 49 says the historical record of
cap refusals cannot be trusted; this vein is evidence that it is not wrong everywhere.

## 21 September 2026 (later) — eleven from the transfer17 vein, and what is actually refusing the rest

Eleventh result: **A252154**, S=18,867, order 11, `n>16` against 24 published terms. All eleven
matched against the entry's own recurrence line and kept by a fresh live OEIS fetch.

**The vein's refusals, counted by what the entry was actually asked:**

| | t17small (55) | t17big (25) |
|---|---:|---:|
| proved and installed | **11** | 0 |
| exceeded memory | 13 at 5 GB | 5 at 7 GB |
| never asked at 8,000,000 | 31 | 20 |

An earlier reading of this called the vein read out, and it was wrong: `uniall_caps.json` still
recorded **2,000,000** for 45 entries — the cap of an older pass, not a current refusal. A stale
cap read as a current one makes a third of a list look settled. The cause was budgets longer
than a container generation: all three shards sat in a restart loop on the same three entries,
correctly re-asking (defect 47) and making no progress. Budgets are 420s now.

**Memory is what refuses this list** — more entries than the cap and the clock together, and
`uniall_tmo.json` is still empty, so not one entry here has run out of budget. Three shards at
5 GB claim 15 GB on a 15 GB machine, so the limit can only rise by running fewer: **two shards
at 7 GB now, and `t17big.sh` stopped to pay for it.** Its 25 entries produced nothing in three
hours while holding 7 GB. Moving memory from the population that has produced nothing to the one
that has produced eleven is the whole of the argument. The 13 entries refused at 5 GB re-open
automatically, because a memory refusal is skipped only while `MEMGB` is no larger than the
limit it failed under.

**`checkclaim.py`** now does the textual half of the binding by-hand check mechanically:
coefficient set lag by lag against the entry's own formula line, and the stated threshold
against both the claimed and the computed one. Disagreements are withheld and printed loudly;
an entry with no parsable line is withheld too and named, since absence of a line is not
evidence against a claim. It does not replace the reading — whether a line is the entry's
conjecture at all still needs a human pass, and that is what caught the `ca2dcount` family.
Validated against the eleven already installed: **11 of 11 re-verified, 0 disagreements.**

## 21 September 2026 (twelfth) — the memory reallocation pays for itself

**A251843**, S=66,006, an order-42 recurrence in steps of three, stated on the entry for `n>50`
against 19 published terms. Roster 13,776 → 13,777.

It is the first result found by `checkclaim.py` rather than by hand, and more to the point **it
is one of the 13 entries that had been refused at `MEMGB=5`**. Raising the limit to 7 GB — paid
for by stopping `t17big.sh`, whose 25 entries had produced nothing in three hours — released it
with no bookkeeping at all, because a memory refusal is skipped only while `MEMGB` is no larger
than the limit it failed under. The reallocation was argued from the counts and it returned a
result within the hour.

Twelve now. The vein's 55 small-shape entries stand at 12 proved, 14 refused at 5 GB and
re-askable, 29 never yet asked at 8,000,000.

## 21 September 2026 (evening) — a vein that did not exist yesterday

Fixing STATE.md defect 49 — every build timeout was being swallowed by `uniform.build`'s
`except Exception: return None` and recorded as a cap refusal — turned an invisible population
into a named one. Folding the shard files, including the **untagged** ones, which is where the
biggest runners write:

| | |
|---:|---|
| 3,362 | `uniall_caps.json` — the state space exceeded the cap |
| 117 | `uniall_oom.json` — the container refused it |
| **62** | `uniall_tmo.json` — the CLOCK refused it |

Every one of the 62 is off the roster, carries a parsable conjecture and is still open. The
budgets they failed under: **40 at ninety seconds**, 20 at 150, 2 at 420. Ninety seconds is a
seventh of the shortest container generation seen all day. `tmorun.sh` asks all 62 at 900.

Two faults of my own found on the way, both about reading rather than mathematics:

**`TAG=` is a real tag, and it is the one the biggest runners use.** 54 timeout rows appeared to
vanish between two commands; they were in the untagged shard files, and the command that listed
the tags rendered the empty tag as an empty string, so `" t17c "` read as "only t17c". Folding
the empty tag took the recorded timeouts from 2 to 59 and the out-of-memory rows from 60 to 116.

**The other half of defect 48.** `sweep_shard` skipped what the machine had refused but not what
the clock had refused, because `uniall_tmo.json` did not exist when that guard was written. So
`merge_shards` deleted the per-shard done file, the timeout rows went somewhere nothing read,
and both `t17c` shards looped on A252112 and A251948 for hours — recording correctly, advancing
not at all. Measured before fixing: A252112 asked alone under the runner's own settings reported
`build timed out` and wrote `{"A252112": 420}`. The machinery was right; nothing read it. With
the guard in place the vein moved again within the hour — 14 entries newly asked at 8,000,000,
ten of which genuinely exceed it.

## 21 September, late: five results, and the discovery that a third of the record had no witness

**Five results installed**, each on a distinct entry, papers 13,765 → 13,782.

| entry | order | evidence |
|---|---:|---|
| A183618 | 30 | 30 coefficients identical to the entry's own `Empirical:` line; holds at all 87 testable indices of its 117-term b-file |
| A208412 | 29 | threshold n>32; verified at 178 b-file indices |
| A252381 | — | checked mechanically against the entry's own recurrence line; its DATA guard read 22 terms |
| A252420 | — | checkclaim: coefficients and threshold identical; fresh live fetch, revision 6, open |
| A252470 | — | checkclaim: coefficients and threshold identical; fresh live fetch, revision 6, open |

**The finding that matters more than the five.** `sweep_shard` keeps a proved recurrence only
if it reproduces the entry's published terms, testing index `k` when `off + k > nthr` and
`k >= order`. A183618 has order 30 and fourteen published terms, so there was no such index:
the guard read nothing and printed what it prints on success.

**2,132 of 5,987 held results — 36% — are in that position.** They are not thereby wrong; the
model is matched against the whole of DATA before any recurrence is derived, and the recurrence
comes from the transfer matrix rather than a fit. What had no witness was the annihilation step
alone. Cached b-files supply one, and have now tested **2,358 proved recurrences at 412,240
indices, orders to 99, with zero failures**. `sweep_shard` falls back to the b-file when DATA
is short, and every hit records `btested`, so a result can no longer carry silence where its
evidence should be.

**Three defects.** (50) `BUDGET` is per-phase, so an entry costs `3*BUDGET`; five runners had
an outer `timeout` smaller than that, and four entries had been written down as 11 GB memory
refusals when a shell timeout killed them — withdrawn. (51) the guard above. And an
out-of-memory row can mean anything: A183618's said 6 GB and means 391 seconds and 0.07 GB.

**Still open:** 7,256 open conjectures have never been checked against their b-files — the
largest untouched population here, and the disproof side.
