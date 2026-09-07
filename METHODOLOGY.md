# Methodology

How a conjecture recorded as open in the OEIS becomes a proved result in this repository,
what each gate is for, and what has gone wrong.

**Author and director of the work: Adrian Perez Fontelles.** The standards described here —
what counts as settled, what must be verified and how, what may be claimed, and what must be
withdrawn — are his specification. The mathematics, code and drafting were carried out by an
AI system (Claude) working to it. Where this document says "the rule is", that rule came from
the specification, not from the machine.

---

## 1. The problem

Thousands of OEIS entries carry a line beginning `Empirical:` or `Conjecture:` — usually a
linear recurrence fitted to the terms the entry publishes, and never proved. A large family
of these, contributed chiefly by R. H. Hardin, count arrays of a fixed width over a fixed
finite alphabet subject to a local condition.

For a great many of them, the conjecture is not merely unproved. It is **decidable**, and
nobody had run the decision procedure.

## 2. Why these are decidable

Fix a width `W` and an alphabet `{0..m}`, and consider arrays of `W` columns and `n` rows
under a condition that, for each cell, involves only cells within a bounded number of rows.
Say it reaches `U` rows up and `D` rows down. A window of `U+D+1` consecutive rows then
decides whether the middle row passes, so the last `U+D` rows are a sufficient **state**.

Take those states as the vertices of a digraph, with an edge from one to the next exactly
when appending a row keeps every completed cell legal. An array of `n` rows is a walk; every
array arises from exactly one walk. With `M` the adjacency matrix, `i` the indicator of
starting states and `t` of accepting ones,

```
a(n) = iᵀ Mⁿ⁻ᶜ t
```

so `a` satisfies the linear recurrence given by the characteristic polynomial of `M`, and is
in particular **C-finite**.

**The decision procedure.** Let `q(t) = t^d - Σ cᵢ t^(d-i)` be the characteristic polynomial
of the proposed recurrence and put `u_j = iᵀ M^j q(M) t`. Then `u_j` is exactly the residual
`a(j+c+d) - Σ cᵢ a(j+c+d-i)`, so the recurrence holds from some point on **iff** `u_j = 0` for
all large `j`. By Cayley–Hamilton, `S` consecutive zeros (with `S` the number of states) force
every later one, and the last nonzero `u_j` **pins the threshold exactly** — the procedure
returns the smallest `n` beyond which the recurrence holds, not merely that one exists.

The computation runs on the vector `q(M)t`, so the matrix is never formed.

**State merging.** Two states from which the same number of arrays can be completed, for every
remaining length, contribute identically to `iᵀ Mⁿ t` and may be identified. The annihilation
test's length is governed by the state count, so this is not tidying — it is what makes the
larger models decidable at all. Observed reductions: 2022 states → 199, 4666 → 37, 8820 → 783.

## 3. Not everything is a walk

Three other shapes recur, and needed different machinery.

**The alphabet grows instead of the shape.** Where the array has a *fixed* shape over `0..n`,
there is no digraph to walk. Three sub-methods handle these:

- *Inclusion–exclusion over constraints.* A set of forced equations makes the values alternate
  along each connected component; a component with an odd cycle forces `2x = t`, possible for
  only one parity. The result is an exact quasi-polynomial of period 2, valid for every `n`
  with no threshold, and the recurrence follows by polynomial division.
- *Translation classes.* Where the condition constrains only differences, adding a constant to
  every entry preserves admissibility. A class spanning `s` contributes `max(0, n+1-s)` arrays
  over `0..n`, and no class can span more than `d` times the graph diameter — so the count is
  **exactly linear from a point known in advance**, and two evaluations pin it.
- *Classical formulas.* Matrices over `0..n` with rows and columns nondecreasing are, reversed,
  plane partitions in a box; MacMahon's product applies and telescopes to a polynomial.

**The conjecture is a closed form, not a recurrence.** Hypergeometric summation, Ore-algebra
division, and holonomic annihilation.

**The conjecture is a generating function.** A walk count has `A(x) = N₁/D₁` with
`D₁ = det(I - xM)` of degree at most `S`. If the conjecture is `N₂/D₂`, then
`R = N₁D₂ - N₂D₁` is a polynomial of bounded degree, and `A = N₂/D₂` exactly when `R = 0` —
so comparing `S + deg N₂ + deg D₂ + 1` coefficients **proves** the identity. Each such proof
also yields a recurrence, read off the denominator, that the entry does not record.

## 4. The hard part is the English

The engine is unconditional once a model is fixed. Fixing the model means reading a sentence
written by a human, in a compressed and idiosyncratic style, and turning it into a predicate.
**That is where the risk lives.** Three examples, each caught by the entry's own data:

**"The same population."** A224654 counts 0..2 matrices whose every 3×3 subblock has "the same
population". Two readings: the *sum* of the nine entries, or the *multiset* of how often each
value occurs. **On a binary alphabet the two agree** — which is why the sum reading survived
every binary entry of the family. Over `{0,1,2}` the sum reading gives **102789**; the entry
publishes **67797**, which is what the multiset reading gives. Both agree at `n=1`, where the
condition is vacuous, so checking the first term alone would have missed it.

**"Its 72 absolute element differences."** A234834 asks for 3×3 subblocks whose "72 absolute
element differences" sum to 34. `72 = 9·8` names the *ordered* pairs — but that sum is always
even, so 34 is unachievable and the reading gives **0**. Summing over the `C(9,2) = 36`
*unordered* pairs gives **4032**, the entry's first term. The entry counts each pair once and
names it twice.

**"Diagonally, horizontally or vertically."** A189305 counts permutations where each cell moves
zero or one space so. Read as the eight king moves plus staying put, `a(2) = 24`; the entry
publishes **14**. Each word names an **axis** — a pair of opposite offsets — so the list names
three axes, not eight directions.

**The rule that follows:** pin the reading against the published data *before* writing the
engine, and treat any disagreement as evidence about the reading rather than about the entry.

## 5. The four gates

No result is accepted on one calculation.

1. **The data gate.** The model must reproduce **every** term the entry publishes, exactly, in
   integer arithmetic, with the index shift read off the entry's offset rather than fitted.
2. **An independent brute force.** The objects are enumerated a second time directly from the
   entry's English — writing out the arrays and testing the condition cell by cell, no transfer
   matrix, no closed form — and compared with the published terms. Written against the *entry*,
   not against the engine.
3. **The conjecture on the raw data.** Evaluated on the published terms alone, no model
   involved, wherever the proved range and the data overlap.
4. **The annihilation test.** Carried to the Cayley–Hamilton bound over the whole vector, in
   exact integer arithmetic, never sampled.

Alongside these run a **duplicate guard** (no entry gets two papers for the same conjecture), an
**openness guard** (re-checked against the live entry text before anything is counted), and a
**page-count and LaTeX-error check** on every built paper.

## 6. The errors

<a name="the-errors"></a>
A reader assessing work of this size is entitled to the error record. The full dated version is
in [LEDGER.md](LEDGER.md); these are the ones with a lesson.

**A brute force that shares the engine's misreading is not a check.** One family writes the
array with its width growing, so the natural walk runs across *columns* — but the entries also
carry a clause about the order in which values first appear, stated in *row major* order. An
engine that transposes the array must not transpose the clause with it. One did, and the brute
force written alongside it made the identical substitution, so the two agreed with each other
*and both matched the published terms*. It was caught only by writing a third count in the
entry's own orientation. **Independence is a property of how a check was written, not of the
fact that one exists.**

**The check has twice been the faulty side.** Writing brute forces for a nine-entry batch, three
of them dropped clauses from the entry names — a neighbour list in two, a canonical-form clause
in the third. All three disagreed with the model; in all three the *check* was wrong. A check is
worth exactly the care taken over it.

**A check that disagrees with forty papers at once is the check that is wrong.** A re-audit
reported forty thresholds off by exactly one. They were not: the audit's minimal-order
computation counted leading terms the entry never publishes. A systematic disagreement of fixed
size against many results at once is a signature of the checker.

**Three audits that cried wolf, one cause.** Each was written against a different interface from
the one that produced the result: PDF text extraction silently dropped superscripts, so `k^n` was
compared as `kn`; a trailing comma turned an expression into a one-element tuple; a call to an
engine's internal routine skipped a division stated in the entry's name, so "half the number of…"
came out doubled. **An audit must go through the same interface the sweep does, or it is testing
a different claim.**

**A real error in 477 papers, found by re-audit.** An earlier version stated the proved range
using a converted index, and the conversion was wrong. The mathematics was sound and the
recurrences true; the stated ranges were not. All 477 were corrected.

**Silent refusals — five of them, and the most expensive class of bug here.** A wrapper called an
engine with an argument it did not take; the `TypeError` was swallowed by a broad exception
handler, so 42 entries were reported "too large to model" when the model built in seconds. A
shared generating-function parser required a bare `G.f.:` and rejected any body containing
"empirical" — while the corpus writes `Empirical g.f.:`; **2837 entries carry such a line and
2775 parse the moment the marker is stripped.** A refusal that looks like a size limit or an
absence, and is really a crash or a spelling difference, is invisible.

**A prose error in 66 papers.** For one family the parser rewrites a negated condition positively,
so the negation already sits inside the displayed formula; the surrounding sentence then quoted
the entry's own "no" and negated it a second time. The models were unaffected and reproduced every
published term, but 66 papers described their object as the opposite of what the entry asks.
Corrected and rebuilt.

**Withdrawals.** Nine papers withdrawn as duplicates or as settling something already recorded as
settled. One whole engine and its ten papers withdrawn on discovering an existing engine already
performed the identical reduction. Three papers named the wrong contributor — an attribution
hard-coded in a template rather than read from the entry — all corrected.

**What counts as grounds for withdrawal, and what does not.** Every paper prints the date it was
written, and [comments/by-date.md](comments/by-date.md) lists every entry in the order it was
settled. A paper is withdrawn when the result turns out to have been settled *before* that date:
it was never ours to claim, and the count comes down. A conjecture settled by somebody else
*after* that date is a different thing entirely — the work here still came first — and nothing is
removed; the entry is simply annotated so that no paper claims an entry is open when it is not.
Later is not earlier.

## 6a. How targets are chosen

The standing rule is to work in **chunks**, biggest first. A chunk is a family of open
conjectures that one engine can settle together; settling entries one at a time is the
slowest possible use of the effort and is a last resort, not a default.

So the choice of what to attack is made by measurement rather than by whatever is in view.
`engine/src/chunks.py` groups every open, conjecture-carrying entry that no engine reaches
by the shape of its clause and prints the groups largest first; it also sizes the cheapest
chunk of all, the entries an engine already parses that were refused at some earlier cap and
never revisited. That pool has repeatedly turned out to hold real results, because a cap is
a setting and not a wall.

If the largest chunk needs machinery that does not exist, the choice is to build it or to
write down precisely what stops it — not to skip it quietly. A chunk measured and found to
hold no conjectures is itself recorded, so that nobody measures it twice.

## 7. Scope

105 distinct arguments across 10027 entries. The full breakdown is in
[papers/index.csv](papers/index.csv); the largest groups:

| Papers | Argument | What it settles |
| ---: | --- | --- |
| 3008 | `transfer-matrix` | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 432 | `quadratic` | the residual test over one square root, or none |
| 301 | `subblock-3x3` | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 290 | `relabelling` | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 233 | `gf-implies-rec` | the recurrence follows from a generating function the entry records as fact |
| 201 | `budget` | a cell condition with an exception budget, counted up to relabelling |
| 194 | `monotone-subblock` | a statistic of every 2 X 2 or 3 X 3 subblock monotone along named directions of the subblock grid |
| 188 | `table-column` | a table's column recurrences, each column being a fixed-width array count |
| 171 | `global-count` | a global count of marked adjacent pairs carried in the state, then a walk count |
| 169 | `image-count` | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 161 | `monotone-statistic` | a statistic of short runs of cells, whose derived array is required to be monotone in a named direction |
| 157 | `walk-closed-form` | an explicit closed form, turned into the recurrence it satisfies |
| 156 | `neighbour-set` | a condition on every cell over the neighbour set the entry names |
| 126 | `index-change` | grid permutations with a bounded index change, as a matching turned into a walk |
| 111 | `pattern-avoidance` | short absolute or relative patterns forbidden along the rows, columns and diagonals of a grid |
| 104 | `edge-count` | the number of clockwise, counterclockwise or rightwards-and-downwards edge increases in every 2 X 2 subblock |
| 101 | `pattern-neighbour` | a cell condition counted up to relabelling, by falling-factorial inversion |
| 99 | `order-statistic` | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 94 | `matrix-subblock` | the determinant, permanent or trace of every 2 X 2 subblock: singular, all equal, differing from a neighbour, or monotone |
| 91 | `subblock-difference` | a statistic of every 2 X 2 subblock differing from its neighbours by exactly a fixed amount |
| 90 | `clockwise-perimeter` | conditions read round the clockwise perimeter of every 2 X 2 subblock: the pattern its corners spell, the number of edge increases each way round, and how those counts compare with the neighbouring subblocks' |
| 85 | `ray-sum` | no entry equal, modulo m, to a constant plus the sum of the entries along a ray out of it |
| 76 | `reciprocal-link` | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 76 | `subblock-coloring` | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 74 | `neighbour-existential` | what a cell demands that SOME neighbour of it look like: one at least as large, one of a named value, an allowed number of them, or its own value plus and minus one |
| 73 | `subblock-line-sum` | the sums along the rows, columns and diagonals of every K X K window of a grid, constrained or compared |
| 72 | `digit-divisibility` | rows and columns read as base-b numbers and required to be divisible, or not, by given moduli |
| 68 | `order-cond` | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 68 | `order-recovery` | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 68 | `lex-subblock-statistic` | each 2 X 2 subblock reduced to one number -- a determinant, a permanent, a sum, or an order statistic -- with the rows and columns of the derived array in lexicographic order |

…and 63 further arguments; see [papers/index.csv](papers/index.csv).


## 8. The walls

Recorded rather than quietly omitted:

- **`n × n` arrays**, where both sides grow. No fixed width to walk along. A genuine
  obstruction, not a parser gap.
- **State spaces too large** for the annihilation test even after merging.
- **Triangular inclusion–exclusion** running over `2^|E|` subsets, out of reach past ~30 edges.
- **113 generating-function-only entries** whose names no engine reads yet. A gap, not a wall.

## 9. How long a paper is

Length follows the result, and until 6 September 2026 it did not. Every family is written by
its own generator, and each generator emitted a fixed structure, so within a family every paper
came out the same length whether its object had six states or sixty-five thousand. The
mathematics was never truncated — these proofs are complete in three pages — but the
*explanation* did not adapt, and that was a defect in the generators rather than a fact about
the results.

The measured distribution before the change: 8587 of 9035 papers were exactly three pages, and
whole families of two hundred papers were 100% one length. The only family with real spread was
the hand-written number-theoretic one, which is exactly what you would expect when length
follows content.

Generators are now being made to scale their explanation to the object: the state space spelled
out concretely when it is large and left alone when it is small, the reason enumeration is
hopeless given with the actual figure when the arrays outnumber the states by orders of
magnitude, and the exactness of a threshold stated when the entry's own terms establish it. The
largest family, 1080 papers, has been rebuilt this way; the rest follow as each is next touched.

## 10. How to check a single result

Every paper is self-contained and checkable independently of everything else here — which is the
point of the independence rule. To check one:

1. Read the conjecture as the paper quotes it, and compare it with the live OEIS entry.
2. Read the paper's description of the condition, and satisfy yourself it is what the entry's
   name says. **This is where an error would be.**
3. Enumerate the objects yourself for the first two or three values of `n` and compare with the
   entry's published terms. Cheap, and it tests the modelling.
4. The recurrence check is then a finite exact computation, described in the paper.

Step 3 is the one worth doing. If the model is right, everything after it is mechanical; if it is
wrong, step 3 says so at once.
