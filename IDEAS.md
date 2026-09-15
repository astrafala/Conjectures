# Every angle of attack, and where each one stands

**RULE 1: NEVER STOP.** Finish one, start the next immediately. When the list runs low, add to
it — new veins, untried conjecture types, re-measurements of anything called dead.

A standing list, not a plan. Each section is a way to settle conjectures; each says what it is
worth and what happened when it was tried. **When one is finished, the next is started without
waiting to be asked.** Ideas found genuinely dead stay here with their numbers so nobody
re-runs them.

**Counting rule.** Two results are distinct when they are on different entries, or when the
entry names them as different conjectures. A generating function whose denominator *is* a
recurrence already proved for that entry is the same conjecture in another notation and is not
counted twice.

---

## A. Settled by machinery already built

| # | idea | pool | status |
| --- | --- | ---: | --- |
| A1 | transfer-matrix models of array-counting names | 3,453 | **done, installed** |
| A2 | order line re-asked on the whole sequence | 245 | **done** |
| A3 | order line re-asked on tails — a claim "for n > t" is not a claim from term 0 | 493 | **done** |
| A4 | T(n,k) table columns and rows | 1,729 | **running**, 184 tables so far |
| A5 | closed forms proved from a transfer-matrix model | 1,100+ | **running** |
| A6 | conjectured recurrence from a **g.f. the entry states as fact** | 2,817 | **null: 2 proved.** The 2,151 rested on a generating function inside the same `Conjectures from X: (Start)' block as the recurrence — one conjecture written twice. 1,336 of them were installed and have been withdrawn; see WITHDRAWN.md |
| A7 | conjectured recurrence from a **closed form stated as fact** | 442 | **null**: all 41 rested on a block line; purged |
| A8 | further conjectures on sequences already proved C-finite | 13,109 | **running**, 297 with new content |

## B. Engines written for name shapes nothing could read

| # | family | pool | status |
| --- | --- | ---: | --- |
| B1 | lexicographic subblock arrays | 37 | **done** |
| B2 | min-filter images of sorted arrays (`transfer95`) | 134 | **97 proved** |
| B3 | one-dimensional words under a window condition (`transfer96`) | 101 | **done** |
| B4 | cusp-form dimensions from the classical formula (`cuspdim`) | 51 | **46 proved** |
| B5 | elementary cellular automaton rows (`ecarow`) | 51 | **done**; the other 71 are genuinely fractal. Confirmed twice on 9 September: widening the shape search from period 8 / settling point 15 / 46 steps to period 16 / settling point 27 / 80 steps finds **nothing**, and dropping the requirement that the row grow by exactly 2p -- searching every cut, as the two-dimensional engine does -- also finds **nothing**. Unlike the 2-D case, where the same widening found 30, here the bound was never the obstacle. The widening is kept because checking over more steps makes every accepted shape a stronger claim; all 51 installed papers still certify under it |
| B6 | derived arrays — indicators of a larger array's subblocks | 54 | **next engine**; `transfer26` has the right machinery |
| B7 | coordination sequences of tilings | 414 | **already harvested** — 384 were proved by the generating-function vein (A6) before this family was ever looked at as one. Listing it as untried was wrong. |
| B8 | two-dimensional CA active-cell counts | 168 | **untried** |
| B9 | CA x-axis and diagonal representations | 294 | **untried**; same shape-certificate idea as B5 |
| B10 | permutations with bounded displacement | 35 | **28 proved** (`permdisp.py`). Only 2d+1 values are ever in play, so a bitmask of the sliding window is the whole state, and a permutation of 0..n-1 is a CLOSED walk: the accepting mask is the one the walk starts from, because the negative half of the window does not exist at the start and the half above n-1 does not exist at the end. 32 of the 35 are read and every one reproduces its published terms; 3 use wordings not yet parsed |
| B11 | arrays constrained through their REPEATED VALUES (`repval`) | 156 | **92 of the 96 length-varying ones proved.** The other 60 fix the length and vary the alphabet: a different argument, untried |
| B12 | length FIXED, alphabet varying -- `Number of length-5 0..n arrays with ...` | 292 | **57 proved** (`ordpoly.py`). When the condition is decided by the ORDER of the terms alone, the array is described by its weak ordering and a(n) = sum_m N_m C(n+1, m): an exact polynomial in n of degree at most L, so the residual test runs with S = L + 1. All 57 models reproduce every published term. 11 are over the state cap and 15 take more than 25 seconds to build. A condition naming an actual difference or a modulus is NOT order-only and is refused |
| B13 | coordination sequences Gal.u.t.v | 379 | **untried**, and the largest single unreadable family. The name alone does not give the tiling; the Galebach data would have to be read |
| B14 | window conditions written the second way -- `Number of 0..7 arrays x(0..n+1) of n+2 elements without any interior element ...` | 164 | **17 proved**; the reader is in `window.py` as `parse_name2`. Two spellings are held back on purpose: "each no smaller than the sum of its two previous neighbors modulo k" matches neither the sliding nor the cyclic reading against published data (11 entries), and "no adjacent pair equal to its immediately preceding adjacent pair" carries a canonical-form clause the engine does not have (6). A reader that half-works settles conjectures about the wrong object |
| B15 | `set{t,u,v in 0,1}((x[i+t]+x[j+u]+x[k+v])*(-1)^(t+u+v))` conditions | 55 | **untried**; the condition ranges over all triples of indices, so it is not a sliding window |
| B16 | `the sum of ... of adjacent triples multiplied by some arrangement of +-1 equal to zero` | ~20 | **refused, with a reason**: whether zero is reachable depends on a set of partial sums that grows with n, so the model is not finite-state |
| B17 | the 1,446 entries with a readable conjecture and a readable name that the cached candidate list had never heard of | 1,446 | **1,017 asked, about 190 proved, and the rest is CAP-BOUND: 811 refused with `state space > cap` at CAP = 2,000,000.** A trial at CAP = 6,000,000 built two models in five minutes and proved neither, and a second attempt at the standing cap was killed by the kernel for memory: `uniform.build` allocates its way toward the cap before it can refuse, so re-asking these is not merely slow, it takes the whole container down and the other sweeps with it. They are marked done again on purpose. The 429 not yet asked are still worth asking. What would actually open this is lumping equivalent states BEFORE the build rather than after it -- `lumpauto.lump` exists and is used only in `threshold()`, far too late |

## C. Claim types, not name shapes

| # | claim type | entries | status |
| --- | --- | ---: | --- |
| C1 | linear recurrence / generating function | 15,978 | the only type attempted before today |
| C2 | congruence and divisibility | 4,130 | **built** (`congruence.py`); only **17** sit on C-finite sequences |
| C3 | ratio-limit asymptotics | 3,978 | **built** (`asympt.py`); **0** of the 47 with a ratio claim has a recurrence |
| C4 | inequality or bound | 5,726 | **untried**; positivity of a C-finite sequence is decidable in low order and open in general |
| C5 | primality or factorisation | 1,618 | **untried**; almost certainly out of reach |
| C6 | always / never / infinitely many | 541 | **untried** |
| C7 | algebraic (radical) generating functions | 193 | **next**; decidable against a proved rational g.f. |
| C9 | conjectured rational generating function, marker written BEHIND the expression | 2,809 | the shared parser refuses `G.f.: ... (conjectured).' outright, so no sweep had ever seen these. `conjgf.py` reads them. Premise veins (D7, D8) are null; the model vein is live |
| C8 | e.g.f. and Dirichlet g.f. claims | 19 | **untried** |

## D. Structural tricks that need no model at all

| # | idea | status |
| --- | --- | --- |
| D1 | premise from a formula the entry states as fact | **null, and it was the biggest mistake of the project.** The corpus almost never states a formula as fact beside a conjectured one; what looked like 2,800 such entries were block conjectures. `factlines.facts` is now the only allowed source of a premise |
| D2 | premise from a proof this project already owns | A8 |
| D3 | closure under transforms — partial sums, differences, bisections | **measured, small**: 2,074 such entries, only 43 with an open conjecture, 12 usable |
| D4 | entries carrying both a known recurrence and a conjecture | 558, mostly already covered |
| D5 | equivalence between two entries the OEIS cross-references | **untried** |
| D6 | a conjecture on a table implying one on each of its columns | **untried** |
| D7 | conjectured g.f. from a recurrence the entry states as fact -- the mirror of D1 | **null: 6 of 1,048.** The census said 1,048 had a stated recurrence; almost every one of them was a line inside the same conjecture block as the g.f., which is the same conjecture in another notation and no premise at all |
| D8 | conjectured g.f. from a closed form stated as fact | **null: 0 of 204**, same reason |
| D9 | conjectured g.f. proved from a transfer-matrix model of the name | 1,565 entries no sweep had read | **running** |

## E. Auditing what the machinery refuses — the highest-yield habit

Every large vein found so far was reachable by machinery already built and hidden by how a
sweep chose what to look at. Not one was hidden by mathematics.

| # | defect found | cost when it was there |
| --- | --- | --- |
| E1 | pool built from a stale snapshot | seven times; 40 to 1,718 entries each |
| E2 | conjectural word required ON the line, so block conjectures were invisible | in the pool filter, in every sweep, and in the live re-check |
| E3 | a sweep that skips without recording the skip re-reads the same index for ever | table sweep had asked 11 of 1,729 |
| E4 | no clock, so one slow entry eats every run | table sweep: 43 entries per window became 266 |
| E5 | a formula split across continuation lines read as truncated | 19 false disproofs |
| E6 | a threshold scan starting one index late | 6 false disproofs |
| E7 | a claim's qualifier dropped ("for odd n") | 1 false disproof |
| E8 | an instrument that cannot see what it is asked about returns a confident zero | nearly cost the whole closed-form vein |
| E9 | **a new sweep reading a block conjecture as a premise** | 774 false proofs, caught before a single paper was built. E2 again, in code written the same day the defect was written down. A line carrying no conjectural word is NOT a fact: an entry writes `Conjectures from X: (Start)' and then bare formula lines. Any sweep that looks for a premise must exclude everything `conjlines` returns, not merely lines with the word on them. |

## E10. A refusal I read wrongly, and the cost of that

`transfer35` refuses a name when `A ** (K * W) > 2,000,000`. I decided that figure described
nothing -- the rows are A^W, so surely the states were too -- and replaced it with a bound on
rows and row pairs. It is the states that are K-tuples of rows: `product(rows, repeat=K)`, so
there really are A^(K*W) of them. The "fix" let the build start and walk the whole product,
giving up only when `len(states) > cap` fired, minutes later instead of instantly. It is
reverted.

Reading a refusal is the habit that has found every large vein here. Reading it WRONG turns a
fast no into a slow one, and the difference is only visible if you check the claim against the
code that does the work rather than against the shape of the constant. Check what the states
actually are before deciding a bound is wrong.

## F0. What an engine DOES read and still is not proved -- the whole of it, 9 September 2026

1,127 entries outside the roster carry a readable conjecture AND a name an engine reads.
`deep-check/unproved-by-engine.json` lists them. Every one is blocked by a reason already
written down, and they account for each other almost exactly:

| how many | engine | why it is not proved |
| ---: | --- | --- |
| 144 | `ca2dcount` | refused on purpose: an active-cell count has no proved generating function, so no bound exists and the residual test cannot certify |
| 811 | mostly `transfer35`, `transfer9`, `transfer26`, `transfer23`, `transfer17` | `state space > cap` at 2,000,000, and re-asking runs the container out of memory before the build can refuse |
| 82 | `ca2d` | no growth certificate even at period 16, settling point 24, 64 steps |
| 71 | `ecarow` | genuinely fractal; the same widening finds nothing and neither does dropping the grow-by-2p rule |

**There is no hidden mass left in the reachable pool.** Everything an engine can read and has
not proved is one of those four, and three of the four are a hard wall rather than a setting.
The one that is not is the cap, and the way through it is lumping equivalent states BEFORE the
build rather than after: `permdisp` turned 31,187 states into 1,159 by lumping afterwards, and
`transfer17`'s pair-free construction already merges before the states exist. Doing that
generally is the single piece of work that would open 811 entries, and it is engine-by-engine
research rather than a setting to widen.

## G. `latpoly`: fixed length, growing alphabet, ARITHMETIC conditions (12 September 2026)

`ordpoly` reads fixed-length arrays over `0..n` whose condition is decided by the ORDER of the
terms. Its arithmetic twin was the 130 entries F1 recorded as "fixed length, alphabet growing,
but the conditions are arithmetic rather than order-only", and measuring it properly found far
more: **414 names in the clone, of which every one that has been checked reproduces the
entry's published data exactly.**

The argument. Every condition in the family is a boolean combination of statements
`sum c_i x_i + c n <> 0` --- the box `|x_i| <= n` or `0 <= x_i <= n`, a vanishing sum, a
difference that must not vanish, a pair totalling exactly `n`, a window sum bounded by `2n`.
Each is HOMOGENEOUS in `(x, n)` jointly, so the admissible `x` at a given `n` are the integer
points at height `n` of a finite union of relatively open rational cones in R^(L+1), and
`a(n)` is the Ehrhart quasi-polynomial of that union.

The period was what stopped this family before, and it is derived. Each ray of each cell is
cut out by `L` of the arrangement's hyperplanes; by Cramer its primitive generator's height
divides the determinant of their x-parts, and a ray leaving the box bounds no cell of the
region. With `T` the surviving heights,
`A(z) = prod_{d | some t in T} Phi_d^(L+1)` annihilates `a` and `S = deg A`. Two things make
this usable where the obvious version is not:

* the CYCLOTOMIC form, not `(z^P - 1)^(L+1)` with `P = lcm T`. Seven elements with no two
  neighbours equal: `P = 420` would ask for 3360 exact terms, the product of cyclotomics asks
  for 96.
* dropping the rays that leave the region. On the same family that is 420 down to 60 before
  the cyclotomic saving is even applied.

The numerator over `A` has degree below `S`, so `a(0..S-1)` determine every later term: no
threshold is fitted, and the derived annihilator is tested on terms the model was not asked
for before anything is claimed.

**The bound was one short, and the guard caught it.** The numerator over A has degree below
S for every cell of the arrangement that has a ray, because such a cell's numerator collects a
fundamental parallelepiped whose heights are below the sum of its generators' heights. The
origin is a cell too and it has no ray: its series is the constant 1, which over A is A/A and
has numerator degree exactly S. So a(0..S-1) do not determine the rest and a(0..S) do; the
bound in force is z*A. A189327 is where it showed -- the count is 3n on the even n and
(5n-1)/2 on the odd from n = 1, but a(0) = 1 rather than 0, because the all-zero arrangement
is admissible, and that single point is the whole difference. Nothing had been installed
under the smaller bound; every held result was re-asked under the corrected one.

**Where the 441 stand, measured after the install (13 September 2026).** 126 are installed as
`lattice-quasipolynomial`; 167 carry no parsable conjectured recurrence at all, so there is
nothing to settle on them; 4 are no longer open; and **144 are readable, open, carry a
conjecture, and are refused only by the compute limits** -- the derived `S` above the cap, or
the walk's layer above it. That 144 is the pool to attack next, and the attack is engineering
rather than mathematics: a sharper exponent (the cone's dimension rather than L+1, already
done, worth 10-15%), a faster inner loop, or eliminating a variable against an equality before
the walk starts.

What it does NOT reach, and why:

* 12 names whose condition is INHOMOGENEOUS -- "no element more than one greater than the
  previous", "adjacent elements differing by more than one". The region is then a shifted
  polyhedron; its counting function is quasi-polynomial only beyond some `n_0`, and there is
  no proof without a bound on `n_0`. **The way in is the two-parameter cone:** count
  `f(n, c) = #{|x_i| <= n, x_{i+1} - x_i <= c, ...}`, which IS homogeneous in `(x, n, c)`, and
  bound where the line `c = 1` leaves the last chamber of its parameter space. The walls are
  ratios of determinants and can be enumerated the same way the ray heights are.
* the entries whose `S` comes out above 260, or whose arrangement has more than 250,000
  `L`-subsets to test. Both are compute limits, not mathematical ones.
* "nondecreasing average value" (6) and "the sum ahead of each element differing from the sum
  following by n or less" (3): both are conditions on PREFIX sums, which the walk already
  carries as an accumulator but does not yet let a window predicate read.
* "each no smaller than the sum of its previous elements modulo (n+1)" (10). `a mod (n+1)` is
  piecewise linear in `(a, n)` with breakpoints at multiples of `n+1`, which ARE homogeneous
  hyperplanes, so this is reachable and simply not written yet.
* the fixed-shape two-dimensional families -- `3 X 3 0..n arrays` (5), `4X4X4 triangular 0..n
  arrays` (18). A fixed number of cells over a growing alphabet is exactly this engine's
  shape; only the name reader is missing.

## H. `ecacount`: ON and OFF cell counts of an elementary automaton (13 September 2026)

87 entries carry one of four names --- ON or OFF cells in the n-th iteration, or the running
total after n iterations, of a named elementary rule from a single ON cell --- and every one
of them carries a parsable conjectured recurrence. **No engine read any of them**, because
`ecarow` wanted the word "representation" on the line. The mathematics is already built:
`ecarow` derives `w(n+p) = L + w(n) + R` for the row and verifies it over every available
step, and counting the ON cells of that identity gives `on(n+p) = on(n) + ones(L) + ones(R)`.
The width is `2n+1`, so the OFF count is annihilated by one more factor of `(z-1)` and a
running total by one more again; `S = p + 4 + n0` covers all four wordings.

**5 proved.** That is all the end-insertion certificate reaches: of the 30 distinct rules in
the family, 3 have it and 27 do not.

**A null result worth recording.** The obvious generalisation --- growth by inserting a fixed
block at a fixed offset INSIDE the row, `w(n+p) = w(n)[:c] + M + w(n)[c:]` --- certifies
**none** of the 27. Their rows are not self-similar in that way at any period up to 16 or
settling point up to 27. The remaining 82 need a certificate at the level of the COUNT rather
than the row: the interior becoming exactly spatially periodic with the two boundary
transients eventually periodic in n, which makes the count quasi-linear without the row ever
repeating itself. That is the same obstacle as the 82 `ca2d` names with no growth certificate,
and one mechanism would settle both.

## J. `latpoly` with a CONSTANT in the condition (13 September 2026)

**The bound that was missing is computable.** A condition that is not homogeneous in `(x, n)`
was refused outright: the region is a shifted polyhedron and the count is a quasi-polynomial
only past some n_0. But the arrangement's shape in x-space changes exactly where L+1 of the
hyperplanes are concurrent, and solving each (L+1)-subset as a square system in `(x, n)` gives
the largest such n. Past it the combinatorial type is constant, the vertices are affine in n
with the same determinants, and the parametric-polytope theorem gives the quasi-polynomial;
the terms below raise the numerator's degree by n_0 and no more. The annihilator is
`z^(n_0+1) A(z)`, which for a homogeneous condition is the `z A(z)` already in use.

**The pool, measured on the whole clone.** 6,676 names of the fixed-length growing-alphabet
shape sit outside the roster; 6,124 are read by no engine; **245 of those are open and carry a
parsable conjectured recurrence**. Of the 245:

* **113 have a head `latpoly` already parses** and were refused only by the vocabulary. Three
  families are now read (22 names, 16 proved and installed). What is left there, by size:
  - 43 `no repeated value differing from the previous repeated value by ...` and its variants.
    A repeated value is a term equal to the one before it; for FIXED length over 0..n the
    condition is linear in the values once the pattern of repeats is fixed, so it is a finite
    union of cones and the same machinery applies — but the DP needs a state carrying the
    previous repeated value, which `latpoly`'s window DP does not have. `repval` has exactly
    that state and reads the MIRROR shape (`length-n 0..K`, growing length and fixed alphabet).
    Marrying the two is the single largest piece left in this vein.
  - ~15 `the sum of <statistic of adjacent pairs or triples> multiplied by some arrangement of
    +-1 equal to zero`. The sign-arrangement accumulator already exists; what is missing is the
    statistic (max, min, median of a window) as an accumulator input.
  - 7 `no adjacent pair x,x+1 repeated` / `followed at any distance by x+1,x`.
  - 6 `nondecreasing average value`, 3 `the sum ahead of each element ...` — prefix sums.
* **132 have a name shape nothing reads.** By size: 31 `N-bead necklaces labeled with ...`
  (the necklace engine's shape, different wording), 9 `4X4X4 / 3X3X3 triangular 0..n arrays`,
  8 `3 X 3 0..n arrays`, 7 `strictly increasing arrangements`, 6 `second differences of
  arrays`, 5 `arrays of median of ...`, and a tail of two-dimensional fixed shapes.

## M. `edgemark`: SETTLED — what "trailing edge maxima" means (13 September 2026)

    Number of binary arrays indicating the locations of trailing edge maxima of a random
      length-n 0..A array extended with zeros and convolved with 1,4,6,4,1.

Recorded here as null earlier the same day, on the grounds that no tie-breaking rule fit: the
engine reproduced every published term of A221992 (0..1) and was one too many for A221993
(0..2) at n = 10, 85 against 84, and a brute force agreed with the engine, so the reading was
what was wrong. Three tie-breaking rules, four marker windows, two paddings each side and the
reversed kernel all gave 85.

The hidden assumption was that the mark is a RADIUS-ONE test. It is not, and the refusal was
what said so: an exhaustive search over all 512 predicates on the sign pair
(sign(c(i)-c(i-1)), sign(c(i)-c(i+1))), at every contiguous window, fails on A222021 and
A222329 at n = 4. A plateau of the convolved sequence can be arbitrarily long — with kernel
1,1 the plateau condition is x(i-1) = x(i+1), so x = a,b,a,b,... is one plateau throughout.

    Position i is a trailing edge maximum when c(i) > c(i+1) and the nearest EARLIER
    position whose value differs from c(i) is lower.

That is the right-hand end of a plateau which is a strict local maximum, the all-zero left tail
counting as lower. One bit of state carries the unbounded lookback: whether the nearest earlier
different value was lower or higher. The engine is the last |K| input values plus that bit,
emitting one mark per step with a delay of one, determinised for images and lumped. 50 names,
every one reproducing its entry's data exactly and every one confirmed by an independent brute
force. The remaining eight names are two-parameter tables T(n,k) and are refused.

The lesson, which is defect 8 in another dress: an instrument that cannot see what it is asked
about returns a confident answer. A radius-one marker is a perfectly good instrument and it was
answering a question about plateaus that it could not see. What broke the deadlock was asking
which family of instruments COULD fit all the entries at once, and finding that none of them
could — the refusal, not the proof.

## L. THE POOL, measured on the whole clone (13 September 2026)

Every earlier measurement in this file was restricted to a name shape. Asked of everything —
outside the roster, open, carrying a parsable conjectured recurrence, read by no engine — the
answer is

    386,984 entries outside the roster
      3,500 with a parsable conjectured recurrence
      2,225 of those read by NO ENGINE          <- the pool

`deep-check/pool-unread.json` holds the list. By leading words:

     46  Number of n X 2 ...            41  Number of n X 3 ...
     34  Number of binary arrays indicating ...
     29  Number of -2..2 arrays x(i) ...    20  -3..3 ...    11  -1..1 ...
     22  Number of permutations of 1..n ...
     17  Number of n X 4 ...            12  Number of n X n ...
     15  Binary representation of the middle ...   9  Decimal representation of the middle ...
     12  Number of nondecreasing arrangements of ...
     12  a(n) is the number of ...      11  Numbers that are the sum ...
     10  Number of 2Xn 0..3 arrays ...  10  Number of length n arrays ...
     10  Number of nonnegative integer arrays ...
      9  Number of (n+1) X (n+1) ...     9  Sum of the products of ...
      9  Number of arrays of median ...  9  Number of second differences of ...
      ... and a long tail

**The n X k families are 198 entries** and are transfer-matrix shaped — growing height, fixed
width, fixed alphabet — so what stops them is the condition vocabulary, not the model. The
conditions, by size:

     19  rows and columns OF THE LATTER in lexicographically nondecreasing order
     15  rows and columns lexicographically nondecreasing (+ a tail: read backwards, every
         element equal to a neighbour, instance counts within one of each other)
     10  all 1s connected, all 2s connected, ... (connectivity: needs a union-find in the state)
      8  horizontal differences mod 3 never 1, vertical differences mod 3 never ...
      6  new values introduced in each row and column in sequential order
      5  every row and column running average nondecreasing rightwards and downwards
      5  every row and column nondecreasing rightwards and downwards, and ...
      4  each element moving exactly one horizontally or vertically
      3+ each of: no three 1's in a line, no 2x2 circuit 0101, no 1 with an adjacent 1 above
         and to its left, no 1 adjacent to a king-move-neighbouring 1, ...

The engine to build is a ROW TRANSFER WITH FLAGS: the state is (previous row, the lex-comparison
flag of each adjacent column pair, the bitmask of positions whose `equal to at least one
neighbour' obligation is still unmet). Rows lex-nondecreasing is a condition on consecutive
rows; columns lex-nondecreasing is carried by one flag per adjacent pair (equal so far, or
already strictly less — already greater rejects); an obligation that only a row BELOW can meet
is one bit per position. For k = 6 over 0..1 that is 64 x 32 x 64 states. The connectivity
conditions need a union-find of the frontier in the state — the standard broken-profile trick,
and 10 entries plus whatever else it opens.

## K. Two clusters analysed on 13 September: one tractable, one hard

### Necklaces and bracelets with a condition — 31 entries, TRACTABLE, not yet built

`necklace` reads `Number of k-bead necklaces labeled with numbers -n..n ... with sum zero.` and
nothing after it. 31 entries add a condition and are read by no engine:

    8   with no three beads in a row equal
    7   and first differences in -n..n
    7   and avoiding the patterns z z+1 z+2 and z z-1 z-2
    6   and first and second differences in -n..n
    3   and avoiding the pattern z z+1 z+2

Burnside still applies. A labelling fixed by a group element g is constant on each orbit of g,
so for a rotation by d with c = gcd(k, d) the fixed labellings are exactly the c-periodic words,
and the condition on the k-periodic extension is a condition on the length-c cyclic word. The
fixed-point count is then: length-c cyclic words over -n..n with sum zero (the whole sum is
(k/c) times the sum of the c values) and a cyclic window condition. Averaging over G gives the
necklace count exactly.

**What is missing is one feature: CYCLIC windows in `latpoly`.** Its DP already counts
zero-sum -n..n arrays of 7 elements under window conditions (A202257, S = 127); the cyclic
version fixes the wrap-around window and runs the same DP with the closing windows required to
match. Everything else is already proved machinery: the region is still a union of relatively
open rational cones, so each fixed-point count is a quasi-polynomial, and a Burnside average of
quasi-polynomials is one, with the period the lcm over the group elements and the degree at
most k - 1. For a prime bead count only c = 1 and c = k occur, so the identity is the only hard
term; reflections give c about k/2.

### The +-1 arrangement sums — 21 entries, analysed and HARD

    3  the sum of adjacent differences multiplied by some arrangement of +-1 equal to zero
    3  the sum of the maximum of each adjacent pair ... (and 3 for the minimum)
    3  the sum of medians of adjacent triples ... (and 3 each for max-median, max-min)
    2  the sum of the maximum minus twice the median plus the minimum of adjacent triples
    1  the sum of second differences ...   (+1 for cubes, +1 for squares: not piecewise linear)

The condition is `there EXIST signs e_i in {+-1} with sum e_i X_i = 0`, i.e. the multiset of
window statistics splits into two parts of equal sum. For a linear statistic that is a
disjunction of 2^(m-1) linear equations and would fit `latpoly`'s clause vocabulary at once --
except that each equation is GLOBAL, spanning the whole array, so the window DP degenerates to
brute force (2n+1)^L. The obvious repairs all fail:

* an accumulator carrying the partial sum counts (array, sign vector) PAIRS, over-counting
  every array that several sign vectors satisfy;
* an accumulator carrying the SET of achievable partial sums has a state space of frozensets
  drawn from a range that grows with n, so it is not bounded independently of n;
* inclusion-exclusion over the 2^(m-1) hyperplanes is 2^(2^(m-1)) terms.

Max, min and median are piecewise linear, so those add a factor of (orderings)^m on top and do
not change the difficulty; cubes and squares are not piecewise linear at all and are refused
outright. **Recorded as hard, not as unread.** The way in, if there is one, is a bound on the
number of distinct achievable-sum SETS rather than on their contents.

## I. The block template, and the two-dimensional certificate it does NOT give (13 Sep 2026)

**Done and installed.** `ecashape` finds, for a one-dimensional automaton,

    w(n0 + r + j*p) = B_0 . Q_1^j . B_1 . ... . Q_m^j . B_m,

fixed blocks and repeated blocks, the repeats gaining one copy every p steps. It generalises
the end-growth shape `ecarow`/`ecacount` use (that is m = 2 with the outer blocks empty) and
brings in 17 of the 56 rules those refuse — rule 133 gains `1010' in the middle of a periodic
run, rule 141 gains `10' in one run and `11' in another. It is PROVED by locality: p steps of a
radius-1 map have radius p, so verifying the p-step map by simulation at two consecutive j
whose runs exceed the dependence cone carries it to every larger j. `ecablock` (counts, 17
installed) and `ecarowb` (numerals, 15 installed) are the engines.

**The remaining 39 elementary rules are empty at the entry level.** 98 entries sit on them and
not one carries a parsable conjectured recurrence. Nothing to go back for.

**The open problem is two-dimensional.** `ca2d`'s certificate is not provable by locality: the
axis of a 2-D automaton is not a function of the axis before it, so 179 papers were withdrawn
(see WITHDRAWN.md). 21 rules survive because their whole CONFIGURATION is exactly periodic in
time, which determinism alone settles. Three rescues were measured and failed: the
configuration as a fixed frame around the previous one (0 of 39 rules), the interior frozen
with growth only in the new boundary ring (0 of 26), a cross insertion of 2p rows and 2p
columns (2 of 39).

What is left to try, and would recover the 179 plus the 82 `ca2d` names never certified:

* **a 2-D block template with product structure** — C(n+p) is C(n) with fixed row-bands and
  column-bands inserted at fixed positions, the bands themselves repeats. Then 2-D locality
  closes the induction exactly as it does in one dimension. The cross test is the special case
  of a single band each, so the general case is what is untried. The search is the 1-D
  `_templates` run twice, once on the column structure of the centre row and once on the
  sequence of rows with those columns deleted.
* **a band certificate with a growing height.** To get the axis at n+p one needs the band
  |y| <= p at n, and to get THAT band at n one needs |y| <= 2p at n-p. A band identity whose
  verified height grows faster than p per step would close it; measure how the height at which
  the row-wise identity holds grows with n. Rules 3, 73 and 413 already satisfy the row-wise
  identity at every height, which is why they are among the 21 already proved.
* **spatial periodicity of the interior.** Rule 14's bulk is an exact checkerboard with
  bounded transients at the corners and edges. That is the 2-D form of the mechanism section H
  wanted for the counts, and it would settle the axis, the diagonal and the active-cell count
  at once.

**Two of the three were tried on 13 September and are NULL.** The product block template --
C(n+p) is C(n) with whole rows inserted at fixed places and whole columns at fixed places, the
column set taken from the axis certificate, which already says the axis grows at its ends --
holds for **0 of the 51** rules. A bounded periodic interior is worse than null: for rule 14 at
q = (2,2) the width of the region disagreeing with the checkerboard is 0, 1, 5, 7 at stages 16,
18, 22, 24, growing with n rather than staying bounded. The departures sit at a fixed FRACTION
of the radius, which is what a self-similar growth looks like and is exactly why no finite
certificate of this shape exists. The band certificate with a growing height is the one still
untried, and the measurement it needs is how the height at which the row-wise identity holds
grows with n.

Until one of those lands, `ca2d` refuses anything without the temporal-periodicity certificate
and `ca2dcount` refuses everything, which is what they should do.

## F1. What no engine reads, measured fresh on 9 September 2026

2,791 entries outside the roster carry a readable conjectured recurrence and a name no engine
reads. Measured against the clone, not against a cached list -- the earlier census predates
`window`, `repval` and `ordpoly` and is stale by construction.

| how many | family | why it is not read |
| ---: | --- | --- |
| 379 | coordination sequences `Gal.u.t.v` | the name does not give the tiling; the Galebach data would have to be read |
| 199 | two-dimensional arrays growing in BOTH directions (`n X n`, `(n+1) X (n+1)`, `n X 4`) | a transfer matrix along one side has a state space that grows with the other |
| 130 | `-n..n arrays x(i) of n+2 elements ...` | fixed length, alphabet growing, but the conditions are arithmetic rather than order-only |
| 0 | `the diagonal from the corner to the origin` of a two-dimensional automaton | **all 39 proved.** Leading zeros are stripped after the row is laid out and the zeros sit at the CORNER end, so reversing the finished word strips the wrong end. Reading the cells in corner-to-origin order and stripping then matches every published term of all 39 |
| 105 | ON/OFF cell counts of two-dimensional automata | no proved generating function; see `refused.py` |
| 38 | necklaces and bracelets over `-n..n` | **the seven plain sum-zero ones are proved** (`necklace.py`); the other 31 carry pattern conditions naming an actual difference, which Burnside does not reach |
| 39 | `n X n` binary arrays | same as the two-dimensional case |
| 34 | arrays of permutations | a walk on W! vertices is only feasible for small W |
| 20 | self-avoiding walks | no finite-state model |
| 18 | `the sum of ... multiplied by some arrangement of +-1 equal to zero` | whether zero is reachable depends on a set of partial sums that grows with n |
| ~1,800 | a long tail of one-off phrasings | each would need its own reading |

The reachable part of this database has largely been taken. What is left is dominated by
families that are hard for a reason, not by families nobody has read.

## F. Not yet attempted at all

* C4 inequalities, C5 primality, C6 always/never, C7 algebraic g.f.s, C8 e.g.f.s
* B6–B10 engines
* D5, D6
* 3,206 English-only conjectures on proved entries — mostly open research problems
  (Cramér's conjecture among them), not settleable here, and named so they are not mistaken
  for a gap

## N. Walks of a FIXED number of steps on a growing board (13 September 2026)

    Number of 7-step self-avoiding walks on an n X n square summed over all starting positions.
    Number of 3-step one space at a time bishop's tours on an n X n board summed over all
      starting positions.
    Number of 9-step self-avoiding walks on an n X n X n cube summed over all starting
      positions.

**78 in the pool, 156 in the clone.** The number of STEPS is fixed and the BOARD grows, which
is the whole point: the set of walk shapes is finite and does not depend on n at all. Fix the
move set M (four unit steps for a self-avoiding walk, four diagonals for a bishop, eight for a
king, king ∪ knight for a king-knight, and for the "asymmetric" pieces one space leftwards or
up against two spaces rightwards or down, which is why the name adds that its antidiagonal
moves become knight moves). Enumerate every self-avoiding walk of k steps in M up to
translation and take each one's bounding box (w_1,...,w_d). A shape with bounding box w fits an
n X ... X n board in exactly prod_i max(0, n - w_i) positions, so

    a(n) = sum over shapes of prod_i max(0, n - w_i),

which for n > max_i w_i is a POLYNOMIAL of degree d in n. The annihilator is (z-1)^(d+1) and
the threshold is the largest bounding-box side over all shapes — both derived, not assumed, and
the formula also gives the small terms exactly, so the entry's own published data checks it.

Not a transfer matrix and not a walk in a digraph: qpbuild's shape, with the model section
stating the shape count and the bounding-box argument.

Refused, and separately: the seven "k-TURN" entries (bishop's and queen's tours counted by
turns rather than steps) have straight segments of unbounded length, so the shape set is not
finite and this argument does not apply. They need their own reading.

## O. The coordination sequences — the largest single cluster, and what it needs

**378 entries in the pool**, all of the form "Coordination sequence Gal.u.t.v ... in the
Galebach list of u-uniform tilings", each carrying a conjectured recurrence and g.f. of Chai
Wah Wu's from November 2025. Fifty published terms each, no program, no adjacency data on the
entry. The route is real but not short: a coordination sequence of a periodic planar graph is
eventually quasi-polynomial, and an effective proof needs the tiling's own combinatorics (the
trunk-and-branch argument of Goodman-Strauss and Sloane, or an Ehrhart count on a distance
polytope). Nothing here can start until the Galebach tilings are reconstructed as graphs. Noted
because it is by far the largest cluster left and because its size should not be mistaken for
its difficulty in either direction.

## P. What a claim that is NOT a recurrence looks like, and how much of it there is

The circular-digit family taught this and it is the most transferable thing found on
13 September. 229 entries, and only 10 of them carry a conjectured recurrence: every sweep in
this project reported the other 219 as "no parsable recurrence" and moved on. What they carry is

    [Empirical] a(base,n) = a(base-1,n) + F(5) for base >= 5*int(n/2)+1

— a claim relating one entry to ANOTHER entry, in a parameter that is not n. `ratrec` cannot
parse it because it is not a recurrence; nothing else looked. It took four lines to prove.

So the question worth asking of the whole clone is: **how many entries carry a conjecture that
no sweep here can even read as a claim?** Not "carry no conjecture" — carry one of a shape no
parser has. Kinds seen so far in passing, none of them swept:

  * cross-parameter identities: a(k,n) = a(k-1,n) + <something>(n), a(n) = T(n,k) of a table
  * claims about a DIFFERENT sequence: "a(n) is the number of ... in A012345"
  * asymptotics and limits: "a(n) ~ c * r^n", "lim a(n)/a(n-1) = ..."
  * divisibility and congruence claims that name no modulus pattern
  * claims about the positions of terms: "a(n) is prime only for n = ...", "a(n) = 0 iff ..."
  * claims stated as a program or a construction rather than a formula

The measurement to make: for every entry outside the roster, take `conjlines.lines(e)`, ask
`ratrec` and the g.f. parser, and BUCKET WHAT IS LEFT by shape. The 219 above were one bucket
and they were invisible for the whole life of the project.

## Q. Two clusters measured and left, 13 September evening

* **"all 2 X 2 subblocks having the same four values"**, 15 usable entries (plus 2 tables).
  The structure is rigid and worth writing down before coding: for consecutive 2 X 2 blocks in a
  row-pair the shared column forces the column MULTISETS m_j to satisfy m_j + m_{j+1} = V for
  the common four-value multiset V, so they alternate between m and V - m. Given V, an
  alternation pattern and the top row, the bottom row is DETERMINED cell by cell. That makes the
  row digraph tiny and the enumeration trivial; the divisor in the name is (alphabet size)^2.

* **the k-TURN tours**, 7 entries plus tables. `boardwalk` does not apply: a tour with k turns
  has straight segments of unbounded length, so the shape set is infinite. The right model is a
  lattice-point count -- choose the alternating direction sequence, then the segment lengths
  live in a polytope depending on n -- which is `latpoly`'s shape, with self-avoidance handled
  by inclusion-exclusion over crossing patterns. Not attempted.

## R. The knight-distance family: the reading is PINNED, the model is not built (14 September)

    Number of (n+2)X(1+2) nonnegative integer arrays with all values the knight distance from
    the upper left minus as much as 2, with successive minimum path knight move differences
    either 0 or +1, and any unreachable value zero.

18 entries in the pool. The wording is the obstacle and it is now settled, by brute force
against the entries' own first terms:

  * value(x) = kd(x) - t(x) with t(x) in 0..D-1, where D is one more than the "as much as"
    number: "minus as much as 2" gives THREE options, and the value must stay NONNEGATIVE.
    Read with two options, or without the nonnegativity, a 3 X 3 board gives 17, 18 or 71
    where A253112 gives 53; read this way it gives 53, and 272 and 1342 after it. The
    "as much as 3" family gives 69, 488, 1928, its entry's own terms.
  * "successive minimum path knight move differences" are exactly the pairs (p, x) with p a
    knight neighbour of x and kd(p) = kd(x) - 1, and the condition is value(x) - value(p) in
    {0, 1}. In terms of t that is t(x) in {t(p), t(p)+1} -- because kd(x) = kd(p) + 1, the
    kd cancels and the condition becomes local in t alone.
  * unreachable cells are fixed at 0 and lie on no minimum path, so they carry no freedom.

Two facts the model can rest on, both measured:

  * the knight-distance field on an R X C board does NOT depend on R: for C = 3..8 and every
    R from 6 to 40 the field agrees with the field one row taller, everywhere. So the field is
    the infinite strip's and can be computed once.
  * the field's row signature -- the within-row profile together with which knight moves are
    minimum-path predecessors -- is periodic in r with period 4 for every width C = 3..8, kd
    increasing by 2 per period. That is exactly the "n mod 4" in the entries' own empirical
    quasi-polynomials.

What stops it: a minimum-path edge spans at most two rows, so a transfer matrix needs the last
TWO rows in its state, and that is D^(2C) -- 729 at C = 3, but 43 million at C = 8. The family
runs C = 3..8 for each of D = 3 and D = 4, so a straightforward build reaches perhaps six of the
eighteen. Worth doing only with a state reduction: t is nondecreasing along every minimum path
and rises by at most one per step, which ought to collapse the row pairs a long way.

## S. Engines that refused themselves — re-read every one

`transfer88` sat finished and unregistered for weeks because its model rested on a measured
period, and its docstring said exactly which claim was missing. `kdcert` supplied it in an
afternoon and the family paid twenty-one entries. That is a pattern, not an incident: an
engine that refuses itself has already done the expensive half of the work.

The sweep to run is over the engine sources themselves, not over OEIS:

    grep -ln "NOT IN SERVICE\|unregistered\|not proved here\|evidence, not a proof" src/*.py

and for each hit, read what it says is missing and ask whether the two standard devices settle
it. Both are cheap and both apply widely:

  * **Bellman / optimality certificate.** Any function satisfying the relaxation inequality
    and the tightness witness IS the distance (or the value function, or the shortest
    accepting length), whatever its provenance. That turns a guessed table into a proved one.
  * **Local periodicity.** When the conditions at one index read only a bounded window around
    it, a period in the window data makes finitely many indices settle every index. This is
    what makes a "checked over 400 rows" claim into a theorem rather than evidence.

The two together handle any claim of the form "this eventually periodic structure really is
eventually periodic", which is the commonest reason a geometric engine gets shelved.

Also worth asking of every shelved engine: is its REFUSAL RANGE a theorem or a measurement?
`transfer88` refused widths 8 and above on the strength of a table that stopped at 7. The
certificate covers every width up to 14 (i0 = 2C - 3), and three of the twenty-one entries are
in exactly that range. A refusal written from a measurement expires when the measurement does.

## T. What the pool actually is — measured, not guessed (14 September)

The pool, rebuilt as (uni_cands ∪ pool-unread) − roster, filtered to entries with a parsable
conjecture that openness still calls open, is **2,219**. Two measurements on it, and together
they say where the next engines belong.

**By NAME SHAPE** (digits to #, single letters to V), 1,073 distinct shapes. The head:

     378  Coordination sequence Gal.#.#.#                       (section O, needs the tilings)
      43  every 2 X 2 subblock, diagonal sum minus antidiagonal sum = # (constant-stress)
      42  each # X # subblock idempotent
      73  every # X # subblock commuting with each neighbour # X # subblock (5 phrasings)
      64  every # X # subblock row/column/diagonal sum in or not in a given set (6 phrasings)
      19  each element x = the number of its neighbours equal to a given list

**By REASON FOR REFUSAL**, on a random sample of 160 (122 classified before the run was
stopped on a slow build):

      no engine reads the name     82   67%
      state space > cap            39   32%
      annihilation timed out        1
      PROVED                        0
      model does not match DATA     0

Two things follow, and the second is the surprise.

**The pool is not one problem, it is two.** Two thirds is the long tail of 1,073 shapes, most
of them singletons — that is parser work, one name at a time, and the return per hour is low.
One third is refused at the CAP, and that is engine work with a much better return.

**The big clusters are NOT in the unread two thirds.** Every name checked by hand from the six
head clusters above — A234225, A224599, A186562, A186601, A252310, A196074 — is already read,
by transfer3, transfer23, transfer35, transfer35, transfer17 and transfer19 respectively. They
are in the pool because the BUILD refuses them, not the parser. So the head of the pool and the
cap refusals are the same entries, and the ~240 entries in those six clusters are reachable by
machinery that exists, exactly as the standing habit predicts.

**Where to aim.** `transfer88` refused A253117 at the cap for a reason that turned out to be a
construction nobody had looked at twice — it carried the row index in the vertex for rows above
the periodic region, and summing those rows into a weighted start vector took width 7 from
11,458 states to 3,421 and width 8 from refused to reachable (STATE.md defect 19). The question
to put to transfer3, transfer17, transfer23 and transfer35 is the same one: **what is in the
state that does not need to be there?** Candidates to check, in order of how many entries hang
on them:

  * a boundary row carried in full when only its behaviour under the condition matters;
  * an initial segment carried as distinct states per index instead of as weights;
  * vertices distinguished by data the condition cannot see — lump BEFORE building, not after,
    since the cap is hit during exploration and `lumpauto` runs too late to help.

The last is the most likely and the most general: every one of these engines builds the whole
reachable set and only then merges. `transfer88` at width 7 built 20,384 states and merged to
3,421, so more than four fifths of the exploration was redundant. An engine that merges on the
fly — a partition refinement over the frontier rather than over the finished graph — would move
the cap by roughly that factor, and that is one change reaching four engines and ~240 entries.

## U. The coordination sequences are unblocked: the tilings are rebuilt (14 September)

378 pool entries are coordination sequences of Brian Galebach's k-uniform tilings — the single
biggest cluster in the pool, and nothing had been attempted because the tilings were missing.
They are not missing. The OEIS auxiliary file `a250120.html` (the local oeisdata mirror keeps
it only as a git-LFS pointer; fetch it from oeis.org) carries all 1,248 tilings in an expanded
notation that determines each one completely:

    Gal.1.1.1: A: 6^3 ; A 60; A 60; A 60

— vertex type A sits in a 6.6.6 corner, and along each of its three edges in cyclic order one
reaches a type-A vertex whose frame is rotated 60 degrees. A primed angle means the neighbour's
frame is also reflected.

`src/galtile.py` turns that into a graph with no geometry input:

  * the configuration fixes the angles BETWEEN a vertex's edges — between edge j and edge j+1
    sits a regular q-gon contributing 180 - 360/q — so the edge directions in a vertex's own
    frame are the partial sums;
  * the notation fixes each neighbour's frame, so its own directions are known once placed;
  * edges are unit length, so a position is a sum of unit vectors.

Only multiples of 15 degrees occur, so every position is a Z-combination of 24th roots of
unity, and working in Z[zeta_24] = Z^8 modulo x^8 - x^4 + 1 makes vertex identity **exact**.
That is not fastidiousness: a coordination sequence counts vertices at a distance, and a
floating-point near-miss would merge or split vertices and produce a plausible wrong answer.

**Validated: 6,536 of the 6,536 sequences the file itself lists are reproduced exactly, 0
mismatches, 0 errors, 71 seconds.** The parsed tilings are stored in `engine/galebach.json`.

### What remains, and it is the whole proof

Computing terms is not proving the conjecture. Each of the 378 entries carries a linear
recurrence conjectured by Chai Wah Wu (Dec 2018) and a g.f. whose denominator is of the shape
(x-1)^2 (x^2+1)^2 ..., i.e. quasi-linear growth. The chain to a proof:

1. **Certify the distance field — and NOT the way this section first said.** The first
   version of this plan said: claim d(v + lambda) = d(v) + c(lambda) outside a bounded region
   and verify it with `kdcert`'s Bellman conditions. **That claim is false**, and it was worth
   ten minutes to find out rather than a turn. Measured on the reconstructed graphs, the
   difference d(v + lambda) - d(v) takes many values, not one:

       Gal.1.1 (honeycomb)   -2, 0, +2
       Gal.1.2 (4.8.8)       -3, -1, +1, +3
       Gal.4.31              seventeen distinct values from -9 to +9

   Of course it does. The knight strip had ONE unbounded direction, so a single translation
   claim closed the induction. A tiling is unbounded in two, d is asymptotically a polyhedral
   NORM, and the difference along a fixed lambda depends on which direction v lies in — it is
   +|lambda| out one side and -|lambda| out the other. `kdcert` is the right IDEA and the
   wrong CLAIM.

   The true structure is piecewise affine: finitely many cones, and on each cone d is an
   affine function of the lattice coordinates plus a periodic correction per vertex class.
   The certificate is then the same two Bellman conditions checked REGION BY REGION — for
   each cone and each edge type, d(w) <= d(v) + 1 and the witness condition become affine
   inequalities in the lattice coordinates, each decided once for the whole cone. That is
   finite and rigorous, and the work is in fitting the cones, which is the limit shape of the
   graph metric.

   Be aware of what this is: "coordination sequences of crystals are of quasi-polynomial
   type" is a 2021 research theorem (Nakamura, Sakamoto, Mase, Nakagawa), not a lemma. The
   route above is an independent finite certificate for each individual tiling, which is a
   much easier thing than the general theorem — but it is still the largest single piece of
   mathematics this project has attempted, and it should be started with that expectation
   rather than as an afternoon's port of `kdcert`.

2. **Count.** With d certified lattice-linear outside a finite region, {v : d(v) = n} is for
   large n a lattice-point count in a dilating rational polygon, so a(n) is an Ehrhart
   quasi-polynomial of degree 1 with a computable period. `latpoly` already does Ehrhart
   counting with a DERIVED period bound — and STATE.md defect 11 is precisely the warning
   about getting that bound wrong, so reuse its machinery rather than re-deriving.
3. **Compare** the resulting exact annihilator with the conjectured recurrence, as every other
   engine does.

Step 1 is the interesting one and is where to start.

**Step 2 is simpler than feared, and the shape is now pinned.** The counts are eventually
QUASI-LINEAR with a period: measured over 201 terms,

    A310007  Gal.4.31.1   a(n+2p) - 2a(n+p) + a(n) = 0 for n >= 3   with p = 8
    A310025  Gal.4.31.2   the same, p = 8, from n = 3
    A310018  Gal.4.34.1   the same, p = 42, from n = 11

and A310018's conjectured recurrence is a(n) = a(n-6) + a(n-7) - a(n-13), whose characteristic
polynomial is exactly (z^6 - 1)(z^7 - 1) — period lcm(6,7) = 42. The two agree. So the
annihilator to derive is (z^p - 1)^2, no Ehrhart machinery is needed, and the whole problem
reduces to producing p and n0 FROM THE CERTIFICATE rather than from a scan.

**Those (p, n0) above are MEASURED, not proved — that is precisely the `transfer88` situation
and must not be shipped as it stands.** What makes them theorems is step 1: certify
d(v + lambda) = d(v) + c(lambda) outside a bounded region by the Bellman conditions, and p
and n0 fall out of the lattice and the region. Until that is written, this vein has a
validated graph and a pinned shape and zero results, which is exactly where `transfer88`
sat for weeks.

Also worth recording: **6,070 OEIS entries** name a Galebach vertex, not 378. The 378 is what
is in the pool — the rest are already in the roster or carry no parsable conjecture. If the
certificate works, the reachable set is much larger than the cluster that pointed at it.

### U.1 What the distance function actually looks like (measured, 14 September)

`src/gallat.py` finds the translation lattice and splits a tiling into translation classes.
Two things had to be right and one of them cost a false start:

  * a translation is a symmetry when it carries every vertex to one with the same type AND the
    same SET OF EDGE DIRECTIONS. Comparing the raw frame finds **zero** translations, because
    the frame carried by `galtile` is finer than the tiling's own symmetry: a vertex figure
    with a rotational symmetry (6^3 under 120 degrees) has several frames describing the same
    vertex;
  * lattice coordinates are solved exactly over Z^8 and then verified in every coordinate, so
    an accidental agreement in one 2x2 minor cannot pass.

    Gal.1.1 (honeycomb)  2 classes      Gal.1.11 (triangular)  1 class
    Gal.1.2 (4.8.8)      4 classes      Gal.4.31  30 classes     Gal.4.34  25 classes

With d written in lattice coordinates per class, its structure is:

    d(m, n) = max_i ( alpha_i * m + beta_i * n + gamma_i )

— a polyhedral norm, finitely many cones. **For the 1-uniform tilings this is EXACT, with no
exceptional region at all**: Gal.1.1 and Gal.1.11 need 6 cones, Gal.1.2 needs 10, and the
formula reproduces d at every one of the 1,786 / 2,107 / 1,588 interior points including the
origin.

For the k-uniform tilings it is exact except at a handful of points:

    Gal.4.31   28 of 5,839 interior points     Gal.6.110   52 of 5,301
    Gal.4.34  438 of 7,346

and **every miss is in the same direction**: the fitted max is 1 too small (a few are 2), never
too large. So the cones found are genuine and the fit is missing thin ones — cones occupying so
few lattice points that a scan over gradients does not see them. Refining the classes by a
sublattice makes it worse (each piece loses the points the fit needs), and lowering the
gradient-count threshold barely helps, so the scan is the wrong instrument.

**The right instrument is a lower convex hull.** If d is convex in (m, n) then the facets of
the epigraph's lower hull ARE the affine pieces, all of them, thin ones included — a 3-D convex
hull on the points (m, n, d) per class, which is exact integer arithmetic and needs no
threshold. That is the next thing to write. Whether d is exactly convex is the question it will
answer: if some point lies strictly above the hull, the deviation is bounded and becomes the
exceptional region the certificate carries explicitly, exactly as `kdcert` carries heights
below H0.

Then the certificate is: for each ordered pair of classes joined by an edge, and each pair of
cones, `d(w) <= d(v) + 1` and the witness condition are affine inequalities in (m, n), each
decided once for the whole cone pair. Finite, exact, and the periods p and n0 fall out of the
cone geometry rather than out of a scan over terms.

### U.2 The vein is sized: 723 of 1,248 tilings are provable by a standard theorem

`src/galhull.py` fits d per translation class as max_i(A_i*m + B_i*n + C_i), exactly. The
gradient scan alone misses thin cones — always underestimating, never over — so the missing
supports are ADDED by a cubic search run only through the points the scan cannot reach, which
is a few dozen out of thousands. All Fraction and integer arithmetic, no tolerance anywhere.

**Where the fit is exact, the conjecture follows from Ehrhart's theorem and nothing more.**
The ball {v : d(v) <= n} meets each translation class in the lattice points of a rational
polygon dilated by n; Ehrhart gives that count as a quasi-polynomial of degree 2 in n with
period the lcm of the denominators; and a(n) = |B(n)| - |B(n-1)| is then quasi-linear, whose
annihilator is (z^p - 1)^2 — exactly the shape the conjectured recurrences have. No new
mathematics is needed on that half at all.

Scanned over every tiling (interior radius 28, all 1,248):

    exact max-of-affine   723
    not exact             525
    no lattice found        0
    errors                  0

The 723 are listed in `engine/gal_exact.json`. **That is the reachable set today**, and it is
most of the way to the 378 pool entries — how many of those 378 sit on exact tilings is the
first thing to measure next, and it is one join.

The other 525 are not a failure and should not be forced. Their d exceeds the hull by exactly
1 on a sparse set that RECURS with a period — Gal.4.31 at graph distances 9, 10, 17, 18, 25, 26
(period 8, which is its coordination sequence's own period), Gal.6.110 every 4. Refining the
translation lattice to index 4 barely moves it (12 leftovers to 8), so it is not a residue
effect: d is genuinely not convex on those tilings, and the certificate for them needs the
correction carried explicitly rather than fitted away. Do the 723 first.

### U.3 The order of work

1. Join `gal_exact.json` against the 378 pool entries. That number is the size of the batch.
2. Ehrhart on the polygons: for each class, the cones give the polygon's facets; the count of
   lattice points in the n-fold dilate is the quasi-polynomial. `latpoly` already does Ehrhart
   counting with a DERIVED period bound, and STATE.md defect 11 is the warning about getting
   that bound wrong — reuse it rather than re-deriving.
3. a(n) = |B(n)| - |B(n-1)|, compare its annihilator with the conjectured recurrence, and
   install by the ordinary chain.
4. Test the whole path against the 6,536 published coordination sequences before installing
   anything: the terms are already known to match, so any disagreement is in the Ehrhart step.

### U.4 The proof pipeline is built and verified (14 September)

    galtile  ->  gallat        ->  galhull            ->  galehr
    graph        lattice,          d = max-of-affine      lattice-point count,
                 classes           per class              derived period and onset

`galehr` closes the argument where the hull is exact. The ball of radius t meets a class in the
lattice points of {A_i*m + B_i*n + C_i <= t}; every candidate vertex is the meet of two facets
and moves AFFINELY in t, so each vertex's relation to each facet flips at most once, at a single
rational t. Past the largest of those the shape stops changing — that is `onset`, derived, not
scanned. The period divides the lcm of the 2x2 determinants of facet-normal pairs — those are
the only denominators a vertex can have — and `fit` then tries the DIVISORS of that bound in
order and keeps the smallest that reproduces the counts, so the period is checked rather than
assumed. a(n) = |B(n)| - |B(n-1)| is then an explicit quasi-linear function.

Verified end to end against breadth-first search:

    Gal.1.1  q=2   T=2   6 planes/class     Gal.1.5   q=1  T=1
    Gal.1.2  q=12  T=5   9 planes/class     Gal.1.11  q=1  T=1
    Gal.1.3  q=30  T=29  15-18 planes/class

all agreeing on every term computed.

One boundary artifact was found and is worth keeping in mind for anything fitted on a ball: the
patch rim is not a feature of the tiling, and class points there made a spurious plane look
tight. On Gal.1.2 its constant marched with the patch radius — -11, -21, -31 at radii 30, 50,
70 — which is how it was caught, and it inflated the onset from 4 to R-7. `galhull.prune` drops
supports that are never tight well inside. **A quantity that moves with the size of the patch
is a property of the patch.**

### U.4a THE FIT WAS CIRCULAR — read this before trusting U.2 or U.4

`galhull` fits d on a patch and checks it on that same patch. **That is circular.** A cone
whose region lies entirely outside the patch cannot appear as a leftover, so the fit reports
itself exact and is not. On A310102 (Gal.4.16.1) the fitted form agrees with breadth-first
search for 29 terms and diverges at the 30th — one step past the radius it was fitted on.

The Ehrhart half is not at fault and that was checked: the closed form and a direct lattice
count of the fitted region agree with each other at every radius. It is the REGION that is
wrong.

So the "723 of 1,248 exact" figure in U.2 is **not** a count of tilings whose distance function
is max-of-affine. It is a count of tilings where a patch-sized fit did not contradict itself,
which is a much weaker thing and very likely an overcount. `src/galcoord.py` is written and
IS NOT IN SERVICE — `build` returns None for everything — because a pipeline that is right on
29 terms and wrong on the 30th is exactly what this project exists not to ship.

### U.4b The certificate has a gap too — A310511

`src/galcert.py` checks the two Bellman conditions over the whole lattice: exhaustively inside
a breakpoint radius computed from the planes, and at three points per cone outside it. It
passes every test it was given — accepts the honeycomb, 4.8.8 and the triangular tiling,
refuses Gal.4.16 (the 29-terms-then-wrong one), and refuses any tiling whose plane constants
are perturbed by one in either direction.

**It is still not sound.** A310511 is accepted and its fitted form diverges from breadth-first
search at the 35th term. Two gaps, both in the "outside the breakpoint radius" half:

  * `_cone_points` locates a cone by walking out along its plane's gradient, and when the
    heuristic fails it returns None and the cone is SKIPPED. A check that silently skips what
    it cannot find is not a check — this is defect 8 wearing a new hat;
  * three affinely independent points settle an affine statement on a cone, but condition (c)
    is "SOME edge attains equality" and the attaining edge may vary from point to point. Three
    points do not settle a disjunction.

The fix is to stop sampling and compute the arrangement, which in two dimensions is cheap:
sort the planes by gradient angle; the region where plane i is the maximum is bounded by the
rays where it ties with its neighbours in that order. Given a cone as an apex plus two
generator directions, "affine <= affine on the cone" is exact — the difference at the apex and
its linear part on each generator — and condition (c) is decided per cone by intersecting with
each edge's equality region. Nothing sampled, nothing skipped.

One thing that IS settled and should not be redone: **counting is exact.** `galehr.count`
agrees with brute-force enumeration of the region at every radius tried, and `galcoord.ball`
now uses it always. An earlier version used the Ehrhart closed form wherever the derived onset
said it applied, which was wrong on entries the certificate accepted — `galehr.onset` can come
out too small, the quasi-polynomial then gets fitted inside the transient, and its own
verification passes because the transient is locally smooth (A310393 drifted from t = 12). The
closed form's only remaining job is to supply the period for the threshold.

### U.5 What is left

The plumbing is written; what is missing is the mathematics, and it is the part that was
deferred twice. **Verify the closed form over the whole lattice, not over a patch.** For the
fitted D, with the tiling's edges expressed as (class c, class c', lattice offset (dm, dn)):

    (b)  D_{c'}(m + dm, n + dn) <= D_c(m, n) + 1        for every edge and every (m, n)
    (c)  every class and every (m, n) other than the origin has an edge attaining equality

Both sides are convex piecewise-linear, so each condition splits into finitely many tests of
the form "affine <= affine on a polyhedral cone", each an exact rational LP over two variables.
Finite, decidable, and the whole content of the proof. When a tiling passes, its d IS the
max-of-affine and everything downstream follows; when it fails, the fit was short a cone and
the tiling is refused rather than approximated.

Only after that: re-measure how many tilings really are exact (the 723 is an overcount), turn
`IN_SERVICE` on, register in the six places STATE.md lists, sweep, install. And run the whole
path against the 6,536 published coordination sequences first — the terms are already known to
match `galtile`, so any disagreement is downstream of it.

## V. Section P's other buckets, measured (14 September)

`relscan.py` buckets every entry outside the roster whose conjectural line names another
A-number: 25,298 carry a conjectural line, 8,202 of those name an A-number, 6,163 are open with
no parsable recurrence. By the shape of the line:

    ~1,500  Plouffe's Sum_{k>=0} A######(k)/exp(k*Pi) = <constant>   analytic, not this project
        47  a(n) = A000041(n)^2 - cumulative A000712(...)
        66  "the number of letters in the n-th iterate of the mapping 00->001, 1->000"
   ~110     "See A###### for a similar conjecture"                   pointers, not claims
         9  "Conjecture: partial sums of A######"

**The 18 grid-base entries came out of this bucket and are installed.** Two others were looked
at and one is written up below.

### V.1 The block-substitution lengths: the rule is pinned, the proof is not

66 entries say a(n) is the number of letters in the n-th iterate of a mapping like
`00->001, 1->000` from a seed. The rule they mean is settled, by matching the published data:
scan left to right, take the longest left-hand side that matches, copy any character that
matches nothing. That gives 2, 3, 6, 10, 17, 29, 51, 90, 160, 282, 499 for `00->001, 1->000`
and 2, 3, 6, 13, 29, 65, 146, 328, 737, 1656, 3721 for `00->001, 1->011` -- A285665 and
A286062 term for term. `src/morphlen.py` has it.

The natural model does not work and it is worth recording why, because it looked like it did.
Take the state to be (unit being rewritten, characters pending before it) -- finite, since the
left-hand sides are bounded. Measured over nine levels, the map (unit, carry) -> (emitted
units, carry-out) is a FUNCTION: eight states, never a disagreement. That is the check most
people would run, and it passes.

**Ask instead whether the CHILDREN are determined, and it fails**: the same parent pair emits
children with different carries depending on what preceded it -- 198 disagreements over eleven
levels on A285665, 15 on A289131, and 0 on A286062, which is exactly how a partial check
misleads. A child's carry belongs to the next level's parse, not to the buffer position it came
from, and it chains across parent boundaries; adding the next level's carry to the state
introduces the level after that.

So this is an HD0L system, not a substitution. Its length sequence is C-finite for reasons that
need the theory rather than a transfer matrix assembled by inspection, and `morphlen` is left
with `IN_SERVICE = False`. 66 entries, and the reading is done; whoever takes it needs the
HD0L length theorem, not more state.

## W. The refusal census, and what it says to do next (14 September, late)

One pass over the whole clone, classifying every open entry outside the roster that states a
conjecture by **which reader refuses it**:

| count | |
|---:|---|
| 360,774 | no conjectural line |
| 16,368 | neither name nor claim read |
| 12,976 | on the roster |
| 4,976 | not open |
| 2,211 | **claim read, name NOT read** — an engine is missing |
| 1,164 | both read — sweep territory |
| 558 | **name read, claim NOT read** — a *reader* is missing |

`engine/census_namereadable.json` and `engine/census_claimreadable.json` hold the two lists.

### W.1 The 558 are cheap and are now being worked

228 of them defer their conjecture to a linked a-file (`linkrec`, done — the files are in
`afiles/`). 274 more state a closed form the `closedform` module reads outright and were
simply not in the closed-form sweep's hand-made pool (`cfpool`, done). Between them they have
paid 154 results today and the sweeps are still running. What is left of the 558 after those
two is about 50 entries of miscellaneous shapes, several of them one-offs.

### W.2 The 2,211 are 379 Galebach plus a long tail

379 are `Coordination sequence Gal.u.t.v` — the single biggest family in the pool and the one
worth real work. See §U and below. The next largest shape is 25 entries and then it is a tail
of ones and twos: **there is no second Galebach.** Anything further in this bucket is one
engine per few entries, which is the worst ratio in the project.

### W.3 Where the Galebach chain actually stands

The certificate is no longer the weak link. `galpoly` does exact integer region arithmetic in
the plane and `galcert2` decides both Bellman conditions on regions rather than on samples;
it refuses A310511 (which the old one certified and which diverges at term 35) and certifies
Gal.1.1.1 and Gal.1.2.1 outright. `galfit` is the single place that builds planes and edges,
and it validates the fit on the patch **rim**, which `galhull` never did.

Two soundness bugs fell out of that, both recorded as defect 24: `gallat.lattice` was accepting
a translation on signatures alone, and `galcoord` was computing the lattice in a *different
embedding* from the patch it then used it on.

What blocks the vein now is the **fit**:

* `galhull.pieces` is cubic in the fallback and takes minutes per class at radius 70;
* its plane count grows with the radius (15 at 34, 21 at 70) — a fit picking up the patch rim
  rather than the tiling;
* for many tilings the distance is genuinely **not** a max of affine pieces, and those are
  honest refusals, not a gap to close.

The measurement to make next is the simple one: over the 379, how many reach the certificate
at all, and of those how many pass. `scratchpad/galscan.py` does exactly that and its shards
write `galgood_*.json`. **Do not tune the fit before reading that.** If the answer is that
most refuse at "distance is not a max of affine pieces", the fit is not the problem and the
whole max-of-affines premise is — and then the model to reach for is a Bellman certificate
whose D is piecewise affine on a *subdivision that is not convex*, which is a different and
larger piece of work.

## X. The Galebach vein, measured and in service (14 September, late)

`galcoord` is IN SERVICE and has paid 2 results (A315405, A315418) and a 158th argument. §W.3
asked for the measurement before any tuning; here it is, over 98 of the 379:

| | |
|---:|---|
| 72 | the fit fails on the patch **rim** |
| 12 | not a max of affine pieces even on the inner patch |
| 7 | fit timed out |
| 4 | the certificate refuses |
| 2 | **certified** |

**The rim failures are OVER, not under.** Of 17 sampled, 13 have the fitted max EXCEEDING the
true distance, by up to 5; one is exact. That is decisive: a support fitted on inner points
that exceeds `d` further out means `d` is not convex, so no max of affine pieces equals it and
no patch radius fixes it. Refining to a sublattice of index up to 4 did not help on the case
tested (Gal.4.31.1).

### What would reach the other 98%

`galcert2` never uses convexity. It needs only that `D` is affine on each of finitely many
POLYHEDRA that cover the plane — the max-of-affines form was a convenience, because then the
pieces are the cells of the normal fan and come for free. So the open problem is producing a
non-convex piecewise-affine description of `D` from a patch, and verifying it costs nothing
new.

Two shapes worth trying, in order:

1. **Cone × residue.** `D_c(m) = ψ_c(m) + ε_c(m mod L')` for a sublattice `L'`: fit the
   polyhedral norm `ψ` from the asymptotics and the correction `ε` as a lookup on `L/L'`.
   `galfit` already takes a `refine=(k1,k2)` argument that splits the orbits by a sublattice;
   index 4 was not enough on the one case tested, and the thing to measure is whether the
   excess `max - d` is constant on residue classes for SOME sublattice, which is a cheap scan
   over the patch and has not been done.
2. **Cones from the BFS itself.** Partition the patch by which neighbour realises the minimum
   in `D(x) = 1 + min D(y)`; the closure of each part is a candidate region, and the affine
   function on it is read off by least squares in exact arithmetic. This does not assume
   convexity at any point.

Do not spend on the fit before (1)'s scan, which is an afternoon and settles whether the
correction is lattice-periodic at all.

### X.1 The rim refusals were the FIT'S FAULT, not the tiling's (same evening)

`galhull.scan` takes `C = min(d - A*m - B*n)` over the points it is **given**, so every plane
it returns is a support at those points and only those. `galfit` was handing it the inner
patch (`d <= R - 6`) and then checking the rim — where a plane fitted inside can of course
exceed `d`. That is what 72 of 98 entries were refusing on, and it is a statement about which
points the fit had been shown, not about the tiling. Given the WHOLE patch:

| entry | inner fit | full-patch fit |
|---|---|---|
| A310031 Gal.5.39.1 | 319 planes, 0 leftovers, rim fails | 341 planes, **0 leftovers**, exact |
| A310027 Gal.5.41.2 | 680 planes, 0 leftovers, rim fails | 662 planes, **0 leftovers**, exact |
| A310007 Gal.4.31.1 | 12 leftovers | 12 leftovers (genuine non-convexity) |

`galfit` now fits on the whole patch. Whether the planes are right OUTSIDE the patch is not
decided there and must not be — that is `galcert2`'s job, and it still refuses both of the
above: the failure point moves outward with the radius ((4,4) at 60, (5,5) at 80), which is
the signature of a facet whose region lies beyond the patch and that no bounded patch can see.

So the premise is in better shape than §X said and the obstacle has moved: it is not that `d`
fails to be a max of affine pieces, it is that **enumerating the facets from a bounded patch
does not converge**. The thing to try is to get the facet GRADIENTS from the asymptotic shape
(the limit of `d(t·u)/t` over directions `u`, which a modest patch pins down) and only then
fit the constants, rather than discovering gradients from local differences.

### X.2 The correction is not lattice-periodic — shape (1) is dead

Measured on Gal.5.39.1: the excess `max - d` is 0 at 3,632 of 3,664 patch points, and the 32
exceptions do **not** become constant on residue classes under any refinement tried — at
modulus (6,6), 32 of 648 classes still carry more than one value, i.e. refining never separates
a bad point from a good one. The exceptional points also sit on the rim at every radius
(max |m| = 5, 8, 11 at R = 30, 50, 70) rather than in a fixed finite region, so they cannot be
tabulated the way `kdcert` tabulates the boards below H0 either.

### X.3 The fit converges and the certificate still refuses — the obstruction is structural

With `galhull.support` deciding the supporting plane instead of searching for it (a two-variable
LP through `galpoly.polygon`, ~9 ms a point, and a `None` now MEANS no support exists), fitting
a whole tiling went from about 90 seconds to under one. That made the decisive experiment
cheap — push the patch radius and watch both the plane count and the certificate:

| entry | radius 50 | radius 100 | radius 150 |
|---|---|---|---|
| A310089 (11 classes) | 246 planes, refuses | 255 planes, refuses | 255 planes, refuses |
| A310031 (18 classes) | 342 planes, refuses | 337 planes, refuses | 339 planes, refuses |

**The plane count stabilises and the certificate still refuses.** So it is not a facet that a
bounded patch cannot see. The reason is visible once stated: `scan` takes each constant as
`C = min(d - A m - B n)` over the points it is given, and extending the patch can only lower
that minimum — so a patch fit's constants are upper bounds that keep being right on the patch
and wrong beyond it. There is no global max of affine pieces agreeing with `d`; `d` is a
polyhedral norm plus a bounded correction that does not settle to a constant per facet, and
§X.2 already showed that correction is not lattice-periodic either.

**Conclusion: the max-of-affines premise reaches a small minority of these tilings and the
obstruction is structural, not computational. Stop tuning the fit.** What is worth keeping is
everything downstream of it: `galpoly` and `galcert2` verify ANY piecewise-affine `D` on ANY
polyhedral subdivision, convex or not, and `galhull.support` decides convexity questions
outright. A model that produced a non-convex subdivision — §X shape (2), partitioning the patch
by which neighbour realises the minimum in `D(x) = 1 + min D(y)` — would be certified by the
machinery as it stands.

## Y. The 558 name-readable bucket, closed out (14 September, late)

Of the 558 entries whose name an engine reads and whose claim nothing did:

| | |
|---:|---|
| 228 | the claim is in a linked a-file — `linkrec`, **82 results** and still running |
| 274 | the claim is a closed form the stale pool never offered — `cfpool`, **144 results** |
| 7 | "a(n) is a polynomial of degree d for n>k" — `degclaim`, a 159th argument, 2 so far |
| ~49 | a genuine tail of one-offs |

**The tail is worth reading once and then leaving.** Bucketed, it is: 7 "Rule N also generates
this sequence" (a claim about a cellular automaton, not about a(n)); 9 shift identities
`a(n) = A######(n+k)` (measured pool-wide at 26, with both sides on the roster in exactly one
case — §W); ~8 exponential closed forms with shifted exponents, `a(n) = 19*4^(n-2) - 16*3^(n-3)
+ 1`, which `closedform.parse_line` declines — **that is a parse gap and the cheapest thing
left in this bucket**; and about 25 true one-offs (Conway's Game of Life, binary
representations, Fibonacci-then-power splits).

So the next cheap thing in §Y is the exponential parse gap in `closedform`, worth about 8
entries on `ca2dcount`, `ca2d` and `transfer46`. After that this bucket is done and the pool's
remaining mass is the 2,211 claim-readable entries (§W.2: 379 Galebach, now known structural,
plus a tail of ones and twos) and the 16,368 where neither reads.

## Z. The 16,174 where neither reads — characterised at last (14 September, night)

The refusal census (§W) counted this block and stopped. What it is, by the KIND of claim:

| | |
|---:|---|
| 5,338 | no recognised kind at all |
| 4,871 | names another sequence |
| 1,287 | primality |
| 739 | finiteness or existence ("only", "infinitely many", "always") |
| 662 | asymptotic |
| 660 | congruence |
| 651 | **a recurrence, written in words** |
| 627 | a pointer to another entry |
| 568 | positivity or monotonicity |
| 510 | **a closed form** |
| 261 | **a generating function or series** |

Only the three in bold are shapes this project's argument can settle at all — 1,422 entries —
and in every one of them the obstacle is the NAME, not the claim: no engine models the object.
So the question is whether those 1,422 names cluster.

**They do not.** The largest clusters are 24 "complementary equation" entries, 25 of Zhi-Wei
Sun's `x^2+y^2+z^2+w^2` representation counts, 13 `number of (s(0), ..., s(n)) such that ...`,
9 "arrangements of n balls in n boxes", and then it is ones and twos.

And the most walk-shaped of those looked like a null on inspection. The `(s(0), …, s(n))`
family is **41 entries** pool-wide — lattice paths with `|s(i) - s(i-1)| <= 1` and `s(i) >= 0`
— which looks exactly like transfer-matrix territory until you notice the state is UNBOUNDED:
these are Catalan- and Motzkin-like, P-recursive and not C-finite.

**The null was mine, and it is withdrawn.** When this was written the sentence read "all 40
carry no readable claim of any kind, because nobody conjectures a linear recurrence on a
Motzkin number". That was measured with readers that could not read a P-RECURSIVE recurrence
at all — the very shape a Motzkin-like sequence takes. Re-measured with `precrec`: **16 of the
41 carry a readable claim**, every one of them P-recursive, and one of them (A026013) is now
proved and on the roster. The reason the family looked empty was the reader, not the
mathematics, which is the same mistake §X.3 exists to warn about.

What the re-measurement then found is a DIFFERENT refusal, and this one is real. Of the 14 off
the roster, 13 carry no generating function at all — the claim is stated, the premise is
missing — and the fourteenth, A026110, states `z(1-z)M^5` with M the Motzkin g.f., at an index
origin three below its own offset. That last one was a defect of mine too (`algf` could not
read `with M the g.f. of ... (A001006)`, and would not tolerate a stated shift); it is fixed
and the entry now reads. The 13 stand as a genuine null for the holonomic argument: a
conjectured P-recursive recurrence with no stated g.f. is a claim with nothing to prove it
against, and closing them needs the g.f. DERIVED from the walk, which is a new argument, not
a better reader.

### What this says

The pool is close to the end of what the transfer-matrix argument reaches by reading better.
Every large vein so far was machinery already built and hidden by how a sweep chose what to
look at; this block is not that. What remains in it needs either a new ARGUMENT (P-recursive
certificates would open the Catalan/Motzkin families, which are large) or one engine per
entry, which is the worst ratio here.

So the honest ranking of what is left:

1. finish the sweeps now running (`linkrec` high-cap, `cfpool`, `galcoord`, `degree`) — real
   results, already flowing;
2. **P-recursive certificates** — the one new argument with a large family behind it, and the
   natural successor to everything C-finite here;
3. the 4,871 "names another sequence" entries, if a way is ever found to settle an identity
   between two independently-defined sequences mechanically — §W measured the shift-identity
   subfamily at 26, with both sides on the roster in exactly one case, so this needs a real
   idea and not a reader.

## AA. Conjectured P-recursive recurrences (14 September, night)

**459 open entries** conjecture `sum_i p_i(n) a(n-i) = 0` with polynomial coefficients in n.
`ratrec` reads constant coefficients only, so not one had ever been asked about — bigger by
claim count than the linked-a-file vein. `precrec` reads **380**.

The proof route is `holonomic`: where the entry states its generating function as FACT and that
function is algebraic, the claim becomes `B(x) = sum_i x^i (p_i(theta+i)A)(x)`, an element of an
algebraic function field, zero exactly when the recurrence holds everywhere and a polynomial of
degree d exactly when it holds for n > d. An identity, not a run of checks.

### The size, measured

| | |
|---:|---|
| 28 | have a usable algebraic g.f. — **the reachable set** |
| 146 | reference another sequence's g.f. by A-number |
| 137 | have no g.f. line at all |
| 44 | have a g.f. line the reader still refuses |
| 23 | are a sum or a binomial formula — `zeilb`'s territory |
| 6 | give only an exponential g.f. — a different object |

**The reader is not the limit; the proof route is.** This is the first vein whose obstacle is
mathematics rather than instrumentation.

### What would widen it, in order of value

1. **A-number substitution.** 146 entries cite another sequence's g.f. The citations are a long
   tail — Catalan 11, Motzkin 5, central binomial 3, then ones and twos — and several need
   series reversion, which is algebraic but is another operation to implement. `algf.STANDARD`
   already holds a self-verifying table of five; the work is parsing the *reference*, which the
   corpus writes a dozen ways ("where F(x) is the g.f. of A007564", "c(x) g.f. of A000108").
   Realistic gain maybe 15–25 entries.
2. **Creative telescoping** for the 23 sums — `zeilb.py` exists and has 4 results.
3. **Holonomic closure**, building the annihilator from the entry's definition rather than
   reading a g.f. off it. That is the general answer and reaches the 137 with no g.f. line,
   but it is a real piece of work.

### A speed note, if this is picked up again

`holonomic.prove` calls `sp.simplify` then takes two 40-term series of a nested-radical
expression; it runs about two entries per seven minutes. The decision does not need full
simplification: B lies in `Q(x)[y]/(y^2 - D)`, so reducing there and asking whether the
y-coefficient vanishes and the rational part is a polynomial is the same decision in polynomial
arithmetic. Worth doing before widening the pool, not before finishing the 28.

## AB. Creative telescoping: the machinery is real, the remaining refusals are not notation
(14 September, night)

`zeil_run`, `zeilb_run` and `hyp_run` implement Zeilberger with the boundary correction, Ore
right-division, and the hypergeometric-value conversion. 11 installed results. Written in
August, **run once by hand, never given a runner** — `zeilbrun.sh` fixes that and is in
`restart_all.sh` (shards 3–5, so `harvest.py`'s existing glob collects them). 309 candidates.

The 19 parse skips in the August files are stale: every one is
`Conjectured to be D-finite with recurrence: ...`, which `prove_rec.parse_conj` reads today.

### The dominant refusal, read

542 of 761 August verdicts were "no usable hypergeometric sum formula". Of 401 sum lines the
candidate scan offers, `sumparse` refuses 287, and they break down as:

| | |
|---:|---|
| 178 | the summand names ANOTHER sequence (`Stirling1(n+2,k+2)`, `A002426(k)`) |
| 42 | other — mostly Stirling numbers and elided products |
| 35 | a double sum, or an index that is not a single k |
| 29 | an arithmetic function — floor, mod, sigma, phi |
| 3 | an infinite or elided range |

**This is not the pattern that paid all day.** `sumparse`'s own docstring records that its
first census found "most of it was notation, not mathematics" — that was true then and it is
not true now. A summand containing another sequence, a Stirling number, an arithmetic function
or a second index is genuinely outside single-variable creative telescoping. Widening the
parser would only move the refusal one step later, to "no telescoper found".

What would actually reach them, in order of honesty about the cost:

1. **Multivariate telescoping** for the 35 double sums — a real algorithm, not a reader.
2. **Substituting a referenced sequence's own closed form** into the summand, for the subset of
   the 178 where that sequence has a hypergeometric one. Same shape as `algf.of`, and the same
   discipline applies: verify the substitution against the referenced entry's own terms.
3. Stirling numbers have known holonomic representations; a table of them, verified the way
   `algf.STANDARD` is verified, would reach part of the 42.

None of these is a reader fix, and none should be described as one.

## AC. The generating function stated as a CONTINUED FRACTION (15 September)

`algf.OUT` rejects any line containing the words "continued fraction". That was written when
nothing here could read one, and it stayed after `implicit` and `quadratic` made reading one
cheap. **1,509 entries state their g.f. that way** — a pool the size of the largest veins found
so far, invisible because of three words in a refusal list.

It splits cleanly, and the split is mathematics:

| | |
|---:|---|
| 1,015 | a LEVEL-INDEXED fraction — `Q(k) = 1 + (4k+1)x(1+2x)/(k+1 - ...)` |
| 565 | written with an ellipsis and no index |

The first group is **not algebraic** and stays refused: the level map changes with k, so there
is no equation to solve. That refusal is honest and permanent.

The second group is, and the reason is worth keeping because it is why this cost an afternoon
rather than a week. Each level of a continued fraction

    g_i = b_i + s_i * n_i / g_{i+1}

is a Möbius transformation of the level below, matrix `[[b_i, s_i n_i], [1, 0]]`. Composing the
p levels of one period multiplies p such matrices, and the periodic tail is the FIXED POINT of
the composite map: `g = (ag+b)/(cg+d)`, a quadratic. Prefix levels and the head of the line are
further Möbius maps applied to that fixed point and cannot raise the degree. So **a periodic
continued fraction is a quadratic surd, always — never degree 3, never higher** — which is
exactly the field `holonomic.quadratic` decides claims in. `src/cfrac.py`, ~120 lines, no new
solver.

Of the 565: 88 are not open, 435 are open but carry no readable claim of any kind (a continued
fraction is usually the whole content of such an entry), and **42 are open with a claim** — all
42 P-recursive, none C-finite.

### The defect this vein produced, recorded because it is the recurring one

A084261's levels drift: `x^2, x^2, 2x^2, 2x^2, 3x^2, ...`. With two repeats accepted as
evidence of a period, `2x^2, 2x^2` reads as prefix 2, period 1; the g.f. that came out did not
generate the entry's terms, and the sweep recorded **"the stated g.f. does not generate the
DATA"** — an accusation against the entry for a defect of mine. That is the fifth time. The
rule now: two repeats suffice only when the period starts at the top (a drifting fraction never
repeats its FIRST level), and three are required once a prefix is allowed. A084261 also spells
its general level out as `[(n+1)/2]*x^2`, which says in the line itself that it is not periodic
— so the level-index guard was widened from `k` to `k or n`.

### What it actually paid, plainly

**Two results** — A152601 and A292461. Not a large vein, and the 1,509 should not be quoted as
if it were one: 1,015 are the level-indexed shape and permanently out of reach, 88 are not
open, 435 carry no conjecture to settle, and of the 42 that do, **35 were already on the roster
from other veins**. What was left was seven entries, of which two proved, two came back
"residual is not a polynomial" (the claim is simply not established by this route) and three
could not be read as periodic at all.

So the honest summary is: a pool that looked like the largest one left was, after every filter
that matters, seven entries. The machinery is worth keeping — `cfrac` is now a g.f. source for
every sweep and costs nothing when it refuses — but the size of a grep is not the size of a
vein, and this is the clearest example of that so far.

One thing the two results do show: A292461's NAME already gives its g.f. in closed form
(`Expansion of (1 - x - x^2 + sqrt((1 - x - x^2)^2 - 4*x^3))/2`), and `algf.from_name` refused
it. The continued fraction was the second route to a function the first route should have read.
That is a `from_name` defect worth a census of its own, and it is the next thing to measure.

## AD. Where the reader-defect pattern STOPS paying (15 September)

Today's eleven results all came from one move: find the notational defect that makes a reader
refuse a line, fix it, re-sweep. It is the move that has found every large vein in this project,
and the temptation after a morning like this one is to apply it everywhere. So it was applied
to the two places where it should have paid most, and it paid **nothing**, and that is worth
recording as carefully as the successes.

### `algf.from_name` and "in powers of x" — zero

`from_name` is the STRONGER g.f. source (A116388 is why: an entry's formula line can be wrong
where its name is right). It refused `Expansion of (1 - x - x^2 + sqrt(...))/2 **in powers of
x**` because the trailing phrase, which names the variable rather than qualifying the function,
became three unknown words. 1,552 names in the corpus carry that phrase; 756 of them in a form
where the variable is x or z.

Fixed, and then measured: of those 756, **744 carry no readable claim of any kind**, 10 are not
open, 2 are already on the roster. **Zero candidates.** Regression over the P-recursive pool:
1 gained (A292461, already counted through `cfrac`), 0 lost. The fix is right and stays — it
reads a stronger source — but it is not a vein.

### `gfrec.parse_gf` and implicit multiplication — zero

This is the reader behind the largest settleable pool in the project (3,520 entries: a
conjectured recurrence plus a generating function stated as fact). It accepted only a g.f. with
every multiplication spelled out — `1/(1-2x-x^2)`, the commonest notation in the corpus, was
refused, as were `O.g.f.`, `G.f.=`, square-bracket grouping, and `z` as the variable. Exactly
the five defects found in `algf` the same day. It now normalises through `algf._implicit`.

Measured over the whole clone rather than over the pool — **the pool cannot answer this**, since
it was built by a filter using the same reader, so an entry written `1/(1-2x)` never entered it
and a regression over it is blind by construction. Corpus-wide: 3,039 entries read by both
readers, 35 by neither, **5 by the wider one alone**, 0 lost. Of those 5: three state the g.f.
inside a `Conjectures from ... (Start)` block, so it is itself a conjecture and `factlines`
excludes it correctly; one (A092387) is marked proved in the entry; and A090381's own text says
"the defining g.f. implies the recurrence". **Zero results.**

### What this says about the pattern

A reader defect is only a vein when the refused entries have something to prove. Both of these
refusals were real, both fixes are correct, and behind both was a population that carries no
conjecture — 744 of 756 in one case, and in the other a corpus where contributors almost always
write the `*`. The pattern's yield is not in the size of the refusal; it is in the overlap
between the refusal and the entries that state a claim. The Motzkin family this morning had that
overlap (16 of 41) and paid; these two do not and paid nothing.

## AE. Every hand-built pool is a snapshot (15 September)

The reader-defect move stopped paying (§AD). The move that replaced it is blunter and paid
more: **rebuild each sweep's candidate pool from the clone and see how much it was never asked
about.** Nine stale filters had already been found one at a time; this was the first pass that
went looking for them deliberately.

| pool | held | corpus-wide | never asked | off roster | proved |
|---|---:|---:|---:|---:|---:|
| `deep-check/prec.txt` (P-recursive) | 380 | **989** | 609 | 123 | **3** |
| `cfpool_cands.json` (closed form) | 416 | **728** | 564 | 564 | **18** |
| `deep-check/linkrec.txt` (linked a-file) | 192 | 888 | 696 | 35 | 0 |
| `deep-check/degree.txt` (polynomial degree) | 7 | 8 | 1 | 0 | 0 |

Two of the four were badly stale and paid 21 results between them. Two were not, and the reason
each was not is worth keeping:

* **degree** — the phrasing `a(n) is a polynomial of degree d` occurs 8 times in the whole
  database. A pool of 7 was essentially complete. Rarity, not staleness.
* **linkrec** — 888 entries defer a recurrence to a linked a-file, but the sweep needs an ENGINE
  for the name (it tests annihilation against a model, not against published terms), and 30 of
  the 35 off-roster candidates have no engine. The old pool of 192 was not a stale snapshot; it
  was correctly filtered by engine coverage. One real defect did surface: the sweep reads only
  CACHED a-files and reports an uncached one as "a-file absent", so all 35 were refused for a
  fetch I had not done. Fetched (all 35 present on oeis.org), re-run, and the refusal became the
  honest one.

The closed-form rebuild is the clearest case. Its 564 new candidates refuse as: **388 no engine
reads the name**, 85 state space over the cap, 32 not open, 29 no readable closed form, 4 no
integer annihilator, 1 model does not satisfy the annihilator — and **18 PROVED, zero failures**.
So the boundary of that vein is engine coverage, exactly where the refusal census said the mass
was, and the 18 are what was sitting inside the boundary all along, unasked.

### The one that matters most: `namepool`

`deep-check/namepool.txt` feeds `sweep_shard` with `TAG=np`, the highest-yielding sweep in the
project — about 190 proved from 1,017 asked. It holds **1,446** entries, and STATE.md recorded
"429 still unasked are worth asking". Those 429 are now 219 and **every one is already on the
roster**: that TODO is closed, and the pool is spent.

Rebuilt from the clone on the same criterion — off the roster, a readable recurrence or closed
form, and a NAME `uniform.read` models — it is **1,727 entries**, of which 866 were never in the
old file at all. The first 196 asked give **10 proofs and no failures**, so the vein is roughly
where it always was. This is the largest stale pool found in the project, on the sweep where the
cost of not rebuilding was highest.

The rebuild also says what the ceiling is, from the same scan: 12,681 entries carry a
conjectural line this project cannot read as a recurrence or closed form, 11,967 are already on
the roster, and **1,675 have a readable claim whose NAME no engine models** — the §W.2 boundary
again, from a completely different direction, and the same answer.

### The rule this gives

A pool file in `deep-check/` is a claim about the database made on the day it was written. None
of them is rebuilt by anything. Before running a sweep again, rebuild its pool from the clone
and diff — it costs one sharded scan, and of the five checked on 15 September **four were
stale**. Still to do: `second.txt` (13,139), `tabpool.txt`, `rowpool.txt`, `recgf.txt`,
`pool-rec.txt`, `pool-order.txt`.

## AF. Sliding-window image counts — the second large family (15 September)

**The 149 in the first draft of this section was my own error and is withdrawn.** It came from
grouping the refused names by their first seven words, which merges shapes that are not the same
problem: regrouped on the full name there are **76 distinct shapes over 162 entries**, in
clusters of three to seven. §W.2's "there is no second Galebach" survives that correction. What
follows is a real family and a real argument, but it is **11 entries**, not 149, and the number
is stated here rather than in a summary because over-counting a vein is the failure this
project's rules exist to prevent.

The family sits among the entries whose closed-form claim `closedform` reads outright and whose
NAME no engine models — 388 of the 564 new candidates from §AE refuse that way — and it is:

    A228462  Number of arrays of maxima of three adjacent elements of some length 7 0..n array.
             Empirical: a(n) = (2/15)n^5 + (7/6)n^4 + (25/6)n^3 + (19/3)n^2 + (21/5)n + 1.
    A228741  Number of arrays of the median of three adjacent elements of some length-6 0..n array.
    A229013  ... with no adjacent equal elements in the latter array.

Every existing engine here models a FIXED alphabet with n as the length. These invert that: the
length is a small constant and **the alphabet 0..n grows with n**. No transfer matrix applies,
which is why every one of them is invisible.

### The argument, which is exact and cheap

Let the window map be `b_i = f(a_i, ..., a_{i+w-1})` with f a max, min or median, on
`a` of fixed length k over the alphabet {0..n}, so `b` has fixed length L = k-w+1. The question
is the SIZE OF THE IMAGE.

**Whether a given b is in the image depends only on b's ORDER TYPE** — the weak ordering of its
entries — and not on n or on the actual values. For the max window: the componentwise-largest
candidate witness is `a_i = min{ b_j : window j contains i }`, and b is achievable exactly when
that witness reproduces it; both the construction and the test are comparisons among b's
entries alone. No value is ever needed above max(b) or below 0, so the bounds play no part.
(The same holds for min by symmetry, and for median the witness search is over the finitely many
order types of a, which is again comparisons only.)

Therefore, writing `A_m` for the number of achievable order types of L entries using exactly m
distinct values,

    a(n)  =  sum_m  A_m * C(n+1, m),

because the number of tuples in {0..n}^L with a prescribed order type using m distinct values is
exactly C(n+1, m). **That is a polynomial in n of degree at most L, exactly, with no fitting and
no asymptotics** — the entry's conjecture is then either equal to it or it is not, and the
comparison is polynomial identity in Q[n].

The cost is the enumeration of weak orderings of L elements: the ordered Bell numbers, 4,683 for
L = 6, 47,293 for L = 7, 545,835 for L = 8. Each is tested by one witness construction. That is
seconds to minutes per entry, which is the same order as every other sweep here.

### Why an 11-entry family is still worth the build

It is ONE argument for the whole family, and it is not specific to max or median: any window statistic decided by comparisons has the same order-
type invariance, so "no adjacent equal elements", min, and the range statistics in the same
family come along at no extra cost. The build is `src/window.py` (order types, witness,
polynomial assembly) plus a sweep; no new solver, and the verification is the usual one — the
polynomial it derives must reproduce every published term before it is used.

### The defect this build produced, and it is the sixth

A118447 states `O.g.f.: (R-1)^2(R+1)(R+3)/8R^5, where R=sqrt(1-4x)`. In this corpus a juxtaposed
product written straight after a division sign is the whole DENOMINATOR — the line means
division by `8R^5`. Inserting multiplication signs left to right gives `.../8*R**5`, which
MULTIPLIES by `R^5`; the series that came out was 4, −38, 104, … against a published
4, 42, 304, … and the sweep recorded **"the stated g.f. does not generate the DATA"** against an
entry that is entirely correct. Read as written it reproduces every published term.

That is the sixth time a refusal has blamed an entry for a limitation of the reader, and it has
the clearest signature of any of them: the entry's own terms are the disproof of the disproof.
`_denominator_run` now parenthesises a juxtaposed run following `/`; only juxtaposition with no
space is absorbed, so an explicit `*` keeps its left-to-right meaning and `x/2 - 1` is untouched.
Regression over the rebuilt 989-entry pool: **988 unchanged, 0 lost, 0 gained, and A118447 the
single difference** — exactly the intended change and nothing else.

**The standing lesson, now with six instances: a "the entry is wrong" verdict is a claim about
MY reader until it has been checked by hand.** Every one of the six was mine. Not one apparent
disproof in this project has ever turned out to be a false conjecture in the OEIS.

## AG. The 2,211 really do need engines, and where the premise reader was unsound

Two questions the refusal census left open, both answered, both against my expectation.

### AG.1 "An engine is missing" was right

§W recorded 2,211 entries as **claim read, name NOT read** and concluded an engine was missing.
The holonomic and transfer arguments never need the name — they settle a claim against the
entry's OWN generating function — so the conclusion looked premature. Measured over all 2,211:

| | |
|---:|---|
| 2,204 | assert **no generating function at all** |
| 3 | assert one this reader refuses |
| 4 | assert a usable algebraic one |

**The census was right and the objection was wrong.** Those entries need engines; there is no
premise hiding in them. Three of the four exceptions proved (§AG.3) and the fourth is A124869,
whose "G.f." is the generating function of the real parts themselves while its terms are their
numerators — the asserted line is about a related quantity, and reading it as the sequence's own
is a mistake of the reader, not an error in the entry.

### AG.2 The premise reader was reading conjectures as facts

The first pass at AG.1 reported **192 with a factual g.f.** and it was wrong. `algf` tested for
a conjectural word ON THE LINE, and a generating function inside a

    Conjectures from _X_, ... : (Start)
    a(n) = ...
    G.f.: ...
    (End)

block carries none. Of the first 173 it called factual, **170 were inside such a block** — one
conjecture written twice, and no premise at all. That is defect 2, in the module that supplies
the premise, and `factlines.facts` exists precisely for it: its docstring records that 1,336
installed papers once had to be withdrawn for this exact mistake.

**Audited before fixing**: of the 36 entries carrying an installed `holonomic` paper, 33 took
their premise from a fact line and 3 from the entry's NAME, which is always a fact. **None was
affected** — the hole was latent, never exploited. `algf.read` and `cfrac.read` now take lines
only from `factlines.facts`, and the regression over the rebuilt 989-entry pool is 989
unchanged, nothing lost and nothing gained: closing it cost nothing.

### AG.3 `equate`'s filter, and why 3,593 entries were still worth only three

`equate.py` settles a conjectured generating function against one the entry states as fact. It
has **four papers**. Its candidate filter requires the conjectural line to BEGIN with
"Conjectur", and the corpus writes this one overwhelmingly as `Empirical g.f.:` —
**3,593 entries against 131**. Defect 2 again, in the filter of a vein whose own docstring
estimated 353 candidates.

It is the largest instance of that filter found, and it paid **three**: A056328, A056329,
A082975. Of the 3,718 entries carrying such a line, 2,740 are already on the roster; of the 978
that are not, 120 are closed, 78 carry no readable conjectured g.f., and **892 assert neither a
generating function nor a closed form to prove one from**. `src/sweep_gfident.py` is the sweep;
it is worth keeping and it is not a vein.

**Three big-looking numbers in one day — 1,509 continued fractions, 3,593 empirical g.f.s, 2,211
claim-readable entries — and between them they paid five.** The filter defects were all real.
The size of a grep is not the size of a vein, and this is now the third time today that has been
the lesson.

## AH. A vein with results and no builder, and two more hedges (15 September)

`sweep_recgf` is the mirror of the project's largest vein: a RECURRENCE the entry states as
fact, and a conjectured rational generating function that follows from it by polynomial algebra.
Its pool of 1,048 is fully asked. It has **six proved records sitting in `rg_hits_*.json` and
no builder at all** — the same gap `build_gfonly` was written to close, in a different vein.
`src/rgbuild.py` and `src/build_recgf.py` close it; all six install (`recurrence-to-gf`).

Applying the §AG.3 filter lesson to this vein's own pool found ten more entries whose
conjectured g.f. is written `Empirical g.f.:` and which state a recurrence as fact, never asked.
Three proved — **and two of the three would have been unsound papers.**

### Two more hedges, caught by hand before installation

    A020745  a(n) = 2*a(n-1) - a(n-2) + a(n-3) - a(n-4)
             (holds at least up to n = 1000 but is not known to hold in general)
    A153368  Heuristically, a(n) = +6*a(n-2) -9*a(n-4) +2*a(n-6).

Neither line carries a conjectural word, so `factlines` read both as premises. **A formula
qualified by a finite range is not a fact**, and neither is one the contributor calls heuristic;
proving the entry's generating function from either would be proving one conjecture from
another. Counted over the whole clone, the phrasings are: 20 "holds at least up to n = 1000",
24 "but is not known", 130 "probably", 71 "presumably", ~60 "heuristic", plus "checked/verified
up to n = ...". All are now in `factlines.WORD`.

**Audited before and after: zero installed papers rest on a line the widened test now rejects.**
The fix is purely preventive, and what it prevented was two papers in the batch being built at
the time.

This is the third distinct hole found in one day in what counts as a PREMISE — a conjectural
block (§AG.2), a range qualifier, and a heuristic. They share a shape: the entry is perfectly
clear about its own uncertainty, in English, and the filter was looking for one word.

## AI. The second-conjecture vein: 265 results, no builder, and an incomplete argument

`sweep_second` settles the OTHER conjectures on entries this project has already proved
C-finite. Its pool of 13,139 is fully asked and it holds **244 proved records**. It has **no
builder and no installer**, because `install_vein` skips an entry already on the roster — and a
second paper on the same entry is exactly what this vein produces. (27 entries already carry
more than one paper, so the pattern is accepted; only the plumbing is missing.)

Two things were found before any of it was installed, and both matter more than the papers.

### AI.1 The argument was incomplete for a CLOSED FORM

With `q` the characteristic polynomial of the proved recurrence and `p` that of the claim:

* another RECURRENCE — the claim IS "a satisfies p", and `q | p` settles it outright. Correct.
* a CLOSED FORM — the claim is "a(n) = f(n)". `q | p` shows only that `a` and `f` satisfy the
  SAME recurrence. **It says nothing about which solution each one is.** Two solutions of a
  recurrence of order D coincide exactly when they agree at D consecutive indices, and that
  check was absent. The vein was proving "f satisfies the right recurrence" and reporting it as
  "a(n) = f(n)".

Now checked, on a window past the index from which `a` provably satisfies `p` and inside the
published terms. Re-asking all 244: **one is refused by it outright** — a closed form that
satisfies the recurrence and is a different solution of it. One in 244 is a small rate and it is
not the point; the point is that the other 243 were being asserted on an argument that did not
close, and nobody would have known from the output.

### AI.2 The premise list was stale, and I destroyed a hits file

`PROVED` was assembled from a hand-written list of eleven hits files plus two globs. Every vein
added since is invisible, so an entry whose recurrence this project proved is refused as "no
recurrence available as a premise". It now reads every `*_hits*.json` — only records carrying
explicit `coeffs` and no `FAILS` are used, so a file of another shape contributes nothing.

44 of the 45 entries that still drop are of one kind: their proof is a **generating function**,
not a recurrence, so they carry no `coeffs` at all. The reciprocal of a proved g.f.'s denominator
IS the characteristic polynomial, so deriving the premise from it is the obvious widening and is
not yet done. **That is the next thing to build in this vein.**

And a defect of mine, recorded because it is the second of its kind: installing the rebuilt
closed-form pool I wrote its results to `cfnew_hits.json`, **a filename that already existed**,
destroying sixteen records — which `PROVED` reads, which is how it was noticed. Recovered from
git and merged. A new hits file needs a name nothing else has; the glob that finds it will find
the collision too.


## AJ. The second-conjecture vein, and 235 papers withdrawn the day they went in

§AI built the plumbing the vein never had. Installing it produced **235 papers, and all 235
were withdrawn within the hour.** The record of how is the useful part.

The vein settles a FURTHER conjecture on an entry already proved. It already excluded a
generating function that merely restates the proved recurrence in other notation — 383 of them
per shard — which is the obvious duplicate. It did not exclude a claim IDENTICAL to the one the
entry's existing paper was built from. On those entries the "second result" was the first
result stated again: padding, and the rule it breaks is the first one in STATE.md.

**The first test was too weak, and that matters more than the fact that there was one.**
Comparing each settled line against the lines other hits files record caught 118 of the 235 —
it can only catch a duplicate when the entry's paper came from a vein that stores the line it
used. The authoritative comparison is with the PAPER, which quotes the conjecture it settles and
whose TeX is in `paper-sources/`. On that test **all 235 were duplicates**, including all 117
the first test had cleared. A test that clears half of what a better test rejects is not a
weaker version of the right test; it is a different and wrong one.

Over the whole roster, with the paper-text test inside the sweep:

| | |
|---:|---|
| 1,436+ | the claim the entry already has a paper for |
| 1,532 | a generating function that only restates the proved recurrence |
| 1,849 | too few terms past the threshold to confirm the premise |
| 1,152+ | nothing further follows from the proved recurrence |
| 318 | no recurrence available as a premise |
| **203** | **a genuinely further conjecture** |

So the vein is **203**, not 971 and not 235. A sample read by hand: on each of five the existing
paper proves a RECURRENCE and the new claim is a CLOSED FORM, contributed separately. Those are
two conjectures and two results.

One more guard the same episode forced: 368 installed papers have **no stored source**, so for
those the duplicate test cannot run at all. It now refuses rather than assumes — assuming would
put the first result back on the roster as a second one for every one of them.

### The rule

A vein that can produce a second paper on an entry must be able to say what the first one
proved, and must read it from the paper rather than from any file that happens to be nearby.


### AJ.1 The correction to the correction

The withdrawal above was right about 122 papers and wrong about 109, and the reason is worth
more than either number. The test that withdrew the second batch compared each claim against the
TeX of **every** paper on the entry — including the `second-conjecture` paper that states that
very claim. Every record was a duplicate of itself, and the test could not have returned
anything else. It looked like a stronger test than the one before it because it rejected more.

Re-run against the entry's papers EXCLUDING this vein's own:

| | |
|---:|---|
| 122 | genuine duplicates — the entry's own conjecture, stated again |
| 109 | good second results, wrongly withdrawn |
| 4 | no comparable source; stay withdrawn on the refuse-rather-than-assume rule |

The 109 are reinstated and `sweep_second` excludes its own papers from the comparison. Over the
whole roster it now proves **376** further conjectures, all installed.

**A test that rejects more is not thereby a better test.** Both failures in this episode had the
same shape — comparing a claim against a text chosen too loosely — and the first one hid the
second, because a test that says "duplicate" about everything agrees with the truth wherever the
truth is "duplicate".
