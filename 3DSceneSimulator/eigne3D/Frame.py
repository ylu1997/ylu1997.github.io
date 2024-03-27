import numpy as np
from utils.utils import frame_change


class Frame:
    def __init__(self, center: np.ndarray, axis1: np.ndarray, axis2: np.ndarray, normal: np.ndarray):
        self.center = center
        self.axis1 = axis1
        self.axis2 = axis2
        self.normal = normal

    def relative_coord(self, p: np.ndarray, ) -> np.ndarray:
        """
        Converts coordinates to relative coordinates.
        :param p: shape=[N, 3]
        :return:  shape=[N, 3]
        """
        return frame_change(p, self.center, self.axis1, self.axis2, self.normal)

    def relativbe_sphere(self, p: np.ndarray[:, 3]) -> np.ndarray[:, 2]:  # spherical coordinate
        """
        Convert coordinates to relative spherical coordinates.
        :param p: shape=[N, 3]
        :return: shape=[N, 2]
        """
        ans: np.ndarray = self.relative_coord(p)
        r = np.sqrt(ans[:, 0] ** 2 + ans[:, 1] ** 2 + ans[:, 2] ** 2)
        theta = np.arccos(ans[:, 2] / r).reshape(-1, 1)
        varphi = np.arctan2(ans[:, 1], ans[:, 0]).reshape(-1, 1)
        ans = np.concatenate([theta, varphi], axis=1)
        return ans

    def orthogonality(self):
        ans = np.linalg.det(np.array([self.axis1, self.axis2, self.normal]))
        return ans != 0

    def __str__(self):
        s = ('Center: ' + str(self.center) + ';\n Axis1: ' + str(self.axis1) +
             ';\n Axis2: ' + str(self.axis2) + ';\n Normal: ' + str(self.normal))
        return s

    def translation(self, bias: np.ndarray) -> None:
        """
        :param bias: [3], move toward axis1, axis2, normal
        :return:
        """
        if any(np.zeros([3]) != bias):
            self.center = self.center + bias
            self.center = np.round(self.center, 3)

    def rotation(self, angles: np.ndarray) -> None:
        """
        :param angles: rotate along axis1, axis2, normal with center
        :return:
        """
        rotation = np.eye(3)
        a1, a2, a3 = angles[0], angles[1], angles[2]
        if a1 != 0:
            rotation = rotation @ np.array([[1, 0, 0],
                                            [0, np.cos(a1), -np.sin(a1)],
                                            [0, np.sin(a1), np.cos(a1)]])
        if a2 != 0:
            rotation = rotation @ np.array([[np.cos(a2), 0, np.sin(a2)],
                                            [0, 1, 0],
                                            [-np.sin(a2), 0, np.cos(a2)]])
        if a3 != 0:
            rotation = rotation @ np.array([[np.cos(a3), -np.sin(a3), 0],
                                            [np.sin(a3), np.cos(a3), 0],
                                            [0, 0, 1]])
        frame_array = np.array([self.axis1, self.axis2, self.normal])
        frame_array = (frame_array.T @ rotation).T
        frame_array = np.round(frame_array, 3)
        self.axis1 = frame_array[0]
        self.axis2 = frame_array[1]
        self.normal = frame_array[2]

    def transformation(self, translate: np.ndarray = np.zeros([3]), rotate: np.ndarray = np.zeros([3])):
        self.translation(translate)
        self.rotation(rotate)


if __name__ == '__main__':
    x = np.random.random([10, 3]) * 10
    frame = Frame(np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1]))
    # y = frame.relativbe_sphere(x)
    # print(y.shape)
    print(frame.orthogonality())
    frame.translation(np.array([0, 0, 0]))
    frame.rotation(np.array([np.pi / 2, 0, 0]))
