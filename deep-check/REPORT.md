# The 10,000 deep check — report

The roster passed 10,000 on 7 September 2026 and `engine/src/dc_gate.py` reported the check
due. This file is the running record: what has been checked, what was found, and — as
importantly — what has **not** been checked yet.

**Corpus frozen at commit `cad282f`** — 10,054 papers, 10,027 entries, 21,236 tracked files
hashed. Every phase reads `deep-check/frozen-roster.json`, so the corpus cannot shift
underneath the check. Python 3.11.15; pdfminer 20260107; sympy 1.14.0.

## Phases run

| Phase | What it checks | Result |
| --- | --- | --- |
| 0 | Freeze and snapshot | complete; working tree clean at freeze |
| 1 | Inventory integrity | **8 checks, 0 failures** |
| 2 | Forbidden content | **10,054 papers, 0 defects** |
| 3 | The entry, re-fetched cold | **10,054 papers, 0 defects** |
| 7 | Caps, refusals, the untried | complete; findings below |

### Phase 1 — inventory integrity

Ranks are exactly 1..N with no gap or repeat; every indexed paper exists at the path the index
gives and every paper on disk is in the index; every paper sits in the band its rank belongs to
under the name its rank and verdict give; roster and index agree on every (A-number, verdict,
engine); no tracked directory holds more than 1000 entries; the list of source-less papers is
exactly the set of source-less papers; every top-level directory has a README.

### Phase 2 — forbidden content

No suggested-comment appendix, no pointer to a companion paper or a shared argument, no
drafting residue, no credential or foreign email address, in any of the 10,054.

### Phase 3 — the entry, re-fetched cold

Against the 7 September OEIS export: every paper names its own A-number; every term printed in
section 1 is a prefix of the entry's current DATA; every quotation the comparison can
adjudicate is exact.

What it also reports, which is the part worth reading:

* **414 papers typeset their quotation**, so the extracted text cannot equal the entry
  character for character; those are checked on their numbers instead — every integer of two
  digits or more, in order.
* **39 quotations the automated comparison cannot settle**, listed by rank. A string
  comparison is not entitled to a verdict on a typeset formula. **These are outstanding work
  for the reading pass (Phase 12).**
* **381 papers whose section 1 quote could not be located at all** — 3.8%, the early bespoke
  papers whose section 1 is laid out individually. **A gap in the check, not a defect in the
  papers, and outstanding.**
* **3 entries edited since their paper was written** (A079144 r71→r73 on two papers, A262482
  r13→r17). Not defects; the quotations still match.
* **25 entries carry settlement wording.** Every one was read: all 25 are about a different
  statement on the same entry. Two entries were withdrawn earlier the same day when the
  wording was about the same statement and the other proof was **earlier** — A105872 and
  A127361, proved by Easwar in arXiv:2608.22053, submitted 22 August 2026, three days before
  the date on those papers.

### Phase 7 — caps, refusals and everything not attempted

* Entries standing refused: **2,098 at cap 2,000,000** and 5 at cap 400,000.
* Of the candidates an engine reads and that are not settled: 4,052 carry no unsettled
  conjecture; **697 state a recurrence and have never been processed**; **313 state an order
  line and have never been processed**; 144 state a recurrence and were processed without
  being settled; 56 carry a conjecture of a kind no sweep tests; 1 order line processed and
  unsettled.
* **1,010 entries an engine reads, carrying a testable conjecture, never processed at all** —
  listed in `deep-check/phase7-never-processed.txt`. This is the largest single pool of
  untried work in the project.
* 14,699 names no engine reads; of the first 4,000 sampled, 169 carry something unsettled.

## Phases NOT yet run

**These are not passes. They are outstanding, and the check is not complete until they are
done.**

| Phase | What it must check |
| --- | --- |
| 4 | The reading, re-pinned — every paper's reading recomputed cold against published DATA, and every ambiguous word given every plausible reading |
| 5 | The mathematics, recomputed from cold, with every cache deleted; thresholds shown exact; merges verified; falsification beyond the verified range |
| 6 | The independent checks, themselves audited — including every swallowed exception and every ad-hoc regex outside the parser |
| 8 | Wording and logic — verdict agreement, the double-negation class, every number in prose recomputed |
| 9 | Length that follows content |
| 10 | Comments — one per entry, claim matching the paper, dates corroborated, OEIS-safe |
| 11 | The process itself — every mistake listed, every rule given enforcing code, duplicate work, padding audit, reproducibility |
| 12 | Adversarial referee pass over a stratified sample, plus the 39 + 381 quotations Phase 3 could not settle |

Nothing here is optional and nothing may be skipped for time. The corpus stays frozen — **no
new conjectures are added** — until the check finishes.
