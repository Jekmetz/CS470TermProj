"""
File: View.py
Author: Jay Kmetz
"""
from utils.quat import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np


class View:
    # VIEW TYPES
    VT_STATIC = 'VTS'
    VT_SHIP_RELATIVE = 'VTSR'
    VT_ORBIT = 'VTO'

    def __init__(self, vtype=VT_SHIP_RELATIVE, posoff=(0,0,0), lookat=(1,0,0), upvec=(0.0, 1.0, 0.0), orbitr=30):
        self.type = vtype
        self.posoff = posoff
        self.lookat = lookat
        self.upvec = upvec
        self.st_pos = None
        self.st_up = None
        self.orbitr = orbitr
        self.th = 0

    def local_gluLookAt(self, s_pos, s_quat):
        shipx, shipy, shipz = s_pos

        if self.type == View.VT_STATIC: # STATIC VIEW
            px, py, pz = self.st_pos
            ux, uy, uz = self.st_up
            gluLookAt(
                px, py, pz,
                shipx, shipy, shipz,
                ux, uy, uz)

        elif self.type == View.VT_SHIP_RELATIVE: # SHIP RELATIVE VIEW
            px, py, pz = qv_mult(s_quat, self.posoff)
            ex, ey, ez = qv_mult(s_quat, self.lookat)
            ux, uy, uz = qv_mult(s_quat, self.upvec)
            gluLookAt(
                shipx + px, shipy + py, shipz + pz,
                shipx + ex, shipy + ey, shipz + ez,
                ux, uy, uz)

        elif self.type == View.VT_ORBIT: # ORBIT VIEW
            py = self.posoff[1]
            px, pz = (self.orbitr * np.cos(self.th), self.orbitr * np.sin(self.th))
            px, py, pz = qv_mult(s_quat, (px,py,pz))
            self.th = (self.th + np.pi/60) % (2*np.pi)

            ux, uy, uz = qv_mult(s_quat, self.upvec)

            gluLookAt(
                shipx + px, shipy + py, shipz + pz,
                shipx, shipy, shipz,
                ux, uy, uz
            )

    def get_position(self):
        if self.type in (View.VT_SHIP_RELATIVE, View.VT_STATIC):
            return self.posoff
        elif self.type == View.VT_ORBIT:
            py = self.posoff[1]
            px, pz = (self.orbitr * np.cos(self.th), self.orbitr * np.sin(self.th))
            return px,py,pz

    def set_static_view(self, s_pos, s_quat, v_pos, v_up):
        self.st_pos = tuple(map(sum,zip(s_pos,qv_mult(s_quat, v_pos))))
        self.posoff = v_pos
        self.upvec = v_up
        self.st_up = qv_mult(s_quat, v_up)
