#!/usr/bin/env python3
"""One OEIS comment per PAPER, written plainly, keyed to what that paper actually proves.

The first draft keyed the wording to the roster's engine label, and that was wrong: the
label "quadratic" covers both the algebraic-generating-function recurrences and a dozen
bespoke number-theory results, so entries like A000071 (a strong divisibility conjecture)
came out described as a recurrence. The key here is the paper's own TITLE, and where one
title covers several routes, its abstract. Anything not covered by a template is left
without a draft rather than given a plausible-looking one.
"""
import json, re, collections

SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
SIG = " - _Adrian Perez Fontelles_, Sep 06 2026"

HAND = {
 'A000364': "This conjecture is false. The smallest counterexample is k = 27: phi(27) = 18, but a(1) = 1 and a(19) = 10 (mod 27), so 18 is not a period, and any period dividing 18 would make 18 one. It fails again for k = 54, 81, 108, 125, 135, 162, 189, 216, 243, 250, 270, 297 and 324 below 340. The prime case is true and is presumably what suggested it.",
 'A008365': "This is false as stated. The smallest counterexample is n = 17, itself a term of the sequence: 17^24 = 1681 (mod 2310). The image of n -> n^24 on the units mod 2310 has five elements, not four; adding the missing residue 1681 makes it correct, and then it is an equivalence. The exceptions are exactly the 13-rough n = 5 or 6 (mod 11).",
 'A197230': "This empirical recurrence is false. The entry publishes 22 terms with offset 1, so the recurrence first says something at n = 23, and it already fails there: the true value is 1327965802062332 and the recurrence gives 1327965802062198. The sequence is a transfer-matrix count, hence C-finite, and its true minimal recurrence has order 25; its first 22 coefficients are exactly the ones above, so the line is the correct recurrence with its last three terms dropped.",
 'A141135': "Both of these conjectures are false, and the entry's own terms refute them. The generating function reproduces a(1)..a(23) and then disagrees at n = 24, 27 and 30; the recurrence holds up to n = 23 and fails at n = 24 and again at n = 25.",
 'A076217': "This recurrence fails at n = 3^k, 3^k + 1 and 3^k + 2 for every k >= 2, so it fails infinitely often; the observation above that it seems to fail at powers of 3 is exactly right. It follows from a(n) = 1 precisely when n = 3^k - 2, which an induction on the entry's own defining recursion gives, and then the six values around each power of three can be written down.",
 'A129365': "Conjecture A is true, and more: for every prime p, ord_p(a(n)) = Sum_{i>=1} B(floor(n/p^i)) with B(M) = Sum_{k=1..M} (M mod k) = A004125(M). A sum of remainders is nonnegative, so every exponent is, which gives A; the formula is Conjecture D, and B and C follow from it as well. The proof is the known factorisation of the numerator, the identity floor(n/(k*p^i)) = floor(floor(n/p^i)/k) for the denominator, and M^2 - Sum_{k<=M} k*floor(M/k) = Sum_{k<=M} (M mod k).",
 'A092287': "The rectangle conjecture is true. For each prime p, v_p(gcd(j,k)) counts the i with p^i dividing both j and k, so summing over the rectangle and exchanging the order of summation gives ord_p(f(n,m)) = Sum_{i>=1} floor(n/p^i)*floor(m/p^i). The square case m = n is Bala's older conjecture, already confirmed above, and is the diagonal of this.",
 'A000071': "This is true. The sequence itself is not a strong divisibility sequence -- gcd(a(4), a(6)) = 1 while a(gcd(4,6)) = a(2) = 0 -- but restricting the index to a fixed odd geometric progression makes it one. For odd j, F(j) - 1 = F(E)*L(O), where E and O are the even and the odd member of the pair {(j-1)/2, (j+1)/2}; along j = k^n the two indices inherit the cyclotomic gcd structure of k^n -/+ 1, which is exactly what a strong divisibility sequence needs.",
 'A000139': "This is true. By Legendre's formula the parity of a(n) is decided by s(2n+1) + s(n+1) - s(3n) = 1 for the binary digit sum s; writing t for the number of trailing 1s of n and counting the carries in the binary addition n + 2n gives the identity exactly when n is an odd Fibbinary number.",
 'A005329': "This is true. Both sides are governed by a functional equation for an exponential generating function, and the substitution g = e^x f -- which is what taking the binomial transform does -- carries one equation into the other.",
 'A087726': "The converse holds too, so this is an equivalence. No formula for a(p^k) is needed: a is multiplicative with a(p) = p^2, so it is enough that a(p^k) > p^(2k) for k >= 2, and that follows from a lower bound, since every trace-zero X = [[a,b],[c,-a]] has X^2 = (a^2+bc)I.",
}

# The papers whose build directory is gone and whose statement no template covers: written out
# individually, from the entry's own words rather than the paper's rendered PDF -- reading a
# claim out of PDF text drops superscripts, which is how "k^n" once became "kn".
HAND2 = {
 'A000040-proof': "This is true, and it is the degenerate case of a general fact about power maps on a squarefree modulus: for P = p_1*...*p_k the image of the e-th power map on (Z/PZ)* is a subgroup of order Prod_i (p_i - 1)/gcd(e, p_i - 1), and membership in that image characterises coprimality to P. Detlefs' exponent f(n) = lcm(p_1-1, ..., p_n-1) makes that image trivial, which is what produces the clean congruence k^f(n) = 1 (mod P).",
 'A036284-1': "This is true. The whole content is that the carry into binary position n depends only on the low n bits of the two summands, so it has period 3*2^(n-1) -- exactly half the period of the column itself. Since x^(3*2^m) + 1 = (x^3 + 1)^(2^m) in characteristic 2, halving the period is the same as extracting a factor (x^3 + 1)^(2^(n-1)), and the conjectured exponent follows from a valuation count.",
 'A036284-2': "Conjecture 2 is true as well: (x^3 + 1)^(2^(n-1) - 1)*(x + 1) divides the n-th term, so the (x+1)-adic valuation is at least 2^(n-1). It is the same carry-periodicity identity that settles Conjecture 1, read on the factor x + 1 rather than on x^2 + x + 1; because x + 1 does not divide x^2 + x + 1, the cancellation that costs one power on the x^2 + x + 1 side does not happen here.",
 'A037096': "This is true, and the exponent is exact. It rests on one 2-adic fact: 3^(2^(n-2)) = 1 + 2^n (mod 2^(n+1)), so advancing k by a quarter of the window flips bit n. The window is then a block, its complement, the block, its complement, which factors as (x + 1)^(3q - 1) * (B(x)(x + 1) + x^q) with q = 2^(n-2), and 3q - 1 is exactly the conjectured exponent.",
 'A037097': "The corrected statement is true and the exponent is exact: a(n) = (x + 1)^(2^(n-2) - 1) * (B(x)(x + 1) + x^(2^(n-2))) for n >= 3, where B is the first quarter of the doubled window. It rests on 3^(2^(n-2)) = 1 + 2^n (mod 2^(n+1)), which complements bit n. The exponent as originally posted, 2^(n-1) - 1, was indeed too large -- already at n = 3 -- so the correction made on this entry was the right one.",
 'A047926': "This is true once an off-by-one in the indexing is corrected: for every k >= 1 the number of representations of 9^k as a^2 + b^2 + c^2 with 0 < a <= b <= c is (3^k + 2^k - 1)/4 = a(k-1), not a(k). More precisely, exactly k of them have two equal parts and (3^k - 2^k - 1)/4 have three distinct parts; none has three equal parts, and 9^k is never a sum of two positive squares. The argument deflates Pall's classical count r_3(9^k) = 6*(2*3^k - 1) to unordered positive triples, the two degenerate shapes being controlled by the divisor counts attached to x^2 + y^2 and x^2 + 2y^2, both of class number one.",
 'A059324': "This is true, and the sharper statement holds: such a pair (p, q) exists if and only if 6n + 5 is prime, and then it is unique in its first coordinate, namely p = 3 and q = 6n + 5. So this sequence is exactly the set of n >= 1 admitting no such pair. The reason is elementary: every prime p >= 5 has p^2 = 1 (mod 6), which forces 3 | q and hence q = 3, contradicting q > p^2.",
 'A059970-1': "This is true, and the following stronger statement is what the proof gives: for every n >= 0 the nim-product of ALL nonzero nimbers below 2^n equals 1. The conjecture is the special case, since {1, ..., 2^n - 1} is exactly that set. It is a short induction: {0, 1, ..., 2^n - 1} splits into additive cosets of the Conway field of order 2^(2^k), and on each the product collapses by Wilson's theorem for finite fields.",
 'A059970-2': "This is true. Two observations do it. The subspace polynomial of {0, ..., 2^t - 1} in the nimber field is the t-fold iterate of the Artin-Schreier map p(y) = y^2 + y (nim-addition), which identifies a(2^n + 2^(n-1) - 1) with the (n-1)-fold iterate applied to 2^n. That quantity then obeys two recursions -- one stripping the leading binary bit of n, one for n a power of 2 -- which together reduce every case to n = 1.",
 'A061002': "This is true, and it is a restatement of Wolstenholme's theorem rather than merely a consequence of it: the identity holds for a prime p exactly when p^2 divides the numerator of H_(p-1). Writing H_(p-1) = A/B in lowest terms, the two quantities in the quotient are exactly p*A and A/p^2, and the p^2 in the second is the whole content. The restriction p > 3 is therefore not cosmetic: at p = 2 and p = 3 the quotient is 2 and 9, not 8 and 27.",
 'A062368': "This is true. Both sides are multiplicative, so the statement is a single identity between local Dirichlet factors: the generating function of a(p^e) is (1 + 3x)/(1 - x)^4, which is exactly the local factor of 4^omega times three copies of zeta, and the identity is C(e+3,3) + 3*C(e+2,3) = (e+1)(e+2)(4e+3)/6.",
 'A063305': "This is true. The route is the classical dimension formula for S_k(Gamma_1(M)) together with the Atkin-Lehner-Li newform sieve; at N = 32 the sieve leaves a short explicit combination and gives dim S_k(Gamma_1(32))^new = 18k - 23 for k >= 2. There is no parity term, and the sieve says why: the level M = 4, the only one carrying a half-integer correction, does not survive at N = 32. Note also that the tabulated data is offset by one against the name.",
 'A063321': "This is true. By the dimension formula for S_k(Gamma_1(M)) with the Atkin-Lehner-Li sieve, dim S_k(Gamma_1(48))^new = 27k - 31 for k even and 27k - 32 for k odd. The parity term is not an accident: among the levels surviving the sieve, M = 4 is the only one carrying the correction +1/2 at odd k, and that is where it comes from.",
 'A063337': "This is true. By the dimension formula with the Atkin-Lehner-Li sieve, dim S_k(Gamma_1(64))^new = 72k - 83 for k >= 2. As at level 32 there is no parity term, because M = 4 -- the only level carrying a half-integer correction -- does not survive the sieve at N = 64. Note also that the tabulated data is offset by one against the name.",
 'A129364': "This is true, in the sharp form v_p(G(n)) - v_p(d(n)) = Sum_{i>=1} B(floor(n/p^i)) for every prime p, where d(n) = A092287(n), G(n) = a(n), and B(M) = Sum_{k=1..M} (M mod k) is A004125. Every term on the right is a sum of remainders, hence nonnegative, and the divisibility follows at once. The ingredients are the layer-cake count for v_p(G(n)), Legendre's formula with the nested-floor identity for v_p(d(n)), and M^2 - Sum_{k<=M} k*floor(M/k) = Sum_{k<=M} (M mod k).",
 'A129454': "As literally indexed this conjecture is false. The smallest counterexample is n = 4, p = 2: the posted formula gives exponent 9 while the truth is 1, and indeed a(4) = 6. The formula appears to have been transplanted from A092287, whose products run to n rather than n - 1, without adjusting the upper limit. With n replaced by n - 1 it is exactly right: ord_p(a(n)) = Sum_{t>=1} floor((n-1)/p^t)^3, by the counting argument that also gives Legendre's formula.",
 'A305404': "This is true. The argument does not manipulate the sequence at all: form the exponential generating function of the right-hand side and exchange the order of summation. The inner sum is then the central binomial series Sum_k C(2k,k) z^k = (1 - 4z)^(-1/2) at z = e^x/6, and 1 - 4*e^x/6 cancels against the 3 - 2e^x, returning the entry's own generating function. The exchange is justified by absolute convergence on |x| < log(3/2), which is exactly the disc where the generating function is analytic.",
 'A327123': "This is true. The weight sin(d*Pi/2) is the non-principal Dirichlet character chi mod 4, and both sides are the convolution chi * phi: the conjectured side by grouping the summation range by gcd(k,n), the defining side by expanding the generating function as a geometric series. Separately, the multiplicative formula currently posted on this entry is false at every prime p = 1 (mod 4), first at n = 5, where it gives 1 against the entry's own a(5) = 5.",
 'A352117': "This is true for n > 0. Forming the exponential generating function of the right-hand side and exchanging the order of summation turns the inner sum into the central binomial series (1 - 4z)^(-1/2) at z = e^(2x)/8, and 1 - 4*e^(2x)/8 cancels against 2 - e^(2x). What is left over is the k = 0 term, which the summation range excludes, contributing the constant 1/sqrt(2); that affects only the coefficient of x^0, which is exactly why the conjecture has to be stated for n > 0.",
 'A358272': "This is true, and elementary. Group the k in {1, ..., n} by the value of gcd(k,n): any sum of that shape becomes a Dirichlet convolution with Euler's totient, and evaluating the resulting local factor at a prime power is a two-line alternating sum that collapses according to the parity of the exponent.",
 'A358319': "This is true, and elementary. Grouping the summation range by gcd(k,n) converts the sum into a Dirichlet convolution with Euler's totient; at a prime power all but two of the terms are equal and collapse into a single multiple of p^e - p^(e-1).",
}

NOTE = {
 'A162548': "the entry adds 'Formula verified and used for computations - Fung Lam'; that reads as a numerical check rather than a proof, but read it before posting",
 'A185089': "the entry adds 'Formula verified and used for computations - Fung Lam'; that reads as a numerical check rather than a proof, but read it before posting",
 'A129365': "Conjectures B and C were given proofs in Aug 2026 (Adamczewski, arXiv:2608.11941, now linked on the entry); the draft claims A and D and only mentions that B and C follow",
 'A207747': "the empirical recurrence is Hardin's as corrected by Colin Barker",
 'A076217': "Bill McEachen already observed on the entry that it seems to fail at powers of 3; the draft credits that",
 'A092287': "Greathouse confirmed the SQUARE case in 2013; the open one is the rectangle",
}


REC = {}
CLAIMED = {}
OPEN_REC = {}
ENGOF = {}
WINOF = {}
H2BY = {}
MISS = {}


def norm_title(t):
    return re.sub(r'\s+', ' ', re.sub(r'A\d{6}', 'A', t)).strip()


ROWMAJOR = ("This is true. The array grows sideways, so it has to be counted a column at a "
            "time, but the clause about which value turns up first is stated in row major "
            "order, and a walk across columns does not read the cells in that order. What the "
            "walk can carry is, for each named value, the lowest row it has turned up in so "
            "far, together with the order those lowest rows were reached; the clause itself is "
            "checked only at the end, since a value's lowest row can still drop later. That "
            "makes a(n) a walk count on %s states, so it satisfies a constant-coefficient "
            "linear recurrence and checking the one above is a finite exact computation")


QUASI = ("This is true, and the closed form behind it is exact for every n. The shape of "
         "the triangle is fixed and it is the alphabet 0..n that grows, so this is not a walk "
         "count and no transfer matrix applies. Sum over the sets of adjacent pairs instead: a "
         "set of pairs forces the values along each of its connected components to alternate, "
         "so a bipartite component has n+1 choices (n for the target n+1) and a component with "
         "an odd cycle forces 2x = t, which is possible only for one parity of n. Inclusion-"
         "exclusion then gives a(n) = A(n) + (-1)^n C(n) with A and C explicit polynomials, "
         "and the recurrence above is exactly (E-1)^(deg A+1) (E+1)^(deg C+1) applied to that, "
         "so it holds for every n. The two n mod 2 formulas on this entry are the same "
         "statement read at each parity, and are exact as well")


BOXPP = ("The empirical formula is true. Reverse the rows and the columns: a matrix over "
         "0..n that is nondecreasing along rows and down columns becomes one that is "
         "nonincreasing, which is exactly a plane partition with parts at most n inside a "
         "P X Q rectangle -- so a(n) counts the plane partitions in a P X Q X n box, which is "
         "the formula already noted on this entry. That triple product telescopes in its third "
         "index, leaving a(n) = Product_{i=1..P} Product_{j=1..Q} (n+i+j-1)/(i+j-1), a "
         "polynomial in n of degree P*Q. Clearing the denominator of the empirical expression "
         "then turns it into an identity between two polynomials whose degrees are bounded by "
         "inspection, so checking it at that many points settles it")


BOUNDED = ("This is true, and it is exact rather than eventual guesswork. The shape is fixed "
           "and it is the alphabet 0..n that grows, so this is not a walk count. The condition "
           "only ever compares two entries, so adding a constant to every entry keeps an array "
           "admissible: the arrays fall into translation classes, and a class whose largest and "
           "smallest entries differ by s contributes max(0, n+1-s) arrays with entries in "
           "0..n. There are finitely many classes, because any two cells are joined by a path "
           "of at most D edges and each edge moves the value by at most d, so no class has "
           "s > d*D. For n at least that bound every term is positive and a(n) is exactly "
           "linear, so computing a(n) at two points fixes it for good")


GFCONJ = ("The conjectured generating function is correct. Counting the arrays a row at a "
          "time gives a transfer matrix on %s states, and the generating function of a walk "
          "count is 1/det(I - xM) times a polynomial, so it is a ratio of two polynomials whose "
          "degrees are at most the number of states. The conjectured expression is another such "
          "ratio, of known degree, and two of them are equal as soon as enough coefficients "
          "agree: cross-multiplying leaves a polynomial whose degree is bounded, so it vanishes "
          "once that many coefficients match. %s were compared in exact arithmetic. It follows "
          "that a(n) satisfies the linear recurrence whose coefficients are read off the "
          "denominator, which this entry does not currently record")


def array(S, thr):
    s = "The empirical recurrence is true. Counting the arrays a row at a time gives a transfer matrix"
    if S:
        s += " with %s states" % f"{S:,}".replace(',', ' ')
    s += (", so a(n) satisfies a constant-coefficient linear recurrence of order at most that; "
          "checking the one above is then a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def canonical(S, thr):
    """The comment for the family counted up to renaming.

    The `array` wording would say only "counting the arrays a row at a time", which is
    exactly the half of the model that is easy. The point worth putting on the entry is the
    other half: the relabelling condition is not local, and one counter carries it.
    """
    s = ("The empirical recurrence is true. Counting the arrays a line at a time gives a "
         "transfer matrix: the subblock condition looks only at a bounded window of "
         "consecutive lines, and \"new values introduced in row major order\" -- which is "
         "not a condition on any window, since it counts colourings up to renaming -- enters "
         "only through how many values have been introduced so far, one extra integer in the "
         "state")
    if S:
        s += ". That gives %s states" % f"{S:,}".replace(',', ' ')
    s += (", so a(n) satisfies a constant-coefficient linear recurrence of order at most "
          "that; checking the one above is then a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def subblockcond(S, thr):
    s = ("The empirical recurrence is true. The condition is a condition on every subblock of "
         "a fixed size, so a bounded window of consecutive lines decides it, and counting the "
         "arrays a line at a time gives a transfer matrix")
    if S:
        s += " with %s states" % f"{S:,}".replace(',', ' ')
    s += (", so a(n) satisfies a constant-coefficient linear recurrence of order at most "
          "that; checking the one above is then a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def nbrcond(S, thr):
    s = ("The empirical recurrence is true. The condition names only cells one step apart, so "
         "three consecutive lines decide it on the middle one, and counting the arrays a line "
         "at a time gives a transfer matrix")
    if S:
        s += " with %s states" % f"{S:,}".replace(',', ' ')
    s += (", so a(n) satisfies a constant-coefficient linear recurrence of order at most "
          "that; checking the one above is then a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def coldom(S, thr):
    s = ("The empirical recurrence is true. \"In all rows\" quantifies over the whole array, "
         "so no bounded window decides it, but it is a conjunction of independent per-row "
         "facts: keep one bit per adjacent column pair, recording whether every row so far "
         "has put column j above column j-1. A row can only clear bits, and the array is "
         "admissible exactly when all are clear at the end. So the state is that bit mask "
         "alone")
    if S:
        s += ", giving %s states" % f"{S:,}".replace(',', ' ')
    s += (", however large the alphabet, and a(n) satisfies a constant-coefficient linear "
          "recurrence of order at most that; checking the one above is a finite exact "
          "computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def distrep(S, thr):
    s = ("The empirical recurrence is true. The condition ranges over the whole array but "
         "reaches only as far as the value itself, which the alphabet bounds, so carrying "
         "that many lines together with one bit per cell -- has this cell found its partner "
         "yet -- makes the count a walk count")
    if S:
        s += " on %s states" % f"{S:,}".replace(',', ' ')
    s += (". Hence a(n) satisfies a constant-coefficient linear recurrence of order at most "
          "that, and checking the one above is a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def localcond(S, thr):
    s = ("The empirical recurrence is true. The condition is carried by a bounded amount of "
         "state down the array -- a window of three consecutive lines where it names only "
         "cells one step apart, and otherwise a row sum together with one flag per adjacent "
         "column pair -- so counting the arrays a line at a time gives a transfer matrix")
    if S:
        s += " with %s states" % f"{S:,}".replace(',', ' ')
    s += (", and a(n) satisfies a constant-coefficient linear recurrence of order at most "
          "that; checking the one above is then a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def paritydiff(S, thr):
    s = ("The empirical recurrence is true. The condition is carried by a bounded amount of "
         "state down the array -- one bit per column where it asks for a parity reaching back "
         "to the top, and otherwise a window of three consecutive lines, since every cell it "
         "names lies one step away -- so counting the arrays a line at a time gives a "
         "transfer matrix")
    if S:
        s += " with %s states" % f"{S:,}".replace(',', ' ')
    s += (", and a(n) satisfies a constant-coefficient linear recurrence of order at most "
          "that; checking the one above is then a finite exact computation")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def fromgf(thr):
    s = ("The recurrence follows from the generating function this entry already states as "
         "fact: a recurrence with constant coefficients is exactly a denominator of the "
         "generating function, so the two are the same statement")
    return s + ((", and it holds for n > %d." % thr) if thr is not None else ".")


def table(thr, cols=None):
    if not cols:
        which = "The empirical column recurrences are true. "
    elif len(cols) == 1:
        which = "The empirical recurrence for column k = %d is true. " % cols[0]
    else:
        ks = ', '.join(str(k) for k in cols[:-1]) + ' and ' + str(cols[-1])
        which = "The empirical recurrences for columns k = %s are true. " % ks
    return (which + "Each column counts arrays of a fixed width, and counting those a row at a "
            "time gives a transfer matrix, so every column satisfies a constant-coefficient "
            "linear recurrence of order at most the number of states; checking the ones above "
            "is then a finite exact computation, and they hold.")


def closedform_walk(thr):
    s = ("The empirical closed form is correct. The count is a walk count in a finite graph, so "
         "it satisfies a constant-coefficient linear recurrence; the conjectured form satisfies "
         "the same one, and the two agree at enough consecutive indices to agree from then on")
    return s + ((", for n > %d." % thr) if thr is not None else ".")


def alg_gf(thr):
    s = ("Not only empirical: the generating function given above is algebraic, and a recurrence "
         "with polynomial coefficients is a differential operator applied to it")
    return s + ((". Reducing that operator leaves a polynomial of degree %d, so the recurrence "
                 "holds for n > %d." % (thr, thr)) if thr is not None else ".")


def module(thr):
    s = ("The e.g.f. above is not algebraic, but it lies in a finitely generated module over Q(x) "
         "spanned by powers of a logarithm times powers of an exponential, and that module is "
         "closed under differentiation, so a(n) is P-recursive. Reducing the conjectured operator "
         "inside it leaves a polynomial")
    return s + ((", and the recurrence holds for n > %d." % thr) if thr is not None else ".")


def hyper(thr):
    s = ("This follows from the closed form already on the entry. It is a sum of finitely many "
         "hypergeometric terms, so every shift quotient is a rational function of n and the "
         "recurrence collapses to one rational identity in n, which is true")
    return s + ((" for n > %d." % thr) if thr is not None else ".")


def ore(thr):
    s = ("This follows from the recurrence already stated on the entry, which is not labelled a "
         "conjecture: in the Ore algebra Q(n)[N], N the shift, the conjectured operator is a left "
         "multiple of that one, so it annihilates the sequence as well")
    return s + ((", for n > %d." % thr) if thr is not None else ".")


def extraction(thr):
    s = ("The entry posts no generating function, but its definition a(n) = [x^n] f(x)g(x)^n gives "
         "one: reading the extraction as a contour integral and summing the geometric series "
         "leaves a single integral whose only pole inside a small circle is the branch of "
         "x = t*g(x) through the origin, and the residue there is an algebraic function. The "
         "recurrence then follows from it")
    return s + ((", for n > %d." % thr) if thr is not None else ".")


PERIOD = ("This is true. Under t = e^x - 1 the entry's e.g.f. becomes an ordinary power series "
          "with integer coefficients; that integrality kills all but finitely many terms of the "
          "Stirling expansion of a(n) modulo k, and what is left is an integer combination of the "
          "sequences n -> j^n, each eventually periodic mod k with period dividing phi(k).")
GAUSS = ("This is true, for the sequence and for every shift of it. Under t = e^x - 1 the entry's "
         "e.g.f. becomes an ordinary power series with integer coefficients; the operator "
         "(1 + t) d/dt carries that property to every shift, and integrality then reduces a_i(n) "
         "mod p^r to an integer combination of the sequences n -> j^n, for which the Gauss "
         "congruences are classical.")
IDENT = ("This identity is true. Both sides have a generating function that the entries "
         "themselves record, and after clearing denominators the difference is identically zero, "
         "which is a finite polynomial check.")
CONGR = ("This congruence is not just empirical. The functional equation the entry states for the "
         "generating function determines the sequence, and reducing it modulo the modulus turns "
         "it into a recursion over finitely many residues; the claimed residue is invariant under "
         "that recursion, so it holds for every n.")
CLOSED_EQ = ("The conjectured closed form is correct. The entry states a generating function as "
             "fact; a linear recurrence with polynomial coefficients follows from it exactly, the "
             "conjectured form satisfies the same recurrence, and the two agree at enough "
             "consecutive indices to be equal from then on.")
GFPROOF = ("The conjectured generating function is correct: expanding it and the entry's own "
           "definition both give the same linear recurrence, and they agree at enough initial "
           "terms for that to settle it.")

PERM = ("The empirical recurrence is true. The count is a permanent: the cells are permuted and "
        "each one moves by one of the offsets the name lists. Number the cells in row-major "
        "order and let each choose its image; an offset moves a cell by a bounded number of "
        "places in that order, so all that has to be carried is which images inside a window of "
        "%s consecutive positions are already taken. That makes a(n) a walk count on %s states, "
        "hence C-finite of order at most that, and checking the recurrence above is a finite "
        "exact computation")

ARRAY_TITLES = {
 'The empirical recurrence for OEIS A, proved by transfer matrix',
 'The empirical recurrence for OEIS A, proved by a two-line transfer matrix',
 'The empirical recurrence for OEIS A, proved by counting patterns',
 'The empirical recurrence for OEIS A, proved by counting patterns with a budget',
 'The empirical recurrence for OEIS A, proved by a counting transfer matrix',
 'The empirical recurrence for OEIS A, proved by a one-dimensional reduction',
 'The empirical recurrence for OEIS A, proved by counting defective colourings',
 'The empirical recurrence for OEIS A, proved by splitting on the common sum',
}
RECOVER = ("The recurrence in the linked file is correct, and it is the one below. Counting "
           "the arrays a row at a time gives a transfer matrix with %s states, so a(n) "
           "satisfies a constant-coefficient linear recurrence of order at most that, and "
           "Berlekamp-Massey on exact terms returns the minimal one. Its order is %s, the "
           "order stated here, and so is the order of every tail. Any recurrence of that "
           "order the sequence satisfies therefore has the same characteristic polynomial, "
           "so it is this one.")
RECOVER_TAB = ("The recurrences in the linked file are correct. Column k counts arrays of a "
               "fixed width, so it is a walk count in a finite graph and satisfies a "
               "constant-coefficient linear recurrence; Berlekamp-Massey on exact terms "
               "returns the minimal one, its order is the order stated for that column, and "
               "so is the order of every tail, so any recurrence of that order is this one.")
ABS_PAT = [('algebraic-gf', r'quadratic extension|algebraic over|algebraic gener'),
           ('module', r'finitely generated module'),
           ('hypergeometric', r'hypergeometric'),
           ('ore', r'Ore algebra'),
           ('extraction', r'extraction|contour integral')]


def route(rec):
    s = open(rec['f'], errors='ignore').read()
    i = s.find('begin{abstract}')
    ab = ' '.join(s[i:i + 1400].split())
    for k, pat in ABS_PAT:
        if re.search(pat, ab):
            return k
    return None


def main():
    tex = json.load(open(SC + '/texfacts.json'))
    # build/ holds orphan builds that were never integrated; the roster is the authority
    pe = json.load(open('paper-engines.json'))
    keep = collections.Counter(v['anum'] for v in pe.values())
    tex = {a: v[:keep[a]] for a, v in tex.items() if keep.get(a)}
    st = json.load(open(SC + '/status.json'))
    REC.update(json.load(open('audit_recover.json')))
    # 259 papers have no build/ directory left, so no title to key on. For the algebraic
    # generating-function family the residual and its degree are recorded in rec-open.json,
    # which is all the wording needs; the rest are named individually below.
    for a, v in json.load(open('rec-open.json')).items():
        try:
            OPEN_REC[a] = int(v['degree'])
        except Exception:
            pass
    CLAIMED.update(json.load(open(SC + '/table_claimed.json')))
    for k, v in HAND2.items():
        H2BY.setdefault(k.split('-')[0], []).append(v)
    MISS.update(json.load(open(SC + '/missthr.json')))
    for v in json.load(open('paper-engines.json')).values():
        ENGOF[v['anum']] = v['engine']
    import transfer73
    import localentry as _LE
    for a, en in ENGOF.items():
        if en != 'array-permutation':
            continue
        try:
            q = transfer73.parse_name(_LE.get(a)['name'])
            lin = [d1 * q['W'] + d2 for d1, d2 in q['offs']]
            WINOF[a] = max(lin + [0]) - min(lin + [0]) + 1
        except Exception:
            pass
    out, unhandled = {}, collections.Counter()
    live = collections.Counter(v['anum'] for v in json.load(open('paper-engines.json')).values())
    for a in sorted(live):
        if a in tex:
            continue
        if a in HAND or a in H2BY:
            rows = []
            if a in HAND:
                rows.append(HAND[a])
            rows += H2BY.get(a, [])
            out[a] = [{'title': '(hand-written; the paper source is gone)',
                       'conjecture': None, 'S': None, 'thr': None, 'verify': st.get(a),
                       'hold': None, 'note': NOTE.get(a), 'comment': c + SIG} for c in rows]
            continue
        if a in MISS:
            # an ordinary recurrence or closed form whose build directory is gone; the
            # threshold is read from the paper's own theorem line
            rows = []
            for r in MISS[a]:
                t = r['title'].lower()
                if 'closed form' in t:
                    rows.append(CLOSED_EQ)
                elif 'recurrence' in t:
                    rows.append(alg_gf(r['thr']) if r['thr'] is not None else None)
                else:
                    rows.append(None)
            out[a] = [{'title': r['title'][:80], 'conjecture': None, 'S': None,
                       'thr': r['thr'], 'verify': st.get(a),
                       'hold': None if c else 'no draft: nothing records what this proves',
                       'note': NOTE.get(a), 'comment': (c + SIG) if c else None}
                      for r, c in zip(MISS[a], rows)]
            continue
        if a in OPEN_REC:
            out[a] = [{'title': '(build directory gone; residual recorded in rec-open.json)',
                       'conjecture': None, 'S': None, 'thr': OPEN_REC[a],
                       'verify': st.get(a), 'hold': None, 'note': None,
                       'comment': alg_gf(OPEN_REC[a]) + SIG}]
        else:
            out[a] = [{'title': '(no build directory and no recorded residual)',
                       'conjecture': None, 'S': None, 'thr': None, 'verify': st.get(a),
                       'hold': 'no draft: the paper source is gone and nothing records its '
                               'threshold', 'note': None, 'comment': None}]
    for a in sorted(tex):
        for rec in tex[a]:
            t, thr, S = norm_title(rec['title']), rec['thr'], rec['S']
            txt = why = None
            if a in HAND:
                txt = HAND[a]
            elif ENGOF.get(a) == 'array-permutation':
                # the title is the ordinary transfer-matrix one, but the object is not an array
                # count: these permute the CELLS, so the generic wording would be wrong
                txt = (PERM % (WINOF.get(a, 'a few'),
                               f"{S:,}".replace(',', ' ') if S else 'finitely many')
                       + ((' that holds for n > %d.' % thr) if thr is not None else '.'))
            elif t == ('The empirical recurrence for OEIS A, proved by carrying a row major '
                       'clause across columns'):
                txt = (ROWMAJOR % (f"{S:,}".replace(',', ' ') if S else 'finitely many')
                       + ((', and it holds for n > %d.' % thr) if thr is not None else '.'))
            elif t == ('The empirical recurrence for OEIS A, proved by an exact '
                       'quasi-polynomial'):
                txt = QUASI + '.'
            elif t == 'The conjectured generating function for OEIS A, proved':
                txt = (GFCONJ % (f"{S:,}".replace(',', ' ') if S else 'finitely many',
                                 'Enough coefficients')) + '.'
            elif ENGOF.get(a) == 'bounded-difference-triangle':
                txt = BOUNDED + '.'
            elif t == 'The empirical product formula for OEIS A, proved':
                txt = BOXPP + '.'
            elif t.startswith('Arrays counted up to renaming'):
                txt = canonical(S, thr)
            elif t.startswith('A condition on every subblock'):
                txt = subblockcond(S, thr)
            elif t.startswith('A condition on each element and its neighbours'):
                txt = nbrcond(S, thr)
            elif t.startswith('No column above the one before it'):
                txt = coldom(S, thr)
            elif t.startswith('A value repeated at its own distance'):
                txt = distrep(S, thr)
            elif t.startswith('A local condition on an array'):
                txt = localcond(S, thr)
            elif t.startswith('Parities, differences and neighbours'):
                txt = paritydiff(S, thr)
            elif t in ARRAY_TITLES:
                txt = array(S, thr)
            elif t == "The empirical recurrence for OEIS A, derived from the entry's generating function":
                txt = fromgf(thr)
            elif t == 'The empirical column recurrences for the table OEIS A':
                txt = table(thr, CLAIMED.get(a))
            elif t == 'The empirical closed form for OEIS A, proved':
                txt = closedform_walk(thr)
            elif t == 'The empirical recurrence for OEIS A: recovering a conjecture that is not written down':
                r = REC.get(a, {})
                txt = RECOVER % (f"{S:,}".replace(',', ' ') if S else r.get('S', 'finitely many'),
                                 r.get('settled_order', 'the one stated'))
            elif t == 'Recovering the unwritten recurrences of the table OEIS A':
                txt = RECOVER_TAB
            elif t == 'A proof of the conjectured recurrence for OEIS A':
                r = route(rec)
                txt = {'algebraic-gf': alg_gf, 'module': module, 'hypergeometric': hyper,
                       'ore': ore, 'extraction': extraction}.get(r, lambda x: None)(thr)
                if txt is None:
                    why = 'proof route not recognised'
            elif re.match(r'The reduction of OEIS A modulo \$?k', t) or t.startswith('Eventual periodicity'):
                txt = PERIOD
            elif t.startswith('The Gauss congruences'):
                txt = GAUSS
            elif ('identity' in t) or t.startswith('A bisection') or t.startswith('A quadrisection'):
                txt = IDENT
            elif re.match(r'The reduction of OEIS A modulo \$?\d', t) or t.startswith('Every term') or t.startswith('Every odd-indexed'):
                txt = CONGR
            elif t == 'A proof of the conjectured closed form for OEIS A':
                txt = CLOSED_EQ
            elif t == 'A proof of the conjectured generating function for OEIS A':
                txt = GFPROOF
            else:
                why = 'no template for this title'
                unhandled[t] += 1
            v = st.get(a)
            hold = why
            if hold is None and v in ('model too big to rebuild here',
                                      'symbolic engine, not re-derived',
                                      'claim is not a plain recurrence',
                                      None):
                hold = 'not re-verified in the September re-check: ' + v
            out.setdefault(a, []).append(
                {'title': rec['title'], 'conjecture': rec['quote'], 'S': S, 'thr': thr,
                 'verify': v, 'hold': hold, 'note': NOTE.get(a),
                 'comment': (txt + SIG) if txt else None})
    json.dump(out, open('oeis-comments.json', 'w'), indent=1, sort_keys=True)
    seen = set()
    with open('oeis-comments.txt', 'w') as fh:
        for a in sorted(out):
            for r in out[a]:
                key = (a, r['comment'])
                dup = ' [SAME TEXT AS ANOTHER PAPER ON THIS ENTRY]' if key in seen else ''
                seen.add(key)
                fh.write('%s  %s%s%s%s\n' % (
                    a, r['title'],
                    '\n    HOLD: ' + r['hold'] if r['hold'] else '',
                    '\n    NOTE: ' + r['note'] if r['note'] else '', dup))
                if r['conjecture']:
                    fh.write('    conjecture: %s\n' % r['conjecture'][:160])
                fh.write((r['comment'] or '    (no draft)') + '\n\n')
    n = sum(1 for v in out.values() for r in v if r['comment'])
    ready = sum(1 for v in out.values() for r in v if r['comment'] and not r['hold'])
    print('papers', sum(len(v) for v in out.values()), 'drafted', n, 'ready', ready)
    for t, k in unhandled.most_common():
        print('  no template: %-70s %d' % (t[:70], k))


if __name__ == '__main__':
    main()
