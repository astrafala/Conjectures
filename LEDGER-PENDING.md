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
