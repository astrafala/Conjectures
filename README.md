# Proofs and disproofs of open OEIS conjectures

### Adrian Perez Fontelles — independent researcher

**9322 papers** settling conjectures across **9295 entries** of the
[On-Line Encyclopedia of Integer Sequences](https://oeis.org): **9316 proofs** and
**6 disproofs**, by **103 distinct arguments**. Every one was recorded on its OEIS entry
as an open conjecture, an empirical observation, or an unverified formula at the moment
it was settled.

---

## Start here

| | |
| --- | --- |
| **[OVERVIEW.pdf](OVERVIEW.pdf)** | One paper: the method, the verification, and the errors it caught. **Read this first to assess the work.** |
| **[METHODOLOGY.md](METHODOLOGY.md)** | The full method, in detail — how a conjecture becomes a proof here, and every gate it has to pass. |
| **[papers/](papers/)** | All 9322 papers. One folder per band of 500, hardest first. |
| **[paper-sources/](paper-sources/)** | The LaTeX source of every paper, banded and named identically. |
| **[papers/index.csv](papers/index.csv)** | Every paper with its OEIS entry, in one table. |
| **[LEDGER.md](LEDGER.md)** | The working log — every batch, every dead end, every mistake, dated. |
| **[SUBMITTING.md](SUBMITTING.md)** | How these get checked and cited. |
| **[comments/](comments/)** | A proposed OEIS comment for each settled entry, with the date the result was obtained. |

**The paper number is the ranking. 1 is the hardest result; the last is the easiest.**
Ranking is by the depth of the argument, not the size of the sequence or the length of
the paper.

---

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

## Licence

Papers and text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse freely,
with attribution to Adrian Perez Fontelles. Code: MIT.
