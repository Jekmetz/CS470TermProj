"""
File: ColObj.py
Author: Jay Kmetz
"""
from OpenGL.GL import *

from utils.util import is_colliding
from utils.DisplayObj import DisplayObj


class ColObj:
    def __init__(self, pos):
        self.colr = 0
        self.pos = pos

    def is_colliding(self, other):
        return is_colliding(self.pos, self.colr, other.pos, other.colr)