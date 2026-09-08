# Every angle of attack, and where each one stands

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
| A6 | conjectured recurrence from a **g.f. the entry states as fact** | 2,817 | **2,151 proved** — the largest vein found |
| A7 | conjectured recurrence from a **closed form stated as fact** | 442 | **running**, 41 so far |
| A8 | further conjectures on sequences already proved C-finite | 13,109 | **running**, 297 with new content |

## B. Engines written for name shapes nothing could read

| # | family | pool | status |
| --- | --- | ---: | --- |
| B1 | lexicographic subblock arrays | 37 | **done** |
| B2 | min-filter images of sorted arrays (`transfer95`) | 134 | **97 proved** |
| B3 | one-dimensional words under a window condition (`transfer96`) | 101 | **done** |
| B4 | cusp-form dimensions from the classical formula (`cuspdim`) | 51 | **46 proved** |
| B5 | elementary cellular automaton rows (`ecarow`) | 51 | **done**; 87 more are fractal and out of reach |
| B6 | derived arrays — indicators of a larger array's subblocks | 54 | **next engine**; `transfer26` has the right machinery |
| B7 | coordination sequences of tilings | 372 | **untried**; needs the tiling's structure |
| B8 | two-dimensional CA active-cell counts | 168 | **untried** |
| B9 | CA x-axis and diagonal representations | 294 | **untried**; same shape-certificate idea as B5 |
| B10 | permutations with bounded displacement | 35 | **untried**; a transfer matrix on window states |

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
| C8 | e.g.f. and Dirichlet g.f. claims | 19 | **untried** |

## D. Structural tricks that need no model at all

| # | idea | status |
| --- | --- | --- |
| D1 | premise from a formula the entry states as fact | **the biggest win of the project** (A6, A7) |
| D2 | premise from a proof this project already owns | A8 |
| D3 | closure under transforms — partial sums, differences, bisections | **measured, small**: 2,074 such entries, only 43 with an open conjecture, 12 usable |
| D4 | entries carrying both a known recurrence and a conjecture | 558, mostly already covered |
| D5 | equivalence between two entries the OEIS cross-references | **untried** |
| D6 | a conjecture on a table implying one on each of its columns | **untried** |

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

## F. Not yet attempted at all

* C4 inequalities, C5 primality, C6 always/never, C7 algebraic g.f.s, C8 e.g.f.s
* B6–B10 engines
* D5, D6
* 3,206 English-only conjectures on proved entries — mostly open research problems
  (Cramér's conjecture among them), not settleable here, and named so they are not mistaken
  for a gap
