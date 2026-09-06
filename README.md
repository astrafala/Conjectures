# Proofs and disproofs of open OEIS conjectures

**Adrian Perez Fontelles** — independent researcher

**8887 papers** settling conjectures across **8860 entries** of the
[On-Line Encyclopedia of Integer Sequences](https://oeis.org):
**8881 proofs** and **6 disproofs**. Every one of them was recorded as an open
conjecture, empirical observation, or unverified formula on its OEIS entry at the
time it was settled.

## Start here

- **[OVERVIEW.pdf](OVERVIEW.pdf)** — one document explaining the method, the verification, and
  the errors it caught. **Read this first if you are here to assess the work rather than to
  look up an entry.**
- **[papers/](papers/)** — every paper, as a PDF. One folder per band of 500.
- **[papers/README.md](papers/README.md)** — how the ordering works, and the contents page.
- **[papers/index.csv](papers/index.csv)** — every paper with its OEIS entry, in one table.
- **[SUBMITTING.md](SUBMITTING.md)** — how to get these checked and cited.
- **[oeis-comments.txt](oeis-comments.txt)** — a short plain-English summary of each result,
  written to be posted on the entry itself.

**The paper number is the ranking. 1 is the hardest result and the last is the easiest.**
Ranking is by the depth of the argument, not by the size of the sequence or the length of
the paper.

## What is in a paper

Each paper is self-contained and three to five pages. It gives the definition of the
sequence, **quotes the conjecture verbatim with its contributor and date**, states that the
entry still records it as open as of the entry's own "Last modified" line, proves it, and
ends with a verification section reporting the ranges actually checked.

Papers never refer to each other. Where many entries fall to one argument, each paper gives
that argument in full for its own entry.

## How the results were checked

No result was accepted on one calculation. The standing rules were:

1. **Read the entry, then pin the reading against its published data before writing any
   code.** A misreading of the English gives different numbers at the very first term, and
   several readings that looked obviously right were killed this way.
2. **Brute force from the definition, independently of the machinery.** Every family was
   counted a second time by writing out the objects themselves — no transfer matrix, no
   closed form — and compared against the entry's own terms.
3. **Exact integer and rational arithmetic throughout.** No floating point, no sampling of a
   prefix.
4. **Re-verify the whole roster, repeatedly.** Every entry has been re-checked, from the
   entry's current text, several times over; the checks are in the repository and so are the
   errors they caught.

The [ledger](LEDGER-CLAUDE-CODE.md) is the working record. It includes the mistakes: readings
that were wrong, results that were withdrawn, and checks that turned out to be testing
something other than what they claimed.

## Honest limits

- Some results rest on classical theorems, which the papers cite and name. The 41 papers on
  plane partitions in a box lean on MacMahon's 1916 formula; what they settle is each entry's
  own unproved expression, not the classical count. Where the weight sits is stated in the
  abstract of every such paper.
- Many of the array-counting results share one argument — the count is a walk in a finite
  graph, so the sequence satisfies a linear recurrence and checking a proposed one is a finite
  exact computation. That argument is not new. Applying it to a particular entry requires
  reading that entry's English correctly, which is where the work and the risk actually are.
- Nothing here has been peer reviewed.

## Method

These results were produced by directing an AI system (Claude) over an extended series of
sessions: the author set the problem, the standards of proof, the verification rules and the
direction of search, and the system carried out the reading, the modelling, the computation
and the drafting. Every result was checked by at least two independent routes, as above.

This is stated because a reader should be able to judge the work knowing how it was made.

## Reproducing

```
python3 restore_master.py    # rebuild the was-keyed master from papers/ and rank-map.json
python3 rank.py              # re-derive the hardness ordering into papers-ranked/
python3 makeindex.py         # regenerate the index files
```

The engines are `transfer*.py`, the sweeps `sweep_*.py`, the brute forces `bf*.py`, and the
independent re-checks `audit_*.py`.

## Licence

The papers and the text are released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): reuse them freely, with attribution.
The code is under the MIT licence.
