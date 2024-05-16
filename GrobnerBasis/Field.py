from utils_func import type_check


def gcd(a, b):
    if b == 0:
        a, b = b, a
    while b != 0:
        a, b = b, a % b
    return a


class Rational:
    def __init__(self, numerator:int=0, denominator:int=1):
        self.numerator = numerator
        self.denominator = denominator
        self.__reduce_by_equivalence()

        if denominator == 0:
            raise ZeroDivisionError("Denominator can not be zero!")

    def __add__(self, other):
        type_check(other, Rational)
        return Rational(other.numerator * self.denominator + self.numerator * other.denominator,
                        other.denominator * self.denominator)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return Rational(-self.numerator, self.denominator)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        type_check(other, Rational)
        return Rational(self.numerator * other.numerator, self.denominator * other.denominator)


    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        type_check(other, Rational)
        return self * (Rational(other.denominator, other.numerator))


    @staticmethod
    def identity():
        return Rational(1, 1)

    @staticmethod
    def zero():
        return Rational(0, 1)

    def __reduce_by_equivalence(self):
        coe = gcd(self.numerator, self.denominator)
        self.numerator = self.numerator // coe
        self.denominator = self.denominator // coe

    def __str__(self):
        return "Rational(" + str(self.numerator) + ': ' + str(self.denominator) + ")"

    def clone(self):
        return Rational(self.numerator, self.denominator)

    def __pow__(self, power, modulo=None):
        type_check(power, int)
        if power < 0:
            base = Rational(self.denominator, self.numerator)
        else:
            base = Rational(self.numerator, self.denominator)
        power = abs(power)
        ans = Rational.identity()
        while power > 0:
            if power % 2 == 1:
                ans = ans * base
            base = base * base
            power = power // 2
        return ans

    def __eq__(self, other):
        type_check(other, Rational)
        return (self.denominator == other.denominator) & (self.numerator == other.numerator)

    @staticmethod
    def from_int(num):
        return Rational(num, 1)

if __name__ == '__main__':
    r = Rational(1, 2)
    r2 = Rational(5, 3)

    print(r + r)
    print(r*r2)
    print(divmod(5,2))