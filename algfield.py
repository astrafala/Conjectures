#!/usr/bin/env python3
"""Exact arithmetic in an arbitrary algebraic function field Q(x)[y]/(P(x,y)).

The quadratic and multiquadratic engines only reach generating functions written as
sums of independent square roots. A great many are not: nested radicals like
sqrt((1-4x-sqrt(1-8x-32x^2))/24), cube roots, and the very common OEIS style of giving
the generating function implicitly, "A(x) = 1 + x*A(x)^2". All of those live in a simple
algebraic extension of Q(x), and the residual test needs nothing more than that.

The field is closed under theta = x d/dx. Differentiating P(x,y)=0 gives

    y' = -P_x(x,y) / P_y(x,y),

where the quotient is taken in K itself, P_y being invertible because P is the minimal
polynomial and so squarefree in y. For u = sum_i c_i(x) y^i,

    theta(u) = x * ( sum_i c_i'(x) y^i  +  y' * sum_i i c_i(x) y^(i-1) ),

reduced modulo P. Every step is exact rational-function arithmetic, so the verdict
"the residual is a polynomial" is a proof, exactly as in the quadratic case.
"""
import sympy as sp

x, y = sp.symbols('x y')


def _cancel_poly(p):
    return sp.Poly([sp.cancel(c) for c in p.all_coeffs()], y) if p.all_coeffs() else sp.Poly(0, y)


class Field:
    def __init__(self, P):
        self.P = sp.Poly(sp.expand(P), y)
        self.d = self.P.degree()
        if self.d < 1:
            raise ValueError("minimal polynomial must have positive degree in y")
        self.dy = self._dydx()

    # --- ring operations -------------------------------------------------
    def red(self, p):
        p = p if isinstance(p, sp.Poly) else sp.Poly(sp.expand(p), y)
        _, r = sp.div(p, self.P, y)
        return _cancel_poly(r)

    def mul(self, a, b):
        return self.red(a.as_expr() * b.as_expr())

    def inv(self, a):
        """Inverse in K by the extended Euclidean algorithm in Q(x)[y]."""
        a = self.red(a)
        if a.is_zero:
            raise ZeroDivisionError("not invertible")
        g, s, _ = sp.gcdex(a, self.P, y) if False else (None, None, None)
        # sympy's gcdex over the fraction field: use half_gcdex on Poly
        r0, r1 = self.P, a
        s0, s1 = sp.Poly(0, y), sp.Poly(1, y)
        while not r1.is_zero:
            q, r = sp.div(r0, r1, y)
            r0, r1 = r1, _cancel_poly(r)
            s0, s1 = s1, _cancel_poly(s0 - q * s1)
        if r0.degree() > 0:
            raise ZeroDivisionError("P is not squarefree in y")
        c = r0.all_coeffs()[0]
        return _cancel_poly(sp.Poly([sp.cancel(t / c) for t in s0.all_coeffs()], y)
                            if s0.all_coeffs() else sp.Poly(0, y))

    # --- differentiation --------------------------------------------------
    def _dydx(self):
        Px = sp.Poly(sp.diff(self.P.as_expr(), x), y)
        Py = sp.Poly(sp.diff(self.P.as_expr(), y), y)
        return self.mul(_cancel_poly(sp.Poly(-Px.as_expr(), y)), self.inv(Py))

    def deriv(self, u):
        u = self.red(u)
        cs = u.all_coeffs()[::-1]                     # c_0 .. c_{deg}
        part_x = sp.Poly(sum(sp.diff(c, x) * y ** i for i, c in enumerate(cs)), y)
        part_y = sp.Poly(sum(i * c * y ** (i - 1) for i, c in enumerate(cs) if i), y)
        return self.red(part_x.as_expr() + self.mul(part_y, self.dy).as_expr())

    def theta(self, u):
        return self.red(x * self.deriv(u).as_expr())

    # --- the residual test ------------------------------------------------
    def apply_poly_theta(self, poly_in_n, u, shift, nsym):
        if sp.expand(poly_in_n) == 0:
            return sp.Poly(0, y)
        p = sp.Poly(sp.expand(poly_in_n), nsym)
        deg = p.degree() if p.total_degree() >= 0 else 0
        powers = [self.red(u)]
        for _ in range(deg):
            powers.append(self.theta(powers[-1]))
        out = sp.Poly(0, y)
        for (j,), c in zip(p.monoms(), p.coeffs()):
            term = sp.Poly(0, y)
            for i in range(j + 1):
                term = _cancel_poly(term + sp.binomial(j, i) * shift ** (j - i) * powers[i])
            out = _cancel_poly(out + c * term)
        return out

    def residual(self, u, ps, nsym):
        tot = sp.Poly(0, y)
        for i, p in enumerate(ps):
            if sp.expand(p) == 0:
                continue
            tot = _cancel_poly(tot + x ** i * self.apply_poly_theta(p, u, i, nsym))
        return _cancel_poly(tot)

    @staticmethod
    def is_polynomial(r):
        cs = r.all_coeffs()[::-1] if r.all_coeffs() else [sp.Integer(0)]
        for c in cs[1:]:
            if sp.cancel(c) != 0:
                return False, None
        c = sp.cancel(sp.together(cs[0]))
        num, den = sp.fraction(c)
        if not den.is_polynomial(x) or sp.Poly(den, x).total_degree() != 0:
            return False, None
        out = sp.expand(sp.cancel(c))
        if not out.is_polynomial(x) or (out.free_symbols - {x}):
            return False, None
        return True, out


def from_expr(expr, maxdeg=10):
    """Build the field and the element for an explicit algebraic expression."""
    P = sp.minimal_polynomial(expr, y, domain=sp.QQ.frac_field(x))
    P = sp.Poly(sp.expand(sp.together(P) * sp.denom(sp.together(P))), y)
    if P.degree() > maxdeg:
        return None, None
    F = Field(P.as_expr())
    return F, sp.Poly(y, y)
