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

        self.orient = orient    # quaternion that determines orientation
        self.rpy = [0, 0, 0]    # roll pitch yaw angular accelerations
        self.actions = [(Spaceship.STEADY), (Spaceship.STEADY), (Spaceship.STEADY)] # roll pitch yaw actions
        self.force = (0, 0, 0)  # positional force vectors
        self.vel = (0, 0, 0)    # positional velocity vectors
        self.thrusting = 0      # thrusting mode
        if not display_cache:   # load display object
            self.obj = DisplayObj()
            self.obj.objFileImport("./wfobjs/spaceship")
            display_cache = self.obj
            if self.isstatic:
                self.obj.register()
        else:
            self.obj = display_cache
        self.colr = 2 * self.obj.maxr / 3

    # Set rotation based on roll, pitch, yaw, and direction
    def setRot(self, mode: int, d=RIGHT, up=0) -> None:
        if up == KP_UP:
            self.actions[mode] = (Spaceship.STEADY)
        else:
            self.actions[mode] = (Spaceship.ROTSET, (mode, d))

    # reset rotation roll pitch yaw based on mode and up... opposite force
    def resetRot(self, mode: int, up=0) -> None:
        if up == KP_UP:
            self.actions[mode] = (Spaceship.STEADY)
        else:
            self.actions[mode] = (Spaceship.ROTRESET, mode)

    # set positional acceleration
    def setThrust(self, mode=THF, up=0):
        if up == KP_UP:
            self.force = (0, 0, 0)
            self.thrusting = 0
        else:
            self.thrusting = mode

    # add force to velocity
    def applyThrust(self):
        self.vel = add_vecs(self.force, self.vel)

    # apply force opposite to current velocity
    def applyOppThrust(self, up=0):
        if up == KP_UP:
            self.force = (0, 0, 0)
            self.thrusting = 0
        else:
            self.thrusting = 2

    # apply velocity to position
    def applyVel(self):
        self.pos = add_vecs(self.vel, self.pos);
        # self.orient[3][0:3] = add_vecs(self.vel, self.orient[3][0:3])

    # set rotation calculation - set angular velocity to itself + the direction * the rotational
    # acceleration or the Max rotational acceleration... whichever is higher
    def setRotCalc(self, mode: int, d=RIGHT) -> None:
        if np.sign(d) == 1:
            self.rpy[mode] = min(self.rpy[mode] + d * Spaceship.RACC, Spaceship.RMAX)
        elif np.sign(d) == -1:
            self.rpy[mode] = max(self.rpy[mode] + d * Spaceship.RACC, -Spaceship.RMAX)
        # on sign==0, pass

    # Bleed off current rotational velocity by applying a 'force' which is opposite
    def resetRotCalc(self, mode: int) -> None:
        if np.sign(self.rpy[mode]) == 1:
            self.rpy[mode] -= Spaceship.RACC
        elif np.sign(self.rpy[mode]) == -1:
            self.rpy[mode] += Spaceship.RACC

        if abs(self.rpy[mode]) <= Spaceship.RACC:
            self.rpy[mode] = 0
        # on sign==0, pass

    # adjust rotational and positional acceleration based on current state variables
    def adjust(self):
        # Rotational Acceleration
        for rpy in range(3):        # for rpy indicies...
            if self.actions[rpy][0] != Spaceship.STEADY:    # if we are not trying to be steady...
                if self.actions[rpy][0] == Spaceship.ROTSET:    # if we are applying rotation...
                    self.setRotCalc(*self.actions[rpy][1])  # send mode and direction to setRotCalc
                elif self.actions[rpy][0] == Spaceship.ROTRESET:    # if we are resetting rotation...
                    self.resetRotCalc(self.actions[rpy][1]) # send mode to resetRotCalc

        # Positional Acceleration
        if self.thrusting == 2: # If we are applying an opposite thrust...
            if mag(self.vel) <= Spaceship.TOL:
                self.force = (0, 0, 0)
                self.vel = (0, 0, 0)
            else: # if we are trying to slow down...
                # get negative velocity, make it scale with positional acceleration, and apply
                self.force = tuple(map(lambda val: Spaceship.PACC * val, normalize(tuple(map(lambda val: -1 * val, self.vel)))))
        else: # If we are applying a normal force...
            # apply thrusting force in direction of thrusting scaled to positional acceleration
            self.force = tuple(map(lambda val: np.sign(self.thrusting) * Spaceship.PACC * val, self.getHeading()))

    # See Asteroid for further clarification... Take axis and rotate by angle... turn to quat
    # multiply. Success.
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

    # Set thruster color based on current force
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

        # Set the thruster color to necessary material
        self.setThrusterColor()

        # Translate and rotate
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
