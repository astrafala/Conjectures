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
