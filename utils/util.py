from OpenGL.GL import *
import numpy as np

# SHARED GLOBALS
KP_UP = 'KP_UP'


def draw_vec(vec, p1=(0,0,0), col=(1.0,1.0,1.0)):
    glBegin(GL_LINES)
    glColor3fv(col)
    glVertex3fv(p1)
    glVertex3fv(add_vecs(p1,vec))
    glEnd()


def add_vecs(v1,v2):
    return tuple(map(sum, zip(v1,v2)))


def mag(v1):
    return np.sqrt(sum(n*n for n in v1))


def dist(p1, p2):
    return np.sqrt(sum(map(lambda a: (a[1]-a[0])*(a[1]-a[0]), zip(p1,p2))))


def is_colliding(p1, r1, p2, r2):
    return dist(p1, p2) < (r1 + r2)
