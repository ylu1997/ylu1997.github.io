import numpy as np


def batch_points_in_view(normals: np.ndarray, bias_points: np.ndarray, scene_points: np.ndarray) -> np.ndarray:
    """
    Check if scene_points are inside a polyhedron defined by normals and bias_points.
    :param normals: (batch_size1, position_xyz)
    :param bias_points: (batch_size1, position_xyz)
    :param scene_points: (batch_size2, position_xyz)
    :return: (batch_size2)
    """
    plane_num = normals.shape[0]
    point_num = scene_points.shape[0]
    new_normals = np.tile(normals[:, :, np.newaxis], point_num).transpose(0, 2, 1)
    new_bias = np.tile(bias_points[:, :, np.newaxis], point_num).transpose(0, 2, 1)
    new_points = np.tile(scene_points[:, :, np.newaxis], plane_num).transpose(2, 0, 1)
    X = new_points - new_bias
    X = new_normals * X
    X = X.sum(axis=2) >= 0
    X = np.prod(X, axis=0)
    return X


def frame_change(obj_point: np.ndarray, center: np.ndarray,
                 v1: np.ndarray, v2: np.ndarray, v3: np.ndarray) -> np.ndarray:
    """
    We consider the right-hand coordinate
    :param obj_point: [3] or [N, 3]
    :param center: [3]
    :param v1: first axis [3]
    :param v2: second axis [3]
    :param v3: third axis [3]
    :return: The coordinates of obj_point based on v1, v2, v3 at center. [3] or [N, 3]
    """
    frame_mat = np.array([v1,
                          v2,
                          v3])
    if np.linalg.det(frame_mat) == 0:
        raise ValueError("Not a correct frame.")
    vec = obj_point - center

    ans = frame_mat @ vec.T
    return ans.T


def tri_cone_equation(source: np.ndarray, p1: np.ndarray,
                      p2: np.ndarray, p3: np.ndarray) -> (np.ndarray, np.ndarray):
    """
    :param source: Vertex of the cone, shape = [3]
    :param p1: first ray of the cone, shape = [3]
    :param p2: second ray of the cone, shape = [3]
    :param p3: third ray of the cone, shape = [3]
    :return: (batch_normal_of_cone, batch_bias_of_cone), shape = ([3, 3], [3, 3])
    """

    r1 = p1 - source
    r2 = p2 - source
    r3 = p3 - source

    n1 = np.cross(r1, r2)
    n1 = np.inner(n1, r3) * n1
    n2 = np.cross(r2, r3)
    n2 = np.inner(n2, r1) * n2
    n3 = np.cross(r3, r1)
    n3 = np.inner(n3, r2) * n3

    bias_points = np.tile(source, 3).reshape(3, 3)

    return (np.array([n1, n2, n3]), bias_points)


def find_non_overlapping(source: np.ndarray, centers: np.ndarray, tri_points: np.ndarray) -> np.ndarray:
    """
    :param source: view point, shape = [3]
    :param centers: a group of point which are the centers of triangles, shape = [N, 3]
    :param tri_points: a group of the vertices of triangles, shape = [N, 3, 3]
    :return: [N, ]
    """
    ind_centers = np.insert(centers, 0, values=1, axis=1)
    r = -1
    while True:
        r += 1
        if r >= ind_centers.shape[0]:
            break
        if ind_centers[r, 0] == 0:
            continue
        normal, bias = tri_cone_equation(source, tri_points[r, 0, :],
                                         tri_points[r, 1, :], tri_points[r, 2, :])
        index = batch_points_in_view(normal, bias, centers)
        ind_centers[index == 1, 0] = 0
        ind_centers[r, 0] = 1

    return ind_centers[:, 0] == 1



# def spherical_to_cartesian(vec: np.ndarray) -> np.ndarray:
#     theta, varphi = vec[0], vec[1]
#     x = np.sin(theta) * np.cos(varphi)
#     y = np.sin(theta) * np.sin(varphi)
#     z = np.cos(theta)
#     return np.array([x, y, z])
#
#
# def cartesian_to_spherical(vec: np.ndarray) -> np.ndarray:
#     x, y, z = vec[0], vec[1], vec[2]
#     r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
#     theta = np.arccos(z / r)
#     varphi = np.arctan2(y, x)
#     return np.array([theta, varphi])
#
# def vector_normalization(vec: np.ndarray) -> np.ndarray:
#     return vec / np.linalg.norm(vec)

if __name__ == '__main__':
    # b1 = 4
    # b2 = 5
    #
    # N = np.random.random([b1, 3])
    # alpah = np.random.random([b1, 3])
    # s_point = np.random.random([b2, 3])
    #
    # batch_points_in_view(N, alpah, s_point)
    # print(np.random.random([3,5]))
    tri_cone_equation(np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1]))
    # z = frame_change(np.random.random([3]), np.random.random([3]), np.random.random([3]), np.random.random([3]), np.random.random([3]))
    # print(z.shape)

    # find_overlap = True

    if False:
        # find overlapping
        N = 5
        s = np.array([0, 0, 0])
        c = np.random.rand(N, 3) * 2
        v = np.random.rand(N, 3, 3) * 1
        print(c, v)
        print(find_non_overlapping(s, c, v))

    if False:
        vector = np.array([1, 2, 3])
        vectors = np.array([[1, -1, 2],
                            [2, 3, 4],
                            [-1, -2, -3]])
        print(np.dot(vector, vectors))

    pass
