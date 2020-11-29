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


# zip v1 and v2 together and sum elementwise
def add_vecs(v1,v2):
    return tuple(map(sum, zip(v1,v2)))


# zip v1 and v2 together and return v2 - v1
def sub_vecs(v1,v2):
    return tuple(map(lambda a: a[1]-a[0],zip(v1,v2)))


# return v1 .* v2 element wise
def dot_vecs(v1,v2):
    return sum(map(lambda a: a[0]*a[1], zip(v1,v2)))


# return a vector that is perpendicular to v1 and v2
def cross_vecs(v1,v2):
    x1,y1,z1 = v1
    x2,y2,z2 = v2
    return y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2


# Multiply each of the values by a scalar value
def scalar_mult(s, v1):
    return tuple(map(lambda a: s*a,v1))


# Get the magnitude of a vector
def mag(v1):
    return np.sqrt(sum(n*n for n in v1))


# Return distance between two points
def dist(p1, p2):
    return np.sqrt(sum(map(lambda a: (a[1]-a[0])*(a[1]-a[0]), zip(p1,p2))))


# Return if p1 and p2 are colliding within their two radii
def is_colliding(p1, r1, p2, r2):
    return dist(p1, p2) < (r1 + r2)


# takes a var and turns it into a value between 1 and maxval which asymptonically approaches maxval
# dependent on growth_rate and center
def logistic_approaches(var, maxval, growth_rate, center):
    return maxval / (1 + np.e**(-growth_rate * (var - center)))



def spherical_to_cartesian(rho, theta, phi):
    return (
        rho * np.sin(phi) * np.cos(theta),
        rho * np.sin(phi) * np.sin(theta),
        rho * np.cos(phi)
    )


def coltup_to_bytes(tup):
    return bytes.fromhex(''.join(f'{n:02x}' for n in tup))