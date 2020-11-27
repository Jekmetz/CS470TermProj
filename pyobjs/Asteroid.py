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

        self.quat = axisangle_to_q(aa[0:3], aa[3])
        if not display_cache:
            self.obj = DisplayObj()
            self.obj.objFileImport("./wfobjs/asteroid")
            display_cache = self.obj
            if self.isstatic:
                self.obj.register()
        else:
            self.obj = display_cache

        self.colr = 2 * self.obj.maxr / 3

    def render(self):
        # glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        v, a = q_to_axisangle(self.quat)

        glTranslatef(*self.pos)
        glRotatef(a*180/np.pi, *v)

        self.obj.drawObj()

        glPopMatrix()

    def roll(self, angle):
        qt = normalize(axisangle_to_q((1.0,0.0,0.0), angle))
        self.quat = q_mult(self.quat, qt)

    def pitch(self, angle):
        qt = normalize(axisangle_to_q((0.0,1.0,0.0), angle))
        self.quat = q_mult(self.quat, qt)

    def yaw(self, angle):
        qt = normalize(axisangle_to_q((0.0, 0.0, 1.0), angle))
        self.quat = q_mult(self.quat, qt)
