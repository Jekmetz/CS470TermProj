from OpenGL.GL import *
import numpy as np

# SHARED GLOBALS
KP_UP = 'KP_UP'


# Draw vector vec starting at point p1 with color col
def draw_vec(vec, p1=(0,0,0), col=(1.0,1.0,1.0)):
    glBegin(GL_LINES)
    glMaterialfv(GL_FRONT, GL_AMBIENT, col)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, col)
    glMaterialfv(GL_FRONT, GL_SPECULAR, col)
    glMaterialfv(GL_FRONT, GL_EMISSION, col)
    glVertex3fv(p1)
    glVertex3fv(add_vecs(p1,vec))
    glEnd()


def add_vecs(v1,v2):
    return tuple(map(sum, zip(v1,v2)))


def sub_vecs(v1,v2):
    return tuple(map(lambda a: a[1]-a[0],zip(v1,v2)))


def dot_vecs(v1,v2):
    return sum(map(lambda a: a[0]*a[1], zip(v1,v2)))


def cross_vecs(v1,v2):
    x1,y1,z1 = v1
    x2,y2,z2 = v2
    return y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2


def scalar_mult(s, v1):
    return tuple(map(lambda a: s*a,v1))


def mag(v1):
    return np.sqrt(sum(n*n for n in v1))


def dist(p1, p2):
    return np.sqrt(sum(map(lambda a: (a[1]-a[0])*(a[1]-a[0]), zip(p1,p2))))


def is_colliding(p1, r1, p2, r2):
    return dist(p1, p2) < (r1 + r2)


def logistic_approaches(var, maxval, scale):
    return maxval + scale / var


def spherical_to_cartesian(rho, theta, phi):
    return (
        rho * np.sin(phi) * np.cos(theta),
        rho * np.sin(phi) * np.sin(theta),
        rho * np.cos(phi)
    )
