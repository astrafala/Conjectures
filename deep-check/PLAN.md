# The 10,000 deep check

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
3. The entry's `Last modified` line is quoted correctly, and the paper's claim
   that the conjecture is still open is still true **as of the re-fetch** — if
   somebody proved it in the meantime, the paper must say so and the result must
   be reclassified. A result that was open when found and is now closed by
   somebody else is still ours by date, but the paper must not claim otherwise.
4. The entry's DATA still matches the DATA the engine used. Entries get
   corrected; a corrected entry can invalidate a proof.
5. The entry's links and programs are searched for a proof that already existed
   when we started. Anything found is a **padded count** and the paper is
   withdrawn, not softened.

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
most papers and from the papers Phase 4 marked *reading unpinned* — is read the
way a hostile referee reads: find the weakest step, then attack it numerically at
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
