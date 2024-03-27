import cv2
import numpy as np
from eigne3D.Frame import Frame
from utils.utils4camera import rasterization_triangle
from eigne3D.RadianceField import RadTriangle


class Camera:
    def __init__(self, frame: Frame, exposure: np.ndarray, focus_dist: float = 1, width: int = 300, height: int = 200):
        self.frame: Frame = frame
        if self.frame.orthogonality() == Frame:
            raise ValueError("Not Orthogonality!")

        # Thus the center of frame is the position of focus.

        self.n_top = self.frame.normal - self.frame.axis1
        self.n_bot = self.frame.normal + self.frame.axis1
        self.n_left = self.frame.normal + self.frame.axis2
        self.n_right = self.frame.normal - self.frame.axis2

        self.exposure: np.ndarray = exposure
        self.focus_dist: float = focus_dist
        self.width: int = width
        self.height: int = height
        self.screen_center: np.ndarray = self.frame.center + self.focus_dist * self.frame.normal
        self.energy_screen = np.zeros([height, width, 3], dtype=np.uint8)
        self.nBuffer = np.full([height, width], np.inf)

    def update(self):
        self.n_top = self.frame.normal - self.frame.axis1
        self.n_bot = self.frame.normal + self.frame.axis1
        self.n_left = self.frame.normal + self.frame.axis2
        self.n_right = self.frame.normal - self.frame.axis2
        self.screen_center: np.ndarray = self.frame.center + self.focus_dist * self.frame.normal

        self.energy_screen = np.zeros([self.height, self.width, 3], dtype=np.uint8)
        self.nBuffer = np.full([self.height, self.width], np.inf)

    def energy_sense(self) -> np.ndarray:
        ans = self.energy_screen.copy()
        e_R, e_G, e_B = self.exposure[0], self.exposure[1], self.exposure[2]
        ans[ans[:, :, 0] > e_R] = e_R
        ans[ans[:, :, 1] > e_G] = e_G
        ans[ans[:, :, 2] > e_B] = e_B
        e_R_per_pix, e_G_per_pix, e_B_per_pix = e_R / 255, e_G / 255, e_B / 255
        ans[:, :, 0] = np.round(ans[:, :, 0] / e_R_per_pix)
        ans[:, :, 1] = np.round(ans[:, :, 1] / e_G_per_pix)
        ans[:, :, 2] = np.round(ans[:, :, 2] / e_B_per_pix)
        ans = ans.astype(np.uint8)
        return ans

    def screen_projection(self, points: np.ndarray) -> np.ndarray:
        """
        :param points: [N, 3]
        :return: [N, 3], (screen_x, screen_y, depth)
        """
        rel_points = self.frame.relative_coord(points)
        screen_xy = rel_points[:, :2] * self.focus_dist / (rel_points[:, 2].reshape(3, 1))
        depth = np.sqrt(np.sum(rel_points ** 2, axis=1)).reshape(-1, 1)
        ans = np.concatenate([screen_xy, depth], axis=1)
        return ans

    def pixel_coordinate(self, points: np.ndarray) -> np.ndarray:
        """
        :param points: [N, 3] float
        :return: [N, 3] float
        """
        p = (points[:, :2] + 1) * (np.array([self.height, self.width])).reshape(1, -1) / 2
        # p[0] = self.height - p[0]
        p = np.concatenate([p, points[:, 2].reshape(-1, 1)], axis=1)
        return p

    def triangle_in_view(self, triangle: RadTriangle) -> bool:
        vertices = triangle.to_batch_points()
        v_batch = vertices - self.frame.center
        c1 = (self.n_top * v_batch).sum(axis=1) >= 0
        c2 = (self.n_bot * v_batch).sum(axis=1) >= 0
        c3 = (self.n_left * v_batch).sum(axis=1) >= 0
        c4 = (self.n_right * v_batch).sum(axis=1) >= 0
        v2_batch = vertices - self.screen_center
        c5 = (self.frame.normal * v2_batch).sum(axis=1) >= 0
        ans = (c1 * c2 * c3 * c4 * c5).sum() != 0
        return ans

    def raster(self, rad_triangles: list[RadTriangle]):
        for tri in rad_triangles:
            if self.triangle_in_view(tri):
                points = tri.to_batch_points()
                points = self.screen_projection(points)
                points = self.pixel_coordinate(points)
                energy = tri.gaussian_emission(self.frame.center.reshape(1, -1))

                rasterization_triangle(self.energy_screen, self.nBuffer, points, energy)

    def view(self, rad_triangles: list[RadTriangle]) -> np.ndarray:
        self.raster(rad_triangles)
        return self.energy_sense()

    def move(self, translation: np.ndarray, rotation: np.ndarray) -> None:
        """
        :param translation: [3], translate frame center along: axis1, axis2, normal
        :param rotation: [3], rotate frame around axis1, axis2, normal with focus center
        :return:
        """
        self.frame.transformation(translation, rotation)
        self.update()


class Scene:
    def __init__(self):
        self.triangles: list[RadTriangle] = []
        self.light_sources: list[RadTriangle] = []
        self.camera: Camera = None

    def add_triangles(self, triangles:list[RadTriangle]):
        self.triangles = self.triangles + triangles

    def add_sources(self, sources: list[RadTriangle]):
        self.light_sources = self.light_sources + sources

    def triangle_to_arrays(self) -> tuple[np.ndarray, np.ndarray]:
        ans1 = []
        ans2 = []
        for tri in self.triangles:
            ans1.append(tri.to_batch_points())
            ans2.append(tri.orientation.p)
        return np.array(ans1), np.array(ans2)

    def source_to_array(self) -> np.ndarray:
        ans = []
        for s in self.light_sources:
            ans.append(s.center)
        return np.array(ans)

    def trace_combine(self):
        space_triangle_vertices, space_triangle_orientation = self.triangle_to_arrays()
        for i, s in enumerate(self.light_sources):
            index = s.is_emission(space_triangle_vertices,
                                  space_triangle_orientation)

            for j in range(len(self.triangles)):
                if index[j] == 1:
                    self.triangles[j].record_source.append(s)
        for i, tri in enumerate(self.triangles):
            index = tri.is_emission(space_triangle_vertices,
                                    space_triangle_orientation)
            for j in range(len(self.triangles)):
                if index[j] == 1 and i != j:
                    self.triangles[j].record_source.append(tri)

    def render(self):
        for tri in self.triangles:
            for source in tri.record_source:
                tri.absorption(source.center.p, source.gaussian_emission(tri.center.p))
        for tri in self.triangles:
            tri.reset()
            for source in tri.record_source:
                tri.absorption(source.center.p, source.gaussian_emission(tri.center.p))

    def set_camera(self, new_camera: Camera):
        self.camera = new_camera

    def run(self):
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)  # 指定窗口为可调整大小
        cv2.resizeWindow("Camera", 600, 400)
        while True:
            key = cv2.waitKeyEx(500) & 0xFFFFFF
            trans = np.array([0., 0., 0.])
            r_x = 0
            r_y = 0
            if key == ord('w') or key == ord('W'):
                trans = np.array([0, 0, 1]) * 0.1
            elif key == ord('s') or key == ord('S'):
                trans = np.array([0, 0, -1]) * 0.1
            elif key == ord('a') or key == ord('A'):
                trans = np.array([0, 1, 0]) * 0.1
            elif key == ord('d') or key == ord('D'):
                trans = np.array([0, -1, 0]) * 0.1
            elif key == 2490368:
                r_y = 0.5 / np.pi
            elif key == 2621440:
                r_y = -0.5 / np.pi
            elif key == 2424832:
                r_x = 0.5 / np.pi
            elif key == 2555904:
                r_x = -0.5 / np.pi
            elif key == 27:
                break
            trans = np.sum(np.array([self.camera.frame.axis1,
                                     -self.camera.frame.axis2,
                                     self.camera.frame.normal]) * trans.reshape(-1, 1), axis=0)
            self.camera.move(trans, np.array([r_x, r_y, 0]))

            cv2.imshow("Camera", self.camera.view(self.triangles))


if __name__ == '__main__':
    x = np.random.random([3, 3])
    y = np.ones([3]).reshape(-1, 1)
    y[1] = 2
    y[2] = 3
    print(x + y)

    s = Scene()
    camera = Camera(Frame(np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])),
                    np.array([100, 100, 100]))
    s.set_camera(camera)
    s.run()

    # c = Camera(Frame(np.array([0, 0, 0]),np.array([1,0,0]),np.array([0,1,0]), np.array([0,0,1])),np.array([2,2,2]),)
    # c.energy_screen = np.random.random([200, 300, 3])*100
    # ans = c.energy_sense()
    # cv2.imshow('123', ans)
    #
    # cv2.waitKey(0)
    #
    pass
