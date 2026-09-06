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


def norm_title(t):
    return re.sub(r'\s+', ' ', re.sub(r'A\d{6}', 'A', t)).strip()


def array(S, thr):
    s = "The empirical recurrence is true. Counting the arrays a row at a time gives a transfer matrix"
    if S:
        s += " with %s states" % f"{S:,}".replace(',', ' ')
    s += (", so a(n) satisfies a constant-coefficient linear recurrence of order at most that; "
          "checking the one above is then a finite exact computation")
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
    out, unhandled = {}, collections.Counter()
    live = collections.Counter(v['anum'] for v in json.load(open('paper-engines.json')).values())
    for a in sorted(live):
        if a in tex:
            continue
        if a in HAND:
            out[a] = [{'title': '(hand-written; the paper source is gone)',
                       'conjecture': None, 'S': None, 'thr': None, 'verify': st.get(a),
                       'hold': None, 'note': NOTE.get(a),
                       'comment': HAND[a] + SIG}]
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
