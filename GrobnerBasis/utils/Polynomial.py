from utils.Monomial import Monomial
from utils.MonomialOrder import lexicographical_order
from utils.Term import Term

class Polynomial():
    def __init__(self, term: Term):
        self.varlist = term.mono.varlist
        self.initial = term

    @staticmethod
    def zero(varlist):
        return Polynomial(Term.zero(varlist))

    @staticmethod
    def term_to_poly(term: Term):
        return Polynomial(term)

    @staticmethod
    def mono_to_poly( mono: Monomial):
        return Polynomial.term_to_poly(Term.mono_to_term(mono))

    def __type_check(self, other):
        if type(other) != Polynomial:
            raise TypeError("Must be Polynomial.")
        if self.varlist != other.varlist:
            raise ValueError("The variable lists can not match.")

    def __add__(self, other):
        self.__type_check(other)
        initial = Term.zero(self.varlist)
        m1 = self.initial
        m2 = other.initial
        tail = initial

        while True:
            if m1 is not None:
                if m2 is not None:
                    tag = lexicographical_order(m1.mono.ind, m2.mono.ind)
                    if tag == 1:
                        m = m1.deepcopy()
                        m1 = m1.next
                    elif tag == -1:
                        m = m2.deepcopy()
                        m2 = m2.next
                    else:
                        m = Term(m1.mono.varlist, m1.mono.ind, m1.coe + m2.coe)
                        m1 = m1.next
                        m2 = m2.next
                else:
                    m = m1.deepcopy()
                    m1 = m1.next
            elif m2 is not None:
                m = m2.deepcopy()
                m2 = m2.next
            else:
                break
            if m.coe != 0:
                if tail.coe == 0:
                    tail.substitute(m)
                else:
                    tail.append_next(m)
                    tail = tail.next
        return Polynomial(initial)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        ans = self.deepcopy()
        def f(node):
            node.coe = node.coe * -1
        ans.initial.traverse(f)
        return ans

    def __mul__(self, other):
        self.__type_check(other)
        m2 = other.initial
        initial = Term.zero(self.varlist)
        ans = [Polynomial(initial)]
        def f(node):
            ans[0] = ans[0] + self.__mul_by_Mono(node)
        m2.traverse(f)
        return ans[0]

    def __rmul__(self, other):
        return self * other

    def __mul_by_Mono(self, m: Term):
        p = self.deepcopy()
        initial = p.initial
        def f(node):
            node.substitute(node * m)
        initial.traverse(f)
        return p

    def __sub__(self, other):
        return self + (-other)

    def deepcopy(self):
        initial = self.initial.deepcopy()
        tail = [initial]
        def f(node):
            tail[0].append_next(node.deepcopy())
            tail[0] = tail[0].next
        if self.initial.is_tail():
            return Polynomial(initial)
        else:
            self.initial.next.traverse(f)
            return Polynomial(initial)

    def __str__(self):
        s = ['']
        def f(node):
            s[0] += ('+' if str(node)[0] != '-' else '') + str(node)
        self.initial.traverse(f)
        s = s[0]
        if s[0] == '+':
            s = s[1:]
        return s

    def __divmod__(self, other):
        self.__type_check(other)
        divisor = other
        quotient = Polynomial(Term.zero(self.varlist))
        remainder = self
        while True:
            tag = lexicographical_order(remainder.initial.mono.ind, divisor.initial.mono.ind)
            if tag == 1 or tag == 0:
                if remainder.initial.mono.divisibility(divisor.initial.mono):
                    m = remainder.initial/divisor.initial
                    m = Polynomial(m)
                    remainder = remainder - m * divisor
                    quotient = quotient + m
                else:
                    break
            else:
                break
        return quotient, remainder

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        self.__type_check(other)
        mono1 = self.initial
        mono2 = other.initial
        while True:
            if mono1 == None and mono2 == None:
                break
            if mono1 == mono2:
                mono1 = mono1.next
                mono2 = mono2.next
            else:
                return False

        return True

if __name__ == '__main__':
    varlist = ('x','y')
    p = Polynomial(Term(varlist, (3, 0), 2)) + \
         Polynomial(Term(varlist, (2, 1), -1)) + \
         Polynomial(Term(varlist, (0, 3), 1)) + \
         Polynomial(Term(varlist, (0, 1), 3))
    q1 = Polynomial(Term(varlist, (2, 0), 1)) + \
         Polynomial(Term(varlist, (0, 2), 1)) + \
         Polynomial(Term(varlist, (0, 0), -1))
    q2 = Polynomial(Term(varlist, (1, 1), 1)) + \
         Polynomial(Term(varlist, (0, 0), -2))
    # print(p)
    # print(q1)
    # print(q2)
    xxx = Polynomial(Term(varlist, (1,0),2))
    #
    print(q1, xxx)
    print(xxx * q1)
    print(Polynomial.zero(varlist) == (q1-q1))