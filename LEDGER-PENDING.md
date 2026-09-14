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

## 13 September 2026 — `binwin`: windows of a binary array read as numbers, in order

    Number of (n+2) X 9 binary arrays with consecutive windows of three bits considered as a
      binary number nondecreasing in every row and column.

Sixteen entries, none read. The width W is fixed and the height grows. Along a ROW the W-w+1
windows of w consecutive bits, read as binary numbers, must not decrease left to right — a
property of the row alone, and an extremely restrictive one: of the 512 binary rows of width 9
only 14 survive it for a window of three and 21 for a window of four. Down a COLUMN the same
must hold of the vertical windows, and a vertical window spans w rows, so comparing two
consecutive ones needs w+1 rows; the state is the last w rows, each of them one of that
handful. That is why the height in the name is n + w - 1 and why the names read (n+1), (n+2),
(n+3) as the window widens: the array must be at least w tall to have a vertical window at all.

**16 names read, every one reproducing its entry's published data exactly, and six confirmed by
a separate brute force that enumerates the arrays and tests the windows directly.**

## 13 September 2026 — `circdigit` and `circbase`: circular digits, and a claim about the BASE

    Number of base 7 circular n-digit numbers with adjacent digits differing by 5 or less.

229 entries, none read. The model is one line: let G be the graph on the digits 0..b-1 with an
edge between u and v when |u-v| <= d, loops included. A circular n-digit string is a closed walk
of length n in G with a marked start, so a(n) = trace(M^n) for n >= 1, and the characteristic
polynomial of M annihilates it — monic of degree exactly b, by Cayley–Hamilton, with no bound to
estimate. The entry counts every string, leading zeros included: requiring a nonzero first digit
gives 4, 11, 25 where A124698 gives 5, 13, 29. At n = 0 the entries write a(0) = 1 where the
trace is b; that is a convention at one index and the papers say so.

Only **10** of the 229 carry a conjectured recurrence. **219 carry something else entirely**,
which is why every sweep called them "no parsable recurrence":

    [Empirical] a(base,n) = a(base-1,n) + F(5) for base >= 5*int(n/2)+1
    and F(d) is the largest coefficient in (1+x+...+x^(2d))^n

It is not a recurrence in n. It relates two DIFFERENT entries. It is also true, sharply, and the
proof is four steps with no computation in it:

  1. a(base,n) - a(base-1,n) counts the admissible cyclic tuples over {0..b-1} that USE the
     value b-1, since the rest are exactly the tuples over {0..b-2}.
  2. Every admissible cyclic tuple has max - min <= d*floor(n/2): the two arcs between a
     position of the max and one of the min have lengths summing to n, so one has length at
     most floor(n/2), and along an arc of length L the value moves by at most d*L.
  3. A tuple using b-1 has maximum b-1, so all its values lie in a window of width
     d*floor(n/2) below b-1. The hypothesis base >= d*floor(n/2)+1 says exactly that the
     window fits inside the alphabet, so the count is that of the admissible cyclic tuples
     over Z with maximum 0 — independent of the base.
  4. Translation is free on those, each orbit has one representative with max 0 and one with
     c_1 = 0, and the latter are the step vectors in {-d..d}^n summing to zero, of which there
     are [x^(dn)](1+x+...+x^(2d))^n — the entry's own F(d).

The entry's threshold is exactly the hypothesis of step 3 and is sharp: one base lower the
window no longer fits and the identity fails, which was checked for d = 1, 2, 3 and every
n <= 8.

**10 proved as recurrences and installed as `circular-digit-trace`; 219 cross-base identities
verified over their whole claimed range and installed as `circular-base-identity`.** Twenty-six
of those 219 are flagged by the openness check, and in all twenty-six the settlement wording is
Ray Chandler's confirmation of the LINEAR RECURRENCE on the entry, a different statement; the
cross-base line is still marked empirical on each.

## 13 September 2026 — `linbase`: the same claim on the linear strings, and where the -2 comes from

    Number of base 11 n-digit numbers with adjacent digits differing by two or less.
      [Empirical] a(base,n)=a(base-1,n)+5^(n-1) for base>=2n-1;
                  a(base,n)=a(base-1,n)+5^(n-1)-2 when base=2n-2.

130 more entries, found by asking section P's question of the clone: 121 of them came back in
the "two-parameter identity" bucket, the rest by name. The model is the same one step simpler —
strings, not cycles, so a(n) = 1^T M^(n-1) 1 and a(0) = 1 is the empty string — and the proof is
the same four steps with the boundary case now IN the claim:

  1. a(base,n) - a(base-1,n) counts the admissible strings over {0..b-1} using the value b-1.
  2. Translation acts freely on the admissible strings over Z; each orbit has one representative
     with c_1 = 0, determined by its step vector in {-d..d}^(n-1), so there are (2d+1)^(n-1)
     orbits, and every orbit has a range at most d(n-1).
  3. A string counted in 1 is the representative with maximum b-1 of an orbit whose range is at
     most b-1, and conversely. So the difference counts the orbits of range <= b-1.
  4. If b >= d(n-1)+1 every orbit qualifies: the difference is (2d+1)^(n-1). If b = d(n-1)
     exactly, the orbits of range d(n-1) are lost, and an orbit has that range only if the walk
     from its minimum to its maximum uses all n-1 steps in one direction at full size — so
     exactly TWO of them, all +d and all -d.

That is the entry's second clause, and the -2 is those two monotone strings. Both thresholds are
the entry's own.

**130 verified over their whole claimed range and installed as `linear-base-identity`.** One
entry, A126404, is refused: it declares offset 1 while its first published term is the empty
string's 1, so the entry's own n and the string length are out of step by one and no reading of
"n" in the claim can be defended. Three more are flagged by the openness check, and in all three
the settled statement is the linear recurrence (Barker's conjecture, or the transfer-matrix
identity), not the cross-base line.

## 13 September 2026 — `ratrec` refused four kinds of ordinary recurrence line

The parser that decides whether a line states a constant-coefficient recurrence takes everything
after `a(n) =` and then refuses the line if anything is left over once the recurrence terms are
removed. That leftover test is what makes it safe. It is also what refused these:

    Empirical: a(n)=16*a(n-1)-...-a(n-16) (=polynomial of degree 15)
    Empirical: a(n) = 4*a(n-3) n > 14.
    Empirical: a(n) = 3*a(n-1) ... -a(n-14), for n>18.
    Empirical: a(n) = a(n-1) + 3*a(n-2) + 2*a(n-3). (Follows from g.f. ...)

A trailing parenthetical, a qualifier with no "for", a comma before the qualifier, and a second
sentence. Each is now removed before the leftover test, and only when the removed text carries
no recurrence term — which matters more than it looks: a trailing parenthetical is also what
the LAST TERM of every one of these lines ends with, `-a(n-16)`, so the strip had to require the
parenthesis to stand alone, preceded by whitespace. Without that the parser silently dropped the
final term of the recurrence it was reading. A bare `n > k` qualifier is now read as a threshold
as well.

Checked against a baseline of 11,176 lines that parsed before the change: **0 lost, 0 changed,
15 gained.** Ten of the fifteen proved immediately.

And the question the change raises, asked of the sweep's own candidate list: **790 entries that
`sweep_uni` marked done are not in the roster and DO carry a parsable recurrence.** The done set
records no reason, so they are being re-asked rather than guessed at. `sweep_engine.py` grew an
`ONLY_ANUMS` filter for exactly this: when a PARSER is widened rather than an engine written, the
entries that changed are known by name, and sweeping every name of sixty-six engines to reach
them is hours of work for nothing.

### The one entry of that family that is refused, and why

`circdigit` now also reads "base-6 circular n-digit numbers" and "circular n-letter words over
the alphabet {0,1,2,3}", which are two more spellings of the same count; that added five entries
and four of them are installed. The fifth, **A124696**, is refused. Its range clause reads

    for base = 1..floor(n/2)+1

where all 228 of its siblings read `for base >= d*floor(n/2)+1`. That is the opposite
inequality, and read literally the claim is FALSE: at base 3 it asserts the identity from n = 6
onwards, where the difference is 135 and F(1,6) is 141. It is plainly a typo. Recording it as a
disproof would be recording a defect in someone's typing, and quietly reading it the other way
round would be putting words in the entry's mouth, so `circbase` now requires the clause to be
of the `for base >= ...` form and refuses anything else.

## 13 September 2026 — `samefour`: every 2 X 2 subblock holding the same four values

    1/16 the number of (n+1) X 7 0..3 arrays with all 2 X 2 subblocks having the same four
      values.

Fifteen entries, none read. "The same four values" is the same MULTISET in every block, and the
condition is rigid enough to write down in a paragraph. Two horizontally adjacent blocks of a
row pair share a column, so with m_j the multiset {r_j, s_j} of the pair's j-th column the
condition reads m_j + m_{j+1} = V for every j, V being the common four-value multiset. The m_j
therefore ALTERNATE: m, V-m, m, V-m, .... Once V, the alternation and the top row are fixed the
bottom row is DETERMINED cell by cell — s_j is what is left of the required multiset after
removing r_j — and the top row is only constrained to have each r_j in that multiset. The whole
count is the disjoint union over V of these digraphs, disjoint because V is read off any one
block and so cannot change within an array. Lumped, every one of the fifteen comes down to
S = 4 states, whatever the width.

The name's divisor is the square of the alphabet size, 16 over 0..3 and 9 over 0..2. `unibuild`
now prints the quotient in the formula rather than the walk count, because a paper may not show
the entry's sequence as something it is not.

**15 names read, every one reproducing its entry's published data exactly, and five confirmed by
a separate brute force that enumerates the arrays and tests the blocks directly.**

## 13 September 2026 — `partsum`: sums that are unbounded and a condition that is not

    Number of length n 1..(4+1) arrays with every leading partial sum divisible by 2, 3 or 5.

Twenty-three entries, none read. The partial sums grow without bound and the condition does not
depend on them: divisibility by any of d_1,...,d_r is decided by the sum modulo
M = lcm(d_1,...,d_r). So the state is that residue, the digraph has exactly M vertices, an array
is a walk from residue 0 — the empty prefix — through residues each divisible by one of the
divisors, and the alphabet 1..K contributes K edges out of every vertex of which only the
admissible ones survive. The bound is M, read off the divisors.

**23 names read, every one reproducing its entry's published data exactly, and three confirmed
by a separate brute force that enumerates the arrays and adds up the prefixes.**

### And the pool file is stale again

`deep-check/pool-unread.json` still lists the sixteen "every x(i) in a subsequence of length 1
or 2 with sum zero" entries as read by no engine. `coverzero` reads all sixteen, and thirteen of
them are already in the roster, proved this morning. That is defect 1 for the eighth time: the
pool is a snapshot and every engine written since invalidates it. It is re-measured below rather
than trusted.

## 13 September 2026 — two more, both found by asking what the pool still could not read

    Number of n element 0..2 arrays with each element the minimum of 7 adjacent elements of a
      random 0..2 array of n+6 elements.
    Number of 0..5 arrays x(0..n-1) of n elements with each no smaller than the sum of its two
      previous neighbors modulo 6.

**`winimage`, widened: 10 entries.** The same sliding-window image the engine was written for,
with the name written the other way round — the entry gives the OUTPUT length first and calls
the input "a random 0..2 array of n+6 elements" instead of "some length n+6 0..2 array". Not a
new model; a new sentence. That is the shape of most of what the pool still holds.

**`modprev`: 11 entries.** Each element must be no smaller than a sum of earlier ones taken
modulo M. The sums are unbounded and the condition is not. For the "k previous neighbors" form
the sum runs over a window, so the state is the last k values — their residue is what the
condition reads, but the window must be carried in full because the oldest value leaves it. For
the "previous elements" form the sum runs over everything read so far, and the running total
modulo M IS the state, one vertex per residue. At the start there are fewer previous elements
than the window asks for; the entries' own terms say the sum is over those that exist, so x(0)
is unconstrained and a(1) is the whole alphabet, and every published term follows.

**21 names read and proved; every one reproducing its entry's published data exactly.**

## 13 September 2026 — `covwin`: a window that must hold everything, and an order it cannot see

    Number of length n+3+1 0..3 arrays with every value 0..3 appearing at least once in every
      consecutive 3+2 elements, and new values 0..3 introduced in order.

Ten entries, none read, and two conditions of opposite character. The COVERAGE is local: a
window of w consecutive elements must contain all of 0..k, so the last w-1 values decide whether
a given value may be added next. The INTRODUCTION ORDER is not local at all — a value may be
used only when every smaller one has already appeared, and "already appeared" reaches back
without bound. One counter carries it, because the values arrive in order: how many of 0..k have
been introduced so far.

So the vertex is (the last w-1 values, that counter), and what the edge relation tests is a
window CLOSING. The alphabet has k+1 values and the window is k+2 or k+3 wide, so a closing
window holds every value with one or two to spare; that is restrictive enough to keep the
reachable state count manageable — 191 states at k=3 and 1,174,575 at k=7, lumping to 16 and 60.
The entry's length, n+k+1 or n+k+2, is exactly where the first window closes.

**10 names read, all 10 proved, every one reproducing its entry's published data exactly.**

## 14 September 2026 — `introord`: an order the array is introduced in, from one end or both

    Number of 0..5 arrays of length n with no adjacent pair equal to its immediately preceding
      adjacent pair, and new values introduced in 0..5 order.
    Number of length n 0..5 arrays with new values introduced in order from both ends.

Eleven entries. The introduction order is a condition no window can decide, and one counter
carries it: how many values have been introduced so far, the values arriving in order.

The first family's other clause had to be settled by brute force, and the obvious reading is
wrong. "No adjacent pair equal to its immediately preceding adjacent pair" is NOT "no three
equal in a row": the pairs OVERLAP, and the pair immediately preceding (x_i, x_{i+1}) is
(x_{i-2}, x_{i-1}), the one starting two places back. The condition forbids a window of four
with period two and is vacuous below length four — which is exactly what the entries' own a(3)
says, 5 where the three-in-a-row reading gives 4. The non-overlapping reading gives 36 at n=5
against the entry's 33; the overlapping one gives 33 and every later term.

The second family is the better piece of machinery. Introducing new values in order from BOTH
ends says every prefix AND every suffix has a value set of the form {0,1,...,m}. The prefix half
is the counter. The suffix half is the same condition on the reversed array, so read left to
right it is the REVERSE of a deterministic automaton — nondeterministic, but UNAMBIGUOUS, since
each array has exactly one run backwards, and an unambiguous automaton's walk count is still the
number of words. So the vertex is (introduced in the prefix, still to be introduced in the
suffix, the total), the two ends tied together by that total, and the walk runs from (0,t) to
(t,0). A first attempt tracked the suffix MAXIMUM instead of the suffix count and silently
reproduced the plain introduction-order numbers — the maximum does not know whether the values
below it are all present.

**11 names read, all 11 proved, every one reproducing its entry's published data exactly, and
both readings settled against a brute force before any engine was written.**

## 14 September 2026 — `seconddiff`: half the arrays whose second differences never vanish

    Half the number of 0..2 arrays of length n+2 with second differences nonzero.

Six entries. The second difference at i is x_i - 2x_{i+1} + x_{i+2}, a window of three, so the
condition is the edge relation on the pairs and the digraph has (k+1)^2 vertices — nothing to
discover there. What the paper has to get right is the entry's divisor. It is the reflection
x -> k - x: that map sends every second difference to its negative, so it preserves the counted
set, it is an involution, and it has NO fixed point in that set, since a fixed array is constant
and a constant array has second difference zero. So the count is even and half of it counts the
reflection orbits.

The one index where that argument fails is the one the entry does not use. At length 2 there is
no second difference at all, every array qualifies, and the constant array k/2 IS fixed when k
is even — so the count is odd and has no half. The entry's a(1) is the length-3 count, and the
engine steps the walk once before emitting anything. Three of the six came back as "terms
failed" until that was fixed, which is the refusal saying what the reading is.

**6 names read, all 6 proved, every one reproducing its entry's published data exactly.**

## 14 September 2026 — `rcintro`: an introduction order along every row AND every column

    Number of n X 4 0..2 arrays with new values introduced in each row and column in
      sequential order starting with zero.

Eight names, six of them open and proved. The ROW condition is a property of one row, so the
admissible rows are a fixed finite set computed once — 14 of them at width 4 over 0..2, 877 at
width 7 unbounded. The COLUMN condition is decided by no window at all, and does not need one:
the values arrive in order, so all a column needs is HOW MANY values it has introduced so far.
The vertex is one counter per column; adding a row asks only that each entry not exceed its
column's counter, and increments the counter when it equals it.

The "nonnegative integer" half of the family needs no alphabet bound argued for. A row of width
k has at most k distinct values and its own introduction order forces r_j <= j, so no entry can
exceed k-1 however "nonnegative integer" is read; the two halves differ only in where the cap
bites, and the engine sets A = min(A, k-1) for both.

**8 names read, all 8 reproducing their entries' published data exactly; 6 open and installed.**

## 14 September 2026 — `neighdiff`: an obligation, not a window

    Number of 0..6 arrays of length n with each element differing from at least one neighbor
      by 1 or less, starting with 0.

33 names read, 19 of them open and proved. "At least one neighbour" cannot be decided where it
is written: the element's left neighbour is known when it is read and its right neighbour is
not. One bit carries it — whether the element just read is still waiting for a partner — so the
vertex is (that element, that bit). Reading the next element either discharges the debt, in
which case the new element is itself already partnered, or leaves it standing, in which case the
array is dead if a debt was already outstanding. An array is admissible exactly when it ends
with no debt. Three relations appear in the names — "1 or less", "something other than 1", "2 or
more" — and each with and without "starting with 0".

A length-1 array is never admissible, since its one element has no neighbour at all, and every
entry of the family publishes a(1) = 0. A first version special-cased that index and waived the
debt, with a paragraph of prose explaining why; the entries' own first term said otherwise at
all 33 names at once. The walk already gave 0 and the special case was the error.

**33 names read, every one reproducing its entry's published data exactly; 19 open and
installed.**

## 14 September 2026 — `triangsq`: a Pell equation in disguise, and why the order is 5

    Indices k such that 6 plus the k-th triangular number is a perfect square.

Seventeen entries, none read, and the first result here that is number theory rather than a
transfer matrix. k(k+1)/2 + c is a square exactly when eight times it is, and completing the
square gives

    (2k+1)^2 - 2(2m)^2 = 1 - 8c,

so with X = 2k+1 and Y = 2m the admissible k are the solutions of X^2 - 2Y^2 = N, X odd
positive and Y even nonnegative. The form's automorph from the unit 3 + 2*sqrt(2) is
T(X,Y) = (3X+4Y, 2X+3Y); every solution is T^j of a FUNDAMENTAL one, whose preimage leaves the
region, and there are finitely many of those — r of them, found by a search that is CHECKED
rather than bounded by a quoted theorem: run to a limit, re-run to four times the limit, and the
engine refuses unless the two agree.

The bound comes from one observation. On X >= 1, Y >= 0 we have Y = sqrt((X^2-N)/2), increasing
in X, so T(X) = 3X + 4Y is strictly increasing: **T preserves the order of solutions**. Hence
once the sorted list has its (n+r)-th entry equal to T of its n-th for r consecutive n, it does
for ever, and the r orbits interleave in a fixed cyclic order from there. Within an orbit
X_{j+2} = 6X_{j+1} - X_j, so k_{j+2} = 6k_{j+1} - k_j + 2, and therefore

    a(n + 2r) = 6 a(n + r) - a(n) + 2,

annihilator (z-1)(z^{2r} - 6 z^r + 1) of degree 2r+1. Sixteen of the seventeen have r = 2, which
is the order-5 recurrence every one of them conjectures; A154145 has r = 4 and conjectures the
order-9 one. The number the entries could only observe is the number of fundamental solutions.

**17 names read, every one reproducing its entry's published data exactly; 10 open and
installed.**

## 14 September 2026 — `pellsq` is NULL, and it is worth saying why

Having proved the triangular-number family by way of its Pell equation, the obvious next step
was the general shape: **numbers k for which A k^2 + B k + C is a perfect square**. The engine
is written (`src/pellsq.py`), it reads 49 names, and 37 of them build a correct model — the
orbits, the interleaving, the annihilator (z-1)(z^{2r} - 2u z^r + 1).

**Not one of them is a result.** Of the 552 entries in the clone whose name has the shape
"Numbers/Indices ... is a (perfect) square" and which are outside the roster, exactly TWO carry
a conjectured recurrence a parser can read, and both are triangular-number entries already
counted here. The rest state no conjecture at all: there is nothing open to settle. Proving a
recurrence an entry does not claim is not a result by this project's rules, and padding the
count with 37 of them would be exactly the kind of inflation the ledger forbids.

The engine stays registered. If such an entry ever grows a conjecture, it is now read.

Two things were learned on the way and are kept in the code:

  * the conjugate solution (X, -Y) is a solution too, and its T-images re-enter the region as a
    DIFFERENT orbit. Seeding only with Y >= 0 lost half the orbits and produced sorted lists
    with holes in them — twenty-four names showed it at once, each with a term missing from the
    middle of the published data.
  * the generated list is checked against a direct search over k below a limit. A missed orbit
    then shows up as a missing TERM rather than as a plausible wrong recurrence, and the engine
    refuses instead of guessing. Twelve of the 49 are refused that way.

## 14 September 2026 — an empirical verification read as a settlement

`openness.status` flagged A154151 as not open on the strength of

    The first conjecture is true for the first 1000 terms of the sequence. - Harvey P. Dale

which is a verification, not a proof. The entry's conjecture is the order-5 recurrence the
Pell argument settles, and it was excluded from the batch it belonged in. `FINITE` — the list
of phrasings that mean "a finite check, not a proof" — now includes "for the first N terms".
A154151 is proved and installed.

The first attempt at that fix was wider: any "for n = <number>" counted as a finite check. That
turned **A185526** from settled to open, and A185526 carries Robert Israel's complete proof —
a transfer-matrix argument whose last step happens to read "for n=4". A guard that makes a proof
look like a check is worse than the gap it closes, so the added phrasing is the narrow one, and
the wider version is recorded here as the thing not to do.

## 14 September 2026 — the shelved engine, and the theorem that unshelved it

`transfer88` reads the knight-distance family:

    Number of (n+2) X (k+2) nonnegative integer arrays with all values the knight distance
    from the upper left minus as much as s, with successive minimum path knight move
    differences either 0 or +1, and any unreachable value zero.

It was written weeks ago, its reading pinned by brute force, its builder finished — and then
deliberately left OUT OF SERVICE, with the reason written into its own docstring. The transfer
matrix needs the local structure of the board to repeat down the strip, and that rests on

    d(i+4, j) = d(i, j) + 2                                                       (P)

for every column once i is large enough. The inequality `<=` is immediate: the moves (2,1)
then (2,-1) drop four rows and return to the same column. The inequality `>=` had only been
CHECKED, over a few hundred rows. A finite check of an infinite claim is evidence and not a
proof, so nothing was shipped and the obstruction was written down instead. That was the right
call, and it is worth recording that it was: the engine sat unregistered for weeks rather than
ship twenty-one papers resting on a measurement.

**(P) is now a theorem.** The device is the pair of Bellman conditions. For any
D : S_C -> N u {oo} on the strip,

    (a) D(0,0) = 0,
    (b) D(y) <= D(x) + 1 for every knight-adjacent pair,
    (c) every x != (0,0) with D(x) < oo has a knight neighbour y with D(x) = D(y) + 1,

together force D = d. Each half is one induction, and neither cares where D came from — which
is the whole point. So take the field breadth-first search gives on the first few rows, DEFINE
it on the rest of the strip by declaring (P), and check (a), (b), (c). A knight move changes
the row by 1 or 2, so the conditions at row i read only rows i-2..i+2; once all five lie in
the region where the definition reads D(r,j) = D(r-4,j) + 2, the condition at row i IS the
condition at row i-4 with 2 added to both sides. Finitely many rows therefore settle every
row, and the guessed field is the distance.

The same certificate settles the second thing the model needed. The entries count arrays on a
board of exactly n+2 rows, and the short board's distance is NOT the strip's: on a 3 X 3 board
the centre is unreachable, while on any taller board it is at distance 4. What decides it is
whether a cell has a chain of minimum-path predecessors that never needs a row the short board
lacks, and that is computed by

    rho(x) = min over minimum-path predecessors y of max(row(x)+1, row(y)+1, rho(y)),

whose offset from the row index is period-4 for the same reason the field is. The threshold
comes out at H0 = 5 for every width: heights 2, 3 and 4 are genuinely exceptional and are
counted on their own boards, where there is nothing to prove.

`src/kdcert.py` is the certificate. Before it was trusted it was tested on cases whose answers
were known — defect 8 in STATE.md, an instrument that cannot see what it is asked about returns
a confident zero:

  * the field it produces agrees cell for cell with a direct breadth-first search for every
    width 3..9 and every height from H0 to 59;
  * H0 is tight — at height H0-1 the two genuinely disagree, at every width;
  * perturbing one entry of its table by one makes the checker REFUSE, at each width tried.

It also reproduces, from the theorem, the hand-made table `transfer88` had measured:
`{3: 5, 4: 5, 5: 7, 6: 9, 7: 11}` is exactly the certificate's i0 + 2 at every width the old
table covered. That agreement is the one piece of evidence a proof cannot supply itself. The
old table stopped at width 7 and the engine refused widths 8 and up as "showing no period";
the certificate covers every width tried up to 14, i0 = 2C - 3, so those widths are in service
too — three more entries than the family was thought to have.

A second, independently written model (`src/knightval.py`, a row-pair DP carrying the phase in
the vertex and merging by a different rule) reproduces every published term of every entry in
the family. Two engines sharing no code and agreeing on all of it is what the Verification
section of each paper now cites as its third check.

The sweep, the install and the count are below.

### The batch

`sweep_engine.py transfer88` over every name, with no candidate cache in between:
**16 PROVED**, 3 refused at `state space > cap` (widths 8 and 9 at slack 2 and 3, where the
row alphabet is 3^8 and 4^9), 2 with no parsable recurrence (the two diagonal entries
`(n+2) X (n+2)`, whose board grows in both directions and which this model does not read).
Every one of the 16 was re-checked against the live OEIS: 16 kept, 0 dropped, 0 flagged.

    A253112 A253113 A253114 A253115 A253116        slack 2, widths 3..7
    A253335 A253336 A253337 A253338                slack 3, widths 3..6
    A253417 A253418 A253419 A253420 A253421        slack 1, widths 3..7
    A253422 A253423                                slack 1, widths 8 and 9 -- the two the old
                                                   refusal range would have thrown away

Orders 9 to 49, state counts 64 to 11,458, thresholds 15 to 71. Each entry also carries four
quasi-polynomial formulas, one per residue of n mod 4; those follow from the recurrence whose
annihilator has the factor $(z^4-1)$, so they are the same conjecture in another notation and
are NOT counted. **16 results, one per entry.**

Roster: 12,877 -> 12,893 papers over 12,866 entries, 156 arguments.

One thing caught on the way out. `t88build` carried `\date{7 September 2026}` hard-coded from
the day it was drafted, so the whole batch would have been stamped a week before the theorem
that makes it true -- the same shape as defect 16, a paper reporting a date that belongs to
an earlier text. The date now comes from `PAPER_DATE` with today's as the default, as
`unibuild` has always done, and the sixteen PDFs were rebuilt and reinstalled through
`papers-old-numbering/` rather than through the ranked copy (defect 14).
