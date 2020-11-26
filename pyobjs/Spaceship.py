"""
File: Spaceship.py
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


class Spaceship(ColObj):
    RACC = .001  # Rotation Acceleration
    RMAX = .1  # Rotation Max
    RIGHT = 1  # Rotate Right
    LEFT = -RIGHT  # Rotate Left

    PACC = .01  # Positional Acceleration
    THF = 1  # Thrust Forward
    THB = -THF  # Thrust Back
    TOL = .01

    ROLL = 0  # Roll index
    PITCH = 1  # Pitch index
    YAW = 2  # Yaw index

    ROTSET = "ROTSET"
    ROTRESET = "ROTRESET"
    STEADY = "STEADY"

    def __init__(self, pos=(0, 0, 0), orient=(0, 1, 0, 0)):
        global display_cache
        super().__init__(pos, False)

        self.orient = orient
        self.rpy = [0, 0, 0]
        self.actions = [(Spaceship.STEADY), (Spaceship.STEADY), (Spaceship.STEADY)]
        self.force = (0, 0, 0)
        self.vel = (0, 0, 0)
        self.thrusting = 0
        if not display_cache:
            self.obj = DisplayObj()
            self.obj.objFileImport("./wfobjs/spaceship")
            display_cache = self.obj
        else:
            self.obj = display_cache
        self.colr = 2 * self.obj.maxr / 3

        if self.isstatic:
            self.obj.register()

    def setRot(self, mode: int, d=RIGHT, up=0) -> None:
        if up == KP_UP:
            self.actions[mode] = (Spaceship.STEADY)
        else:
            self.actions[mode] = (Spaceship.ROTSET, (mode, d))

    def resetRot(self, mode: int, up=0) -> None:
        if up == KP_UP:
            self.actions[mode] = (Spaceship.STEADY)
        else:
            self.actions[mode] = (Spaceship.ROTRESET, mode)

    def setThrust(self, mode=THF, up=0):
        if up == KP_UP:
            self.force = (0, 0, 0)
            self.thrusting = 0
        else:
            self.thrusting = mode

    def applyThrust(self):
        self.vel = add_vecs(self.force, self.vel)

    def applyOppThrust(self, up=0):
        if up == KP_UP:
            self.force = (0, 0, 0)
            self.thrusting = 0
        else:
            self.thrusting = 2

    def applyVel(self):
        self.pos = add_vecs(self.vel, self.pos);
        # self.orient[3][0:3] = add_vecs(self.vel, self.orient[3][0:3])

    def setRotCalc(self, mode: int, d=RIGHT) -> None:
        if np.sign(d) == 1:
            self.rpy[mode] = min(self.rpy[mode] + d * Spaceship.RACC, Spaceship.RMAX)
        elif np.sign(d) == -1:
            self.rpy[mode] = max(self.rpy[mode] + d * Spaceship.RACC, -Spaceship.RMAX)
        # on sign==0, pass

    def resetRotCalc(self, mode: int) -> None:
        if np.sign(self.rpy[mode]) == 1:
            self.rpy[mode] -= Spaceship.RACC
        elif np.sign(self.rpy[mode]) == -1:
            self.rpy[mode] += Spaceship.RACC

        if abs(self.rpy[mode]) <= Spaceship.RACC:
            self.rpy[mode] = 0
        # on sign==0, pass

    def adjust(self):
        # Rotational Acceleration
        for rpy in range(3):
            if self.actions[rpy][0] != Spaceship.STEADY:
                if self.actions[rpy][0] == Spaceship.ROTSET:
                    self.setRotCalc(*self.actions[rpy][1])
                elif self.actions[rpy][0] == Spaceship.ROTRESET:
                    self.resetRotCalc(self.actions[rpy][1])

        # Positional Acceleration
        if self.thrusting == 2: # If we are applying an opposite thrust...
            if mag(self.vel) <= Spaceship.TOL:
                self.force = (0, 0, 0)
                self.vel = (0, 0, 0)
            else:
                self.force = tuple(map(lambda val: Spaceship.PACC * val, normalize(tuple(map(lambda val: -1 * val, self.vel)))))
        else: # If we are applying a normal force...
            self.force = tuple(map(lambda val: np.sign(self.thrusting) * Spaceship.PACC * val, self.getHeading()))

    def rotate(self):
        if self.rpy[0]:
            rot_x = normalize(axisangle_to_q((1.0, 0.0, 0.0), self.rpy[0]))
            self.orient = q_mult(self.orient, rot_x)

        if self.rpy[1]:
            rot_z = normalize(axisangle_to_q((0.0, 0.0, 1.0), self.rpy[1]))
            self.orient = q_mult(self.orient, rot_z)

        if self.rpy[2]:
            rot_y = normalize(axisangle_to_q((0.0, 1.0, 0.0), self.rpy[2]))
            self.orient = q_mult(self.orient, rot_y)

    def showMat(self):
        print(self.orient)

    def setThrusterColor(self):
        if self.thrusting == -1:  # backwards
            kd = (0.800000, 0.002302, 0.001986)
            ks = (1.000000, 0.002732, 0.002428)
            ke = (2.000000, 0.005755, 0.004965)
        elif self.thrusting == 1:  # forwards
            kd = (0.160080, 0.640000, 0.632630)
            ks = (0.160080, 0.640000, 0.632630)
            ke = (0.400200, 1.600000, 1.581574)
        elif self.thrusting == 2:  # stabalize
            kd = (0.007062, 0.800000, 0.000000)
            ks = (0.008568, 1.000000, 0.000000)
            ke = (0.017654, 2.000000, 0.000000)
        else:  # no thrust
            kd = (1.000000, 0.629645, 0.067944)
            ks = (1.000000, 0.630757, 0.068478)
            ke = (0.000000, 0.000000, 0.000000)

        self.obj.mats["Thruster"].set_dse(kd, ks, ke)

    def render(self):
        self.applyVel()

        # glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        # draw_vec(tuple(map(lambda a: 7 * a, self.getHeading())), self.pos,
        #          (
        #              int(self.thrusting == -1),
        #              int(self.thrusting == 1),
        #              int(self.thrusting == 2)
        #          )
        #          if self.thrusting else
        #          (1.0, 1.0, 1.0)
        #          )

        self.setThrusterColor()

        v, a = q_to_axisangle(self.orient)

        glTranslatef(*self.pos)
        glRotatef(a * 180 / np.pi, *v)

        # do ypr calculations

        self.adjust()
        self.rotate()

        self.applyThrust()

        # Cube.draw_cube()  # eventually draw ship
        # self.draw_collision_sphere() # collision sphere
        self.obj.drawObj()

        glPopMatrix()

    def getHeading(self):
        return qv_mult(self.orient, (1.0, 0.0, 0.0))
