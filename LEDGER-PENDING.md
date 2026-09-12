
## 12 September 2026 — a new engine, and two defects in what was already installed

### `latpoly`: fixed-length arrays over `-n..n` and `0..n`, counted as an Ehrhart quasi-polynomial

`ordpoly` counts fixed-length arrays whose condition is decided by the ORDER of the terms.
This is its arithmetic twin. The length is fixed, the alphabet grows, and the condition names
actual values — a sum, a difference, a residue, a pair totalling exactly `n`. Every such
condition in this family is a boolean combination of statements `sum c_i x_i + c n <> 0`,
which are HOMOGENEOUS in `(x, n)` jointly, so the admissible `x` at a given `n` are the
lattice points at height `n` in a finite union of rational cones in R^(L+1) and `a(n)` is
their Ehrhart quasi-polynomial.

The period was the whole difficulty and it is DERIVED, never assumed. Each ray of each cell is
cut out by `L` of the arrangement's hyperplanes; by Cramer its primitive generator's height
divides the determinant of their x-parts, and a ray that leaves the box bounds no cell of the
region and is dropped. With `T` the surviving heights,
`A(z) = prod_{d | some t in T} Phi_d(z)^(L+1)` annihilates `a` and `S = deg A`. Writing that as
`(z^P - 1)^(L+1)` with `P = lcm T` would be far larger: for seven elements with no two
neighbours equal, `P = 420` gives 3360 where the cyclotomic form gives 96. The numerator over
`A` has degree below `S`, so `a(0..S-1)` determine every later term and nothing is fitted.

**219 entries read, every one reproducing the entry's published data exactly, no mismatches.**
The readings were pinned by brute force against the published terms before the engine was
written, and the derived annihilator is tested on terms the model was not asked for: a bound
that is too small fails that test, which is why it is run.

Said plainly: where `T = {1}` the count is an ordinary polynomial in `n` and the result is
elementary once seen — the conjectured recurrence is `(1-x)^d` and the content is that the
degree is right. The substance of the vein is the cases with period above one, where the
naive "it is a polynomial" reading is false.

Refused on purpose and recorded: 12 names whose condition is NOT homogeneous ("no element
more than one greater than the previous", "adjacent elements differing by more than one").
Their region is a shifted polyhedron, whose counting function is quasi-polynomial only beyond
some `n_0`, and without a bound on `n_0` there is no proof.

### Defect: 461 installed papers described a model that is not a walk as a walk

`unibuild` writes the transfer-matrix paper — the condition is local to a window, the windows
are the vertices of a digraph, the arrays are its walks, Cayley–Hamilton bounds the work. That
is true of most engines here and false of seven: `cuspdim`, `ca2d`, `ecarow`, `ordpoly`,
`necklace`, `multiset` and now `latpoly`. Those results went to `unibuild` because
`build_new.py` dispatches by engine and they were not in its table, so 461 papers described a
digraph that does not exist — including one telling a reader that A063089, the dimension of a
space of cusp forms, is a walk count on eight vertices contributed by R. H. Hardin.

The mathematics behind every one of them was sound and no result is withdrawn. The sentence
describing it was not, and a paper may not say a false thing about the object its numbers came
from. `qpbuild.py` writes the model each of those engines actually has, and all 461 have been
regenerated and recompiled in place at their existing ranked paths.

`unibuild` also printed "contributed by R. H. Hardin" unconditionally. All but one of its
entries are Hardin's and carry his own `Empirical:` line; on A221783 the recurrence is Vaclav
Kotesovec's. It now reads the name off the conjecture line, and that paper was rebuilt.

### Defect: `necklace.py` assumed `S = k` for bracelets, and that is false

For a NECKLACE every orbit of a rotation has the same size, so Burnside's equation reduces to
`sum x_i = 0`, every determinant is 1, and the count is a polynomial of degree below `k`:
`S = k` is right. For a BRACELET a reflection of odd length fixes one bead and pairs the rest,
giving weights 1 and 2 and forcing `x_0 = -2(x_1 + ...)` to be even, so that term has PERIOD
TWO. The fifth difference of A208826 is `-36, 48, -60, ...` and never vanishes: `S = 5` was
not an annihilator bound at all.

The bound is now computed from the orbit sizes. Re-run under it, all seven results still hold
with threshold 0 — the residual test had demanded `S + order` vanishing values and that run
happened to exceed the true bound in every case — so nothing is withdrawn, but two papers
stated a bound that was false and have been rebuilt with the derived one.
