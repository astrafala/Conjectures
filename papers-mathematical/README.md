# The mathematical papers

These are the results whose proof is an argument, not a check.

The other 402 papers in `papers/` are real proofs and every one of them settles a
conjecture that was open — but each works the same way: take the generating
function the entry already posts, apply a decision procedure, read off the answer.
The mathematics in those lives in the engine, not in the paper. Written honestly,
each is a verification.

The ones here are different. Each needed an argument found for that problem.

## Thirty separate arguments

| file | entry | what it turns on |
|---|---|---|
| `1-PROOF.pdf` | A047926 | layer-cake counting of representations as three squares |
| `2-DISPROOF.pdf` | A008365 | counterexample, then the corrected characterisation |
| `3-PROOF.pdf` | A000040 | the structure of the multiplicative group mod a primorial |
| `5-DISPROOF.pdf` | A000040 | two counterexamples to a Fibonacci-Fermat primality test |
| `6-PROOF.pdf` | A059324 | a converse, not just the stated direction |
| `8-PROOF.pdf` | A061002 | shown equivalent to Wolstenholme's theorem |
| `9-PROOF.pdf` | A063305 | dimensions of newforms for a congruence subgroup |
| `10-PROOF.pdf` | A000071 | strong divisibility for F(k^n) - 1, k odd |
| `11-PROOF.pdf` | A000139 | parity via Legendre and Kummer |
| `12-DISPROOF.pdf` | A000364 | counterexample to a periodicity claim for the Euler numbers |
| `13-PROOF.pdf` | A059970 | nimbers: consecutive integers form an F_2-subspace |
| `14-PROOF.pdf` | A059970 | the same field structure, second cycle length |
| `15-PROOF.pdf` | A036284 | carry periodicity forces a large factor in GF(2)[X] |
| `16-PROOF.pdf` | A036284 | the extra factor, from a half-period flip |
| `17-PROOF.pdf` | A092287 | p-adic valuation of a rectangular product of gcds |
| `18-PROOF.pdf` | A129454 | a triple product, and an off-by-one in the posted statement |
| `19-PROOF.pdf` | A129365 | a closed form for the p-adic valuation, hence integrality |
| `21-PROOF.pdf` | A037096 | a bit that flips at half period |
| `22-PROOF.pdf` | A037097 | the half-window of the powers of 3 |
| `23-PROOF.pdf` | A087726 | square matrices that square to zero |
| `24-PROOF.pdf` | A063321 | a parity term traced to the level-4 cusp |
| `25-PROOF.pdf` | A063337 | newform dimensions for a second subgroup |
| `26-PROOF.pdf` | A005329 | one differential equation serving two transforms |
| `27-PROOF.pdf` | A129364 | a divisor of the gcd-product |
| `28-PROOF.pdf` | A062368 | multiplicativity: compare one local factor |
| `29-PROOF.pdf` | A358272 | the gcd-sum lemma, sum_{k<=n} f(gcd(k,n)) = (f * phi)(n) |
| `30-PROOF.pdf` | A358319 | the same lemma on a totient-like function |
| `31-PROOF.pdf` | A327123 | the same lemma, weighted by the character mod 4 |
| `329-PROOF.pdf` | A305404 | exchange of summation, justified by Tonelli, on a convergent series |
| `330-PROOF.pdf` | A352117 | the same exchange, and why the claim starts at n = 1 |

Papers 2, 5 and 12 are disproofs: the posted statement is false as written, and
each paper gives the counterexample and then the corrected version.

## One theorem, twenty entries

`32-PROOF.pdf` … `51-PROOF.pdf` — Bala's periodicity conjecture.

If a sequence has exponential generating function G(e^x - 1) with integer
coefficients, then a(n) mod m is eventually periodic with period dividing phi(m).
The proof writes a(n) = sum_k c_k k! S(n,k), notes that mod m every term with
k >= m dies because m divides k!, and expands k! S(n,k) = sum_j (-1)^(k-j) C(k,j) j^n
to leave an integer combination of j^n, whose period divides phi(m) by Euler.

That is one theorem, proved once and applied to twenty entries. It is counted as
twenty results because it settles twenty separate conjectures, but the argument is
shared and each paper says so.

## A middle tier, deliberately left out

Two of the engines carry real mathematical content in their lemmas — the algebraic
function field Q(x)[y]/(P(x,y)), closed under x d/dx because y' = -P_x/P_y can be
computed inside it; and creative telescoping, which derives a recurrence from a
sum with a certificate rather than checking a guess. Those lemmas are proved in
full in every paper that uses them. But the per-paper work is still a computation,
so they are not here. If you want them, they are the papers whose section 2 states
a lemma about Q(x)[y]/(P) or about telescoping.
