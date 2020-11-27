"""
File: Planet.py
Author: Jay Kmetz
"""

# PYTHON IMPORTS
import numpy as np
import random
from OpenGL.GL import *

# LOCAL IMPORTS
from utils.quat import *
from utils.DisplayObj import DisplayObj
from utils.DisplayObj import Material
from utils.util import *
from pyobjs.ColObj import *


landing_material = Material(
    amb=(0.069405, 0.640000, 0.047737),
    diff=(0.069405, 0.640000, 0.047737),
    spec=(0.043250, 0.399551, 0.029756),
    emm=(0.045981, 0.424000, 0.031626)
)


class Planet(ColObj):
    NUM_TREES = 20

    def __init__(self, landingplanept, radius=20, pos=(0, 0, 0)):
        global display_cache

        self.tree_obj = DisplayObj()
        self.tree_obj.objFileImport("./wfobjs/tree")
        self.tree_obj.register()

        self.radius = radius
        self.landingplanept = landingplanept

        super().__init__(pos, True)

        self.obj = DisplayObj()
        self.obj.objFileImport("./wfobjs/sphere")

        self.colr = self.obj.maxr
        self.obj.scale = self.radius

        self.obj.mats["landable"] = landing_material

        self.choose_landing_spot(landingplanept)

        if self.isstatic:
            self.obj.register(self.populate_trees)

    def render(self):
        # glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glTranslatef(*self.pos)

        self.obj.drawObj()

        glPopMatrix()

    def populate_trees(self):
        nvec = self.landingplanept
        d = dot_vecs(nvec,self.landingplanept)

        def generate_tree():
            go = True
            vert = None
            while go:
                theta = random.random() * 2 * np.pi
                phi = random.random() * np.pi
                vert = spherical_to_cartesian(1.0,theta,phi)
                if dot_vecs(nvec, scalar_mult(self.radius,vert)) < d:
                    go = False

            rv = cross_vecs((0,1,0), vert)
            ra = np.arccos(dot_vecs((0,1,0),vert))
            print(mag(vert),ra)

            return vert, rv, ra

        for i in range(Planet.NUM_TREES):
            glPushMatrix()
            position, v, a = generate_tree()
            glTranslatef(*position)
            glRotatef(a * 180 / np.pi, *v)
            self.tree_obj.drawObj()
            glPopMatrix()

    def deregister(self):
        super().deregister()
        self.tree_obj.deregister()

    def choose_landing_spot(self, planept):
        nvec = planept
        d = dot_vecs(nvec,planept) # planept is both the normal vector and the point on the plane
        marked_verts = set()

        for i,vert in enumerate(self.obj.verts):
            vert = scalar_mult(self.radius, vert)
            if dot_vecs(nvec, vert) >= d:
                marked_verts.add(i)

        for i,surf in enumerate(self.obj.surfs):
            if set(surf[0]).issubset(marked_verts):
                self.obj.cols[i] = "landable"
