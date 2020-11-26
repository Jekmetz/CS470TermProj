import os
import numpy as np
from OpenGL.GL import *


def loadMats(fname):
    # Init vars
    mats = {}
    curmat = None

    with open(fname) as fp:
        line = fp.readline()
        while line:
            args = line.strip().split(" ")  # Split arguments on space after removing \n from end
            cmd = args[0]   # command is always the first arg

            if cmd == "newmtl": # new material
                curmat = args[1]
                mats[curmat] = Material()
            # elif cmd == "Ka": # ambient color
            #     mats[curmat].amb = (float(args[1]),float(args[2]),float(args[3]))
            elif cmd == "Kd": # diffuse color
                mats[curmat].amb = (float(args[1]), float(args[2]), float(args[3]))
                mats[curmat].diff = (float(args[1]),float(args[2]),float(args[3]))
            elif cmd == "Ks": # diffuse color
                mats[curmat].spec = (float(args[1]),float(args[2]),float(args[3]))
            elif cmd == "Ke": # diffuse color
                mats[curmat].emm = (float(args[1]),float(args[2]),float(args[3]))
            elif cmd == "d": # transparency
                mats[curmat].trans = float(args[1])
            else: # anything else
                pass

            line = fp.readline()

    return mats


class DisplayObj:
    def __init__(self, verts=None, norms=None, edges=None, surfs=None, cols=None, nam=None, mats=None):
        self.verts = verts
        self.norms = norms
        self.edges = edges
        self.surfs = surfs
        self.cols = cols
        self.name = nam
        self.mats = None
        self.maxr = 0
        self.scale = 1.0

        self.dlindex = -1

    def objFileImport(self, objName):
        # Init vars
        objFname = objName + ".obj"
        curmat = None

        # Reset current ivars
        self.verts = []
        self.norms = []
        self.edges = []
        self.surfs = []
        self.cols = []
        self.mats = None

        if not os.path.exists(objFname):
            raise FileNotFoundError(objFname + " does not exist!")

        curdir = os.path.dirname(os.path.abspath(objFname))

        # Read in verts, edges, and surfs
        with open(objFname) as fp:
            line = fp.readline()
            while line:
                args = line.strip().split(" ")  # get line args
                cmd = args[0]

                if cmd == "mtllib": # mtl library
                    mtlFname = curdir + '/' + args[1]
                    if not os.path.exists(mtlFname):
                        raise FileNotFoundError(mtlFname + " referenced but does not exist!")
                    self.mats = loadMats(mtlFname)
                elif cmd == "o": # object name
                    self.name = args[1]
                elif cmd == "v": # vertex
                    vert = (float(args[1]),float(args[2]),float(args[3]))
                    self.verts.append(vert)
                    sum_squares = sum(map(lambda a: a*a, vert))
                    if self.maxr < sum_squares:
                        self.maxr = sum_squares
                elif cmd == "vn": # vertex normal
                    self.norms.append((float(args[1]),float(args[2]),float(args[3])))
                elif cmd == "usemtl": # use material
                    curmat = args[1]
                elif cmd == "f": # face
                    self.loadFaceCmd(args[1:])
                    if self.mats and curmat: # if we have a material to load...
                        self.cols.append(curmat)
                line = fp.readline()
            self.maxr = np.sqrt(self.maxr)

    def loadFaceCmd(self, args):
        # EDGES
        vertlist = []
        tmp = None
        for arg in args:
            tmp = arg.split("/")
            vertlist.append( int(tmp[0])-1 ) # append the vertex number (first number in str) -1 to make index
        norm = int(tmp[2])-1 # grab the vertex normal number

        for i in range(len(vertlist) - 1):
            edge = (vertlist[i],vertlist[i+1])  # get edge of face
            if edge not in self.edges and (edge[1],edge[0]) not in self.edges: # if we don't have a copy of this yet...
                self.edges.append(edge)

        edge = (vertlist[-1],vertlist[0])  # append last and first
        if edge not in self.edges and (edge[1], edge[0]) not in self.edges:  # if we don't have a copy of this yet...
            self.edges.append(edge)

        # FACE
        self.surfs.append((tuple(vertlist),norm))

    def drawObj(self):
        if self.dlindex == -1:  # Immediate mode
            glScalef(self.scale, self.scale, self.scale)
            for col, surface_norm in zip(self.cols, self.surfs):
                mat = self.mats[col] or Material()
                glMaterialfv(GL_FRONT, GL_AMBIENT, mat.amb)
                glMaterialfv(GL_FRONT, GL_DIFFUSE, mat.diff)
                glMaterialfv(GL_FRONT, GL_SPECULAR, mat.spec)
                glMaterialfv(GL_FRONT, GL_EMISSION, mat.emm)

                surface = surface_norm[0]
                norm = surface_norm[1]
                if len(surface) == 3:
                    glBegin(GL_TRIANGLES)
                elif len(surface) == 4:
                    glBegin(GL_QUADS)
                else:
                    glBegin(GL_POLYGON)
                glNormal3fv(self.norms[norm])
                for vertex in surface:
                    glVertex3fv(self.verts[vertex])
                glEnd()
            glScalef(1.0,1.0,1.0)

            # glBegin(GL_LINES)
            # glColor3fv((0.0, 0.0, 0.0))
            # for edge in self.edges:
            #     for vertex in edge:
            #         glVertex3fv(self.verts[vertex])
            # glEnd()
        else: # Display List
            glCallList(self.dlindex)

    def register(self):
        index = glGenLists(1)
        glNewList(index,GL_COMPILE)
        self.drawObj()
        glEndList()
        self.dlindex = index

    def deregister(self):
        glDeleteLists(self.dlindex, 1)


class Material:
    def __init__(self):
        self.amb   = (0.2,0.2,0.2,1.0)
        self.diff  = (0.8,0.8,0.8,0.8)
        self.spec  = (0.0,0.0,0.0,1.0)
        self.emm   = (0.0,0.0,0.0,1.0)
        self.trans = 1.0

    def set_dse(self,d,s,e):
        self.amb = d
        self.diff = d
        self.spec = s
        self.emm  = e
