"""
File: Asteroid.py
Author: Jay Kmetz
"""

# PYTHON IMPORTS
import numpy as np
from OpenGL.GL import *

# LOCAL IMPORTS
from utils.quat import *
from utils.DisplayObj import DisplayObj
from utils.util import *
from pyobjs.ColObj import *


# GLOBALS
display_cache = None


class Asteroid(ColObj):
    def __init__(self, pos=(0, 0, 0), aa=(1, 0, 0, 0)):
        global display_cache
        super().__init__(pos, True)

        self.quat = axisangle_to_q(aa[0:3], aa[3]) # create rotation from axis angle
        if not display_cache:
            self.obj = DisplayObj()                     # Initialize display obj
            self.obj.objFileImport("./wfobjs/asteroid") # Use asteroid
            display_cache = self.obj                    # cache it
            if self.isstatic:                           # if this is a static object...
                self.obj.register()                     # register it into a call list
        else:
            self.obj = display_cache

        self.colr = 2 * self.obj.maxr / 3   # 2/3rds the max sphere that bounds it

    def render(self):
        # glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        v, a = q_to_axisangle(self.quat)    # grab openGL happy rotation

        glTranslatef(*self.pos)     # translate
        glRotatef(a*180/np.pi, *v)  # rotate

        self.obj.drawObj()      # draw object

        glPopMatrix()

    # Roll Pitch and yaw work by creating quaternions that represent
    # different rotations around respective axis by given angle
    def roll(self, angle):
        qt = normalize(axisangle_to_q((1.0,0.0,0.0), angle))
        self.quat = q_mult(self.quat, qt)

    def pitch(self, angle):
        qt = normalize(axisangle_to_q((0.0,1.0,0.0), angle))
        self.quat = q_mult(self.quat, qt)

    def yaw(self, angle):
        qt = normalize(axisangle_to_q((0.0, 0.0, 1.0), angle))
        self.quat = q_mult(self.quat, qt)
