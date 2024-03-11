import numpy as np
from utils.utils import frame_change, batch_points_in_view, tri_cone_equation, find_non_overlapping
from math import comb

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
    def __init__(self, p1: Point, p2: Point, p3: Point, control_points: np.ndarray=np.array([[0,0,0],[1,1,1]])):
        self.p1 = p1 # Start
        self.p2 = p2 # End 1
        self.p3 = p3 # End 2
        self.radiance_field = Radiance_Field(control_points)

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
        return Point.array_to_Point((self.p1.p + self.p2.p + self.p3.p) / 3)

    def __str__(self):
        return "Triangle(" + str(self.p3.p) + "->" + str(self.p1.p) + "->" + str(self.p2.p) +")"

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

    def export_frame(self):
        axis2 = Vector.wedge(self.orientation, self.axis1)
        return Frame(self.center, self.axis1.normalized(), axis2, self.orientation.normalized())

    def tri_cone(self, source: Point) -> (np.ndarray, np.ndarray):
        return tri_cone_equation(source.p, self.p1.p, self.p2.p, self.p3.p)

class Frame:
    def __init__(self, center: Point, axis1: Vector, axis2: Vector, normal: Vector):
        self.center = center
        self.axis1 = axis1
        self.axis2 = axis2
        self.normal = normal

    def relative_coord(self, p: Point,) -> Point:
        return Point.array_to_Point(frame_change(p.p, self.center.p,
                                                 self.axis1.p, self.axis2.p, self.normal.p))

    def __str__(self):
        s = ('Center: ' + str(self.center) + ';\n Axis1: ' + str(self.axis1) +
             ';\n Axis2: ' + str(self.axis2) + ';\n Normal: ' + str(self.normal))
        return s

class Radiance_Field:
    # Radiate in the direction of the half-plane"

    def __init__(self,  control_points: np.ndarray):
        self.control_points = control_points

        # record the coordinates of the local frame
        self.emission_direction = np.zeros([0, 3], np.float32)
        self.emission_energy = np.zeros([0, 3], np.float32)


    def decay_rate(self, r:float) -> np.ndarray[3]:
        n = len(self.control_points) - 1
        result = np.zeros_like(self.control_points[0])

        for i, point in enumerate(self.control_points):
            result += point * comb(n, i) * ((1 - r) ** (n - i)) * (r ** i)
        return result


    def in_view_check(self, frame: Frame, triangles: list[Triangle]) -> list[Triangle]:
        normal = frame.normal.p.reshape(1, 3)
        bias_point = frame.center.p.reshape(1, 3)
        pts = np.concatenate([item.to_batch_points() for item in triangles])
        ans = batch_points_in_view(normal, bias_point, pts).reshape(-1, 3)
        ans = np.prod(ans, axis=1) == 1
        result = [triangles[i] for i in range(ans.shape[0]) if ans[i] and Vector.dot(frame.normal, triangles[i].orientation) < 0]
        return result

    def obstruct_check(self, frame: Frame, triangles: list[Triangle]) -> list[Triangle]:
        source = frame.center.p
        b_center = []
        b_vertices = []
        for i in range(len(triangles)):
            triangle = triangles[i]
            b_center.append(triangle.center.p)
            b_vertices.append(triangle.to_batch_points())
        b_center = np.array(b_center)
        b_vertices = np.array(b_vertices)
        index = find_non_overlapping(source, b_center, b_vertices)
        un_obstruct = [triangles[i] for i in range(len(index)) if index[i]]
        return un_obstruct

    def emission(self, frame: Frame, targets: list[Triangle]):
        in_view_tri = self.in_view_check(frame, targets)
        un_obstruct = self.obstruct_check(frame, in_view_tri)
        for tri in un_obstruct:
            rel_coord: Point = frame.relative_coord(tri.center) 



    def absorption(self, frame: Frame, rad_sources: Point, energy: np.ndarray):
        rel_coord: Point = frame.relative_coord(rad_sources)
        emission_vec = np.array([[-rel_coord.x, -rel_coord.y, rel_coord.z]])
        self.emission_direction = np.concatenate([self.emission_direction, emission_vec], axis=0)
        self.emission_energy = np.concatenate([self.emission_energy, energy], axis=0)


if __name__ == '__main__':

    p1 = Point(1,0,0)
    p2 = Point(0,1,0)
    p3 = Point(0,0,0)
    t = Triangle(p3, p2, p1)
    f = Radiance_Field([0,0,1])
    # f.in_view_check(t.export_frame(), [Triangle(Point(3,3,-5),Point(4,3,-1), Point(2, 2, -1)),
    #                                    Triangle(Point(3,3,0),Point(4,3,1), Point(2, 2, -1))])
    print(f.obstruct_check(Frame(Point(0,0,0),Vector(1,0,0),Vector(0,1,0), Vector(0,0,1)),
                     [Triangle(Point(2,-1,0),Point(2,0,-1),Point(2,1,0)),
                              Triangle(Point(3, -0.5,0),Point(3,0,-0.5), Point(3,0.4,0))]))

    # print(t.export_frame())