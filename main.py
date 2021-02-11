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

# Pygame init
WIDTH = HEIGHT = 800 

PG.init()
screen = PG.display.set_mode((WIDTH,HEIGHT))
PG.display.set_caption("PlanetSystem")
clock = PG.time.Clock()

PG.mouse.set_cursor(*PG.cursors.diamond)

#EVENTS
PAUSED = True

class DState(Enum):
    SIM = 1
    LOAD = 2
    ABOUT = 3

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
startCamPos = PG.Vector2(0,0)
camXY = copy.copy(startCamPos)
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
SMALL = PG.font.SysFont('Arial', 14, False, False)

#CONSTANTS
FPS = 30 
GRAV_CONS = 6.67430*10**(1)
camMoveSpeed = 15
BGCOLOR = (10,10,10)

def backgroundDrawing(): # Redraw background
    screen.fill(BGCOLOR)

def spaceObjectDrawing(): # Drawing space objects and its paths
    for obj in objectList: # Sim path draw
        obj.DrawSimPath(screen, camXY, camZOOM, forwardSimSteps, PAUSED, TIMESTEP, objectList)

    for obj in objectList: # Object draw
        pos = obj.GetStepPos(TIMESTEP, camXY)
        if (SELECTED == obj):
            PG.draw.circle(screen, PG.Color(100,100,100), pos, int(obj.size/camZOOM)+10, 1)
        PG.draw.circle(screen, obj.color, pos, int(obj.size/camZOOM))

loadSIndex = 0 # Load start index - for LOADMENU pages
fDraw = False
def loadDrawing(screen): # Drawing/Logic LOADMENU
    global DRAWSTATE, fDraw, loadSIndex

    # Load own events
    events = PG.event.get()

    # Main rect drawing and dimensions
    mainRect = PG.Rect(WIDTH//8, HEIGHT//10, 6*WIDTH//8, 5*HEIGHT//6)
    PG.draw.rect(screen, PG.Color(40,40,40), mainRect, border_radius=20)

    zero = PG.Vector2(WIDTH//8, HEIGHT//10)
    width = PG.Vector2(6*WIDTH//8, 0) 
    height = PG.Vector2(0, 5*HEIGHT//6) 

    # Test if cursor inside window (problem with first draw cycle -> fDraw check)
    if not (mainRect.collidepoint(PG.mouse.get_pos())) and (fDraw): DRAWSTATE = DState.SIM
    fDraw = True

    # File loading
    text = HEADER.render("SAVE FILES", True, PG.Color("gray"))
    screen.blit(text , PG.Vector2(width.x//2 - 100, 10) + zero)

    files = os.listdir("./.saves")
    saves = sorted([f for f in files if ".sim" in f])
    imgs =  sorted([f for f in files if ".png" in f])

    # Arrow drawing + logic for mouse hover and clicks
    arrowUp   = HEADER.render("/\\", True, PG.Color("gray"))
    arrowDown = HEADER.render("\\/", True, PG.Color("gray"))
    arrowUpPos = PG.Vector2(width.x//2 - 45, height.y-45) + zero
    arrowDownPos = PG.Vector2(width.x//2 + 15, height.y-45) + zero

    UpRect = PG.Rect(arrowUpPos-PG.Vector2(10,5), (40, 40), border_radius=3)
    DownRect = PG.Rect(arrowDownPos-PG.Vector2(10,5), (40, 40), border_radius=3)

    bg_color = PG.Color(30,30,30)
    if not (loadSIndex == 0):
        if (UpRect.collidepoint(PG.mouse.get_pos())):
            bg_color = PG.Color(50,50,50)
            for event in events: 
                if (event.type == PG.MOUSEBUTTONDOWN): loadSIndex -= 1
    else: arrowUp = HEADER.render("/\\", True, PG.Color(45,45,45)) 
    PG.draw.rect(screen, bg_color, UpRect)

    bg_color = PG.Color(30,30,30)
    if not ((loadSIndex+1)*4 >= len(saves)):
        if (DownRect.collidepoint(PG.mouse.get_pos())): 
            bg_color = PG.Color(50,50,50)
            for event in events: 
                if (event.type == PG.MOUSEBUTTONDOWN): loadSIndex += 1
    else: arrowDown = HEADER.render("\\/", True, PG.Color(40,40,40))
    PG.draw.rect(screen, bg_color, DownRect)

    screen.blit(arrowUp, arrowUpPos)
    screen.blit(arrowDown, arrowDownPos)

    # Showing save files
    _zip = list(zip(saves, imgs))
    for idx in range(loadSIndex*4, len(_zip)):
        save = _zip[idx][0]
        img = _zip[idx][1]

        index = idx - loadSIndex*4
        if (index == 4): break # show 4 max on a page
            
        # Rect pos, dimensions, mouse logic
        pos = zero+PG.Vector2((width.x//2)*(index%2)+25, 75+280*(index//2))
        rect = PG.Rect(pos.x, pos.y, width.x//2 - 50, 250)

        bg_color = PG.Color(30,30,30)
        if (rect.collidepoint(PG.mouse.get_pos())): bg_color = PG.Color(50,50,50)

        # Rect drawing
        name = FONT.render(save[:len(save)-4], True, PG.Color("white"))
        _img = PG.image.load(f"./.saves/{img}")
        _img = PG.transform.scale(_img, (200,200))

        PG.draw.rect(screen, bg_color, rect)
        screen.blit(name, pos+PG.Vector2(25,222))
        screen.blit(_img, pos+PG.Vector2(25,15))

        # Button logic
        if not ("preset" in save): # If delete button should be drawn (presets can't be removed)
            delrect = PG.Rect(delpos.x, delpos.y, 60, 25)
            delete = FONT.render("delete", True, PG.Color("white"))

            del_color = PG.Color("red4")
            if (delrect.collidepoint(PG.mouse.get_pos())): del_color = PG.Color("red")

            PG.draw.rect(screen, del_color, delrect)
            screen.blit(delete, delpos+PG.Vector2(3,2))

        for event in events:
            if (event.type == PG.QUIT): sys.exit()

            if (rect.collidepoint(PG.mouse.get_pos())):
                if not ("preset" in save):
                    if (event.type == PG.MOUSEBUTTONDOWN and delrect.collidepoint(event.pos)): # Delete button pressed
                        os.remove(f"./.saves/{save}")
                        os.remove(f"./.saves/{img}")

                        if (loadSIndex > 0 and (len(saves)-1)%4 == 0):
                            loadSIndex -= 1
                        return

                if (event.type == PG.MOUSEBUTTONDOWN and rect.collidepoint(event.pos)): # Save file pressed -> Load
                    global objectList, camXY, startCamPos, camZOOM, staticObj, TIMESTEP, SIMSPEED, SELECTED # Set everything as saved (Timestep, simspeed, selected = default)
                    load = pickle.load(open(f"./.saves/{save}", "rb"))
                    objectList, startCamPos, camZOOM, staticObj = load
                    camXY = copy.copy(startCamPos)
                    TIMESTEP = 0
                    SIMSPEED = 1
                    SELECTED = None

                    DRAWSTATE = DState.SIM
                    return

def aboutDrawing(screen): # Drawing/Logic ABOUTMENU
    global DRAWSTATE, fDraw

    # Main rect drawing and dimensions
    mainRect = PG.Rect(WIDTH//8, HEIGHT//10, 6*WIDTH//8, 5*HEIGHT//6)
    PG.draw.rect(screen, PG.Color(40,40,40), mainRect, border_radius=20)

    zero = PG.Vector2(WIDTH//8, HEIGHT//10)
    width = PG.Vector2(6*WIDTH//8, 0) 
    height = PG.Vector2(0, 4*HEIGHT//6) 

    # Test if cursor inside window (problem with first draw cycle -> fDraw check)
    if not (mainRect.collidepoint(PG.mouse.get_pos())) and (fDraw): DRAWSTATE = DState.SIM
    fDraw = True

    # Text setup and draw
    header = HEADER.render("ABOUT", True, PG.Color("gray"))
    screen.blit(header, PG.Vector2(30, 40) + zero)

    mainText = ["  This application gives user the possibility to design",
                "  his own planetary system and to see it work in ",
                "  proper physical simulation.",
                "",
                "Controls:",
                "  Left mouse button (free space) - Create planet",
                "  Left mouse button (planet) - Show planet properties", 
                "", 
                "  Right mouse button (planet) - Remove planet", 
                "", 
                "  Arrow keys (when planet selected) - Move planet in space", 
                "", 
                "  WSAD keys - Camera movement", 
                "  Mousewheel - Camera zoom", 
                "", 
                "  Space - Start simulation", 
                "  R - Reset simulation to start", 
                ]

    lower = ["The app was developed as a final project for subject Programming 1 - MFF UK",
             "by Marek Bečvář (ZS 2020/21)."]

    # Pygame text drawing line by line
    for line in range(len(mainText)):
        text = FONT.render(mainText[line], True, PG.Color("gray"))
        screen.blit(text, PG.Vector2(30,90+line*25) + zero)

    for line in range(len(lower)):
        text = SMALL.render(lower[line], True, PG.Color("gray"))
        screen.blit(text, PG.Vector2(30,600+line*25) + zero)
    
def step(): # SimStep update
    global TIMESTEP
    sim(step_size)

    TIMESTEP += step_size

def sim(steps=1, reset=False): # Simulation
    if (reset or TIMESTEP == 0): # When editing -> resets constantly for updates
        for obj in objectList: obj.ResetSteps()

    collision = False
    for s in range(steps): # Each object has to be simulated before making another step
        if (collision): break # if last step collided -> stop

        for obj in objectList: # Loop through objects and calculate them against all other object (not cheap)
            # New object position taken from last step position and velocity,
            # we are calculating velocity for the next step

            nPos = PG.Vector2(obj.simSteps[-1].pos) + (obj.simSteps[-1].vel * PHSXTIME)/camZOOM

            # New velocity vector - takes the current object velocity
            nVel = PG.Vector2()
            nVel += obj.simSteps[-1].vel

            # Sim mode - static central object selected (staticObj is always
            # first in the objectList)
            if not (staticObj == None): nVel -= staticObj.simSteps[TIMESTEP+s].vel 
            
            # Calculate against every other object
            for other in objectList:
                if (obj != other):
                    m = obj.mass*other.mass
                    r = ((obj.simSteps[-1].pos - other.simSteps[-1].pos)*camZOOM).magnitude()
                    F = GRAV_CONS * (m)/(r**2)

                    _dir = (obj.simSteps[-1].pos - other.simSteps[-1].pos).normalize()
                    accel = _dir * (F/obj.mass)
                    nVel -= (accel * PHSXTIME)

            obj.simSteps.append(SO.simVars(nPos,nVel))

        if (reset): # while editing test for collisions on all objects (overlaps)
            for obj in objectList:
                if (obj.Collides(s, objectList, camZOOM) != None):
                    collision = True
                    break
                
def CheckSimUpdate(): # Checking if objects need new sim update (saves a lot)
    global objectList, staticObj

    # Check if there are any new static objects (move static object to index 0)
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

    # Checking simUpdate variable on objects
    for obj in objectList:
        if (obj.simUpdate):
            TIMESTEP = 0
            sim(forwardSimSteps, True)

            for _obj in objectList:
                _obj.simUpdate = False
            break

WSADKeysPressed = [False,False,False,False] 
def WSADmoveKeys(event): # Cam movement keys
    global WSADKeysPressed
    # This enables continuous movement
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
def ARROWmoveKeys(event): # Object movement keys
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

def shortcutEvents(event, mods): # Key shortcuts
    global PAUSED, TIMESTEP, SELECTED, camXY, SIMSPEED, step_size, topBar

    if (event.key == PG.K_SPACE): # PLAY/PAUSE
        PAUSED = not PAUSED
        SELECTED = None

    if (event.key == PG.K_DELETE and mods != "delete"): # REMOVE SELECTED
        if not (SELECTED == None):
            global staticObj
            if (SELECTED == staticObj): staticObj = None
            objectList.remove(SELECTED)
            SELECTED = None

            # Re-sim if needed
            if (len(objectList) > 0): objectList[0].simUpdate = True

    elif (event.key == PG.K_r): # RESET SIM
        PAUSED = True
        TIMESTEP = 0
        camXY = copy.copy(startCamPos)
        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        for obj in objectList: obj.ResetSteps()
    
    elif (event.key == PG.K_GREATER) or (event.key == PG.K_PERIOD and PG.key.get_mods() & PG.KMOD_SHIFT): # SIM SPEED UP
        SIMSPEED += 0.25
        if (SIMSPEED > 5): SIMSPEED = 5

        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        step_size = int(SIMSPEED / PHSXTIME)


    elif (event.key == PG.K_LESS) or (event.key == PG.K_COMMA and PG.key.get_mods() & PG.KMOD_SHIFT): # SIM SPEED DOWN
        SIMSPEED -= 0.25
        if (SIMSPEED < 0.25): SIMSPEED = 0.25

        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        step_size = int(SIMSPEED / PHSXTIME)

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

    # Change coordinates of objects - linear algebra forever!
    for obj in objectList:
        obj.ChangeCoordinates(oldzoom, camZOOM, TIMESTEP, PAUSED, forwardSimSteps)

def mouseClick(event): # Mouse click events - add, select/deselect, remove
    global SELECTED, PAUSED, TIMESTEP

    if (event.type == PG.MOUSEBUTTONDOWN): # <- handle only one press (no continuous)
        pos = PG.mouse.get_pos()

        # LEFT CLICK
        if (PG.mouse.get_pressed()[0]):
            # Test for mouse over object hover -> SELECT
            for obj in objectList: 
                if (obj.Contains(pos, TIMESTEP, camXY, camZOOM)):
                    SELECTED = obj
                    popup.inputs = []

                    TIMESTEP = 0
                    PAUSED = True
                    return
            
            # Else (free space) add object to mouse pos -> ADD
            c = screen.get_at(PG.mouse.get_pos()) 
            if not (SELECTED) and (c == BGCOLOR):
                # pos - camXY = shown mouse position without translation
                objectList.append(SO.Object(pos - camXY, [0,0], 1000, objectList, camZOOM))

                TIMESTEP = 0
                PAUSED = True
            
            # Test for click outside of popup window -> DESELECT
            if (SELECTED and c == BGCOLOR): 
                SELECTED = None

        # RIGHT CLICK
        if (PG.mouse.get_pressed()[2]):
            # Click on object -> REMOVE
            for obj in objectList: 
                if (obj.Contains(pos, TIMESTEP, camXY, camZOOM)):
                    global staticObj
                    if (obj == staticObj): staticObj = None

                    objectList.remove(obj)
                    SELECTED = None

                    # Re-sim if needed
                    if (len(objectList) > 0): objectList[0].simUpdate = True
                    break

def TopBarHandling(out): # Top menu bar logic
    global PAUSED, TIMESTEP, SELECTED, camXY, startCamPos, camZOOM, staticObj, objectList, SIMSPEED, step_size, topBar, DRAWSTATE, fDraw, loadSIndex
    if (out == None): return

    # Logic after clicking some of the topbar buttons 
    if (out == "newFile"):
        PAUSED = True
        TIMESTEP = 0
        SIMSPEED = 1
        SELECTED = None
        startCamPos = PG.Vector2(0,0)
        camXY = copy.copy(startCamPos)
        camZOOM = 1
        staticObj = None
        objectList = []
        topBar[0].SELECTED = False

    elif (out == "saveFile"):       
        global SCREENSHOT, SSNum
        try: os.mkdir("./.saves")
        except FileExistsError: pass
        
        # *asymptotic time complexity cries*
        files = sorted([f for f in os.listdir("./.saves") if "save" in f and ".sim" in f]) 

        index = 1
        for f in files: 
            if (int(f.split('_')[1].split('.')[0]) == index): index += 1 
            else: break
                
        # using pickle for saving/loading
        pickle.dump((objectList, camXY, camZOOM, staticObj), open("./.saves/save_{}.sim".format(index), "wb"))
        # next frame the screenshot will be saved
        SCREENSHOT = True
        SSNum = index
        topBar[0].SELECTED = False

    elif (out == "loadFile"):
        try: os.mkdir("./.saves")
        except FileExistsError: pass

        # prepares for opening LOADMENU
        PAUSED = True
        SELECTED = None
        PG.mouse.set_pos(WIDTH//2,HEIGHT//2)
        DRAWSTATE = DState.LOAD
        topBar[0].SELECTED = False
        fDraw = False
        loadSIndex = 0

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
        topBar[1].SELECTED = False

    elif (out == "sim_reset"):
        PAUSED = True
        TIMESTEP = 0
        topBar[1].SELECTED = False
        topBar[1].inItems[0] = UI.MenuItem("Speed: {}".format(SIMSPEED), None, width=130)

        for obj in objectList: obj.ResetSteps()

    elif (out == "about"):
        PAUSED = True
        SELECTED = None
        PG.mouse.set_pos(WIDTH//2,HEIGHT//2)
        DRAWSTATE = DState.ABOUT
        fDraw = False

def SetupTopBar(): # Setting up top menu bar (at the start)
    global topBar

    topBar = [UI.TopMenu() for m in range(3)]
    topBar[0].items = ["Files"]
    # MenuItem class - (text, pointer, shortcut, shortcut offset, width)
    topBar[0].inItems = [UI.MenuItem("New...", 'newFile',  width=90), 
                         UI.MenuItem("Save",   'saveFile', width=90), 
                         UI.MenuItem("Load",   'loadFile', width=90)]
    topBar[0].borderRect = PG.Rect(0,0,120,130)

    topBar[1].items = ["Sim"]
    topBar[1].itemPos = PG.Vector2(21, 5)
    topBar[1].inItems = [UI.MenuItem("Speed: {}".format(SIMSPEED),                    width=130),
                         UI.MenuItem("Speed  +",   "sim_speedUP",   ">",     (130,5), width=150),
                         UI.MenuItem("Speed  -",   "sim_speedDOWN", "<",     (130,5), width=150),
                         UI.MenuItem("Reset",      "sim_reset",     "r",     (130,5), width=150),
                         UI.MenuItem("Pause",      "sim_pause",     "space", (130,5), width=190)]
    topBar[1].borderRect = PG.Rect(90,0,230,190)

    topBar[2].items = ["About"]
    topBar[2].itemPos = PG.Vector2(13, 5)

SetupTopBar()
while True: # Main app loop - ends on Pygame quit event
    backgroundDrawing()

    print(PAUSED and TIMESTEP == 0)
    # While editing always check for needed sim updates
    if (PAUSED and TIMESTEP == 0): CheckSimUpdate()

    spaceObjectDrawing()

    # In the need of img for save files (draw before topbar/popup)
    if (SCREENSHOT):
        PG.image.save(screen, "./.saves/sImg_{}.png".format(SSNum))
        SCREENSHOT = False
        SSNum = -1

    if (SELECTED and PAUSED): 
        popup.Draw(screen, SELECTED) # Drawing object popup menu 
        if (TIMESTEP == 0): SELECTED.ChangeStartPos(ARROWKeysPressed, 2) # Moving objects (if not in sim) 

    # Drawing top bar items
    for index, item in enumerate(topBar):
        item.Draw(screen, index)

    # Events on different DRAWSTATES - SIM/LOAD-screen/ABOUT-screen
    if (DRAWSTATE == DState.SIM):
        camMovement() 

        # PYGAME EVENTS
        arrowsOnText = False
        out = None
        for event in PG.event.get():
            if (event.type == PG.QUIT): sys.exit()
            if (SELECTED and PAUSED): # If popup is active
                out = popup.Event_handler(event, objectList)
                arrowsOnText = True if out == "arrows" else False
            if (event.type == PG.KEYDOWN): shortcutEvents(event, out)
            
            # Events on top bar
            for tb in topBar: TopBarHandling(tb.Event_hanlder(event, topBar)) 

            mouseClick(event)
            mouseWheel(event)
            WSADmoveKeys(event)
            if not (arrowsOnText): ARROWmoveKeys(event)

        # Physics step - stable physics steps
        if not (PAUSED):
            REALTIME += clock.get_time()/1000
            if (REALTIME > 1/FPS):
                REALTIME = 0
                step()

    elif (DRAWSTATE == DState.LOAD): 
        loadDrawing(screen)

    elif (DRAWSTATE == DState.ABOUT): 
        aboutDrawing(screen)
        for event in PG.event.get():
            if (event.type == PG.QUIT): sys.exit()
        
    PG.display.flip()
    clock.tick(60)
