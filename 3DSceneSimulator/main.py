from eigne3D.RadianceField import RadTriangle, RadSource
from eigne3D.Geometry import Point
from eigne3D.SceneCamera import Scene, Camera
from eigne3D.Frame import Frame
import numpy as np
from eigne3D.RadianceSurface import RadParallelogram, RadPlane

scene = Scene()
camera = Camera(Frame(np.array([0, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1]), np.array([1, 0, 0])),
                np.array([100, 100, 100]), )

# t.absorption(np.array([0, 0, 0]), np.array([100,0,100]))
s = RadSource(Point(0,0,4), Point(0, 1, 4), Point(1, 0, 4),np.array([100, 300, 300]))
scene.add_sources([s])

p = RadParallelogram(Point(5,0,0), Point(5,1,1), Point(5,1,0), absorb_rate=np.array([0,1,0]))
scene.add_triangles(p.get_triangles())
p = RadPlane(Point(5, 0, 0), Point(4.5, -2, 2), Point(5, 1, 1), 2, 2)
scene.add_triangles(p.get_triangles())
scene.trace_combine()
scene.render()
for item in scene.triangles:
    print(item.emission_energy)

scene.set_camera(camera)
scene.run()
