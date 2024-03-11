import numpy as np

def angle2sphere(theta, varphi):
    x = np.sin(theta) * np.cos(varphi)
    y = np.sin(theta) * np.sin(varphi)
    z = np.cos(theta)
    return x,y,z

def sphere2angle(x, y, z):
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    theta = np.arccos(z/r)
    varphi = np.arctan2(y , x)
    return theta, varphi


def rand_coord_sphere():
    x = np.random.random()
    rest = 1 - x** 2
    y = np.sqrt(rest * np.random.random())
    z = np.sqrt(rest - y ** 2)
    return np.array([x,y,z])

def f():
    varphi = (np.random.random() * 2 - 1) * np.pi
    theta = np.random.random() * np.pi

    x, y, z = angle2sphere(theta, varphi)
    t1, v1 = sphere2angle(x, y, z)
    return (t1 - theta)**2+( v1 - varphi)**2

x = np.zeros([0, 3])

y=np.concatenate([x, np.array([1,2,3]).reshape(1,-1)],axis=0)

print(y)