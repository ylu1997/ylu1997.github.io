class Monomial:
    def __init__(self, varlist=() ,ind=()):
        if len(varlist) != len(ind):
            raise ValueError("The length of variable list %d does"
                             " not match the length of degree list %d"
                             % (len(varlist),len(ind)))
        self.varlist = varlist
        self.ind = ind


    def degree(self) -> int:
        return sum(self.ind)

    def deepcopy(self):
        return Monomial(self.varlist, self.ind)

    def substitute(self, another):
        self.__type_check(another)
        self.ind = another.ind

    def __type_check(self, other):
        if type(other) != Monomial:
            raise TypeError("Must be Monomial.")
        if self.varlist != other.varlist:
            raise ValueError("The variable lists can not match.")

    def __mul__(self, other):
        self.__type_check(other)
        ans_ind = tuple([self.ind[i] + other.ind[i] for i in range(len(self.varlist))])
        return Monomial(self.varlist, ans_ind)

    def __rmul__(self, other):
        return self * other

    def __eq__(self, other):
        if other == None:
            return False
        self.__type_check(other)
        return (self.ind == other.ind)

    def __str__(self) -> str:
        s = ''
        for i,var in enumerate(self.varlist):
            if self.ind[i] != 0:
                s += var + "^{%d}" % self.ind[i]
        return s

    def __repr__(self):
        return str(self)

    def divisibility(self, other):
        self.__type_check(other)
        for i, ind in enumerate(self.ind):
            if other.ind[i] > ind:
                return False
        return True

    def __truediv__(self, other):
        self.__type_check(other)
        r_ind = []
        for i, ind in enumerate(self.ind):
            if other.ind[i] > ind:
                raise ValueError("Cannot be divided.")
            r_ind.append(ind-other.ind[i])
        r_ind = tuple(r_ind)
        return Monomial(self.varlist, r_ind)

    def GCD(self, other):
        self.__type_check(other)
        ind = tuple(min(ind, other.ind[i]) for i, ind in enumerate(self.ind))
        return Monomial(self.varlist, ind)

    def LCM(self, other):
        self.__type_check(other)
        ind = tuple(max(ind, other.ind[i]) for i, ind in enumerate(self.ind))
        return Monomial(self.varlist, ind)
