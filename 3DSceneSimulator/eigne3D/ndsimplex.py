def type_check(self: object, other: object):
    """
        Check if the passed object has the same type as the current object.

        Args:
            self (object): The current object instance.
            other (object): The object to be checked.

        Raises:
            TypeError: If `other` is not an instance of the same type as `self`.
                       An error message indicating the expected type is included.

        """
    if not isinstance(other, type(self)):
        raise TypeError("Argument must be of type {}".format(type(self)))


def check_attar(self: object, other: str):
    """
        Check if the current object has a specified attribute.

        Args:
            self (object): The current object instance.
            other (str): The name of the attribute to be checked.

        Raises:
            AttributeError: If the current object does not have the specified attribute.
                            An error message indicating the missing attribute is included.

        """
    if not hasattr(self, other):
        raise AttributeError("Attribute '{}' does not exist in MyClass".format(other))


class TopologySimplex:
    obj_num = 0

    def __init__(self, dim: int):
        self.dim = dim
        for i in range(dim + 1):
            setattr(self, "s_" + str(i), None)
        TopologySimplex.obj_num += 1
        self.identity = str(self.obj_num)

    def get_subsimplex(self) -> list:
        ans = []
        for i in range(self.dim + 1):
            ans.append(getattr(self, "s_" + str(i)))
        return ans

    def set_simplex(self, index: int, other: object):
        if self.dim == 0:
            raise ValueError("Cannot add one sub simplex for 0-Simplex!")
        type_check(self, other)
        if other.dim != self.dim - 1:
            raise ValueError("Only able to add a %d-Simplex, but not %d-Simplex." % (self.dim - 1, other.dim))
        attr_name = "s_" + str(index)
        check_attar(self, attr_name)
        setattr(self, attr_name, other)

    def __str__(self):
        return "%d-Simplex id:%s" % (self.dim, self.identity)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.identity == other.identity
        else:
            return False


s2 = TopologySimplex(2)
s2.set_simplex(0, TopologySimplex(1))
print(s2.s_0)
s1 = TopologySimplex(1)
print(s2.get_subsimplex())