# Pending batch notes

## 15 September 2026 — ten more, and an eighth self-inflicted disproof

**10 papers; roster 13,718 → 13,728 over 13,325 entries; 163 → 164 arguments.**

Nine from the rebuilt name-readable pool (§AE), which is now in the standing rotation as
`np2run.sh` and had reached 623 of its 1,727 entries. One new argument below.

### The pending-result scan, and what most of it was

189 A-numbers sat in `*_hits*.json` files without a paper. Read one by one: 19 had been
withdrawn, 18 are no longer open, and most of the rest are not results at all —
`brack_hits.json`, `residual_hits.json`, `extr_hits.json` and others are CENSUS files whose
records carry no proof, and they match the `*_hits*` glob only by their names. Of the genuinely
proved and uninstalled, `known_hits.json` holds 7 and `uni_hits.json` 2, and **eight of those
nine entries are marked settled on the live OEIS** — each names the person who proved it, two of
them in 2026 arXiv preprints. Correctly withheld, and worth saying plainly: that file's "PROVED"
means this project's machinery closed it, not that the conjecture was open.

The ninth, **A034267**, was open and is a real result.

### `hypergeometric-ratio` (new argument, `src/hyperrec.py`)

A034267 states `a(n) = binomial(2n, n+1)(n^2+n+1)/(n+2)` as a fact and conjectures a second-order
P-recursive recurrence. The closed form is hypergeometric — `a(n)/a(n-1)` is a rational function
of n — so the sequence satisfies an exact FIRST-order recurrence, and the conjectured one is
settled by reducing it with that ratio. The reduction is identically zero in `Q(n)`: an identity,
not an agreement of terms. **No generating function is needed**, which is the point, because 228
entries in the P-recursive pool state none at all.

Measured over the whole 989-entry pool it is **one entry**, and the first measurement said zero
for a reason worth keeping: `closedform.parse_line` refuses `binomial(...)` outright, so a census
built on it cannot see the shape that makes this argument work. `hyperrec` has its own narrow
reader — binomials, factorials, powers, rational functions, nothing else.

### The eighth self-inflicted disproof

A060774 states `a(n) = 6*binomial(3n,n) - 6*binomial(2n,n)`, which gives 0 at n = 0 where the
entry has 1 — the empty path — and matches every term after it. Demanding agreement from the
offset made that "the stated closed form does not generate the DATA", an accusation against a
correct entry. A closed form is routinely stated for n past the first index or two; what is
required is agreement from SOME index on, with enough terms after it to mean anything, and the
conjecture is then proved from that index. A060774 now refuses honestly and for a different
reason: a SUM of two hypergeometric terms has no rational ratio.

**Eight for eight.** Every apparent disproof this project has produced has been my reader.

## 15 September 2026 — the table-column pool rebuilt: 296 new candidates, no results

`deep-check/tabpool.txt` held 1,729 entries; rebuilt from the clone on the same criterion (an
entry stating a per-column recurrence, off the roster) it is 1,851, so **296 were never asked**.
Swept: **zero results**, and the refusals are worth more than the zero.

| | |
|---:|---|
| 181 | the name is not a `T(n,k)` table |
| 108 | no explicit column recurrence |
| 5 | nothing proved on this table |
| 2 | not open |

Two defects found on the way, both fixed:

**The 276 that vanished without a counter.** `sweep_table` skipped every name not beginning
`T(n,k)` and recorded nothing — defect 3, the one STATE.md has carried since the beginning. The
skip is now counted, which is how the 181 above is known at all.

**The layout wrapper.** The corpus writes the same table a dozen ways — "Triangle read by rows:
T(n,k) is ...", "Array read by descending antidiagonals: A(n, k) = ...", "Triangular array read
by rows: ..." — and the wrapper says how the table is LAID OUT, which matters to the reader of
the data and not at all to the name of column k. `tablecol.PREFIX` strips it, and 115 of the 296
became rewritable. None proved, but the widening applies to the standing pool too.

The 108 "no explicit column recurrence" are honest: they state a **generating function** for
column k (`G.f. for column k: (1-x)^2*x^k/(...)`) rather than a recurrence, which is a different
argument — `gfrec` per column, with the conjecture still to be found. Noted, not built.

## 15 September 2026 — the pool-rebuild campaign, finished and tallied

Every candidate pool in `deep-check/` is a claim about the database made on the day it was
written, and nothing rebuilds them. All of them are now rebuilt from the clone:

| pool | held | in the clone | never asked | proved |
|---|---:|---:|---:|---:|
| `second.txt` (further conjectures on proved entries) | 13,139 | 13,315 | 1,460 | **376** |
| `namepool.txt` (readable claim + readable name) | 1,446 | 1,727 | 866 | **25** so far |
| `cfpool_cands.json` (closed form) | 416 | 728 | 564 | **18** |
| `prec.txt` (P-recursive) | 380 | 989 | 609 | **3** |
| `gfpool.txt` (conjectured g.f.) | 2,893 | 2,767 | 624 | **2** |
| `tabpool.txt` (table columns) | 1,729 | 1,851 | 296 | 0 |
| `linkrec.txt` (linked a-file) | 192 | 888 | 696 | 0 |
| `rowpool.txt` (table rows) | 444 | 573 | 26 | 0 |
| `gfdef.txt` (conjectured rec + factual g.f.) | 2,817 | — | 10 | 0 |
| `recgf.txt` (conjectured g.f. + factual rec) | 1,048 | — | 3 | 0 |
| `degree.txt` (polynomial degree) | 7 | 8 | 0 | 0 |

**424 papers from eleven rebuilds**, and the zeros are as informative as the numbers. Three
pools were not stale at all — `degree` because the phrasing occurs eight times in the whole
database, `recgf` and `gfdef` because their criterion is narrow enough that the original scan
caught nearly everything. `linkrec` and `tabpool` were stale by hundreds and still paid nothing,
because both need an ENGINE for the name and the rebuilt entries do not have one; that boundary
is the same one the refusal census found from the other direction.

**The rule, now with eleven measurements behind it: rebuild a sweep's pool from the clone before
running it again.** It costs one sharded scan. It was wrong eight times out of eleven.

## 15 September 2026 — `engine/src` split before it hit GitHub's listing cap

913 tracked files against a 1,000-entry cap. 525 of the 882 Python files were referenced by no
import, no runner and no document — one-off scripts from past rounds — and moved to
`engine/attic/` with `git mv`, which leaves `src/` at 470 and deletes nothing.

**Two static scans were wrong before one was right.** The first missed every name after the
first in `import entry, phispec, phitex, phimeta`. The second missed `uniform.py`'s 133 engines,
which are loaded through `importlib.import_module` over a list and appear in no import
statement. 82 files came back. The check that settled it reads imports with `ast` and resolves
each name against `src/` or an installed package — and it must not be done by importing, since a
sweep module RUNS on import and an import-based smoke test starts the whole engine.

Verified after: 0 unresolvable imports across all 470 files, every `src/*.py` named by a runner
exists, every path named in the documentation exists, `restart_all.sh` brings up 20 runners, and
`status.py` runs.

`engine/` itself is now the largest tracked directory at 714 and grows with every sweep, because
the hits and done files live there and every script opens them by bare name from `cwd=engine`.
Moving those is a real refactor, not a `git mv`. Recorded as defect 32 so it is done before 1,000.

## 15 September 2026 — the column generating functions: measured, and null

108 table entries refused as "no explicit column recurrence" state a **generating function for
column k** instead — `G.f. for column k: (1-x)^2*x^k/(...)`. Substituting a particular k gives a
rational g.f. for that column, so `gfrec`'s argument would apply per column. Measured before
building anything: of the **202** entries in the rebuilt table pool that state such a line,

| | |
|---:|---|
| 191 | conjecture **nothing at all** |
| 6 | conjecture something that is not about a column |
| 5 | conjecture something about a column |

and of the five, two are conjectured column g.f.s with no factual premise to prove them from,
one is an asymptotic, one a supercongruence, one a combinatorial identity. **Nothing to build.**
A g.f. for column k is usually the whole content of such an entry, not a premise sitting beside
a conjecture.

## 15 September 2026 — `sweep_second` re-asked as the roster grows

The vein's premise store is the roster itself, so every paper installed gives it something new
to work with. Ten entries joined the roster after the 376-paper pass; re-asking just those gives
**one** further conjecture, A222892 — its existing paper proves a fourth-order recurrence, and
the new claim is a closed form contributed separately. Live-checked and installed.

**Roster 13,729 over 13,325 entries, 164 arguments.** Re-ask this sweep after any batch; it
costs seconds for ten entries and it is the one vein that grows with the project's own output.

## 15 September 2026 — the engine root: measured, thinned of scratch, and NOT refactored

`engine/` reached 716 tracked files against GitHub's 1,000-entry listing cap, growing by 101 in
one day. Measured before acting:

* **all 682 root JSON files are read by some current code path** — literal `open()`, a glob, or a
  name assembled at run time — so the directory cannot be thinned by deleting dead data;
* they are tracked on purpose: a container restart wipes the engine, so a sweep's state survives
  only in git;
* they are opened by bare name from `cwd=engine` in **105 source files**, many with names built
  at run time, so moving them is a real refactor and not a `git mv`.

What it CAN be thinned of is scratch. **92 of the 101 files added today were one-off runs** — a
rebuilt pool asked once, an experiment, a measurement — and every proved record in them was
already in the canonical file beside them. Checked before removing: exactly two records existed
nowhere else, A020745 and A048580, and both are the deliberately refused ones whose premise is
hedged. Untracked; the root is at 624 and `engine/scratch/` is in `.gitignore` for the next one.

**And the refactor is not being done.** What the cap costs is a truncated directory LISTING on
github.com — a browsing cosmetic, not a broken clone — and the growth was almost entirely scratch,
which is now ignored. Doing an invasive move of 682 files across 105 call sites to fix a display
limit would be the wrong trade. Recorded in STATE.md under defect 32 with the measurement, so the
next round decides from numbers rather than from the alarm.
