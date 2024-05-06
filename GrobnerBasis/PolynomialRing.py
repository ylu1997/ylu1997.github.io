from Field import Rational
from utils_func import source_ring_check, type_check

def lex_ord(v1, v2):
    for i in range(len(v1)):
        if v1[i] - v2[i] > 0:
            return 1
        if v1[i] - v2[i] < 0:
            return -1
    return 0


def grlex_ord(v1, v2):
    if sum(v1) > sum(v2):
        return 1
    elif sum(v1) < sum(v2):
        return -1
    else:
        return lex_ord(v1, v2)

def grelex_ord(v1, v2):
    if sum(v1) > sum(v2):
        return 1
    elif sum(v1) < sum(v2):
        return -1
    else:
        for i in range(len(v1)):
            if v1[len(v1) - 1 - i] < v2[len(v1) - 1 - i]:
                return 1
            elif v1[len(v1) - 1 - i] > v2[len(v1) - 1 - i]:
                return -1
        return 0

def monomial_ordering(order_type='lex'):
    """
    :param v1: multi_degree1
    :param v2: multi_degree2
    :param order_type: ['lex', 'grlex', 'grelex']
    :return: -1 -> less; 0 -> equal; 1 -> larger
    """

    if order_type == 'lex':
        return lex_ord
    elif order_type == 'grlex':
        return grlex_ord
    elif order_type == 'grelex':
        return grelex_ord
    else:
        raise ValueError("Only these three order types are supported: ['lex', 'grlex', 'grelex']")


class Monomial:
    def __init__(self, multi_degree, base_ring=None):
        self.multi_degree = multi_degree
        self.base_ring: PolyAlg = base_ring

    def __mul__(self, other):
        type_check(other, Monomial)
        source_ring_check(other.base_ring, self.base_ring)
        return Monomial(tuple(self.multi_degree[i] + other.multi_degree[i]
                                      for i in range(len(self.multi_degree))), self.base_ring)

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        type_check(power, int)
        return  Monomial(tuple(item * power
                                   for item in self.multi_degree),
                             self.base_ring)

    def __str__(self):
        s = [self.base_ring.var_list[i] + "^{" + str(self.multi_degree[i]) + '}'
             for i in range(len(self.multi_degree))]
        return ''.join(s)

    def __eq__(self, other):
        type_check(other, Monomial)
        return self.multi_degree == other.multi_degree and self.base_ring == other.base_ring

    def __gt__(self, other):
        type_check(other, Monomial)
        ans = self.base_ring.ordering(self.multi_degree, other.multi_degree)
        return ans == 1

    def __lt__(self, other):
        type_check(other, Monomial)
        ans = self.base_ring.ordering(self.multi_degree, other.multi_degree)
        return ans == -1

    def __ge__(self, other):
        return (self == other) | (self > other)

    def __le__(self, other):
        return (self == other) | (self < other)

    @staticmethod
    def lcm(m1, m2):
        type_check(m1, Monomial)
        type_check(m2, Monomial)
        source_ring_check(m1.base_ring, m2.base_ring)
        multi_deg = tuple(max(m1.multi_degree[i], m2.multi_degree[i]) for i in range(len(m2.multi_degree)))
        return Monomial(multi_deg, m1.base_ring)

    def divisibility(self, other):
        type_check(other, Monomial)
        source_ring_check(self.base_ring, other.base_ring)
        mul_deg1 = self.multi_degree
        mul_deg2 = other.multi_degree
        for i in range(len(mul_deg1)):
            if mul_deg1[i] < mul_deg2[i]:
                return False
        return True

    def __floordiv__(self, other):
        type_check(other, Monomial)
        if self.divisibility(other):
            return Monomial(tuple(self.multi_degree[i] - other.multi_degree[i]
                           for i in range(len(self.multi_degree))), self.base_ring)
        else:
            raise ValueError(str(self) + " cannot be evenly divided by " + str(other))

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args):
        if len(args) != self.base_ring.deg_len:
            raise ValueError("Bad input.")
        ans = args[0] ** self.multi_degree[0]
        for i, deg in enumerate(self.multi_degree[1: ]):
            ans = ans * (args[i + 1] ** deg)
        return ans

class Term(Monomial):
    def __init__(self, coefficient, multi_degree, base_ring):
        super(Term, self).__init__(multi_degree, base_ring)
        self.coefficient = coefficient

    def __mul__(self, other):
        if isinstance(other, self.base_ring.basic_field):
            other = Term(other, tuple(0 for i in range(len(self.multi_degree))), self.base_ring)
        type_check(other, Term)
        source_ring_check(other.base_ring, self.base_ring)
        result = super(Term, self).__mul__(other)
        return Term(self.coefficient * other.coefficient, result.multi_degree, self.base_ring)

    def __add__(self, other):
        type_check(other, Term)
        source_ring_check(other.base_ring, self.base_ring)
        if self.multi_degree == other.multi_degree:
            return Term(self.coefficient + other.coefficient, self.multi_degree, self.base_ring)
        else:
            raise ValueError("Two terms must have same multi-degree.")

    def __neg__(self):
        return Term(-self.coefficient, self.multi_degree, self.base_ring)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        s = str(self.coefficient) + "*" + super(Term, self).__str__()
        return s

    def __eq__(self, other):
        type_check(other, Term)
        ans = super(Term, self).__eq__(other)
        return ans & (self.coefficient == other.coefficient)

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            ans = super(Term, self).__pow__(power)
            coefficient = self.coefficient ** power
            return  Term(coefficient, ans.multi_degree, ans.base_ring)
        else:
            raise TypeError("Power must be integer.")

    def __repr__(self):
        return self.__str__()

    def __truediv__(self, other):
        type_check(other, Term)
        tmp_ans = super(Term, self).__floordiv__(other)
        coe = self.coefficient / other.coefficient
        return Term(coe, tmp_ans.multi_degree, tmp_ans.base_ring)

    @staticmethod
    def zero(dim_degree, base_ring):
        return Term(base_ring.basic_field.zero(),
                    tuple(0 for i in range(dim_degree)),
                    base_ring)

    @staticmethod
    def identity(dim_degree, base_ring):
        return Term(base_ring.basic_field.identity(),
                    tuple(0 for i in range(dim_degree)),
                    base_ring)

    @staticmethod
    def from_monomial(m: Monomial):
        type_check(m, Monomial)
        return Term(m.base_ring.basic_field.identity(), m.multi_degree, m.base_ring)

    def in_mono_ideal(self, mono_ideal: list):
        for item in mono_ideal:
            if not self.divisibility(item):
                return False
        return True


    def formal_derivative(self, variable_index=[]) -> list:
        ans = []
        for i in range(len(self.multi_degree)):
            tmp = [i for i in self.multi_degree]
            if (i in variable_index) & (tmp[i] > 0):
                coe = self.base_ring.basic_field.from_int(tmp[i]) * self.coefficient
                tmp[i] = tmp[i] - 1
                term = Term(coe, tmp, self.base_ring)
                ans.append(term)
            else:
                ans.append(Term.zero(len(self.multi_degree),self.base_ring))
        return ans

class Polynomial:
    def __init__(self, base_ring, terms: list):
        self.base_ring = base_ring
        self.terms = terms

    @property
    def dim_degree(self):
        return len(self.terms[0].multi_degree)

    def __add__(self, other):
        if isinstance(other, Polynomial):
            index1 = 0
            index2 = 0
            ans = []
            zero_term = Term(self.base_ring.basic_field.zero(),
                                            tuple(0 for i in range(len(self.terms[0].multi_degree))),
                                            self.base_ring)
            while True:
                if len(ans) > 0:
                    if ans[-1] == zero_term:
                        ans.pop()
                if index1 < len(self.terms):
                    term1 = self.terms[index1]
                    if index2 < len(other.terms):
                        term2 = other.terms[index2]
                        if term1 > term2:
                            if term1.coefficient != self.base_ring.basic_field.zero() :
                                ans.append(term1)
                            index1 += 1
                        elif term1 < term2:
                            if term2.coefficient != self.base_ring.basic_field.zero():
                                ans.append(term2)
                            index2 += 1
                        else:
                            t = term1 + term2
                            if t.coefficient != self.base_ring.basic_field.zero():
                                ans.append(term1 + term2)
                            index1 += 1
                            index2 += 1
                    else:
                        if term1.coefficient != self.base_ring.basic_field.zero():
                            ans.append(term1)
                        index1 += 1
                else:
                    if index2 < len(other.terms):
                        term2 = other.terms[index2]
                        ans.append(term2)
                        index2 += 1
                    else:
                        if ans == []:
                            ans.append(zero_term)
                        return Polynomial(self.base_ring, ans)
        else:
            raise TypeError("Must be a polynomial.")

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        ans = []
        for item in self.terms:
            ans.append(-item)
        return Polynomial(self.base_ring, ans)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        type_check(other, Polynomial)
        ans = Term.zero(self.dim_degree, self.base_ring)
        ans = Polynomial(self.base_ring, [ans])
        for item in self.terms:
            tmp = [item * item2 for item2 in other.terms]
            ans = ans + Polynomial(self.base_ring, tmp)
        return ans

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        type_check(power, int)
        ans = Polynomial(self.base_ring, [Term.identity(self.dim_degree, self.base_ring)])
        base = self
        while power > 0:
            if power % 2 == 1:
                ans = ans * base
            base = base * base
            power = power // 2
        return ans

    def __str__(self):
        s = ''
        for item in self.terms:
            s = s + str(item) + '+'
        return s[:-1]

    def __eq__(self, other):
        type_check(other, Polynomial)
        if len(self.terms) != len(other.terms):
            return False
        else:
            for i, term in enumerate(self.terms):
                if other.terms[i] != term:
                    return False
            return True

    @property
    def LT(self):
        return self.terms[0]

    @property
    def LM(self):
        t = self.LT
        return Monomial(t.multi_degree, self.base_ring)

    @property
    def LC(self):
        return self.LT().coefficient

    def __divmod__(self, other):
        type_check(other, Polynomial)
        remainder = self
        quotient = Polynomial(self.base_ring, [Term.zero(self.dim_degree,
                                                         self.base_ring)])
        while True:

            if remainder.LM.divisibility(other.LM):
                q = Polynomial(self.base_ring,[remainder.LT / other.LT])
                remainder = remainder - (q * other)
                quotient = quotient + q
            else:
                break
        return quotient, remainder

    def __floordiv__(self, other):
        ans, _ = self.__divmod__(other)
        return ans

    def __mod__(self, other):
        _, ans = self.__divmod__(other)
        return ans

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_term(term: Term):
        type_check(term, Term)
        return Polynomial(term.base_ring, [term])

    @staticmethod
    def from_monomial(monomial: Monomial):
        type_check(monomial, Monomial)
        return Polynomial.from_term(Term.from_monomial(monomial))

    @staticmethod
    def syzygy_poly(p1, p2):
        type_check(p1, Polynomial)
        type_check(p2, Polynomial)
        lcm = Polynomial.from_monomial(Monomial.lcm(p1.LM, p2.LM))
        c1 = lcm // Polynomial.from_term(p1.LT)
        c2 = lcm // Polynomial.from_term(p2.LT)
        return c1 * p1 - c2 * p2


    def in_mono_ideal(self, mono_ideal: list):
        for term in self.terms:
            if not term.in_mono_ideal(mono_ideal):
                return False
        return True

    def normal_form(self, polys):
        _, ans = divmod(self, polys[0])
        for item in polys[1: ]:
            _, ans = divmod(ans, item)
        return ans

    def formal_derivative(self, variable_index=[]) -> list:
        ans = [Polynomial(self.base_ring,[poly])
               for poly in self.terms[0].formal_derivative(variable_index)]
        for term in self.terms[1:]:
            der_term = term.formal_derivative(variable_index)
            for i in range(len(ans)):
                ans[i] = ans[i] +  Polynomial(self.base_ring, [der_term[i]])
        return ans

    def __call__(self, *args):
        ans =  self.terms[0](*args)
        for item in self.terms[1: ]:
            ans = ans + item(*args)
        return ans

def G_criterion(i, j, polys, indices):
    for k in range(len(polys)):
        if ((min(i, k), max(i, k)) not in indices) & ((min(j, k), max(j, k)) not in indices):
            fi: Polynomial = polys[i]
            fj: Polynomial = polys[j]
            fk: Polynomial = polys[k]
            if Monomial.lcm(fi.LM, fj.LM).divisibility(fk.LM):
                return True
    return False


class PolyAlg:
    def __init__(self, var_list, basic_field:object=Rational, ordering=None):
        self.basic_field = basic_field
        self.var_list = var_list
        self.ordering = ordering

    @property
    def deg_len(self):
        return len(self.var_list)

    def get_monomial(self, multi_degree) -> Monomial:
        if len(multi_degree) != self.deg_len:
            raise ValueError(f"Expected tuple of size {len(self.var_list)}, got {len(multi_degree)}")
        return Monomial(multi_degree, self)

    def get_term(self, multi_degree, coefficient) -> Term:
        if len(multi_degree) != self.deg_len:
            raise ValueError(f"Expected tuple of multidegree {self.deg_len}, got {len(multi_degree)}")
        type_check(coefficient, self.basic_field)
        return Term(coefficient, multi_degree, self)

    def get_poly(self, multi_degree, coefficient) -> Polynomial:
        t = self.get_term(multi_degree, coefficient)
        return Polynomial(self, [t])

    def get_const(self, coefficient) -> Polynomial:
        t = self.get_term(tuple(0 for i in self.var_list), coefficient)
        return Polynomial(self, [t])

    def get_zero(self) -> Polynomial:
        return self.get_const(self.basic_field.zero())

    def __str__(self):
        s = ', '.join(self.var_list)
        return self.basic_field.__name__ + '[' + s + ']'

    @staticmethod
    def leading_term_element(poly_element):
        ans = []
        for item in poly_element:
            ans.append(item.LT)
        return ans

    @staticmethod
    def Groebner_Basis(polynomials: list):
        indices = [(i, j) for i in range(len(polynomials)) for j in range(i + 1, len(polynomials))]
        ans = [item for item in polynomials]
        s = len(polynomials) - 1
        p0: Polynomial = polynomials[0]
        p0: Term = p0.terms[0]
        num_deg = p0.base_ring.deg_len
        base_ring = p0.base_ring
        while True:
            print(len(indices))
            if indices == []:
                break
            i, j = indices[-1]
            fi: Polynomial = ans[i]
            fj: Polynomial = ans[j]
            c1 = ((Monomial.lcm(fi.LM, fj.LM)) != (fi.LM * fj.LM))
            # Criterion
            c2 = G_criterion(i, j, ans, indices)
            if c1 & (~c2):
                S = Polynomial.syzygy_poly(fi, fj).normal_form(ans)
                if S != Polynomial.from_term(Term.zero(num_deg, base_ring)):
                    s = s + 1
                    ans.append(S)
                    indices = indices + [(k, s) for k in range(s - 1)]
            indices.pop()

        # minimization and reduction, reduced Groebner is unique.
        i = 0
        N = len(ans)
        while True:
            if i >= N:
                break
            item: Polynomial = ans.pop()
            i += 1
            if item.normal_form(ans) != Polynomial.from_term(Term.zero(num_deg, base_ring)):
                for id_term, term in enumerate(item.terms):
                    if Polynomial.from_term(term).normal_form(ans) == Polynomial.from_term(Term.zero(num_deg, base_ring)):
                        item.terms.pop(id_term)
                ans = [item] + ans
        return ans

    def generators(self):
        ans = []
        for i in range(self.deg_len):
            ans.append(self.get_poly(tuple(1 if j == i else 0 for j in range(self.deg_len)), Rational(1)))
        return ans

class Homomorphism:
    def __init__(self, source_alg, target_alg, map_law):
        self.source_alg = source_alg
        self.target_alg = target_alg
        self.map_law = map_law

    def __call__(self, *args, **kwargs):
        pass

if __name__ == '__main__':
    # r1 = PolyAlg(('x', 'y', 'z'), ordering=monomial_ordering('lex'))
    # x = r1.get_poly((1,0,0),Rational(1))
    # y = r1.get_poly((0,1,0),Rational(1))
    # z = r1.get_poly((0,0,1),Rational(1))
    # print(x, y, z)
    # print(x ** 3 * (y - x ** 2) + (-(x ** 2)) * (z - x ** 3))

    # r = PolyAlg(('x', 'y'), ordering=monomial_ordering('lex'))
    # x = r.get_poly((1, 0), Rational(1))
    # y = r.get_poly((0, 1), Rational(1))
    # c = r.get_const(Rational(1))
    # f = x * (y ** 2) - x
    # f1 = x * y + c
    # f2 = y ** 2 - c
    # a1, r1 = divmod(f, f2)
    # a2, r2 = divmod(r1, f1)
    # print(a1, r1)
    # print(a2, r2)

    r = PolyAlg(('x','y','t_1', 't_2'), ordering=monomial_ordering('lex'))
    x = r.get_poly((1, 0, 0, 0), Rational(1))
    y = r.get_poly((0, 1, 0, 0), Rational(1))
    t1 = r.get_poly((0, 0, 1, 0), Rational(1))
    t2 = r.get_poly((0, 0, 0, 1), Rational(1))
    # print((x * y + y * z).formal_derivative([0,1,2]))
    f1 = x ** 2 * y - t1
    f2 = x * y - t2
    ans = r.Groebner_Basis([f1,f2])
    g = x ** 3 * y ** 2
    print(ans)
    print(g.normal_form(ans))

    # r = PolyAlg(('x'), Rational, ordering=monomial_ordering('lex'))
    # x = r.get_poly((1,), Rational(1))
    # print((x**2 + x).formal_derivative([0]))