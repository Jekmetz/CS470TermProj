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

# Material definition for landing zone
landing_material = Material(
    amb=(0.069405, 0.640000, 0.047737),
    diff=(0.069405, 0.640000, 0.047737),
    spec=(0.043250, 0.399551, 0.029756),
    emm=(0.045981, 0.424000, 0.031626)
)


class Planet(ColObj):
    NUM_TREES = 20
    MAX_ACCEPTABLE_LANDING_VELOCITY = .1
    LANDING_ANGLE_TOLERANCE = np.pi/6   # 30 degree landing angle tolerance

    def __init__(self, landingplanept, radius=20, pos=(0, 0, 0)):

        # creating call list for tree
        self.tree_obj = DisplayObj()
        self.tree_obj.objFileImport("./wfobjs/tree")
        self.tree_obj.register()

        # Radius and landing plane point for planet
        self.radius = radius
        self.landingplanept = landingplanept

        super().__init__(pos, True)

        # Planet display object
        self.obj = DisplayObj()
        self.obj.objFileImport("./wfobjs/sphere")

        # collision radius set to maxr. This is a sphere after all
        self.colr = self.radius
        self.obj.scale = self.radius

        # Initialize landable material
        self.obj.mats["landable"] = landing_material

        # do landing spot calculations to change colors of correct faces
        self.choose_landing_spot()

        if self.isstatic:
            self.obj.register(self.populate_trees) # Throw in the trees to minimize call list

    def render(self):
        # glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glTranslatef(*self.pos)

        self.obj.drawObj()

        glPopMatrix()

    def populate_trees(self):
        # Normal vector is from 0,0,0 to the landing point i.e. the landing point
        nvec = self.landingplanept
        d = dot_vecs(nvec,self.landingplanept) # get dot from nvec and landingplanept to do outside calcs

        def generate_tree():
            go = True
            vert = None
            while go:   # while we still need to guess...
                # pick a random theta and phi inside the circle
                theta = random.random() * 2 * np.pi
                phi = random.random() * np.pi
                vert = spherical_to_cartesian(1.0,theta,phi)
                # Check if it is outside the landing spot
                if dot_vecs(nvec, scalar_mult(self.radius,vert)) < d:
                    # if it is good, march on, soldier
                    go = False

            rv = cross_vecs((0,1,0), vert)          # rotation vector axis is cross between y axis and the point -> landing point vec
            ra = np.arccos(dot_vecs((0,1,0),vert))  # rotation angle calculation
            # don't divide by magnitudes in above arrow calculation because (0,1,0) and vert have magnitude 1

            return vert, rv, ra

        for i in range(Planet.NUM_TREES):
            glPushMatrix()
            position, v, a = generate_tree()
            glTranslatef(*position)
            glRotatef(a * 180 / np.pi, *v)
            self.tree_obj.drawObj()
            glPopMatrix()

    def is_landing_area_pt(self, pt):
        nvec = self.landingplanept
        d = dot_vecs(nvec, self.landingplanept)  # get dot from nvec and landingplanept to do outside calcs
        return dot_vecs(nvec, pt) < d

    def deregister(self):
        super().deregister()
        self.tree_obj.deregister()

    def choose_landing_spot(self):
        nvec = self.landingplanept
        d = dot_vecs(nvec,self.landingplanept) # landingplanept is both the normal vector and the point on the plane
        marked_verts = set()

        # for each of the verticies...
        for i,vert in enumerate(self.obj.verts):
            vert = scalar_mult(self.radius, vert)
            if dot_vecs(nvec, vert) >= d:   # if the vert is on the opposite side of the plane than the center...
                marked_verts.add(i) # Mark that john

        for i,surf in enumerate(self.obj.surfs):    # for each surf...
            if set(surf[0]).issubset(marked_verts): # if each of the surf verts exist in the marked_verts...
                self.obj.cols[i] = "landable"   # color it with the landable color

    def ejectpoint(self):
        # Grab the landing plane vector, make it of length radius + 20, and then add it to the position
        return add_vecs(self.pos,scalar_mult(self.radius + 20,normalize(self.landingplanept)))

    def is_good_landing(self, s_pos, s_vel, s_up):
        to_ship_vec = sub_vecs(self.pos, s_pos) # get the vector from the planet to the ship
        angle = np.arccos(dot_vecs(s_up, to_ship_vec) / (mag(s_up) * mag(to_ship_vec)))

        is_landing_area = self.is_landing_area_pt(sub_vecs(s_pos, self.pos))
        slow_enough = s_vel <= Planet.MAX_ACCEPTABLE_LANDING_VELOCITY
        angle_good = angle <= Planet.LANDING_ANGLE_TOLERANCE
        print(is_landing_area, s_vel, angle)
        dmgtxt = ""

        if not is_landing_area:
            dmgtxt += "You did not land in the landing area! "
        elif not slow_enough:
            dmgtxt += "You were coming in too hot! "
        elif not angle_good:
            dmgtxt += "You did not land flat enough! "

        # return true if
        # we are on the right side of the landing plane and
        # we are not coming in too hot and
        # we are pointing with our bottom facing the planet
        return is_landing_area and slow_enough and angle_good, dmgtxt
