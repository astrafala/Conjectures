#!/usr/bin/env python3
"""Generate a large, low-overlap query list for collecting recurrence conjectures.

OEIS caps a search at ~200 results without a login, so breadth has to come from
many distinct queries rather than deep pagination. We cross the recurrence marker
with a wide vocabulary drawn from OEIS entry names.
"""
ORDERS = ["a(n-2)", "a(n-3)", "a(n-4)", "a(n-5)", "a(n-6)"]

WORDS = """
Catalan Motzkin Schroeder Narayana Fibonacci Lucas Pell Jacobsthal Delannoy
binomial trinomial central convolution transform Riordan array triangle diagonal
column row partitions compositions permutations involutions derangements trees
forests paths walks lattice Dyck ballot bridges meanders necklaces bracelets
polyominoes animals graphs digraphs matchings tilings dissections polygons
generating expansion coefficients series product quotient reversion inverse
sums differences bisection trisection interleaved alternating signed weighted
labeled unlabeled rooted planar cyclic linear ordered increasing decreasing
avoiding containing pattern statistic height width depth peaks valleys returns
ascents descents runs blocks parts summands divisors primes squarefree powers
factorial subfactorial hypergeometric Bessel Legendre Chebyshev Hermite Laguerre
Bernoulli Euler Stirling Bell Genocchi Fubini Eulerian secondary structures RNA
staircase skew shifted Hankel determinant continued fraction algebraic

Somos Padovan Perrin Tribonacci Tetranacci Leonardo Pillai Thue Rudin Shapiro
Beatty Stern Calkin Wilf Sierpinski Pascal Gould Vandermonde Abel Touchard
Dobinski Ramanujan Rogers Gauss Jacobi theta modular eta elliptic Weierstrass
Apery Domb Franel Delannoy Whitney Tutte chromatic matching independence
clique cover flow spanning Laplacian adjacency incidence circulant Cayley
semigroup monoid lattice poset chain antichain Boolean simplicial complex
Coxeter Weyl root nilpotent solvable abelian dihedral symmetric alternating
knots links braids tangles genus embedding orientable surfaces maps
codes weights Hamming Gray Golay Reed binary ternary quaternary base radix
digits palindromes repunits automatic morphic substitution fixed point
queens rooks bishops knights chess board grid hexagonal triangular square
sandpile parking functions inversions major index descent statistic
Motzkin Riordan Fine Catalan Bessel Whittaker Kummer Pochhammer Gamma
""".split()


def queries():
    out = []
    for w in WORDS:
        out.append(f"Conjecture+a(n-3)+{w}")
        out.append(f"Conjecture+a(n-4)+{w}")
    for o in ORDERS:
        out.append(f"Conjecture+{o}+g.f.")
    seen, uniq = set(), []
    for q in out:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq


if __name__ == "__main__":
    qs = queries()
    print("\n".join(qs))
