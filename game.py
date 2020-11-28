"""
File: game.py
Author: Jay Kmetz
"""

# LOCAL IMPORTS
from pyobjs.Spaceship import Spaceship
from pyobjs.Asteroid import Asteroid
from pyobjs.Planet import Planet

from utils.quat import *
from utils.View import View
from utils.util import *

pinstalled = True

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    print("DEPENDENCY: 'OpenGL' NOT MET")
    pinstalled = False

try:
    import pygame
    from pygame.locals import *
except ImportError:
    print("DEPENDENCY: 'OpenGL' NOT MET")
    pinstalled = False

try:
    import numpy as np
except ImportError:
    print("DEPENDENCY: 'numpy' NOT MET")
    pinstalled = False

if not pinstalled:
    print("Please install the dependenc(y|ies) above using pip or a similar service. Thank you!")
    exit()

import random


# GLOBALS
# KEY ABSTRACTION
ROLL_LEFT       = 'RL'
ROLL_RIGHT      = 'RR'
ROLL_CENTER     = 'RC'
PITCH_LEFT      = 'PL'
PITCH_RIGHT     = 'PR'
PITCH_CENTER    = 'PC'
YAW_LEFT        = 'YL'
YAW_RIGHT       = 'YR'
YAW_CENTER      = 'YC'
THRUST_UP       = 'TU'
THRUST_DOWN     = 'TD'
THRUST_CENTER   = 'TC'
VIEW_FL         = 'VFL'
VIEW_BR         = 'VBR'
VIEW_T          = 'VT'
VIEW_STATIC     = 'VS'
VIEW_ORBIT      = 'VO'

U_KEYS = {
    ROLL_LEFT: 97,      # A
    ROLL_RIGHT: 100,    # D
    ROLL_CENTER: 102,   # F #122,   # Z

    PITCH_LEFT: 119,    # W
    PITCH_RIGHT: 115,   # S
    PITCH_CENTER: 50,   # 2 #120,  # X

    YAW_LEFT: 101,      # Q
    YAW_RIGHT: 113,     # E
    YAW_CENTER: 114,    # R #99      # C

    THRUST_UP: 273,     # UP_ARROW
    THRUST_DOWN: 274,   # DOWN_ARROW
    THRUST_CENTER: 32,  # SPACE_BAR

    VIEW_FL: 117,       # U
    VIEW_BR: 108,       # L
    VIEW_T: 105,        # I
    VIEW_STATIC: 107,   # K
    VIEW_ORBIT: 111     # O
}

# VIEWS
V_BACKRIGHT = 'VBR'
V_FRONTLEFT = 'VFL'
V_TOP       = 'VT'
V_STATIC    = 'VS'
V_ORBIT     = 'VO'

U_VIEWS = {
    V_BACKRIGHT: View(vtype=View.VT_SHIP_RELATIVE, posoff=(-20.0, 8.0, 5.0), lookat=(7.0, 0.0, 0.0)),
    V_FRONTLEFT: View(vtype=View.VT_SHIP_RELATIVE, posoff=(20.0, 8.0, -5.0), lookat=(-7.0, 0.0, 0.0)),
    V_TOP:       View(vtype=View.VT_SHIP_RELATIVE, posoff=(0.0, 20.0, 0.0),  lookat=(0.0, 0.0, 0.0), upvec=(1.0, 0.0, 0.0)),
    V_STATIC:    View(vtype=View.VT_STATIC),
    V_ORBIT:     View(vtype=View.VT_ORBIT, posoff=(0.0, 20.0, 0.0), orbitr=30)
}

# Format: (x,y,z) relative to ship and then stay
CURVIEW = V_BACKRIGHT


def handleKeyEvent(env, event):
    # KEY TESTING
    # if event.type == pygame.KEYDOWN:
    #     print(f'u: {event.unicode if hasattr(event,"unicode") else "none"}; k:{event.key}')

    up = KP_UP if event.type == pygame.KEYUP else 0
    ship = env["ship"]

    def rl(up): # roll left
        ship.setRot(Spaceship.ROLL, Spaceship.LEFT, up)
    def rr(up): # roll right
        ship.setRot(Spaceship.ROLL, Spaceship.RIGHT, up)
    def rc(up): # roll center
        ship.resetRot(Spaceship.ROLL)
    def pl(up): # pitch left
        ship.setRot(Spaceship.PITCH, Spaceship.LEFT, up)
    def pr(up): # pitch right
        ship.setRot(Spaceship.PITCH, Spaceship.RIGHT, up)
    def pc(up): # pitch center
        ship.resetRot(Spaceship.PITCH, up)
    def yl(up): # yaw left
        ship.setRot(Spaceship.YAW, Spaceship.LEFT, up)
    def yr(up): # yaw right
        ship.setRot(Spaceship.YAW, Spaceship.RIGHT, up)
    def yc(up): # yaw center
        ship.resetRot(Spaceship.YAW, up)
    def tu(up): # thrust up
        ship.setThrust(Spaceship.THF, up)
    def td(up): # thrust down
        ship.setThrust(Spaceship.THB, up)
    def tc(up): # thrust center
        ship.applyOppThrust(up)
    def vbr(up):    # view back right
        global CURVIEW
        if not up:
            CURVIEW = V_BACKRIGHT
    def vfl(up):    # view front left
        global CURVIEW
        if not up:
            CURVIEW = V_FRONTLEFT
    def vt(up): # view top
        global CURVIEW
        if not up:
            CURVIEW = V_TOP
    def vs(up): # view static
        global CURVIEW
        if not up:
            v_pos = U_VIEWS[CURVIEW].get_position()
            v_up = U_VIEWS[CURVIEW].upvec
            U_VIEWS[V_STATIC].set_static_view(ship.pos, ship.orient,v_pos,v_up)
            CURVIEW = V_STATIC
    def vo(up): # view orbit
        global CURVIEW
        if not up:
            CURVIEW = V_ORBIT

    # Execute Switch on event.key
    func = {
        U_KEYS[ROLL_LEFT]: rl,
        U_KEYS[ROLL_RIGHT]: rr,
        U_KEYS[ROLL_CENTER]: rc,
        U_KEYS[PITCH_LEFT]: pl,
        U_KEYS[PITCH_RIGHT]: pr,
        U_KEYS[PITCH_CENTER]: pc,
        U_KEYS[YAW_LEFT]: yl,
        U_KEYS[YAW_RIGHT]: yr,
        U_KEYS[YAW_CENTER]: yc,
        U_KEYS[THRUST_UP]: tu,
        U_KEYS[THRUST_DOWN]: td,
        U_KEYS[THRUST_CENTER]: tc,
        U_KEYS[V_BACKRIGHT]: vbr,
        U_KEYS[V_FRONTLEFT]: vfl,
        U_KEYS[V_TOP]: vt,
        U_KEYS[V_STATIC]: vs,
        U_KEYS[V_ORBIT]: vo
    }.get(event.key, None)
    if func:
        func(up)


def init_lighting():
    glEnable(GL_LIGHTING)

    # Gentle orange glow
    lmodel_ambient = (255/255, 197/255, 143/255, 0.8)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, lmodel_ambient)

    light_ambient = (0.0, 0.0, 0.0, 0.2)
    light_diffuse = (1.0, 1.0, 0, 0.5)
    light_specular = (0.5,0.5,0.5, 0)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    glEnable(GL_LIGHT0)


def calc_ambient():
    glPushMatrix()

    light_position = (-10, 10, -10, 0.0)

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glPopMatrix()


def calc_view(env):
    ship = env["ship"]
    # calculate view from View object
    U_VIEWS[CURVIEW].local_gluLookAt(ship.pos, ship.orient)


def main():
    # Locals
    init_new_level = True
    level_counter = 1

    ship = None
    planetd = None
    asteroids = []
    objs = []

    def initialize_level():
        nonlocal ship, planetd, asteroids, objs, level_counter, init_new_level

        # reset vars
        asteroids = []

        # deregister all objects if registered
        # for obj in objs:
        #     if obj.isstatic:
        #         obj.obj.deregister()

        objs = []

        # Game generation tweaks
        noise_max = 20
        # planet
        # Generate random radius and spherical coordinates for planet and then translate
        # into cartesian coordinates
        pradius = random.uniform(16,25)
        prho = random.uniform(200, 200 + level_counter * 100)
        ptheta = random.random() * 2 * np.pi
        pphi = random.random() * np.pi
        ppos = spherical_to_cartesian(prho,ptheta,pphi)

        # planet landing plane point
        # grab point inside sphere and then translate to cartesian coordinates. Point moves further out as
        # level increases
        level_adjust = min((level_counter-1) / 50, .3)
        lrho = pradius * random.uniform(.45 + level_adjust, .65 + level_adjust)
        ltheta = random.random() * 2 * np.pi
        lphi = random.random() * np.pi
        lplanepoint = spherical_to_cartesian(lrho,ltheta,lphi)

        # print(lrho / pradius)
        # print(ltheta * 180/np.pi)
        # print(lphi * 180/np.pi)

        # asteroids
        nasteroids = random.randrange(4, 4 + level_counter * 2)

        ship = Spaceship(lose_cond=lose_condition)
        if planetd:
            planetd.deregister()
        planetd = Planet(lplanepoint, pos=ppos, radius=pradius)

        objs.append(ship)
        objs.append(planetd)

        for i in range(nasteroids):
            # choose percentage along line and then create some random noise for each asteroid
            # increase number of asteroids and noise as you go
            percent = random.uniform(.1, .9)
            noise = (
                noise_max * random.uniform(-1,1), # noisex
                noise_max * random.uniform(-1,1), # noisey
                noise_max * random.uniform(-1,1)  # noisez
            )
            apos = map(lambda a: a*percent, ppos) # get position from percentage along vector to planet
            apos = tuple(map(sum,zip(apos, noise))) # add noise
            tmpa = Asteroid(pos=apos)
            asteroids.append(tmpa)
            objs.append(tmpa)

        init_new_level = False
        level_counter += 1

    def lose_condition():
        nonlocal level_counter, init_new_level
        ## TODO: Display lose message and implement 'play again?' logic
        print("YOU LOSE")
        level_counter = 1
        init_new_level = True

    def level_win_condition():
        nonlocal level_counter, init_new_level
        ## TODO: Display level win logic and implement continue feature
        print(f"NEXT LEVEL: {level_counter + 1}")
        level_counter += 1
        init_new_level = True

    def check_collisions():
        nonlocal ship, planetd, asteroids

        if ship.is_colliding(planetd): # if the ship is colliding with the planet...
            s_vel = ship.getVelMag()
            s_up = ship.getUpVec()
            s_pos = ship.pos
            if planetd.is_good_landing(s_pos, s_vel, s_up):
                level_win_condition()
            else:
                lose_condition()
                # TODO: damage the ship and then eject them away from the planet from Planet.landingplanept

        tmp_asteroids = [] # create temp asteroids list
        while asteroids:
            ast = asteroids.pop()   # get each asteroid
            if ship.is_colliding(ast): # if the ship is colliding with an asteroid...
                ship.damage()   # damage the ship and don't add the asteroid back
                print(ship.health)
            else:   # if the ship is not colliding...
                tmp_asteroids.append(ast)   # add the asteroid back
        while tmp_asteroids:    # add all of the asteroids back
            asteroids.append(tmp_asteroids.pop())

    pygame.init()
    display = (1000, 700)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)

    init_lighting()

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    # glTranslatef(0.0, 0.0, -40.0)
    # glRotatef(90, 0, 1, 0)
    # glRotatef(10, 0, 0, 1)

    # pygame clock
    clock = pygame.time.Clock()
    x = 0
    while True:
        # init level if needed
        if init_new_level:
            initialize_level()

        ## EVENT HANDLING ##
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                env = {
                    "ship": ship
                }
                # print(event)
                if event.type == pygame.KEYDOWN and event.key == 118: # V
                    # glMatrixMode(GL_MODELVIEW)
                    # glLoadIdentity()
                    # gluLookAt(0, 0, -10, *ship.pos, 0, 1, 0)
                    # print(glGetDoublev(GL_MODELVIEW_MATRIX))
                    initialize_level()

                handleKeyEvent(env, event)

        ## RENDERING ##
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # consider looping through objs and rendering in two lines
        ship.point_arrow_at(planetd.pos)

        ship.render() # render ship
        planetd.render()    # render planet
        for asteroid in asteroids:  # render asteroids
            asteroid.render()

        # Draw Axes
        # draw_vec((1,0,0),add_vecs(ship.pos,(3,3,3)),col=(1,0,0))
        # draw_vec((0,1,0),add_vecs(ship.pos,(3,3,3)),col=(0,1,0))
        # draw_vec((0,0,1),add_vecs(ship.pos,(3,3,3)),col=(0,0,1))

        ## COLLISION AND GAME LOGIC ##
        check_collisions()

        ## LIGHTING ##
        calc_ambient()

        ## VIEW ##
        glLoadIdentity() # load identity to recalculate glu_lookat

        env = {
            "ship": ship
        }
        calc_view(env)

        pygame.display.flip()   # flip buffers
        clock.tick()    # tick the clock


if __name__ == "__main__":
    main()
