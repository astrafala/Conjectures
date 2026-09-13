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
