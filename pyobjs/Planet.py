"""
File: Planet.py
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


class Planet(ColObj):
    def __init__(self, radius=20, pos=(0, 0, 0)):
        global display_cache

        self.radius = radius

        super().__init__(pos, True)

        if not display_cache:
            self.obj = DisplayObj()
            self.obj.objFileImport("./wfobjs/sphere")
            display_cache = self.obj
        else:
            self.obj = display_cache
        self.colr = self.obj.maxr
        self.obj.scale = self.radius

        if self.isstatic:
            self.obj.register()

    def render(self):
        # glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glTranslatef(*self.pos)

        self.obj.drawObj()

        glPopMatrix()