import numpy as np
import cv2

def triangle_draw_with_buffer(img, n_buffer, points, depths, color):
    P = np.concatenate([points,depths.reshape(depths.shape[0], 1)],axis=1)
    p1, p2, p3 = P
    w, h, _ = img.shape
    p1[0], p1[1] = w - p1[0], h - p1[1]
    p2[0], p2[1] = w - p2[0], h - p2[1]
    p3[0], p3[1] = w - p3[0], h - p3[1]
    Ps = sorted([p1 ,p2,p3],key=lambda x:x[1])

    p1, p2, p3 = Ps

    tmp_vec = Vector.wedge(Vector.array_to_Vector(p2-p1), Vector.array_to_Vector(p3-p1)).p
    # p1[0], p1[1] = w - p1[0], h - p1[1]
    # p2[0], p2[1] = w - p2[0], h - p2[1]
    # p3[0], p3[1] = w - p3[0], h - p3[1]

    for i in range(int(p1[1]), int(p2[1])):
        if i >= 0 and i < h:
            start = (p2[0] - p1[0]) * (int(p1[1]) + (i-int(p1[1])) - p1[1]) / (p2[1] - p1[1]) + p1[0]
            end = (p3[0] - p1[0]) * (int(p1[1]) + (i-int(p1[1])) - p1[1]) / (p3[1] - p1[1]) + p1[0]
            start1, end1 = int(min(start, end)), int(max(start, end))
            for j in range(start1, end1):
                if j>=0 and j <w:
                    # buffer and draw
                    depth = ((np.array([j, i]) - p1[:2]) * tmp_vec[:2]).sum() / tmp_vec[2] + p1[2]
                    if depth < n_buffer[j,i]:
                        n_buffer[j, i] = depth
                        img[j, i, :] = color
    for i in range(int(p2[1]), int(p3[1])):
        if i >= 0 and i < h:
            start = (p3[0] - p2[0]) * (int(p2[1]) + (i - int(p2[1])) - p2[1]) / (p3[1] - p2[1]) + p2[0]
            end = (p3[0] - p1[0]) * (int(p1[1]) + (i-int(p1[1])) - p1[1]) / (p3[1] - p1[1]) + p1[0]
            start1, end1 = int(min(start, end)), int(max(start, end))
            for j in range(start1, end1):
                if j>=0 and j < w:
                    depth = ((np.array([j, i]) - p1[:2]) * tmp_vec[:2]).sum() / tmp_vec[2] + p1[2]
                    if depth < n_buffer[j, i]:
                        n_buffer[j, i] = depth
                        img[j, i, :] = color


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


def frame_change(obj_point: Point, center: Point, v1: Vector, v2: Vector, v3: Vector):
    """
    We consider the right-hand coordinate
    :param obj_point:
    :param center:
    :param v1: first axis
    :param v2: second axis
    :param v3: third axis
    :return:
    """
    frame_mat = np.array([v1.normalized().p,
                          v2.normalized().p,
                          v3.normalized().p])
    if np.linalg.det(frame_mat) == 0:
        raise ValueError("Not a correct frame.")
    v = Vector.Points_to_vector(center, obj_point)
    ans = frame_mat @ v.p
    return Point.array_to_Point(ans)


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1 # Start
        self.p2 = p2 # End

    @property
    def direction(self):
        vec = self.p2.p - self.p1.p
        k = np.linalg.norm(vec)
        vec = vec / k
        return Vector.array_to_Vector(vec)

    def __str__(self):
        return "Line(" + str(self.p1.p) + "->" + str(self.p2.p) + ")"


class RadianceField:
    def __init__(self, center: Point, x_axis: Vector, y_axis: Vector,
                   rad_var, absorb_rat):
        self.center = center
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.normal = Vector.wedge(x_axis, y_axis)
        self.rad_var = rad_var
        self.absorb_rat = absorb_rat
        self.mean_pos = None
        self.mean_val = None

    def relative_coord(self, p: Point) -> Point:
        # vec = p.p
        # v_translated = vec - self.center.p
        # mat = np.array([self.x_axis.normalized().p,
        #                 self.y_axis.normalized().p,
        #                 self.normal.normalized().p])
        # ans = mat @ v_translated
        ans = frame_change(p, self.center, self.x_axis, self.y_axis, self.normal)
        return ans

    def in_radiance(self, source: Point, energy):
        """
        :param source: Point
        :param energy: RGB 3-tuple
        :return:
        """
        rel_point = self.relative_coord(source)

        in_direct = Vector(-rel_point.x, -rel_point.y, -rel_point.z)
        if in_direct.z < 0:
            r = in_direct.norm()
            theta = np.arccos(-in_direct.z / r)
            phi = np.arctan2(in_direct.y, in_direct.x)
            if self.mean_pos is None:
                self.mean_pos = np.array([[theta, phi]])
            else:
                self.mean_pos = np.concatenate([self.mean_pos, np.array([[theta, phi]])],axis=0)

            if self.mean_val is None:
                self.mean_val = np.array([energy]) * self.absorb_rat
            else:
                self.mean_val = np.concatenate([self.mean_val, np.array([energy]) * self.absorb_rat],axis=0)


    def out_radiance(self, target: Point) -> object:
        rel_point = self.relative_coord(target)
        out_direct = Vector(rel_point.x, rel_point.y, rel_point.z)
        r = out_direct.norm()
        if out_direct.z < 0:
            return np.array([0,0,0])
        theta = np.arccos(out_direct.z / r)
        phi = np.arctan2(out_direct.y, out_direct.x)
        out_angle = np.array([theta, phi])
        X = (out_angle - self.mean_pos)
        Sigma = np.eye(2) / self.rad_var
        ans = np.einsum("ij,jl->il",X, Sigma)
        ans = np.einsum("ij,ij->i", ans, X)
        ans = np.exp(-ans/2).reshape(ans.shape[0],1)
        ans = ans * self.mean_val
        ans = np.sum(ans, axis=0)
        ans[ans>255] = 255
        return ans


class Triangle:
    def __init__(self, p1: Point, p2: Point, p3: Point, rad_var=1., absorb_rat=1.):
        self.p1 = p1 # Start
        self.p2 = p2 # End 1
        self.p3 = p3 # End 2
        self.rad_var = rad_var
        self.absorb_rat =absorb_rat
        self.radiance_field = RadianceField(self.center, self.l1.direction,
                                            self.l2.direction, self.rad_var, self.absorb_rat)

    def in_radiance(self, source: Point, intensity):
        self.radiance_field.in_radiance(source, intensity)

    def field_reset(self):
        self.radiance_field = RadianceField(self.center, self.l1.direction,
                                            self.l2.direction, self.rad_var, self.absorb_rat)

    @property
    def l1(self):
        return Line(self.p1, self.p2)

    @property
    def l2(self):
        return Line(self.p1, self.p3)

    @property
    def orientation(self):
        v1 = self.l1.direction
        v2 = self.l2.direction
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

class Camera:
    def __init__(self, center: Point, axis1: Vector, axis2: Vector, focus_dist: float=1, width:int=200, height:int=300):
        self.center = center
        self.axis1 = axis1.normalized()
        self.axis2 = axis2.normalized()
        self.focus_dist = focus_dist

        self.normal = Vector.wedge(self.axis1, self.axis2)
        self.focus = Point.array_to_Point(self.center.p - focus_dist * self.normal.p)
        self.n_top = self.normal - self.axis1
        self.n_bot = self.normal + self.axis1
        self.n_left = self.normal + self.axis2
        self.n_right = self.normal - self.axis2

        self.width, self.height = width, height
        self.screen = np.zeros([width, height, 3], dtype=np.uint8)
        self.nBuffer = np.full([width, height], np.inf)

    def move(self, translation:np.ndarray=np.zeros([3],np.float32),
             rotate_axis1:float=0,
             rotate_axis2:float=0,
             rotate_normal:float=0):
        self.center = Point.array_to_Point(self.center.p +
                                           (np.array([self.axis1.p, self.axis2.p, self.normal.p]).T * translation).sum(axis=1))
        rotate = np.array([[1, 0, 0],
                           [0, np.cos(rotate_axis1), -np.sin(rotate_axis1)],
                           [0, np.sin(rotate_axis1), np.cos(rotate_axis1)]])
        rotate = np.array([[np.cos(rotate_axis2), 0, np.sin(rotate_axis2)],
                           [0, 1, 0],
                           [-np.sin(rotate_axis2), 0, np.cos(rotate_axis2)]]) @ rotate
        rotate = np.array([[np.cos(rotate_normal), -np.sin(rotate_normal), 0],
                           [np.sin(rotate_normal), np.cos(rotate_normal), 0],
                           [0, 0, 1]]) @ rotate
        frame = np.array([self.axis1.p,
                          self.axis2.p,
                          self.normal.p]).T
        new_frame = frame @ rotate
        self.axis1.p, self.axis2.p = new_frame.T[:2]
        self.initialization()


    def initialization(self):
        self.normal = Vector.wedge(self.axis1, self.axis2)
        self.focus = Point.array_to_Point(self.center.p - self.focus_dist * self.normal.p)
        self.n_top = self.normal - self.axis1
        self.n_bot = self.normal + self.axis1
        self.n_left = self.normal + self.axis2
        self.n_right = self.normal - self.axis2
        self.screen = np.zeros([self.width, self.height, 3], dtype=np.uint8)
        self.nBuffer = np.full([self.width, self.height], np.inf)

    def view_scene(self, scene):

        for item in scene:
            if self.trangle_in_view(item):
                self.rasterization(item)

    def point_in_view(self, p: Point):
        v = Vector.Points_to_vector(self.focus, p)
        c1 = Vector.dot(v, self.n_top) >= 0
        c2 = Vector.dot(v, self.n_bot) >= 0
        c3 = Vector.dot(v, self.n_left) >= 0
        c4 = Vector.dot(v, self.n_right) >= 0
        v2 = Vector.Points_to_vector(self.center, p)
        c5 = Vector.dot(self.normal, v2) >= 0
        return c1 * c2 * c3 * c4 * c5 == 1

    def trangle_in_view(self, t: Triangle):
        p_batch = t.to_batch_points()
        v_batch = p_batch - self.focus.p
        c1 = (self.n_top.p * v_batch).sum(axis=1) >= 0
        c2 = (self.n_bot.p * v_batch).sum(axis=1) >= 0
        c3 = (self.n_left.p * v_batch).sum(axis=1) >= 0
        c4 = (self.n_right.p * v_batch).sum(axis=1) >= 0
        v2_batch = p_batch - self.center.p
        c5 = (self.normal.p * v2_batch).sum(axis=1) >= 0
        ans = (c1 * c2 * c3 * c4 * c5).sum() != 0
        return ans

    def perspective_projection(self, t: Triangle):
        frame_mat = np.array([self.axis1.p,
                              self.axis2.p,
                              self.normal.p])
        ps = t.to_batch_points() - self.center.p
        new_coord = frame_mat @ (ps.T)
        depth_arr = new_coord[-1, :]
        proj_arr = new_coord[:-1,:] / (depth_arr + 1)
        return proj_arr, depth_arr

    def rasterization(self, t: Triangle) -> None:
        """
        nBuffer and rasterize
        :param proj_arr:
        :param depth_arr:
        :return:
        """
        shape = np.array(self.screen.shape[:2])
        proj_arr, depth_arr = self.perspective_projection(t)
        pixel_arr = (proj_arr.T + 1) * shape / 2
        triangle_draw_with_buffer(self.screen,self.nBuffer, pixel_arr, depth_arr, t.radiance_field.out_radiance(self.focus))


class LightSource:
    def __init__(self, position: Point, intensity):
        self.position = position
        self.intensity = intensity

class Entity:
    def __init__(self):
        self.triangles = []

    def set_triangel(self, tri: Triangle):
        self.triangles.append(tri)

class Scene:
    def __init__(self):
        self.triangles = []
        self.light_sources = []
        self.camera = None

    def set_triangle(self, tri: Triangle):
        self.triangles.append(tri)

    def set_light_sources(self, sour: LightSource):
        self.light_sources.append(sour)

    def set_camera(self, camera: Camera):
        self.camera = camera

    def radiance_render(self):
        for tri in self.triangles:
            tri:Triangle
            tri.field_reset()
            # source radiance
            for source in self.light_sources:
                source:LightSource
                tri.radiance_field.in_radiance(source.position, source.intensity)

            # triangle radiance
            for tri2 in self.triangles:
                tri2:Triangle
                if tri != tri2:
                    tri.radiance_field.in_radiance(tri2.center, tri2.radiance_field.out_radiance(tri.center))

    def run_view(self):
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)  # 指定窗口为可调整大小
        cv2.resizeWindow("Camera", 600, 400)
        while True:
            key = cv2.waitKeyEx(10) & 0xFFFFFF
            trans = np.array([0., 0., 0.])
            r_x = 0
            r_y = 0
            if key == ord('w') or key == ord('W'):
                trans = np.array([0,0,1]) * 0.1
            elif key == ord('s') or key == ord('S'):
                trans = np.array([0,0,-1]) * 0.1
            elif key == ord('a') or key == ord('A'):
                trans = np.array([0,1,0]) * 0.1
            elif key == ord('d') or key == ord('D'):
                trans = np.array([0,-1,0]) * 0.1
            elif key == 2490368:
                r_y = 0.5 / np.pi
            elif key == 2621440:
                r_y = -0.5 / np.pi
            elif key == 2424832:
                r_x = 0.5 /  np.pi
            elif key == 2555904:
                r_x = -0.5 / np.pi
            elif key == 27:
                break
            self.camera.move(trans, rotate_axis1=-r_x, rotate_axis2=r_y)
            self.camera.initialization()
            self.camera.view_scene(self.triangles)
            cv2.imshow("Camera", self.camera.screen)




if __name__ == '__main__':
    scene = Scene()
    light = LightSource(Point(10,0,10), (255,255,255))
    t = Triangle(Point(8,0,5), Point(5, 2, 0), Point(5, -2, 0))
    camera = Camera(Point(0, 0, 0), Vector(0, 0, 1), Vector(0, -1, 0))

    scene.set_triangle(t)
    scene.set_light_sources(light)
    scene.set_camera(camera)
    scene.radiance_render()
    scene.run_view()