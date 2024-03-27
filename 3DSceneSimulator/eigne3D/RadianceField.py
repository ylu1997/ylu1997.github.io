import numpy as np
from eigne3D.Frame import Frame
from utils.utils import batch_points_in_view, find_non_overlapping
from eigne3D.Geometry import Triangle, Point


class RadianceField:
    # Radiate in the direction of the half-plane"
    def __init__(self, absorb_rate: np.ndarray = np.array([1., 1., 1.]),
                 rad_var: float = 1):
        self.rad_var = rad_var
        self.absorb_rate = absorb_rate

        # record the coordinates of the local frame
        self.emission_direction = np.ones([1, 3], np.float32)
        self.emission_energy = np.zeros([1, 3], np.float32)

    def reset(self) -> None:
        self.emission_direction = np.ones([1, 3], np.float32)
        self.emission_energy = np.zeros([1, 3], np.float32)

    def gaussian_emission(self, rel_coord: np.ndarray) -> np.ndarray:
        """
        radiate energy to a group of objects.
        :param rel_coord: a group of parameters about spherical coordinates which is target, shape=[M, 3]
        :return: final emission energy [M, 3]
        """
        M = rel_coord.shape[0]
        N = self.emission_direction.shape[0]
        zero_index = np.where(rel_coord[:, 2] < 0)[0]
        n1 = np.sum(rel_coord * rel_coord, axis=1).reshape(-1, 1)
        rel_coord = rel_coord.reshape(M, 1, 3) / n1
        n2 = np.sum(self.emission_direction * self.emission_direction, axis=1).reshape(-1, 1)
        rad_direct = (self.emission_direction / n2).reshape(1, N, 3)
        X = rel_coord - rad_direct
        X = 1 - np.sum(X * X, axis=2)
        result = np.exp(-X / self.rad_var).reshape(M, N, 1)
        energy = self.emission_energy.reshape(M, N, 3)
        result = np.mean(result * energy, axis=1)
        result[zero_index] = np.array([0, 0, 0])
        return result

    @staticmethod
    def in_view_check(frame: Frame, triangles_vertices: np.ndarray) -> np.ndarray:
        """
        :param frame:
        :param triangles_vertices: [batch_id, vertex_id, coordinate] -> [N, 3, 3]
        :return: the index if the corresponding triangular is available.
        """
        normal = frame.normal.reshape(1, 3)
        bias_point = frame.center.reshape(1, 3)
        vertices = triangles_vertices.reshape(-1, 3)
        ans = batch_points_in_view(normal, bias_point, vertices).reshape(-1, 3)
        result = np.prod(ans, axis=1) == 1
        return result

    @staticmethod
    def obstruct_check(frame: Frame, triangles_vertices: np.ndarray, orientations: np.ndarray) -> np.ndarray:
        """
        :param frame:
        :param triangles_vertices: [batch_id, vertex_id, coordinate], shape=[N, 3, 3]
        :param orientations: [batch_id, coordinate], shape=[N, 3, 3]
        :return: [N, ]
        """
        centers = np.mean(triangles_vertices, axis=1)
        towards = centers - frame.center

        is_towards = np.sum(towards * orientations, axis=1) < 0  # towards is 1 otherwise is 0
        is_obstruct = find_non_overlapping(frame.center, centers,
                                           triangles_vertices)  # non-obstruct is 1 otherwise is 0
        result = is_towards * is_obstruct
        return result

    def is_emission(self, frame: Frame, triangles_vertices: np.ndarray, orientations: np.ndarray) -> np.ndarray:
        ans = self.in_view_check(frame, triangles_vertices)
        in_view_index = np.where(ans)[0]
        triangles_vertices = triangles_vertices[in_view_index, :, :]
        orientations = orientations[in_view_index, :]
        un_obstruct = self.obstruct_check(frame, triangles_vertices, orientations)
        ans[in_view_index] = un_obstruct
        return ans

    def absorption(self, frame: Frame, sources: np.ndarray, energies: np.ndarray) -> None:
        """
        :param frame:
        :param sources: [N, 3]
        :param energies: [N, 3] energy of RGB
        :return:
        """
        rel_coord: np.ndarray[:, 3] = frame.relative_coord(sources)
        rel_coord[:, :2] = -rel_coord[:, :2]
        if sources.shape[0] != energies.shape[0]:
            raise ValueError("Different size of sources and energies.")
        self.emission_direction = np.concatenate([self.emission_direction, rel_coord], axis=0)
        self.emission_energy = np.concatenate([self.emission_energy, energies * self.absorb_rate.reshape(1, -1)],
                                              axis=0)


class RadTriangle(Triangle, RadianceField):
    def __init__(self, p1: Point, p2: Point, p3: Point, absorb_rate: np.ndarray = np.array([1, 1, 1]),
                 rad_var: float = 1):
        Triangle.__init__(self, p1, p2, p3)
        RadianceField.__init__(self, absorb_rate, rad_var)
        self.record_source: list[RadTriangle] = []

    def absorption(self, sources: np.ndarray, energies: np.ndarray, **kwargs) -> None:
        RadianceField.absorption(self, self.export_frame(),
                                 sources.reshape(-1, 3),
                                 energies.reshape(-1, 3))

    def is_emission(self, triangles_vertices: np.ndarray, orientations: np.ndarray, **kwargs) -> np.ndarray:
        """

        :param triangles_vertices: shape=[N, 3, 3] -> (batch_size, point_id, coordinate_id)
        :param orientations: shape=[N, 3] -> (batch_size, coordinate_id)
        :param kwargs: None
        :return: shape=[N, ] -> (index of which radiance triangles can receive this energy)
        """
        return RadianceField.is_emission(self, self.export_frame(), triangles_vertices, orientations)

    def gaussian_emission(self, coords: np.ndarray) -> np.ndarray:
        rel_coord = self.export_frame().relative_coord(coords)
        rel_coord = rel_coord.reshape(-1, 3)
        return super().gaussian_emission(rel_coord)


class RadSource(RadTriangle):
    def __init__(self, p1: Point, p2: Point, p3: Point, energy: np.ndarray):
        super().__init__(p1, p2, p3, rad_var=np.inf)
        source = self.export_frame().center + self.export_frame().normal
        self.emission_direction = np.concatenate([self.emission_direction, source.reshape(1, -1)], axis=0)
        self.emission_energy = np.concatenate([self.emission_energy, energy.reshape(1, -1)], axis=0)

    def absorption(self, sources: np.ndarray, energies: np.ndarray, **kwargs) -> None:
        raise AttributeError("RadSource doesn't have absorption() method.")


if __name__ == '__main__':
    x = np.array([0, 0, 1, 1])
    y = np.random.random([4, 2, 3])
    print(y)
    print(y[x == 1, :, :])
    exit()
    f1 = RadTriangle(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0))
    f1.absorption(np.array([[10, 0, 0]]), np.array([[24, 23, 1]]))
    print(f1.emission_energy, f1.emission_direction)
    print(f1.export_frame())
