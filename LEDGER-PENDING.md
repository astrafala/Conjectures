## 13 September 2026 — the inhomogeneous cone, and a withdrawal that was too blunt

### `latpoly` learns conditions with a constant in them

`latpoly`'s hyperplanes were `(x-form, coefficient of n)` and nothing else, so every condition
had to be homogeneous in `(x, n)` jointly. `no element more than one greater than the previous`
and `each element differing from at least one neighbor by 2 or more` were read and refused, in
so many words, because "the region is then a shifted polyhedron, its counting function is
quasi-polynomial only beyond some n_0, and without a bound on n_0 there is no proof".

There is a bound on n_0, and it is computable. The shape of the arrangement in x-space changes
exactly at an n where L+1 of the hyperplanes are concurrent — a vertex is cut out by L of them
and crosses a further one precisely there. Solving each (L+1)-subset as a square system in
`(x, n)` and taking the largest n over the solutions gives an n_0 past which the combinatorial
type is constant; the vertices are then affine in n with denominators dividing the same
determinants as before, the count is a quasi-polynomial for n > n_0 by the parametric-polytope
theorem, and the terms below n_0 raise the numerator's degree by n_0 and no more. So the
annihilator in force is `z^(n_0+1) A(z)` where A is what the homogeneous part already gave —
which for a homogeneous condition is n_0 = 0 and exactly the `z A(z)` in use, so nothing
already proved changes.

Measured against the whole clone: of 6,676 names of the fixed-length growing-alphabet shape
outside the roster, 6,124 are read by no engine, and 245 of those are open with a parsable
conjectured recurrence. 113 of the 245 have a head `latpoly` already parses and were refused
only by the vocabulary. Three condition families were added — `differing from at least one
neighbor by k or more / k or less / something other than k`, `no element more than k greater
than the previous`, `adjacent elements differing by more than k` — and **22 names became
readable, every one reproducing its entry's published data exactly. 16 are proved and
installed.**

All 148 held `latpoly` results were re-asked afterwards: 76 unchanged, 71 now derive a SMALLER
bound than the installed paper quotes (a conservative bound is a weaker claim, not a wrong
one), 0 in the dangerous direction, 0 that no longer build.

### A withdrawal blocks the argument, not the entry

Nothing had stopped a withdrawn result from being rebuilt and reinstalled, and the first fix
went too far the other way: it blocked the A-NUMBER. Twelve of the newly proved entries turned
out to be among the 1,336 withdrawn on 8 September for `gf-implies-rec` — proving a conjectured
recurrence from a generating function inside the same conjecture block, which settles nothing.
An exact Ehrhart model settling the same open conjecture is a different argument, not the
withdrawn one returning. The block is now on the (entry, argument) pair, which is what
WITHDRAWN.md actually records.

### 633 papers now quote the conjecture they prove

Section 1 must quote the entry's conjecture verbatim. 542 papers printed a placeholder because
every builder tested for a conjectural word ON the line — the defect this project keeps paying
for, since a `Conjectures from X: (Start)' block carries none — and 41 more quoted a different
line of such a block from the one the theorem proves. Fixed in `conjquote.py`, which all 84
builders now delegate to, and 633 installed papers were regenerated in place at their own
dates. 119 held results that had never had a paper built were built and installed at the same
time.

## 13 September 2026 — `ordrep`: fixed length, growing alphabet, constrained by repeated values

A *repeated value* is a term equal to the one before it. `repval` reads the mirror family —
`length-n 0..K arrays`, growing length over a fixed alphabet, where the count is a walk on at
most (K+1)(K+2) states. Here the length is fixed and the ALPHABET grows, so nothing is a walk:
the state that remembers the previous repeated value has as many values as the alphabet.
`ordpoly` reads the name shape but only conditions decided by ORDER alone, and these name an
actual difference. 43 entries of this shape carry a conjectured recurrence and no engine read
one.

The count is taken exactly in O(n²) per step rather than O(n³): with `A[p][v]` the number of
prefixes ending in `v` whose previous repeated value is `p`, appending `t` gives
`A'[p][t] += (Σ_v A[p][v]) − A[p][t]` when `t` differs from the last term and
`A'[t][t] += A[p][t]` when it equals it and the condition allows.

The bound is derived, not assumed. Let `k` be the point past which the predicate stops caring —
it depends on the difference of the two repeated values only through its sign and its magnitude
up to `k`, and is constant beyond that in each direction; `k` is read off the predicate. An
array is its weak ordering plus a base value `g_0 ≥ 0` and gaps `g_i ≥ 1` with `g_0 + Σ g_i ≤ n`.
Every constraint is on a signed sum of consecutive gaps and, since the predicate is constant
past `k`, splits into finitely many cases each fixing that sum to one of at most `2k+1` values
or pushing it beyond `k`. In each case the count is a polynomial in `n` of degree at most `L`,
valid once `n` exceeds the total forced amount, which is at most `L + L(k+1)`. So

    a(n) is a polynomial of degree at most L for n >= n_0 = L + L(k+1),

annihilated by `(z−1)^(L+1)` there and by `z^(n_0+1)(z−1)^(L+1)` everywhere. The annihilator was
then asked for terms the model had not supplied, and reproduced them.

**24 names read, every one reproducing its entry's published data exactly; 22 proved and
installed as `repeated-value-polynomial`.** Two carry no parsable recurrence. The variants
taken modulo n+1 are refused with the reason: the modulus moves with the parameter, the
differences are no longer bounded, and the argument does not reach them.

## 13 September 2026 — `necklace2`: necklaces and bracelets with a condition

`necklace` reads `Number of k-bead necklaces labeled with numbers -n..n ... with sum zero.` and
stops there. 31 entries add a condition — no three beads in a row equal, first differences in
-n..n, avoiding the patterns z z+1 z+2 and z z-1 z-2 — and no engine read one.

Burnside still applies; the condition changes only what is counted at each group element. For a
rotation by d with c = gcd(k, d) the fixed labellings are exactly the c-periodic words, the
whole sum is (k/c) times the sum of one period, and the condition on the k-periodic extension
is the condition on the length-c cyclic word; for a reflection they are the palindromes,
determined by ceil((k+1)/2) values, and the condition is again local in those.

The first count was a dynamic programme over pairs of consecutive beads with the running sum
carried alongside, and closing the cycle means fixing two values, so its cost is (2n+1)^4 times
the sum range: **fourteen minutes for one four-bead entry**. The forbidden windows are defined
by EQUALITIES between bead values with fixed offsets, so inclusion–exclusion over them turns
each term into a count under a set of affine identifications — a union-find with offsets, then
one convolution — and the same entry takes well under a second. Seven beads with no three equal
at n = 30 is a tenth of a second.

The bound is read off the arrangement and was twice wrong in a way the extrapolation guard
caught, which is exactly what that guard is for:

* the multiplicity of each cyclotomic factor was taken as the number of orbit variables, giving
  degree 126 at seven beads where the true bound is a fraction of that — a model that cannot be
  evaluated is a refusal, so this mattered;
* and `|y_i − y_j| ≤ n` was put into the arrangement as a hyperplane through the origin rather
  than as a pair that MOVES with the parameter. The derived annihilator then failed at every
  index. Each form now carries its own coefficient of n.

**26 names read; 13 build within the limits and every one of those reproduces its entry's
published data exactly; 11 are proved and installed as `necklace-condition`.** The seven-bead
cases are refused because the sharp ray enumeration is over budget and the crude fallback gives
an annihilator too large to evaluate; the `first differences in -n..n` condition past five beads
is refused because it has no equality form and needs the slow dynamic programme. Both are
recorded with the reason rather than left to run.

## 13 September 2026 — the pool re-measured, and the automaton's middle column

**The pool is 2,225, not 245.** The earlier measurement was restricted to one name shape. Asked
of the whole clone — outside the roster, open, carrying a parsable conjectured recurrence, read
by no engine — the answer is 2,225. The largest clusters: `n X 2 / n X 3 / n X 4 / n X n ...`
arrays (about 145), `binary arrays indicating ...` (34), fixed-alphabet growing-length arrays
`-1..1 / -2..2 / -3..3 arrays x(i)` (about 60), `permutations of 1..n` (22), the middle column
of an elementary automaton (25), `nondecreasing arrangements of` (12).

### `ecacol`: the middle column

The middle column is the cell at the origin at each step, c(n) = w(n)[n]. `Binary
representation of` concatenates c(0..n) and reads it as a decimal numeral, `Decimal
representation of` as a binary one, and the bare wording lists the bits. 25 entries, none read.

Observing that the column settles into a period is not a proof — defect 12, the one that cost
184 papers this morning. The row certificate gives one. In absolute coordinates the certificate
`w(n+p) = L_r + w(n) + R_r` says `cell(x, n+p) = cell(x + d_r, n)` with `d_r = p − |L_r|`, so
the column reads a diagonal moving by d_r every p steps. Three cases close it:

* **every L_r empty** — the row grows only on the right, every prefix is frozen, so there is a
  single infinite word W with w(n)[i] = W[i] and c(n) = W[n] outright; W is w(n0) followed by
  R_{r_0} R_{r_1} …, eventually periodic with period dividing Σ|R_r|;
* **every R_r empty** — the mirror, reading from the right end;
* **Σ_r d_r = 0** — the diagonal returns to the origin after a full cycle of residues, so
  cell(0, n + p²) = cell(0, n).

Each gives a proved period; the exact one is a divisor found inside one window of computed
rows, which is a finite check. A rule meeting none of the three is refused: its column may well
be periodic, and saying so would be an observation. **72 names read, 18 proved and installed as
`automaton-column`**; rules 25, 109, 137 and 169 are the ones refused.

## 13 September 2026 — `arrlex`: n X k arrays ordered lexicographically

The 198 `n X k` entries in the pool are transfer-matrix shaped — growing height, fixed width,
fixed alphabet — so what stops them is the condition vocabulary, not the model. The largest
condition that can be carried in a finite state is the lexicographic one, and neither half of it
is local to a pair of rows, which is why nothing read them:

* rows lexicographically nondecreasing IS local, a condition on the pair;
* **columns** lexicographically nondecreasing is not — column j and column j+1 are compared
  over the whole height — but one flag per adjacent pair carries it;
* and `every element equal to at least one horizontal or vertical neighbour' is not either,
  since an element's obligation can be met by the row BELOW, which has not been chosen yet.
  One bit per position carries that, and the walk may only end with none outstanding.

The `read forwards, and nonincreasing read backwards' variant needed the flag widened from two
values to three. Read forwards a column pair is decided by its FIRST difference; read backwards
(bottom to top) by its LAST. So the flag is: the two still agree; they have differed and the
latest difference was `less'; they have differed and the latest was `greater'. A pair whose
first difference goes the wrong way is dead either way, and at the end the backward condition
rejects `latest was less'. Reading it as a two-state flag gave 5 where the entry says 2 on a
single row, which is what said the reading was wrong.

**34 names read, every one of the 11 checked reproducing its entry's published data exactly;
11 proved and installed as `lexicographic-array`.** The rest carry no parsable recurrence.

## 13 September 2026 — `pairclique`: a condition over every pair or triple of positions

65 entries of the shape

    Number of -3..3 arrays x(i) of n+1 elements i=1..n+1 with x(i)+x(j), x(i+1)+x(j+1),
      -(x(i)+x(j+1)), and -(x(i+1)+x(j)) having two, three or four distinct values for every
      i<=n and j<=n.

quantify over ALL pairs — or, in the larger variant, all triples — of positions, so no bounded
window decides them and no engine read one. But the condition depends on those positions only
through the ADJACENT PAIRS (x_i, x_{i+1}) they sit at. Writing D for the set of distinct
adjacent pairs an array uses, the condition says exactly that every two (or three) members of D
are compatible: D must be a clique of a fixed graph on the (2A+1)² pairs.

That makes the state (last value, the pairs used so far), and admissibility is subset-closed so
appending only tests the new pair. Two further steps were needed to make it a model that can be
evaluated rather than one that merely exists:

* for a PAIRWISE condition the future depends only on which pairs are still ALLOWED, not on
  which were used — the allowed set is the intersection of the neighbourhoods — and carrying
  that instead took the raw state count from over 300,000 to **189**;
* and the raw automaton is highly redundant, so it is lumped by identical future behaviour:
  9,018 states to **29** for the triple family, 189 to **10** for the pair family. The
  residual test runs until S consecutive residuals vanish, so the state count is the whole cost.

**111 names read, 65 build within the limits and every one of those reproduces its entry's
published data exactly; 52 proved and installed as `pairwise-compatible-array`.** The triple
condition over -3..3 is refused: it is not pairwise, so the state must carry the set of pairs
used rather than the set still allowed, and at 49 pairs that space is past any budget.

## 13 September 2026 — `permset`: displacements restricted to a SET

23 entries read `Number of permutations of 1..n with displacements restricted to
{-5,-4,-2,0,1,3}.` and nothing read one. `permdisp` counts permutations whose displacement lies
in an INTERVAL -d..d and reads a different name shape; here the allowed set has holes in it,
which the same walk handles without changing anything but which values a step may choose.

Build the permutation left to right. At position i the value placed is i+delta for delta in D,
so only the values in the window [i−L, i+R] are ever in play, with L = −min D and R = max D.
Carry a bitmask of which of those W = L+R+1 values are used and slide the window one place each
step; the value i−L can never be reached again once position i is passed, so it must be used by
then, and that is the whole constraint on the slide. Before position 1 the window's values below
1 do not exist, so their bits start set; after n positions every value at most n is used and
every value above n does not exist, so the accepting mask is the one the walk started from. A
permutation is exactly a closed walk of length n.

**22 names read, every one reproducing its entry's published data exactly; 21 proved and
installed as `displacement-set`.** One is not open.

## 13 September 2026 — `arrline`: the growing dimension either way

`arrlex` carries the lexicographic conditions for a growing HEIGHT. Seven more entries grow the
WIDTH — `Number of 5 X n 0..2 arrays with ...` — and add a local condition on the differences
mod 3. Both are the same walk once the array is read line by line along whichever dimension
grows: the fixed dimension gives the line length, one of the two lexicographic conditions
compares CONSECUTIVE lines and is local, the other compares the k lines running the other way
over the whole growth and is carried by one flag per adjacent pair, and a difference condition
is local either way — within a line, or between consecutive lines. The `nonincreasing' variant
is the same flag with the comparison reversed.

A clause the parser does not know makes it refuse the name rather than ignore the clause: an
engine that silently drops a condition counts something the entry did not ask for.

**17 names read, every one reproducing its entry's published data exactly; 13 proved and
installed as `line-order-array`.** Four carry no parsable recurrence.

## 13 September 2026 — `conn`: every value's cells forming ONE connected region

40 entries in the pool turn on connectivity and no engine read one, because connectivity is
decided by no bounded window at all: two cells of the same colour may be joined through a path
that leaves any window and comes back. The FRONTIER carries it. Reading the array row by row,
the state is the colours of the current row, which of its cells lie in the same component of
the region seen so far (a partition of the k positions, refining the colouring, canonically
labelled), and for each colour whether it is unseen, still open, or already CLOSED.

A component closes when the new row has no cell in it — nothing can reach it again — so at that
moment the colour must have had exactly that one component and must not appear later. At the
end every colour that appeared has exactly one component, and the count is a walk in a finite
digraph.

Two things the first version got wrong, both caught by the entries' own published terms:

* the component merging was written by hand over group representatives and lost arrays whose
  two frontier components of one colour are joined by the row below — 24 against the entry's
  30 at n = 2. Replaced by one union-find over the old frontier cells and the new ones
  together, which is the whole of the transition.
* `no element having more than 2 neighbours with the same value' was checked against the left,
  the right and the cell ABOVE, and a cell's fourth neighbour is the one BELOW, which is not
  known when the row is placed. A164760 came out identical to the entry without that clause —
  the clause was being counted as though it were not there. The partial count now travels in
  the state, one small number per position, and is checked when the row below arrives.

**15 names read, every one reproducing its entry's published data exactly; 5 proved and
installed as `connected-regions`.** Nine carry no parsable recurrence and one is not open. The
same machinery reaches the binary `all 1s connected' family and the `slanted' variants, which
add a path condition and a shifted geometry respectively; both are next.

## 13 September 2026 — `conn2` and the slanted geometry

Two extensions of the frontier engine, both small and both caught by the entries' own terms.

**`conn2`, the binary family.** `conn` asks EVERY value's cells to be connected; the binary
names ask it of the 1s alone and leave the 0s free, and enforcing it for the 0s as well counted
10, 61, 273 against A163030's 10, 88, 920. With the 1s in one component, `a path of 1s from the
top row to the bottom row' says exactly that some 1 lies in the top row and some in the bottom —
the path is then automatic — so the endpoint clauses cost four flags and nothing more. **22
names read, all 8 with published data checked reproducing it exactly; 1 proved and installed as
`connected-ones`.** The rest are not open or carry no parsable recurrence: an honest small
number for a family that looked like fourteen.

**The slanted arrays.** `slanted n X k (i=1..n) X (j=i..k+i-1)` is a parallelogram: row i spans
columns i..i+k-1, so the cell below (i,j) sits one place to the LEFT in the next row's own
indexing. One offset in the frontier union-find handles it — and the same offset was needed
again in the neighbour count, which is what the two remaining mismatches were.

**14 names read, every one reproducing its entry's published data exactly; 4 more installed as
`connected-regions`.**

## 13 September 2026 — `multizero`: nondecreasing arrangements with sum zero

A nondecreasing arrangement of n numbers from -A..A is a MULTISET, so it is its counts c_v, and
every condition is linear in those and in n: `sum c_v = n`, `sum v c_v = 0`, `c_v >= 0`, and
sometimes `sum v^2 c_v <= alpha n`. Nothing is a walk — the LENGTH grows and the alphabet is
fixed — and `latpoly` reads the mirror shape where the length is fixed.

Use the first equation to ELIMINATE n and every remaining condition is homogeneous in c alone,
so the admissible c form a union of relatively open rational cones and a(n) counts their lattice
points at height sum c_v = n: an Ehrhart quasi-polynomial. Passing the equality to `latpoly`'s
ray finder instead — which reads its forms in the x variables only — asked for `sum c = 0` and
found two rays where the arrangement has many; the derived annihilator then failed at every
index, which is exactly what the extrapolation guard is for.

**6 names read, 3 build within the limits and all 3 reproduce their entry's published data
exactly; 2 proved and installed as `zero-sum-multiset`.** The square clause costs a third axis
in the count, so an annihilator of degree 138 there is a model that cannot be evaluated and is
refused with the reason; so is -6..6, whose annihilator has degree 160.

## 13 September 2026 — `winimage`: how many distinct arrays a window statistic can produce

    Number of second differences of arrays of length n+2 of numbers in 0..6.
    Number of arrays of median of three adjacent elements of some length n+2 0..3 array, with
      no adjacent equal elements in the latter.
    Number of arrays of maxima of three adjacent elements of some length n+2 0..6 array.

The entry counts the DISTINCT images, not the arrays: two inputs giving the same output word are
one. That is the image of a sliding-window map, so the output words form a regular language and
the count is a walk in its subset construction — a state is the set of input windows still
consistent with the output emitted so far. Nothing about the statistic matters beyond its being
a function of a fixed window, so medians, maxima, minima and k-th differences are one engine.

The subset automaton is enormously redundant — a third difference over 0..5 has 7,917 states
and 21 behaviours — and the residual test runs until S consecutive residuals vanish, so the
state count is the whole cost. Merging states with the same FUTURE changes no count and is what
makes these evaluable at all.

**17 names read, every one reproducing its entry's published data exactly; all 17 proved and
installed as `window-image`.**

This is the same construction `edgemark` uses, where the machinery was right and the reading of
`trailing edge maxima' was not. Here the statistics are unambiguous, and every entry's own terms
confirm it.

## 13 September 2026 — `coverzero`: an obligation a block not yet read can meet

    Number of arrays of -3..3 integers x(1..n) with every x(i) in a subsequence of length 1, 2
      or 3 with sum zero.
    Number of arrays of n 0..14 integers with new values introduced in order 0..14 but
      otherwise unconstrained.

Two families, both walks, neither local on its own. An obligation on position i — that it lie in
a zero-sum block of length at most W — can be met by a block that has not been read yet, so the
state carries the last W−1 values together with which of those positions are still uncovered,
and a position may only leave the window once covered. With W = 3 over -3..3 that is 49 windows
and four flags. `New values introduced in order' needs no values at all: the array is determined
by which of the values already used each term repeats, or that it is the next unused one, so the
state is HOW MANY distinct values have been used — a walk on the alphabet's size with m+1 edges
out of state m.

**18 names read, every one reproducing its entry's published data exactly; 12 proved and
installed as `covered-by-zero-block`.** Six are not open.

### The pool, re-measured

After today's engines the pool is **2,048**, down from 2,225 this morning: 386,840 entries
outside the roster, 3,356 with a parsable conjectured recurrence, 2,048 of those read by no
engine.

## 13 September 2026 — `shiftmult`: values confined to a sliding range, used at most m times

    Number of length n arrays x(i), i=1..n with x(i) in i..i+3 and no value appearing more than
      2 times.

Eight entries, none read. The value x(i) = i + d with d in 0..k, so the value v can be taken
only by the indices v−k..v: at any moment just k+1 values are in play, and how often each has
been used so far is all the condition asks. The state is those k+1 counters, each capped at the
allowed multiplicity, and the walk slides one value out and one in at each step — a value that
leaves has had its final count, and no count is ever required, only bounded.

**8 names read, every one reproducing its entry's published data exactly; all 8 proved and
installed as `shifted-multiplicity`.**

## 13 September 2026 — `modsum`: sums that look unbounded but are taken modulo M

    Number of 2Xn 0..3 arrays with no element equal to zero plus the sum of elements to its
      left or one plus the sum of the elements above it or one plus the sum of the elements
      diagonally to its northwest or one plus the sum of the elements antidiagonally to its
      northeast, modulo 4.

14 entries, none read. The four sums look unbounded, but every comparison is taken MODULO M, so
only the residues matter and the state is finite. Reading the array column by column, the sum to
the left of a cell is its row's running sum; the sum above it is the cell over it in the same
column; the sum diagonally to the north-west is the cell above and one column back. The sum
ANTIDIAGONALLY to the north-east is the cell above and one column FORWARD, which has not been
read yet, so that comparison is deferred by one column — and at the last column it is the empty
sum, which is what the walk accepts on.

**13 names read, every one reproducing its entry's published data exactly; all 13 proved and
installed as `modular-running-sum`.**

## 13 September 2026 — `lexsub`: a lex-ordered source, and the images of its subblocks

    Number of n X 2 (-1,0,1) arrays of determinants of 2 X 2 subblocks of some (n+1) X 3 binary
      array with rows and columns of the latter in lexicographically nondecreasing order.

Nineteen entries, none read, and they are two solved shapes composed. The SOURCE is an
(n+1) X (k+1) binary array whose rows are lexicographically nondecreasing downwards and whose
columns are lexicographically nondecreasing rightwards: the row order is a condition on two
consecutive rows, and the column order needs one bit per adjacent column pair saying whether
that pair is still equal or has already gone strictly less — `arrlex`'s walk. The OUTPUT is the
DISTINCT images of a map whose value on output row i is a function of source rows i and i+1 —
`winimage`'s subset construction, a vertex being the set of source states consistent with the
output emitted so far. Nothing about the statistic matters beyond its being a function of the
four cells, so determinants, permanents, sums, diagonal-minus-antidiagonal, the two lex-order
indicators, the sum indicators and "nonzero determinant" are one engine.

**19 names read, every one reproducing its entry's published data exactly, and every one
confirmed by a separate brute force that shares no code with the engine.**

## 13 September 2026 — `edgemark`, reopened: what "trailing edge maxima" actually means

    Number of binary arrays indicating the locations of trailing edge maxima of a random
      length-n 0..2 array extended with zeros and convolved with 1,4,6,4,1.

This family was recorded as null on 13 September: the machinery was right — a brute force over
all 3^10 arrays agreed with it — and the READING was wrong, giving 85 against A221993's 84 at
n = 10. Three tie-breaking rules, four marker windows, two paddings each side and the reversed
kernel all gave 85, so the reading was declared unpinned and nothing was installed.

What was wrong was the assumption that the mark is a radius-one test. It is not, and no such
test can work: an exhaustive search over ALL 512 predicates on (sign(c(i)-c(i-1)),
sign(c(i)-c(i+1))), at every contiguous window, fails on A222021 and A222329 at n = 4. A
plateau of the convolved sequence can be arbitrarily long — with kernel 1,1 the plateau
condition is x(i-1) = x(i+1), so x = a,b,a,b,... is one plateau throughout — and whether the
plateau's left end rose or fell is not visible from one neighbour.

Position i is a trailing edge maximum when c(i) > c(i+1) and the nearest EARLIER position with
a different value is lower: the right-hand end of a plateau that is a strict local maximum, the
all-zero tail on the left counting as lower. One bit of state carries the unbounded lookback.
The model is then an automaton on the last |K| input values together with that bit, emitting
one mark per step with a delay of one; and the entry counting images rather than inputs, the
count is a walk in its subset construction, with an end vector that is NOT an incidence vector
— it records how many distinct completions the forced all-zero tail admits from each vertex.
`unibuild` now prints what a walk is and what the two boundary vectors are per engine, because
its standing sentence ("the vectors recording which windows may begin and end an array") would
have been false here.

**50 names read, every one reproducing its entry's published data exactly, and every one
confirmed by a separate brute force that shares no code with the engine.** The eight remaining
names in the family are two-parameter tables T(n,k) and are refused.

## 13 September 2026 — `boardwalk`: a fixed number of steps, a board that grows

    Number of 7-step self-avoiding walks on an n X n square summed over all starting positions.
    Number of 3-step one space at a time bishop's tours on an n X n board summed over all
      starting positions.

156 entries in the clone, 78 in the pool, and none of them read. The number of steps is fixed
and the BOARD grows, so the set of walk shapes is finite and independent of n. Enumerate every
self-avoiding walk of the stated length in the piece's move set, up to translation; a shape
whose bounding box has sides (w_1,...,w_d) fits a board of side n in exactly
prod_i max(0, n - w_i) positions, and distinct (start, walk) pairs are exactly distinct
(shape, placement) pairs. So a(n) = sum over shapes of prod_i max(0, n - w_i) — exact for every
n, a polynomial of degree d once n reaches the largest bounding-box side, annihilator
z^(n0+1)(z-1)^(d+1) with both numbers read off the enumerated shapes.

Two readings had to be settled and both were settled by the entries' own data. A "k-step" walk
visits k CELLS and therefore makes k-1 moves: with k moves the 3-step bishop of A187156 gives 8
where the entry gives 20, and with k-1 it gives every published term, as does A188152. And the
"asymmetric" pieces take one space leftwards or up against two rightwards or down, which the
name itself checks by adding that the antidiagonal moves become knight moves — (2,1) and
(-1,-2) are knight moves and the other two diagonals are not.

Sixteen move-set readings — self-avoiding walks in 2, 3 and 4 dimensions, one- and
one-or-two-space bishops and rooks, the collinear queen, the king, the king-knight, the knight,
the left-handed knight (out two, left one), the three restricted kings, the asymmetric rook and
the quasi-bishop — were confirmed by a separate brute force that shares no code and no reasoning
with the engine: it walks the actual board from every cell and counts.

Refused and recorded: the "k-TURN" families (bishop's, rook's and queen's tours counted by
turns) have straight segments of unbounded length, so their shape set is not finite and this
argument does not apply; the T(n,k) tables are two-parameter; and seven entries whose shape
count passes eight million are refused at the cap rather than enumerated.

## 13 September 2026 — `block2x2`: the two medians of every 2 X 2 subblock

    Number of (n+1) X (7+1) 0..2 arrays with the minimum plus the upper median equal to the
      lower median plus the maximum in every 2 X 2 subblock.
    Number of (n+1) X (7+1) 0..2 arrays with the upper median equal to the lower median in
      every 2 X 2 subblock.

Twenty-seven entries, none read, and the machinery was already here: the width is fixed and the
height grows, so a row is a state and a condition spanning two consecutive rows is the edge
relation. What was missing was a reading.

For a 2 X 2 block with entries sorted v1 <= v2 <= v3 <= v4 the minimum is v1, the lower median
v2, the upper median v3 and the maximum v4, so the first family asks v1 + v3 = v2 + v4. Since
v1 <= v2 and v3 <= v4 the left side never exceeds the right, and equality forces BOTH v1 = v2
and v3 = v4: the four entries form two equal pairs. That is why the digraph is sparse — 65,536
rows and 67,072 edges at width 8 over 0..3 — and the edges are found by walking the row one
column at a time rather than by testing 4 x 10^9 pairs of rows. The sibling family asks only
v2 = v3.

Two entries of the family are (n+1) X (n+1): both dimensions grow, no row is a state, and they
are refused.

**27 names read, every one reproducing its entry's published data exactly, and eight of them
confirmed by a separate brute force that enumerates the arrays cell by cell and shares no code
with the engine.**

## 13 September 2026 — the block defect, found once more in the sweep that feeds everything

`sweep_uni` decided which lines of an entry to read with a word test, `onjectur|Empirical`, on
the line. That is defect 2, and it was fixed in the pool filter, in the live re-check and in
`pooltrim` — and never in the standing sweep. It went unnoticed because the CANDIDATE LIST the
sweep reads was already filtered with `conjlines`, so only six of its candidates were hidden by
it. Asked of every name instead, by the new `sweep_engine.py`, the same test refused 170 of 205
entries as "no parsable recurrence": every lexsub name and every boardwalk name, with the
recurrence in plain sight inside a `Conjectures from X: (Start)` block. Both sweeps now read
`conjlines.lines(e)`.

`sweep_engine.py` exists because a newly written engine was invisible to every sweep until
`uni_cands.json` was rebuilt, a quarter of an hour of work that three engines in one afternoon
restarted three times. It asks the named engines about every name with no cache in between.
