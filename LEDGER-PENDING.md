# Pending batch notes

Batch notes are appended here by the hourly working routine and folded into `LEDGER.md` by the
daily one. Everything written before 20 September 2026 has been folded; this file is empty of
unfolded notes.

## 20 September 2026 — six installed, and a refusal list that was three things at once

**Installed: 13,739 → 13,745.** A186955, A230751 and A263664 (transfer-matrix, transfer-matrix,
bounded-displacement); **A185863**, the one result the new merged `transfer40` build bought; and
**A184710** and **A188239**, the first two from re-asking the capped entries that actually carry
a conjecture. Every one re-checked against the live OEIS before counting.

### What `uniall_caps.json` turned out to be

Three separate mechanisms write entries into it under the single label *state space > cap*:

1. **the pre-parse size estimate**, which fires before the entry is checked for a conjecture at
   all — so 1,255 of its 2,311 off-roster rows carry no conjecture to prove. `transfer40` has 3
   of 199; `latpoly` (133), `ca2d` (122) and `ca2dcount` (66) are real in full;
2. **a `MemoryError` flattened to `None`.** `uniform.build` wrapped its body in
   `except Exception: return None`, and `sweep_shard` reads `None` as the cap. Every build that
   outgrew its shard's `MEMGB` was recorded as a model too big for a cap it never reached;
3. **an engine of an earlier round** that genuinely refused where the current one does not —
   defect 34. A184710 builds in **353** states and A188239 in **41**, against a cap of
   2,000,000. Neither the cap nor a memory limit explains those.

**It is not a list of models too big to build. It is a list of entries some sweep declined to
finish, for reasons it did not write down.**

### The null that this explains

`caprun.sh` produced **0 proofs in 546 entries** of `deep-check/capped2.txt`. That null is real
and now accounted for: it was asking a list that is 57 per cent entries with nothing in them to
prove, at `MEMGB=1.5` — the tightest memory budget in the project, aimed at the population most
likely to need memory, where every out-of-memory came back wearing the cap's name. Rewritten to
sweep the 734 conjecture-carrying entries at 6 GB; `rcaprun.sh` added for the 255 `latpoly` and
`ca2d`. Both in `restart_all.sh`.

`sweep_second` on today's six new entries: **nothing** — five have too few terms past the
threshold to confirm the premise, one carries no further claim.

### The merged build: exact, verified, and aimed at the wrong population

`transfer40.build_merged` counts identically to the unmerged build on all 40 entries where both
succeed and on 590 parameter shapes, zero mismatches. Its bound opens 42 entries — and **40 of
the 42 contain no conjectural text at all**. The engineering was sound and the target was not.
A185863 and A186012 are the two that carry one; A185863 is installed, and A186012 builds at
`S=900096` under the cap but its lumping needs more memory than the container has with the
rotation up, so it sits in the new `uniall_oom.json` rather than being filed as capped.

### Three defects, two of them in my own measurements

**37.** The daily routine calls `src/ledger_table.py`; the `engine/src` split moved it to
`attic/`, so that step has ended with `can't open file` every day since and the ledger's RESULTS
HELD table had drifted 25 rows — precisely what its docstring says it exists to prevent. A
tidy-up that moves a file moves every path that names it, and the paths inside a scheduled
routine are not in the repository to be grepped.

**38.** A check reported **99 of 99 identical** and had compared nothing: its helper returned its
own `TypeError` as the compared value, so both sides matched. An exception must never be returned
as the value being compared — such a harness reports perfect agreement exactly when it is testing
nothing. The claim it produced was retracted before anything was wired in.

**39.** Catching an out-of-memory is not enough if the handler allocates. A186012's shard caught
one, then died inside `save()` — because saving allocates and the address space was still
exhausted — and left no file at all to say the entry had been asked. A failure the recorder
cannot survive leaves no trace, which is worse than the wrong label.
