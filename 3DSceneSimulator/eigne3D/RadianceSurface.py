from eigne3D.RadianceField import RadTriangle, Point
import numpy as np
from abc import ABC, abstractmethod


class RadSurface(ABC):
    @abstractmethod
    def get_triangles(self):
        pass


class RadParallelogram(RadSurface):
    def __init__(self, p1: Point, p2: Point, p3: Point, absorb_rate: np.ndarray = np.array([1, 1, 1]),
                 rad_var: float = np.inf):
        self.t1 = RadTriangle(p1, p2, p3, absorb_rate, rad_var)
        p4 = Point.array_to_Point(p2.p + p3.p - p1.p)
        self.t2 = RadTriangle(p2, p4, p3, absorb_rate, rad_var)

    def get_triangles(self) -> list[RadTriangle]:
        return [self.t1, self.t2]


class RadPlane(RadSurface):
    def __init__(self, p1: Point, p2: Point, p3: Point, sample1: int, sample2: int,
                 absorb_rate: np.ndarray = np.array([1, 1, 1]),
                 rad_var: float = np.inf):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.sample1 = sample1
        self.sample2 = sample2
        self.rad_var = rad_var
        self.absorb_rate = absorb_rate
        self.triangle = []
        self.initiate_triangles()

    def initiate_triangles(self) -> None:
        O = self.p1.p
        v1 = (self.p2.p - self.p1.p) / self.sample1
        v2 = (self.p3.p - self.p1.p) / self.sample2
        points: list[list[Point]] = []
        for i in range(self.sample1 + 1):
            tmp: list[Point] = []
            for j in range(self.sample2 + 1):
                tmp.append(Point.array_to_Point(O + i * v1 + j * v2))
            points.append(tmp)
        for i in range(self.sample1):
            for j in range(self.sample2):
                self.triangle.append(RadTriangle(points[i][j], points[i + 1][j + 1], points[i][j + 1],
                                                 absorb_rate=self.absorb_rate, rad_var=self.rad_var))
                self.triangle.append(RadTriangle(points[i][j], points[i + 1][j], points[i + 1][j + 1],
                                                 absorb_rate=self.absorb_rate, rad_var=self.rad_var))

    def get_triangles(self) -> list[RadTriangle]:
        return self.triangle

if __name__ == '__main__':
    p = RadPlane(Point(0,0,0),Point(2,0,0), Point(0,2,0),2,3)
    for item in p.get_triangles():
        print(item.orientation)