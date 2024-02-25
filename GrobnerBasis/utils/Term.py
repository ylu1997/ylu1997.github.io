from utils.Monomial import Monomial
from utils.ListChain import Node

class Term(Node):
    def __init__(self, varlist=() ,ind=(), coe=1):
        super(Term, self).__init__()
        self.mono = Monomial(varlist, ind)
        self.coe = coe
        if coe == 0:
            self.ind = tuple(0 for i in range(len(varlist)))

    def __type_check(self, other):
        if type(other) != Term:
            raise TypeError("Must be Monomial.")
        if self.mono.varlist != other.mono.varlist:
            raise ValueError("The variable lists can not match.")

    @staticmethod
    def zero(varlist):
        return Term(varlist, tuple(0 for i in range(len(varlist))), 0)

    @staticmethod
    def mono_to_term(mono: Monomial):
        return Term(mono.varlist, mono.ind, 1)

    def __mul__(self, other):
        self.__type_check(other)
        m = self.mono * other.mono
        return Term(m.varlist, m.ind, self.coe * other.coe)

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        return str(self)

    def __truediv__(self, other):
        self.__type_check(other)
        m = self.mono / other.mono
        return Term(m.varlist, m.ind, self.coe / other.coe)

    def deepcopy(self):
        return Term(self.mono.varlist, self.mono.ind, self.coe)

    def __eq__(self, other):
        if type(other) != Term:
            return False
        else:
            return (self.mono == other.mono) and (self.coe == other.coe)

    def substitute(self, other):
        self.__type_check(other)
        self.coe = other.coe
        self.mono.substitute(other.mono)

    def degree(self):
        return self.mono.degree()

    def __str__(self):
        s = str(self.coe) + str(self.mono)
        return s

if __name__ == '__main__':
    varlist = ('x','y')
    print(Term(varlist, (1,2), 2))