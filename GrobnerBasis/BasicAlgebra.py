from CommutativeRing import CommutativeRing, Domain

class Integer(Domain):
    def __init__(self, value:int=0):
        self.value = value

    def _addition(self, other):
        return Integer(self.value + other.value)

    def _equality(self, other):
        return self.value == other.value

    def _negative(self):
        return Integer(-1 * self.value)

    def _multiplication(self, other):
        return Integer(self.value * other.value)

    def _self_text(self) -> str:
        return str(self.value)

    def identity_element():
        return Integer(1)

    def zero_element():
        return Integer(0)

    def _divmod(self, other):
        other: Integer
        if other == self.zero_element():
            raise ZeroDivisionError("Cannot be divided by zerr.")
        return Integer(self.value // other.value), Integer(self.value % other.value)

    def _invertible(self) -> bool:
        return self == self.identity_element()

    def _true_div(self, other):
        return Integer(self.value // other.value)

    def __divmod__(self, other):
        return self._divmod(other)



if __name__ == '__main__':
    a = Integer(3)
    b = Integer(4)
    def cer_3(self):
        if self.value != 0:
            tmp = self.value
            while True:
                if tmp % 3 == 0:
                    tmp = tmp // 3
                else:
                    return tmp == 1

        else:
            return False

    print(Integer.zero_element(), Integer.identity_element())
    Int_3 = Integer.localization(Integer, cer_3, "_3")
    print(Int_3)
    # print(Int_3())
    # print(Int_3()+Int_3())
    # print(Int_3(1)/Int_3(3))
    # print(b // a)
