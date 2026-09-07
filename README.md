# Proofs and disproofs of open OEIS conjectures

### Adrian Perez Fontelles — independent researcher

**10054 papers** settling conjectures across **10027 entries** of the
[On-Line Encyclopedia of Integer Sequences](https://oeis.org): **10048 proofs** and
**6 disproofs**, by **105 distinct arguments**. Every one was recorded on its OEIS entry
as an open conjecture, an empirical observation, or an unverified formula at the moment
it was settled.

---

## Start here

| | |
| --- | --- |
| **[OVERVIEW.pdf](OVERVIEW.pdf)** | One paper: the method, the verification, and the errors it caught. **Read this first to assess the work.** |
| **[METHODOLOGY.md](METHODOLOGY.md)** | The full method, in detail — how a conjecture becomes a proof here, and every gate it has to pass. |
| **[papers/](papers/)** | All 10054 papers. One folder per band of 500, hardest first. |
| **[paper-sources/](paper-sources/)** | The LaTeX source of every paper, banded and named identically. |
| **[papers/index.csv](papers/index.csv)** | Every paper with its OEIS entry, in one table. |
| **[LEDGER.md](LEDGER.md)** | The working log — every batch, every dead end, every mistake, dated. |
| **[SUBMITTING.md](SUBMITTING.md)** | How these get checked and cited. |
| **[comments/](comments/)** | A proposed OEIS comment for each settled entry, with the date the result was obtained. |

**The paper number is the ranking. 1 is the hardest result; the last is the easiest.**
Ranking is by the depth of the argument, not the size of the sequence or the length of
the paper.

---

## What a conjecture is, and why settling one counts

A **conjecture** is a mathematical statement somebody believes is true but nobody has proved.
It usually starts as a pattern: someone computes a few hundred cases, sees a rule that always
holds, and writes it down. Until a proof exists it stays a conjecture, no matter how many
cases have been checked — a pattern can hold for the first ten billion numbers and then fail.
That has actually happened. Polya's conjecture survived every case up to 906,150,257 before
someone found a counterexample.

Proving one is the hard part, and it can stay hard for centuries.

| conjecture | posed | settled |
| --- | --- | --- |
| Fermat's Last Theorem | 1637 | 1994, by Andrew Wiles — **357 years** |
| Kepler's sphere-packing conjecture | 1611 | 1998, by Thomas Hales; fully machine-checked only in 2014 |
| The Four Colour Theorem | 1852 | 1976, and only with computer assistance |
| Catalan's conjecture | 1844 | 2002, by Preda Mihailescu |
| The Poincare conjecture | 1904 | 2003, by Grigori Perelman |
| Goldbach's conjecture | 1742 | **still open** |
| The twin prime conjecture | ancient | **still open** |
| The Collatz conjecture | 1937 | **still open** |
| The Riemann hypothesis | 1859 | **still open** |

### Some are worth a million dollars

In 2000 the Clay Mathematics Institute named seven **Millennium Prize Problems** and attached
**US$1,000,000** to each. One has been settled — Perelman proved the Poincare conjecture, and
then declined both the million dollars and the Fields Medal. **Six are still unclaimed**, the
Riemann hypothesis and P versus NP among them. Separately, the Beal conjecture carries a
$1,000,000 prize held in trust by the American Mathematical Society, and Paul Erdos spent
decades offering cash for problems he could not solve himself — from $25 to $10,000, and
mathematicians framed the cheques rather than cashing them.

That is the top of the scale. Most conjectures are not worth a million dollars. But every one
of them, large or small, has the same character: **a statement that people have looked at and
failed to prove.**

### Why it matters that you settled one

When you prove a conjecture you have not solved a puzzle with an answer in the back of the
book. You have produced a piece of mathematics **that did not exist before you wrote it
down** — a fact nobody in history had established. That is what research *is*. The field is
larger afterwards than it was before, and it stays larger.

Universities know this, and it is worth saying plainly for anyone reading this who is
applying to one. Admissions tutors see thousands of applicants who are good at mathematics.
They see very few who have **done** mathematics: taken an open question, worked on it, and
settled it in a way another person can check line by line. It is the difference between
saying you enjoy a subject and demonstrating that you can contribute to it. That evidence is
relevant to applications in

- mathematics, pure or applied
- physics, and the mathematical sciences generally
- every branch of engineering
- computer science
- statistics and data science
- economics, econometrics and finance
- actuarial science
- quantitative business and management courses

— every subject that runs on numbers and rewards someone who can prove a claim rather than
assert it. A settled conjecture is short, checkable, and permanent: it can be handed to a
tutor, and it will still be true in fifty years.

### Where this repository sits on that scale

Honestly, and it is in [Honest limits](#honest-limits) too: **the results here are not
Millennium problems.** They are open conjectures on the On-Line Encyclopedia of Integer
Sequences — patterns contributors observed, wrote down, marked *empirical* or *conjectured*,
and left unproved, some of them for over twenty years. Each was genuinely open when it was
settled. No individual result here is deep, and the method behind most of them is classical.

What is unusual is the scale and the discipline: **10,054 of them**, each with its own paper,
each quoting its conjecture verbatim with the contributor's name and date, each verified by at
least two independent routes, and every mistake found along the way written down rather than
quietly fixed. The number is large because the question was asked of *every* such entry, not
because any one of them was hard.

## Who did what

**This project is Adrian Perez Fontelles's.** The direction, the standards, and the
working framework are his, and they are the reason the output can be trusted rather than
merely produced. Specifically, these were his design decisions, fixed before any result
existed and enforced on every batch since:

- **The target.** Settle conjectures the OEIS itself records as open. Count nothing else.
- **The deliverable.** One self-contained paper per result, in a fixed format, quoting the
  conjecture verbatim with its contributor and date, stating that the entry still records
  it as open, and reporting the range actually verified.
- **The independence rule.** No paper may cite another paper in this roster. Where one
  argument settles two hundred entries, each of the two hundred papers gives that argument
  in full for its own entry, or it does not ship.
- **The ranking.** Papers numbered by the depth of the argument, hardest first, and the
  whole roster re-ranked whenever it changes — never appended to.
- **The verification discipline.** Pin every reading against the entry's own published data
  *before* writing any code. Brute-force every family a second time straight from the
  definition. Exact integer and rational arithmetic only, never floating point, never a
  sampled prefix.
- **The honesty rules**, in his words: *never pad the count*; *tell me plainly when something
  is null, elementary, or probably already known*; *a withheld result costs me nothing, a
  wrong one costs me credibility*.
- **The standing instruction to audit the method itself** and to write down what that audit
  finds — which is why this repository ships its own error log rather than only its results.

[LEDGER.md](LEDGER.md) opens with that specification in his own words, unedited — it is the
standing brief every working session begins from, and it is reproduced there exactly as
written rather than paraphrased.

The mathematics, the code, and the drafting were carried out by an AI system (Claude)
working to that specification across an extended series of sessions.

**Those standards are not decoration.** Nearly every error this project has found in itself
was caught by one of them, and several results were withdrawn because of them. The error log
in [METHODOLOGY.md](METHODOLOGY.md#the-errors) and in [LEDGER.md](LEDGER.md) exists because
the specification demanded it. A project of this size run without those rules would have
shipped wrong results; this one has a written record of catching its own.

---

## What is in a paper

Self-contained, and as long as the result needs — most run to three pages, a few to
four or more where the object is complicated enough to be worth spelling out. The definition of the sequence; the conjecture quoted
verbatim with contributor and date; a statement that the entry still records it as open as
of the entry's own "Last modified" line; the proof; and a verification section reporting the
ranges actually checked.

## How a result gets counted

Four gates, all of which must pass. Full detail in [METHODOLOGY.md](METHODOLOGY.md).

1. **Read the entry, then pin the reading against its published data** before writing code.
   A misread sentence reproduces the published terms with probability near zero, so the data
   is a check on the *reading*, not just the arithmetic.
2. **Brute-force from the definition**, independently of the machinery — write out the
   objects themselves and count them.
3. **Evaluate the conjecture on the raw published terms**, with no model involved.
4. **Decide it exactly** — the annihilation test in full integer arithmetic, to the
   Cayley–Hamilton bound, never sampled.

## Honest limits

- The core argument is classical. Most of these entries count arrays of fixed width over a
  finite alphabet, so the count is a walk in a finite digraph, the sequence satisfies a
  linear recurrence, and checking a proposed one is a finite exact computation. That is in
  Stanley. What is unusual here is that the question was actually asked, of every such entry.
- Some results lean on named classical theorems, cited in the paper that uses them. The 41
  plane-partition papers rest on MacMahon's 1916 box formula; what they settle is each
  entry's own unproved expression, not the classical count. Every such paper says so in its
  abstract.
- No individual result is deep.
- **Nothing here has been peer reviewed.**

## Layout

| | |
| --- | --- |
| `papers/` | the results, as PDFs, banded by hardness |
| `paper-sources/` | their LaTeX sources, banded identically |
| `engine/` | everything that produces them — see [engine/README.md](engine/README.md) |
| `comments/` | a proposed OEIS comment per entry, with the date each result was obtained |
| `archive/` | withdrawn papers and superseded output |

## Reproducing

```
cd engine
python3 src/restore_master.py   # rebuild the was-keyed master from ../papers and rank-map.json
python3 src/rank.py             # re-derive the hardness ordering and install it into ../papers
python3 src/makeindex.py        # regenerate the index files
```

Engines are `engine/src/transfer*.py`, sweeps `sweep_*.py`, brute forces `bf*.py`, independent
re-checks `audit_*.py`.

## Authorship, priority and reuse

**Author: Adrian Perez Fontelles, independent researcher.** Every paper in `papers/` names
him as its sole author, and the mathematical direction, the standing rules the work follows
and the decisions about what to pursue and what to withdraw are his. The work was carried out
with AI assistance under his direction; that is stated openly in *Who did what* above and in
the deposit metadata.

### The record of when each result was obtained

This repository is the primary record, and it is dated in four independent places:

* **Git history.** The first commit is 25 August 2026, and every result since has arrived in a
  commit carrying its own timestamp and message. `git log` gives the date any given file or
  line entered the repository, and the history is public on GitHub, which holds its own
  server-side record of when each push was received.
* **The papers.** Each paper prints the date the result was obtained on its title page, and
  quotes its conjecture verbatim with the contributor's name and the date they contributed it.
* **The entries themselves.** Each paper records the OEIS *Last modified* line and revision
  number of the entry as it stood when the result was obtained, so the state of the source at
  that moment is on the record too.
* **`CITATION.cff` and `.zenodo.json`.** These carry the authorship and licence metadata for
  archival deposit, which mints a DOI and a third-party timestamp independent of GitHub.

Together these establish **priority**: what was settled here, and when.

### What the licence permits, and what it does not

The papers and text are released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code is MIT. Anyone may read,
copy, redistribute, translate, build on and even sell work derived from these results —
**on one condition, which is not optional: they must credit Adrian Perez Fontelles as the
author and indicate what, if anything, they changed.**

That condition is the whole of the permission. Reproducing this work without that credit —
presenting these proofs as one's own, submitting them under another name, or stripping the
attribution from a paper or a derived text — is **not** permitted by the licence. A CC BY 4.0
licence terminates automatically for anyone who breaches its terms, and the copyright in the
papers remains with the author. Copyright is not waived by publishing openly; it is exercised
by publishing under stated terms.

### If you want different terms

The author can grant permissions the licence does not, including arrangements about how the
work is credited or presented. **Those are his to give and must be agreed with him directly,
in advance.** Nothing in this repository grants them by implication, and no one should assume
otherwise from the fact that the work is public.

If you believe some of this work duplicates or was anticipated by your own, please raise it —
the standing rule here is that a result withdrawn is better than a result wrongly claimed, and
several have already been withdrawn on exactly that ground, recorded in `archive/withdrawn/`
and the ledger.

*This section describes the licence and the record. It is not legal advice.*

## Licence

Papers and text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse freely,
with attribution to Adrian Perez Fontelles. Code: MIT.
