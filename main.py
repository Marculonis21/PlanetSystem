#!/usr/bin/env python3

from enum import Enum
import copy
import os
import pickle
import sys

import numpy as np
import pygame as PG

import SpaceObject as SO
import UIObject as UI

WIDTH = HEIGHT = 800 

PG.init()
screen = PG.display.set_mode((WIDTH,HEIGHT))
PG.display.set_caption("SCREEN")
clock = PG.time.Clock()

PG.mouse.set_cursor(*PG.cursors.diamond)

#EVENTS
PAUSED = True

class DState(Enum):
    SIM = 1
    LOAD = 2
    HELP = 3

DRAWSTATE = DState.SIM

#VARIABLES
REALTIME = 0
TIMESTEP = 0

PHSXTIME = 0.005
# PHSXTIME = 0.01
SIMSPEED = 1
step_size = int(SIMSPEED / PHSXTIME)
forwardSimSteps = 20000

SELECTED = None
camXY = PG.Vector2(0,0)
camZOOM = 1

staticObj = None
objectList = []
popup = UI.ObjPopup()

SCREENSHOT = False
SSNum = -1

topBar = []
topBarSelected = False

HEADER = PG.font.SysFont('Arial', 35, False, False)
FONT = PG.font.SysFont('Arial', 20, False, False)

#CONSTANTS
FPS = 30 
GRAV_CONS = 6.67430*10**(1)
camMoveSpeed = 15
BGCOLOR = (10,10,10)

def backgroundDrawing():
    global gridSize
    screen.fill(BGCOLOR)

def spaceObjectDrawing(): # Drawing space objects and its paths
    for obj in objectList: # Sim path draw
        obj.DrawSimPath(screen, camXY, camZOOM, forwardSimSteps, PAUSED, TIMESTEP, objectList)

    for obj in objectList: # Object draw
        pos = obj.GetStepPos(TIMESTEP, camXY)
        if (SELECTED == obj):
            PG.draw.circle(screen, PG.Color(100,100,100), pos, int(obj.size/camZOOM)+10, 1)
        PG.draw.circle(screen, obj.color, pos, int(obj.size/camZOOM))

fDraw = False
def loadDrawing(screen): # Drawing Load menu
    global DRAWSTATE, fDraw

    mainRect = PG.Rect(WIDTH//8, HEIGHT//10, 6*WIDTH//8, 5*HEIGHT//6)
    PG.draw.rect(screen, PG.Color(40,40,40), mainRect, border_radius=20)

    if not (mainRect.collidepoint(PG.mouse.get_pos())) and (fDraw): DRAWSTATE = DState.SIM
    fDraw = True

    zero = PG.Vector2(WIDTH//8, HEIGHT//10)
    width = PG.Vector2(6*WIDTH//8, 0) 
    height = PG.Vector2(0, 4*HEIGHT//6) 

    text = HEADER.render("SAVE FILES", True, PG.Color("gray"))
    screen.blit(text , PG.Vector2(width.x//2 - 100, 10) + zero)

    files = os.listdir("./.saves")
    saves = sorted([f for f in files if ".sim" in f])
    imgs =  sorted([f for f in files if ".png" in f])

    events = PG.event.get()
    sIndex = 0 
    for idx, (save, img) in enumerate(zip(saves, imgs)):
        index = sIndex + idx
        if (index == 4): break
            
        pos = zero+PG.Vector2((width.x//2)*(index%2)+25, 75+280*(index//2))
        rect = PG.Rect(pos.x, pos.y, width.x//2 - 50, 250)

        bg_color = PG.Color(30,30,30)
        if (rect.collidepoint(PG.mouse.get_pos())): bg_color = PG.Color(50,50,50)

        name = FONT.render(save[:len(save)-4], True, PG.Color("white"))
        _img = PG.image.load(f"./.saves/{img}")
        _img = PG.transform.scale(_img, (200,200))

        PG.draw.rect(screen, bg_color, rect)
        screen.blit(name, pos+PG.Vector2(25,222))
        screen.blit(_img, pos+PG.Vector2(25,15))

        delpos = pos + PG.Vector2(rect.width, 222) - PG.Vector2(85,0)
        delrect = PG.Rect(delpos.x, delpos.y, 60, 25)
        delete = FONT.render("delete", True, PG.Color("white"))

        del_color = PG.Color("red4")
        if (delrect.collidepoint(PG.mouse.get_pos())): del_color = PG.Color("red")

        PG.draw.rect(screen, del_color, delrect)
        screen.blit(delete, delpos+PG.Vector2(3,2))

        for event in events:
            if (event.type == PG.QUIT): sys.exit()
            if (rect.collidepoint(PG.mouse.get_pos())):
                if (event.type == PG.MOUSEBUTTONDOWN and delrect.collidepoint(event.pos)):
                    os.remove(f"./.saves/{save}")
                    os.remove(f"./.saves/{img}")
                    return

                if (event.type == PG.MOUSEBUTTONDOWN and rect.collidepoint(event.pos)):
                    global objectList, camXY, camZOOM, staticObj

                    load = pickle.load(open(f"./.saves/{save}", "rb"))
                    objectList, camXY, camZOOM, staticObj = load
                    TIMESTEP = 0
                    SIMSPEED = 1
                    SELECTED = None

                    DRAWSTATE = DState.SIM
                    break

def step(): # SimStep update
    global TIMESTEP
    sim(step_size)

    TIMESTEP += step_size

def sim(steps=1, reset=False): # Simulation
    if (reset or TIMESTEP == 0):
        for obj in objectList: obj.ResetSteps()

    collision = False
    for s in range(steps):
        if (collision): break

        for obj in objectList:
            nPos = PG.Vector2(obj.simSteps[-1].pos) + (obj.simSteps[-1].vel * PHSXTIME)/camZOOM

            nVel = PG.Vector2()
            nVel += obj.simSteps[-1].vel
            if not (staticObj == None): nVel -= staticObj.simSteps[TIMESTEP+s].vel

            for other in objectList:
                if (obj != other):
                    m = obj.mass*other.mass
                    r = ((obj.simSteps[-1].pos - other.simSteps[-1].pos)*camZOOM).magnitude()
                    F = GRAV_CONS * (m)/(r**2)

                    _dir = (obj.simSteps[-1].pos - other.simSteps[-1].pos).normalize()
                    accel = _dir * (F/obj.mass)
                    nVel -= (accel * PHSXTIME)

            obj.simSteps.append(SO.simVars(nPos,nVel))

        for obj in objectList:
            if (obj.Collides(s, objectList, camZOOM) != None):
                collision = True
                break
                
WSADKeysPressed = [False,False,False,False] 
def WSADmoveKeys(event): # Cam movement keys
    global WSADKeysPressed
    if (event.type == PG.KEYUP):
        if event.key == PG.K_w:
            WSADKeysPressed[0] = False
        if event.key == PG.K_s:
            WSADKeysPressed[1] = False
        if event.key == PG.K_a:
            WSADKeysPressed[2] = False
        if event.key == PG.K_d:
            WSADKeysPressed[3] = False
        
    if (event.type == PG.KEYDOWN):
        if event.key == PG.K_w:
            WSADKeysPressed[0] = True
        if event.key == PG.K_s:
            WSADKeysPressed[1] = True
        if event.key == PG.K_a:
            WSADKeysPressed[2] = True
        if event.key == PG.K_d:
            WSADKeysPressed[3] = True

def camMovement(): # Cam movement
    if not (SELECTED):
        if (WSADKeysPressed[0]): camXY[1] += camMoveSpeed
        if (WSADKeysPressed[1]): camXY[1] -= camMoveSpeed
        if (WSADKeysPressed[2]): camXY[0] += camMoveSpeed
        if (WSADKeysPressed[3]): camXY[0] -= camMoveSpeed

ARROWKeysPressed = [False,False,False,False] 
def arrowKeys(event): # Object movement keys
    global ARROWKeysPressed
    if (event.type == PG.KEYUP):
        if event.key == PG.K_UP:
            ARROWKeysPressed[0] = False
        if event.key == PG.K_DOWN:
            ARROWKeysPressed[1] = False
        if event.key == PG.K_LEFT:
            ARROWKeysPressed[2] = False
        if event.key == PG.K_RIGHT:
            ARROWKeysPressed[3] = False
        
    if (event.type == PG.KEYDOWN):
        if event.key == PG.K_UP:
            ARROWKeysPressed[0] = True
        if event.key == PG.K_DOWN:
            ARROWKeysPressed[1] = True
        if event.key == PG.K_LEFT:
            ARROWKeysPressed[2] = True
        if event.key == PG.K_RIGHT:
            ARROWKeysPressed[3] = True

def shortcutEvents(event): # Key shortcuts
    global PAUSED, SELECTED, camXY, SIMSPEED, step_size

    if (event.key == PG.K_SPACE):
        PAUSED = not PAUSED
        SELECTED = None

    elif (event.key == PG.K_r): 
        TIMESTEP = 0
    
    elif (event.key == PG.K_GREATER) or (event.key == PG.K_PERIOD and PG.key.get_mods() & PG.KMOD_SHIFT):
        global topBar
        SIMSPEED += 0.25
        if (SIMSPEED > 5): SIMSPEED = 5

        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        step_size = int(SIMSPEED / PHSXTIME)


    elif (event.key == PG.K_LESS) or (event.key == PG.K_COMMA and PG.key.get_mods() & PG.KMOD_SHIFT):
        SIMSPEED -= 0.25
        if (SIMSPEED < 0.25): SIMSPEED = 0.25

        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        step_size = int(SIMSPEED / PHSXTIME)

    pass

def mouseWheel(event): # Mousewheel events for zooming
    if (event.type == PG.MOUSEBUTTONDOWN):
        if (event.button == 5): # scrool down
            camZooming(0.1)
        if (event.button == 4): # scrool up
            camZooming(-0.1)

def camZooming(zoom): # Cam zooming
    global camXY, camZOOM
    oldzoom = copy.copy(camZOOM)
    camZOOM += zoom

    for obj in objectList:
        obj.ChangeCoordinates(oldzoom, camZOOM, PAUSED, forwardSimSteps)

def mouseClick(event): # Mouse click events - add, select/deselect, remove
    global SELECTED, PAUSED, TIMESTEP

    if (event.type == PG.MOUSEBUTTONDOWN):
        # LEFT CLICK
        if (PG.mouse.get_pressed()[0]):
            pos = PG.mouse.get_pos() - camXY

            # Test for mouse over object hover -> SELECT
            for obj in objectList: 
                if (obj.Contains(pos, camZOOM)):
                    SELECTED = obj
                    popup.inputs = []

                    PAUSED = True
                    return
            
            # Else add object to mouse pos -> ADD
            c = screen.get_at(PG.mouse.get_pos()) 
            if not (SELECTED) and (c == BGCOLOR):
                objectList.append(SO.Object(pos, [0,0], 1000, objectList, camZOOM))

                TIMESTEP = 0
                PAUSED = True
            
            # Test for click outside of popup -> DESELECT
            if (SELECTED and c == BGCOLOR): 
                SELECTED = None

        # RIGHT CLICK
        if (PG.mouse.get_pressed()[2]):
            pos = PG.mouse.get_pos() - camXY

            # Remove object
            for obj in objectList: 
                if (obj.Contains(pos, camZOOM)):
                    global staticObj
                    if (obj == staticObj): staticObj = None

                    objectList.remove(obj)
                    SELECTED = None

                    # Re-sim if needed
                    if (len(objectList) > 0): objectList[0].simUpdate = True

                    return

def CheckSimUpdate(): # Check if objects need sim
    global objectList, staticObj

    found = False
    for obj in objectList:
        if (obj.static):
            staticObj = obj
            found = True
            break

    if not (found): staticObj = None

    if not (staticObj == None):
        del objectList[objectList.index(staticObj)]
        objectList.insert(0, staticObj)

    for obj in objectList:
        if (obj.simUpdate):
            sim(forwardSimSteps, True)

            for _obj in objectList:
                _obj.simUpdate = False
    
def TopBarHandling(out): # Top menu bar logic
    global PAUSED, TIMESTEP, SELECTED, camXY, camZOOM, staticObj, objectList, SIMSPEED, step_size, topBar, DRAWSTATE
    if (out == None): return

    if (out == "newFile"):
        PAUSED = True
        TIMESTEP = 0
        SIMSPEED = 1
        SELECTED = None
        camXY = PG.Vector2(0,0)
        camZOOM = 1
        staticObj = None
        objectList = []
        topBar[0].SELECTED = False

    elif (out == "saveFile"):       
        global SCREENSHOT, SSNum
        try: os.mkdir("./.saves")
        except FileExistsError: pass
        
        files = sorted([f for f in os.listdir("./.saves") if ".sim" in f])

        index = 1
        for f in files: 
            if (int(f.split('_')[1].split('.')[0]) == index): index += 1 
            else: break
                
        num = index

        pickle.dump((objectList, camXY, camZOOM, staticObj), open("./.saves/save_{}.sim".format(num), "wb"))
        SCREENSHOT = True
        SSNum = num
        topBar[0].SELECTED = False


    elif (out == "loadFile"):
        try: os.mkdir("./.saves")
        except FileExistsError: pass
        global fDraw

        PAUSED = True
        SELECTED = None
        PG.mouse.set_pos(WIDTH//2,HEIGHT//2)
        DRAWSTATE = DState.LOAD
        topBar[0].SELECTED = False
        fDraw = False


    elif (out == "sim_speedUP"):
        SIMSPEED += 0.25
        if (SIMSPEED > 5): SIMSPEED = 5

        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        step_size = int(SIMSPEED / PHSXTIME)

    elif (out == "sim_speedDOWN"):
        SIMSPEED -= 0.25
        if (SIMSPEED < 0.25): SIMSPEED = 0.25

        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        step_size = int(SIMSPEED / PHSXTIME)

    elif (out == "sim_pause"):
        PAUSED = not PAUSED

    elif (out == "help"):
        pass

def SetupTopBar(): # Setting up top menu bar (at the start)
    global topBar
    topBar = [UI.TopMenu() for m in range(3)]
    topBar[0].items = ["Files"]
    topBar[0].inItems = [UI.MenuItem("New...", 'newFile'), 
                         UI.MenuItem("Save", 'saveFile'), 
                         UI.MenuItem("Load", 'loadFile')]

    topBar[1].items = ["Sim"]
    topBar[1].inItems = [UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130),
                         UI.MenuItem("Speed  +",   "sim_speedUP",   ">", (130,5), width=150),
                         UI.MenuItem("Speed  -",   "sim_speedDOWN", "<", (130,5), width=150),
                         UI.MenuItem("Reset",      "sim_Reset",     "r",     (130,5), width=150),
                         UI.MenuItem("Pause",      "sim_pause",     "space", (130,5), width=190)]

    topBar[2].items = ["Help"]

SetupTopBar()
while True:
    backgroundDrawing()

    if (PAUSED and TIMESTEP == 0): CheckSimUpdate()

    spaceObjectDrawing()

    # In the need of img for save files (draw before topbar/popup)
    if (SCREENSHOT):
        PG.image.save(screen, "./.saves/sImg_{}.png".format(SSNum))
        SCREENSHOT = False
        SSNum = -1

    if (SELECTED and PAUSED): 
        popup.Draw(screen, SELECTED) # Drawing object popup menu 
        if (TIMESTEP == 0): SELECTED.ChangeStartPos(WSADKeysPressed, 2) # Moving objects (if not in sim) 

    # Drawing top bar items
    for index, item in enumerate(topBar):
        item.Draw(screen, index)

    # Events on different DRAWSTATES - SIM/LOAD-screen/HELP-screen
    if (DRAWSTATE == DState.SIM):
        camMovement() 

        # PYGAME EVENTS
        for event in PG.event.get():
            if (event.type == PG.QUIT): sys.exit()
            if (event.type == PG.KEYDOWN): shortcutEvents(event)

            mouseClick(event)
            mouseWheel(event)
            WSADmoveKeys(event)
           
            if (SELECTED and PAUSED): popup.Event_handler(event, objectList) # If popup is active
            for tb in topBar: TopBarHandling(tb.Event_hanlder(event, topBar)) # Events on top bar

        # Physics step - stable physics steps
        if not (PAUSED):
            REALTIME += clock.get_time()/1000
            if (REALTIME > 1/FPS):
                REALTIME = 0
                step()

    elif (DRAWSTATE == DState.LOAD): 
        loadDrawing(screen)

    elif (DRAWSTATE == DState.HELP): 
        helpDrawing(screen)
        for event in PG.event.get():
            if (event.type == PG.QUIT): sys.exit()
        
    PG.display.flip()
    clock.tick(60)
