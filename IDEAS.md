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
