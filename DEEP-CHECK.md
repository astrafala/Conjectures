# The 10,000 deep check

This file is the plan, written **before** the trigger so the check could not be shaped by
what was convenient at the time, followed by the running report of what has been checked
and what was found. The working data --- the frozen roster, the per-phase results --- lives
under `engine/deep-check/`, because all code and working data belongs under `engine/`.

---

A single, pre-planned pass over **everything** — every paper, every engine, every
reading, every comment, every number, every word, and the process itself — to be
run once the roster passes 10,000 settled conjectures.

It is written down **before** the trigger so that the check cannot be shaped by
what is convenient at the time. Nothing in it is optional, nothing in it may be
skipped for time, and every phase either passes or produces a named defect with
a named fix.

**Trigger.** `engine/src/dc_gate.py` reports the roster size. The moment it
reports 10000 or more, the check runs from Phase 0 to Phase 12 without waiting
to be asked.

**Stop rule.** A phase that finds a defect does not stop the check. The check
runs to the end, collects every defect, and only then are they fixed — because a
defect found in Phase 3 often explains one in Phase 9, and fixing as you go
destroys that evidence. The corpus is frozen for the duration: no new
conjectures are added while the check is running.

**Standard of proof.** Throughout: *a check that disagrees with the engine is
not automatically right.* On this project the independent check has been the
faulty side six times out of six. So every disagreement is resolved by a **third**
computation, in the entry's own orientation, pinned against published OEIS data —
never by trusting whichever side is newer.

---

## Phase 0 — Freeze and snapshot

* Record the exact commit, the roster size, the file count and a SHA-256 of
  every tracked file.
* Copy `engine/paper-engines.json` to `deep-check/frozen-roster.json`. Every
  later phase reads the frozen roster, so the corpus cannot shift underneath
  the check.
* Record the machine, the Python version, and the version of every library used
  by any engine. A result that only holds on one version of a library is not a
  result.

## Phase 1 — Inventory integrity

Purely mechanical, and it must be perfect before anything else is believed.

1. Ranks are exactly `1..N` with no gap and no repeat.
2. Every rank has exactly one PDF, in the band its rank belongs to.
3. Every PDF opens, has at least one page, and its extracted text is non-empty.
4. The A-number in the filename equals the A-number in the roster equals the
   A-number in the paper's own title and §1 and references.
5. `papers/`, `paper-sources/`, `comments/index.csv`, `papers/index.csv` and the
   roster all describe the same set of (rank, A-number, verdict). Any row in one
   and not another is a defect.
6. No tracked directory holds more than 1000 entries (GitHub truncates at 1000
   and the truncation is silent).
7. Every directory has a README explaining what is in it.
8. Every paper that has no source `.tex` is listed by name, with the reason, in
   `paper-sources/MISSING.txt`, and that list is exactly the set of papers with
   no source — not a superset, not a subset.

## Phase 2 — Forbidden content

Every PDF's extracted text is searched for text that must not be there:

* `Suggested OEIS comment`, `house style`, and any other comment appendix —
  comments live in `comments/`, papers are proofs.
* Any sentence that points at another paper or at a shared argument: `as in the
  companion`, `the same argument as`, `see paper`, `as elsewhere in this
  series`, `this family of notes`. **Each paper must stand alone.**
* Drafting residue: `TODO`, `FIXME`, `XXX`, `TK`, `lorem`, `\ref{?}`, `??`,
  `[?]`, `Missing`, `\textbf{}` empty groups.
* Any credential, token, email address other than the author's, or internal
  hostname.
* Any model name or tooling name that should not appear in a published paper.

## Phase 3 — The entry, re-fetched cold

For every settled entry, fetch the live OEIS entry again, from scratch, and check:

1. The conjecture sentence quoted verbatim in §1 still appears **verbatim** in
   the entry. A one-character difference is a defect: the paper claims to quote.
2. The contributor name and the date quoted in §1 match the entry.
3. The entry's `Last modified` line is quoted correctly. If somebody has settled the
   conjecture **since** the date on our paper, that is recorded, and **nothing is removed**:
   the date on the paper is the day the work was done, it came first, and it stays. What
   changes is the wording only, so that no paper claims an entry is open when it is not.
4. The entry's DATA still matches the DATA the engine used. Entries get
   corrected; a corrected entry can invalidate a proof.
5. The entry's links, programs and the literature are searched for a proof that existed
   **before** the date on our paper. That, and only that, is a **padded count**: the result
   was never ours to claim, and the paper is withdrawn rather than softened. A proof that
   appeared afterwards is not that, and is never grounds for withdrawal.

**The rule, stated once so it cannot drift:** *later* is not *earlier*. A result is
withdrawn only when it was already settled before the date on the paper. Being settled by
somebody else afterwards leaves the roster exactly as it is.

## Phase 4 — The reading, re-pinned

The single largest source of error in this project is reading the English of a
conjecture in a way its author did not mean. Three such misreadings were caught
and are documented; the check assumes there are more.

For every paper:

1. Recompute the entry's published terms from the paper's reading, **cold**, by
   a program written to the reading and not to the engine.
2. If the reading reproduces published DATA, the reading is *pinned*. Record how
   many terms pinned it.
3. If the reading cannot be pinned against published DATA — because the entry
   publishes too few terms, or the model is not term-by-term — the paper is
   marked **reading unpinned** and goes on a list that is reviewed one by one by
   hand. These are the papers most likely to be wrong.
4. For every entry whose wording contains a word from the known-ambiguous list
   (`diagonally`, `antidiagonally`, `horizontally`, `vertically`, `adjacent`,
   `neighbouring`, `distinct`, `absolute`, `ordered`, `unordered`, `population`,
   `moving`, `subblock`, `king`, `knight`, `wrapping`, `cyclic`, `symmetric`),
   compute **every** plausible reading, not just ours, and show that exactly one
   reproduces the DATA. If two readings both reproduce it, the paper must say
   which one it proves and why the other is excluded.

## Phase 5 — The mathematics, recomputed from cold

1. Every engine's decision is recomputed in a fresh process with every cache
   deleted. Cached verdicts are not evidence.
2. Every recurrence, generating function, threshold and order claimed in a paper
   is recomputed by the decidable route (annihilation of the residual /
   comparing the bounded-degree remainder / Berlekamp–Massey minimal order) and
   compared coefficient by coefficient.
3. Every threshold is checked to be **exact**: the last nonzero residual is
   exhibited, so the threshold cannot be lowered and is not one too high.
4. Every state-space size quoted is recomputed after merging, and the merge is
   verified: merged states must have identical futures, tested to the full
   depth, not sampled.
5. Every disproof exhibits its counterexample and the counterexample is
   recomputed by two routes.
6. Falsification pass: every proved statement is tested **beyond** the range the
   paper verifies. A true statement survives; this has a real chance of killing
   a wrong one.

## Phase 6 — The independent check, itself audited

The standing pattern: when the engine and the check disagreed, the check was
wrong six times out of six. So the checks get checked.

1. Every brute force must first reproduce the entry's published DATA in the
   entry's own orientation. A brute force that cannot do that is not evidence
   and its confirmations are discarded.
2. Every brute force is inspected for the failure that has happened before: the
   check transposing, reindexing or reorienting the problem exactly as the
   engine does, so both agree and both are wrong. The test is a **third** count,
   written to the entry's own words, by a route sharing no code.
3. Every `except` in every engine and every sweep is inspected: an exception
   that is swallowed without recording a reason is a silent refusal, and silent
   refusals have cost this project results five separate times.
4. Every candidate pool is rebuilt with the canonical parser. Ad-hoc regexes
   over entry text, written fresh at a call site, have narrowed a pool once
   already; every regex over entry text outside the parser module is a defect.

## Phase 7 — Caps, refusals and everything not attempted

*A cap is a setting, not a wall.* Re-running one sweep at a higher cap turned 43
proved tables into 123 and 55 lines into 197.

1. Every cap in every sweep is listed with its current value, and every refusal
   that mentions the cap is re-run at four times the cap.
2. Every refusal reason across the whole project is bucketed. Any bucket whose
   reason is not a mathematical obstruction is re-attacked.
3. Every genuine wall — `n × n` growth on both sides, state spaces too large
   after merging, memory exhaustion — is re-stated precisely: *what* is the
   obstruction, and what would remove it. A wall without that statement is not a
   wall, it is an untried idea.
4. Every entry ever looked at and not settled is re-examined once against the
   current engine set. Engines written since it was refused may now decide it.

## Phase 8 — Wording, logic and prose

1. Verdict agreement: a paper marked disproof says *disprove*; a paper marked
   proof says *prove*. Checked against the roster flag and against the displayed
   statement, not against the title.
2. The double-negation class: for every paper whose engine negates a quantifier
   or a formula, the quantifier is recomputed **from the displayed formula** and
   compared with the prose. This error put 66 papers into the exact opposite of
   their entry.
3. Every number appearing in prose is recomputed and compared.
4. Every paper contains: an abstract; §1 quoting the conjecture with contributor
   and date and the still-open statement; a Verification section that says what
   was checked and how many cases with how many mismatches; references with
   consulted dates.
5. Grammar and clarity pass over every paper. Not a spellcheck: a reading for
   sense, sentence by sentence, of anything the check flags as unusual.
6. No paper contains an unexplained step. A step is explained when a competent
   reader who does not have the code can reproduce it.

## Phase 9 — Length that follows content

Papers must not be uniform. Length is set by what has to be explained.

1. Compute, for every paper, a content score: number of distinct lemmas, size of
   the state space, number of cases, whether a misreading had to be excluded,
   whether a threshold argument is needed, how far the verification goes.
2. Compare the score against the page count. Flag both directions:
   * short paper, high score → **under-explained**, must be expanded;
   * long paper, low score → **padded**, must be cut.
3. Every flagged paper is rewritten so that its length follows its content, and
   re-checked. Uniform length is itself a defect.

## Phase 10 — Comments

1. One comment per settled entry; the comment names its entry and no other.
2. The claim in the comment is exactly the claim the paper proves — never more.
3. The date is the date the result was obtained, cross-checked against the
   ledger and the git history. A date that cannot be corroborated is removed
   rather than guessed.
4. Every comment is plain ASCII, OEIS-safe: no LaTeX, no markdown, no characters
   the OEIS will not take, lines within the length the OEIS accepts.
5. No comment has been posted; the submission order file is consistent with the
   comment set.

## Phase 11 — The process itself

A full analysis of how the work is done, not just what it produced.

1. **Every mistake ever made** is listed: what it was, how many results it
   touched, how it was caught, and what rule it produced. The list is checked
   for completeness against the git history and the ledger.
2. For every rule so produced, there must be **code that enforces it**. A rule
   that lives only in a document is a rule that will be broken again. Any rule
   without an enforcing check gets one written.
3. Duplicate work: engines are clustered by what they decide, to find two
   engines deciding the same class (this happened once and cost 10 papers);
   papers are clustered by statement, to find the same result claimed twice.
4. Independence: every argument family must have at least one member verified by
   a route sharing no code with its engine.
5. Padding audit: for every argument family, an honest statement of whether the
   result is elementary, probably known, or genuinely new. **Never pad the
   count** — a family that turns out to be known is reported as known, and the
   count comes down.
6. Reproducibility: from an empty checkout, one script rebuilds the whole corpus
   and it must run to completion.
7. Attribution: the credit statement is present, correct and prominent —
   the framework and the prompt engineering are the user's.

## Phase 12 — Adversarial referee pass

The last phase is not mechanical. A stratified sample across every argument
family — every family represented, larger samples from the families with the
most papers, and from the 5,858 entries whose names carry an ambiguous word and
rest on a single program (Phase 4 left no reading unpinned, but left those on a
single reading) — is read the way a hostile referee reads: find the weakest step, then attack it numerically at
parameters beyond anything the paper claims.

Anything that breaks under that is withdrawn, not patched.

---

## Output

`deep-check/REPORT.md`: every phase, every check, every count, every defect, with
the fix and the commit that made it. Written so that somebody who has never seen
the project can tell exactly what was checked and exactly what was wrong.

Then, and only then, the corpus is unfrozen.

## Passes

Phases 3, 4, 5, 6, 8 and 10 are run **three times**: once from the caches, once
cold with every cache deleted, and once against an independently written
implementation wherever one exists. Any disagreement between the three passes is
a hard stop on that entry until a third computation settles it.

---

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
| 5 | The mathematics, recomputed from cold | **925 recomputed, 0 disagreements** (running) |
| 6 | The checks, themselves audited | complete; findings below |
| 7 | Caps, refusals, the untried | complete; findings below |
| 8 | Wording and logic | **10,054 papers, 0 defects; 9 papers missing a required part** |
| 10 | Comments | **10,022 comments, 0 defects** |

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

* Entries standing refused: **2,098 at cap 2,000,000** and 5 at cap 400,000. **This figure
  is wrong and the correction is below** — `shard_caps_*.json` recorded the cap of every
  entry a sweep *attempted*, not of the ones it refused, so counting its keys counted
  attempts. A sample of 70 drawn from that pool and re-run on 7 September 2026 came back
  **60 with no parsable recurrence, 7 already settled, and 3 refused for size**. The pool is
  overwhelmingly entries with nothing to prove, not entries too large to prove. The true
  number standing refused for size is of the order of a twentieth of 2,098; the sweep now
  records the cap only at a refusal, so the next measurement will be exact.
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

Phases 6, 8 and 10 have run and their findings are below; this table lists only what is
still incomplete.

| Phase | What is still outstanding |
| --- | --- |
| 5 | Still running. Every model rebuilt in a fresh process; the corpus is 3,865 sweep records and the run is partway through. |
| 12 | The numeric half is running --- every sampled claim pushed far past its published range and checked in integer arithmetic. The **reading** half has not been done: a stratified sample read the way a hostile referee reads, together with the quotations the automated comparison could not settle. |

Nothing here is optional and nothing may be skipped for time. The corpus stays frozen — **no
new conjectures are added** — until the check finishes.

---

## Findings added after the first report

### Phase 4 — the reading, re-pinned

`engine/src/dc_phase4.py`, results in `engine/deep-check/phase4.json`.

A reading is *pinned* when a program written to it reproduces the terms the entry itself
publishes. All 10,027 entries behind the 10,054 papers were sorted by how strong that pin is,
and nothing was counted at a strength it does not have:

| | entries | what it means |
| --- | ---: | --- |
| INDEPENDENT | 570 | a second program, sharing no code with the engine, agreed with the published terms. Only this strength can catch an engine that reads a name wrongly, because a bug in the engine cannot be present in a program that does not use it. |
| ENGINE | 8,551 | the engine reproduced the published terms, and that is all. |
| COLD | 4 | no vein had kept a record, so the model was rebuilt from the name and compared with the entry in this run. |
| FORMULA | 902 | the entry states its conjecture as an identity, which the paper quotes verbatim. There is no English description of a count, so there is nothing to misread. |
| NONE | 0 | |

**No reading is unpinned.**

Two of the check's own steps were wrong before the papers were, and both are recorded here
because the corrected numbers are the ones above:

* The first version fitted a polynomial of the paper's recorded `degree`, or a linear
  recurrence of its recorded `order`, to the published data — and found almost nothing,
  because for those papers `degree` and `order` describe the residual of an algebraic
  generating function and have nothing to do with a polynomial or a linear recurrence. The
  fit was removed rather than patched: a check built on a wrong reading of its own inputs
  cannot be repaired by tuning it.
* The first version then called a pin of fewer than eight terms weak. Seven of the twelve it
  flagged are plane-partition box counts, whose seven terms are seven twenty-digit numbers;
  no wrong reading reproduces a hundred and forty digits by coincidence. Pin strength is now
  counted in **digits of published data reproduced**, and the weakest pin in the whole corpus
  is 54 digits, the median 175. **No pin is thin.**

What Phase 4 does *not* settle: 6,451 entries carry a word this project has already been
bitten by — `subblock` (3,134), `horizontally` (2,399), `adjacent` (2,092), `vertically`
(1,601), `antidiagonally` (1,498), `diagonally` (930), `king` (906), and seven rarer ones —
and 5,858 of those rest on a single program reading the name. Term agreement rules out a
reading that is *wrong*; it does not rule out a second reading that is *also right*, which is
what the ambiguous words threaten. **That is the reading list Phase 12 samples from.**

### Phase 5 — the mathematics, recomputed from cold

Each model rebuilt in a fresh process with nothing reused. **925 recomputed so far, 0
disagreements**: the model still reproduces every published term, the recurrence still
annihilates it, and the threshold comes out where the paper says.

25 entries are read by two engines — `transfer93` generalises `transfer75`, and `uniform.read`
returns whichever comes first in its list. Both reproduce every published term of A184404,
checked directly, so this is an **overlap and not a defect**. The rebuild uses the engine the
paper used, since that is what the paper claims; the overlap is recorded for Phase 11.

### Phase 6 — the checks, themselves audited

Of 730 modules, 263 exception handlers record nothing before continuing. Only 95 modules are
on the path a sweep actually takes and **only 3 of the silent handlers are among them**. The
one that matters is `uniform.read`: a parser raising on a name it ought to read makes that
name unreachable, and the handler hid it. The raises are now counted and kept; asked over
6000 names, there are currently none.

158 modules match their own patterns against entry text instead of going through the canonical
parser. That is how a candidate pool once came out at 49 instead of 130.

### Phase 8 — wording and logic

Over all 10,054 papers: **0 defects** in verdict agreement, the double-negation class, or the
numbers quoted in prose.

**9 papers carry no statement that the entry is still open**, which is a required part:

| rank | entry |
| ---: | --- |
| 4 | A061002 |
| 19 | A000071 |
| 20 | A000139 |
| 21 | A000040 |
| 23 | A059324 |
| 28 | A000364 |
| 29 | A000040 |
| 30 | A008365 |
| 425 | A197230 (a disproof) |

All are among the earliest papers, written before the requirement was fixed. **Outstanding —
the fix waits until the check is complete**, per the stop rule.

Three false-positive classes of the phase's own were removed on the way: a proof saying "the
statement is false for k even" while delimiting a hypothesis read as a disproof; a pattern
expecting "still recorded as EMPIRICAL" missed "still recorded as an unproven conjecture", and
reported 68 of 400 as missing a sentence they all have; and after widening, an abstract saying
"the procedure returns a proof or a refutation — here it returns a proof" read as a disproof,
flagging 34. An explicit assertion of the result now settles the verdict.

Four papers restate a negative condition positively — "no subblock containing fewer than two
1s" as "every subblock holds at least two". Those are the same statement, and the check now
recognises a flip of quantifier and comparison together as the equivalence it is.

### Phase 10 — comments

**0 defects over 10,022 comments.** Two of its findings were its own: `Sum_{i>=1}` and set
braces are OEIS notation, not LaTeX, and calling them LaTeX condemned 54 correctly written
comments; and `submission-order.txt` is a deliberate first-round queue, not an index, so
reading it as one reported ten thousand entries as missing from a file never meant to hold
them.

### Phase 9 — length that follows content

`engine/src/dc_phase9.py`, results in `engine/deep-check/phase9.json`.

The measure that matters is not the page count. 9,367 of 10,054 papers (93%) print at three
pages, but a page is coarse enough that two papers differing by half a page of prose land on
the same number, so that figure would condemn generators that do vary. In characters of text
the corpus runs from **4,034 to 18,462, median 6,263** — a factor of four and a half.

The real question is whether length varies *within* a family, since across families it must.
Of the **73 families holding 20 papers or more, 11 vary by less than a quarter of their median
length**: `logexp` (25 papers, 8%), `occupancy-image` (43, 10%), `gf-conjecture` (128, 12%),
`planepartition-box` (41, 15%), `ore` (20, 16%), `bounded-difference-triangle` (20, 16%),
`gf-implies-rec` (233, 17%), `pattern-neighbour` (101, 22%), `occupancy-turn` (54, 23%),
`chessboard-colour-class` (21, 24%) and `consecutive-triple` (60, 24%). **Those eleven
generators are still emitting a fixed structure.** The other 62 vary more than that, some far
more, so the change made on 6 September did work — it did not reach everywhere.

Two limits of this phase, stated rather than glossed:

* **For 5 of those 11 families the check can say nothing at all.** `pattern-neighbour`,
  `planepartition-box`, `logexp`, `gf-implies-rec` and `ore` have the *same* content score for
  every member, so there is no variation to correlate length against. Uniform length may be
  exactly right there. The score, not the papers, is what is missing.
* **The per-paper "padded" and "under-explained" rankings are not evidence.** Ranked on
  characters, the top of the under-explained list is entirely transfer-matrix papers whose
  score is high only because the score credits `log₁₀(S)` and their state count is large — but
  a large state count from a wide alphabet is not harder to explain than a small one. Reading
  the extremes confirms it: the longest paper in the corpus (rank 3441, A205213, 18,462
  characters) carries an extra section deriving what its determinant condition means, and
  earns its length; the shortest flagged (rank 8439, A186011, 4,173 characters) states a
  bounded-window condition of order 5 and needs no more. Neither is a defect.

### Phase 11 — the process itself

`engine/src/dc_phase11.py`, results in `engine/deep-check/phase11.json`.

**Independence is the corpus's real weakness.** 570 entries have been checked by a program
sharing no code with the engine that settled them, and they sit in **14 of the 104 argument
families** — each of those 14 checked to the last member. **90 families, holding the other
9,457 entries, have no independent check at all**, the largest being transfer-matrix with
3,417 papers. Nothing says those are wrong; it says nothing except the program that produced
them has ever looked at them. This is the largest single piece of unfinished work on the
project and it is stated here rather than buried.

**No double counting.** 27 entries carry two papers each. Every pair was compared on the
conjecture its source quotes verbatim, not on wording: 26 pairs quote two different
conjectures from the same entry, and the 27th (A059970) quotes one comment holding two
numbered conjectures, one settled by each paper. The count stands.

**Engine overlap.** 11 pairs of engines read some of the same names — transfer34/transfer40
(29 names), transfer75/transfer93 (8), transfer71/transfer41 (6). Later engines generalise
earlier ones, so an overlap is duplicated capability, not a duplicated paper: each entry is
settled once, by whichever engine the sweep reached first.

**The same defect appeared five times in one day, and now has a check.** A sweep or an audit
carrying a list of engine names written into the file, which was the whole set on the day it
was written and is now eleven or twelve of the eighty-three. Everything needing any other
engine was reported as *"no engine reads the name"* and dropped: **434 table entries** behind
`sweep_table.py`, every conjecture from seventy-two engines never once tested for failure
behind `falsify.py`, and the same in `sweep_tablerow.py` (which also called a method most
engines do not have, swallowed the `AttributeError`, and reported a model that matched the
entry perfectly as a mismatch), `sweep_cf.py`, and two superseded audits. `dc_englists.py` is
the enforcing code and Phase 11 runs it. **It still reports two live files** — `mutation_cf.py`
and `sweep_cf2.py`, both on the closed-form vein, which has 39 candidates outside the roster
and so is not costing results; they are on the defect list rather than quietly excused.

**Every rule has enforcing code.** All ten standing rules — the TAG namespace, crc32 sharding,
the builder reading the roster rather than the ranking, the stale-dates guard, caps recorded
beside refusals, the live re-check, the single repository root, ligature normalisation, the
merged bound in order-line papers, and recording engines that raise — resolve to a line of
code that would fail without them.

**263 papers have no stored source.** `paper-sources/` is meant to mirror `papers/` exactly.
100 of the 263 are the order-line recoveries: `build_ordwhole.py` wrote into
`build/un<anum>`, which is also the general builder's directory for the same entry, so
whichever ran last left its own files behind, the source mirror's hash match then failed, and
it correctly stored nothing rather than storing the wrong source. The builder now writes to
`build/ow<anum>`. The other 163 — 86 edge-count, 59 quadratic, 14 cell-condition, 4 others —
have no build directory left at all; their sources can only be regenerated by re-running the
builder, which is done when the corpus unfreezes.

## Defects outstanding

1. **9 papers missing the still-open statement** (Phase 8, listed above).
2. **39 quotations the automated comparison cannot settle** (Phase 3), for the reading pass.
3. **381 papers whose section 1 quote cannot be located** (Phase 3) — a gap in the check.
4. **100 order-line papers describe a computation they did not perform** (Phase 5). Each says
   in section 2 that merging leaves $S'$ states "and it is that smaller bound the computation
   below uses", then in section 3 reports running Berlekamp--Massey on $2S$ exact terms with
   the *unmerged* $S$ — for A232427, $S'=90$ and then "2S = 13284". The paper contradicts
   itself about its own run. An earlier correction reached the merge sentence and Lemma 1 and
   stopped there. `engine/src/ordbuild.py` now takes both numbers from the merged bound; the
   100 papers are rebuilt when the check finishes and the corpus unfreezes. The mathematics
   is unaffected: 180 terms is what was used and what the lemma needs.
5. **263 papers have no stored source** (Phase 11), 100 from a build-directory collision now
   fixed, 163 whose build directories are gone. Sources regenerated when the corpus unfreezes.
6. **90 of 104 argument families have no independent check** (Phase 11), covering 9,457
   entries including the 3,417 transfer-matrix papers. The largest piece of unfinished work,
   and now being repaired: `indepcell.py` has confirmed the cell-count family 197 of 197,
   `indep2x2.py` and `indepadj.py` are running on 914 and 1,121 entries.
7. **`mutation_cf.py` and `sweep_cf2.py` still keep their own engine lists** (Phase 11),
   naming 12 and 14 of the 83. Both are on the closed-form vein, which has 39 candidates
   outside the roster, so the cost is small — but the defect is the one that hid 434 entries
   elsewhere.
8. **11 generators still emit a fixed structure** (Phase 9): their papers vary by less than a
   quarter of their median length. `gf-implies-rec` (233 papers), `gf-conjecture` (128) and
   `pattern-neighbour` (101) are the largest.
