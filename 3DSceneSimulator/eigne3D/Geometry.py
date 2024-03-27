import numpy as np
from utils.utils import (tri_cone_equation)
from eigne3D.Frame import Frame

class Point(object):
    def __init__(self, x=0, y=0, z=0):
        self.p = np.array([x, y, z], dtype=np.float32)

    @staticmethod
    def array_to_Point(arr: np.ndarray):
        return Point(arr[0], arr[1], arr[2])

    @property
    def x(self):
        return self.p[0]

    @property
    def y(self):
        return self.p[1]

    @property
    def z(self):
        return self.p[2]

    def __str__(self):
        return "Point(" + str(self.p) + ")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if type(other) != Point:
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z


class Vector(Point):
    def __init__(self, x=0, y=0, z=0):
        super(Vector, self).__init__(x, y, z)

    @staticmethod
    def Points_to_vector(p1: Point, p2: Point):
        """

        :param p1: Start
        :param p2: End
        :return:
        """
        return Vector.array_to_Vector(p2.p - p1.p)

    @staticmethod
    def array_to_Vector(arr):
        return Vector(arr[0], arr[1], arr[2])

    @staticmethod
    def __check_type(other):
        if type(other) != Vector:
            raise TypeError("Input wrong type. You should input " + str(Vector))

    def __add__(self, other):
        Vector.__check_type(other)
        return Vector.array_to_Vector(self.p + other.p)

    def __str__(self):
        return "Vector(" + str(self.p) + ")"

    def __neg__(self):
        return Vector.array_to_Vector(-self.p)

    def __mul__(self, other):
        return Vector.array_to_Vector(self.p * other)

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        return self.__str__()

    def __sub__(self, other):
        Vector.__check_type(other)
        return self + (-other)

    def norm(self):
        return np.linalg.norm(self.p)

    def normalized(self):
        return Vector.array_to_Vector(self.p / self.norm())

    @staticmethod
    def dot(v1, v2) -> float:
        Vector.__check_type(v1)
        Vector.__check_type(v2)
        return np.inner(v1.p, v2.p)

    @staticmethod
    def wedge(v1, v2):
        Vector.__check_type(v1)
        Vector.__check_type(v2)
        return Vector.array_to_Vector(np.cross(v1.p, v2.p))


class Triangle:
    def __init__(self, p1: Point, p2: Point, p3: Point):
        self.p1 = p1  # Start
        self.p2 = p2  # End 1
        self.p3 = p3  # End 2

    @property
    def axis1(self):
        return Vector.Points_to_vector(self.p1, self.p2)

    @property
    def axis2(self):
        return Vector.Points_to_vector(self.p1, self.p3)

    @property
    def orientation(self):
        v1 = self.axis1
        v2 = self.axis2
        v = Vector.wedge(v1, v2)
        return Vector.array_to_Vector(v.p)

    @property
    def center(self):
        return Point.array_to_Point(np.round((self.p1.p + self.p2.p + self.p3.p) / 3, 5))

    def __str__(self):
        return "Triangle(" + str(self.p3.p) + "->" + str(self.p1.p) + "->" + str(self.p2.p) + ")"

    def __repr__(self):
        return self.__str__()

    def to_batch_points(self) -> np.ndarray:
        ps = np.array([self.p1.p,
                       self.p2.p,
                       self.p3.p])
        return ps

    def __eq__(self, other):
        if type(other) != Triangle:
            return False
        return self.p1 == other.p1 and self.p2 == other.p2 and self.p3 == other.p3

    def tri_cone(self, source: Point) -> (np.ndarray, np.ndarray):
        return tri_cone_equation(source.p, self.p1.p, self.p2.p, self.p3.p)

    def export_frame(self) -> Frame:
        v2 = Vector.wedge(self.orientation, self.axis1)
        return Frame(self.center.p, self.axis1.p, v2.p, self.orientation.p)



class Cluster:
    def __init__(self):
        pass


if __name__ == '__main__':
    p1 = Point(1, 0, 0)
    p2 = Point(0, 1, 0)
    p3 = Point(0, 0, 0)
    t = Triangle(p3, p2, p1)
