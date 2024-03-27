import cv2
import numpy as np


def rasterization_triangle(img: np.ndarray, n_buffer: np.ndarray,
                           proj_points: np.ndarray[3, 3], energy: np.ndarray) -> None:
    """
    Input a data of triangle with relative coordinates, and draw the RGB data on screen matrix.
    :param img: RGB matrix
    :param n_buffer:  record the depth of each pixel.
    :param proj_points:  triangle vertices with relative coordinate,
            first 2 coordinates should fall in [-1, 1].
    :param energy: RGB energy.
    :return:
    """
    s_points =  np.argsort(proj_points[:, 1],)
    s_points = proj_points[s_points]

    w, h, _ = img.shape
    p1 = s_points[0, :]
    p2 = s_points[1, :]
    p3 = s_points[2, :]
    f1 = np.floor(p1)
    f2 = np.floor(p2)
    f3 = np.floor(p3)
    tmp_vec = np.cross(p2 - p1, p3 - p1)
    for i in range(int(f1[1]), int(f2[1])):
        if i >= 0 and i < h:
            start = np.floor((p2[0] - p1[0]) * (int(f1[1]) + (i-int(f1[1])) - p1[1]) / (p2[1] - p1[1]) + p1[0])
            end = np.floor((p3[0] - p1[0]) * (int(f1[1]) + (i-int(f1[1])) - p1[1]) / (p3[1] - p1[1]) + p1[0])
            start1, end1 = int(min(start, end)), int(max(start, end))
            for j in range(start1, end1):
                if j>=0 and j <w:
                    # buffer and draw
                    depth = ((np.array([j, i]) - p1[:2]) * tmp_vec[:2]).sum() / tmp_vec[2] + p1[2]
                    if depth < n_buffer[j,i]:
                        n_buffer[j, i] = depth if depth > 0 else np.inf
                        img[j, i, :] = energy
    for i in range(int(f2[1]), int(f3[1])):
        if i >= 0 and i < h:
            start = np.floor((p3[0] - p2[0]) * (int(f2[1]) + (i - int(f2[1])) - p2[1]) / (p3[1] - p2[1]) + p2[0])
            end = np.floor((p3[0] - p1[0]) * (int(f1[1]) + (i-int(f1[1])) - p1[1]) / (p3[1] - p1[1]) + p1[0])
            start1, end1 = int(min(start, end)), int(max(start, end))
            for j in range(start1, end1):
                if j>=0 and j < w:
                    depth = ((np.array([j, i]) - p1[:2]) * tmp_vec[:2]).sum() / tmp_vec[2] + p1[2]
                    if depth < n_buffer[j, i]:
                        n_buffer[j, i] = depth if depth > 0 else np.inf
                        img[j, i, :] = energy




if __name__ == '__main__':
    N, M = 400, 600
    img = np.zeros([N, M, 3])
    n_buffer1 = np.full((N, M), np.inf)

    # for i in range(4):
    #     relpoints = np.random.random([3,3]) * np.array([N, M, 100]).reshape(1, -1)
    #     relpoints[:, 2] = relpoints[:, 2] * np.sign(relpoints[:, 2])
    #     print(relpoints)
    #     denergy = np.array([0, 255, 128])
    #     rasterization_triangle(img, n_buffer1, relpoints, denergy)
    d = 100
    rasterization_triangle(img, n_buffer1, np.array([[10, 100 + d, 10],
                                                     [20, 5 + d, 10],
                                                     [100, 10 + d, 10]]), np.array([245,0,0]))
    cv2.imshow('123', img)
    cv2.waitKey(0)