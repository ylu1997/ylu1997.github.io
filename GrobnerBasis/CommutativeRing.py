from abc import ABC, abstractmethod, ABCMeta
from utils.Structure_Check import class_type_check


class CommutativeRing(ABC):
    @abstractmethod
    def _addition(self, other):
        """
        Abstract method for addition operation. Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _multiplication(self, other):
        """
        Abstract method for multiplication operation. Must be implemented in subclasses.
        """
        pass

    @staticmethod
    @abstractmethod
    def zero_element():
        """
        Abstract method to get the zero element. Must be implemented in subclasses.
        """
        pass

    @staticmethod
    @abstractmethod
    def identity_element():
        """
        Abstract method to get the identity element. Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _equality(self, other):
        """
        Abstract method for equality check. Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _negative(self):
        """
        Abstract method for negation operation. Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _self_text(self) -> str:
        """
        Abstract method to get the string representation of the instance. Must be implemented in subclasses.
        """
        pass

    def _cancel(self):
        pass

    @staticmethod
    def localization(CRingClass, criterion, tag=''):
        CRingClass: CommutativeRing
        class_name = "Local_" + CRingClass.__name__ + tag

        def init(self, numerator=CRingClass.zero_element(), denominator=CRingClass.identity_element()):
            self.numerator = numerator
            self.denominator = denominator
            if numerator == CRingClass.zero_element() and denominator == CRingClass.zero_element():
                raise ValueError("Numerator and denominator can not be both zero.")

        def addition(self, other):
            return SubClass(self.numerator * other.denominator + self.denominator * other.numerator,
                            self.numerator * other.denominator)

        def equality(self, other):
            return self.numerator * other.denominator == self.denominator * other.numerator

        def identity():
            return SubClass(CRingClass.identity_element(), CRingClass.identity_element())

        def zero():
            return SubClass(CRingClass.zero_element(), CRingClass.identity_element())

        def text(self):
            return str(self.numerator) + ":" + str(self.denominator)

        def multiplication(self, other):
            return SubClass(self.numerator * other.numerator, self.denominator * other.denominator)

        def negative(self):
            return SubClass(-self.numerator, self.denominator)

        def truediv(self, other):
            pass

        def div_mod(self, other):
            pass

        SubClass = type(class_name,
                        (CRingClass.__base__, ),
                        {'__init__': init,
                         '_addition': addition,
                         '_equality': equality,
                         '_invertible': criterion,
                         'identity_element': identity,
                         'zero_element': zero,
                         '_self_text': text,
                         '_multiplication': multiplication,
                         '_negative': negative,
                         '_divmod': div_mod,
                         '_true_div': truediv})

        print(SubClass.identity_element() * SubClass())
        return


    @staticmethod
    def quotient(CRing, equivalence):
        pass

    @staticmethod
    def tensor_product(CRing1, CRing2):
        pass

    @staticmethod
    def direct_sum(CRing1, CRing2):
        pass

    @staticmethod
    def extension(CRing, *extenders):
        pass

    @staticmethod
    def competition(CRing):
        pass

    @class_type_check
    def __eq__(self, other):
        """
        Checks if two CommutativeRing instances are equal.
        """
        return self._equality(other)

    @class_type_check
    def __add__(self, other):
        """
        Performs addition operation between two CommutativeRing instances.
        """
        ans = self._addition(other)
        ans: CommutativeRing
        ans._cancel()
        return ans

    def __radd__(self, other):
        """
        Performs reverse addition operation.
        """
        return self + other

    @class_type_check
    def __mul__(self, other):
        """
        Performs multiplication operation between two CommutativeRing instances.
        """
        ans = self._multiplication(other)
        ans: CommutativeRing
        ans._cancel()
        return ans

    def __rmul__(self, other):
        """
        Performs reverse multiplication operation.
        """
        return self * other

    def __neg__(self):
        """
        Performs negation operation.
        """
        return self._negative()

    def __str__(self):
        """
        Returns a string representation of the CommutativeRing instance.
        """
        return str(type(self).__name__) + "(" + self._self_text() + ")"

    def __repr__(self):
        """
        Returns a string representation of the CommutativeRing instance.
        """
        return self.__str__()

    def _inversible(self) -> bool:
        """
        Abstract method to check if the instance is invertible. Must be implemented in subclasses.
        """
        pass

    def _true_div(self, other):
        pass

    @class_type_check
    def __truediv__(self, other):
        """
        Performs true division operation.
        """
        other: CommutativeRing
        if not other._invertible():
            raise ZeroDivisionError("Element %s is not invertible" % (str(other)))
        ans = self._true_div(other)
        ans: CommutativeRing
        ans._cancel()
        return ans

class Domain(CommutativeRing):
    @abstractmethod
    def _invertible(self) -> bool:
        """
        Abstract method to check if the instance is invertible. Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _true_div(self, other):
        """
        Abstract method for true division operation. Must be implemented in subclasses.
        """
        pass

    @abstractmethod
    def _divmod(self, other):
        """
        Abstract method for divmod operation. Must be implemented in subclasses.
        """
        pass

    @class_type_check
    def __divmod__(self, other):
        """
        Performs division and modulo operation between two Domain instances.
        """
        return self._divmod(other)

    def __mod__(self, other):
        """
        Performs modulo operation.
        """
        return self._divmod(other)[1]

    def __floordiv__(self, other):
        """
        Performs floor division operation.
        """
        return self.__divmod__(other)[0]


class Field(Domain):
    def _divisibility(self, other):
        """
        Checks if the input is divisible by zero element.
        """
        return other != Field.zero_element()

    def _inversible(self) -> bool:
        """
        Checks if the Field instance is invertible.
        """
        return self != Field.zero_element()

