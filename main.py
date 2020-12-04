#!/usr/bin/env python3

import pygame as PG
import sys

import SpaceObject as SO
import UIObject as UI

WIDTH = HEIGHT = 800 

PG.init()
screen = PG.display.set_mode((WIDTH,HEIGHT))
PG.display.set_caption("SCREEN")
clock = PG.time.Clock()

#EVENTS
PAUSED = True
POPUP = False

#VARIABLES
TIMESTEP = 0
REALTIME = 0

POPUP_obj = None
camXY = PG.Vector2(0,0)
staticObj = None
objectList = []
popup = UI.ObjPopup()

#CONSTANTS
PFPS = 30 
GRAV_CONS = 6.67430*10**(1)
camMoveSpeed = 10
gridSize = int(WIDTH//7)
BGCOLOR = (30,30,30)


def backgroundDrawing():
    global gridSize
    screen.fill(BGCOLOR)

    for i in range(WIDTH//gridSize + 1):
        posX = i*gridSize + camXY[0] - gridSize * (camXY[0]//gridSize)
        PG.draw.line(screen, PG.Color(50,50,50), (posX, 0), (posX, HEIGHT), 1)

    for i in range(HEIGHT//gridSize + 1):
        posY = i*gridSize + camXY[1] - gridSize * (camXY[1]//gridSize)
        PG.draw.line(screen, PG.Color(50,50,50), (0, posY), (WIDTH, posY), 1)

def spaceObjectDrawing():
    for obj in objectList:
        PG.draw.circle(screen, obj.color, obj.GetStepPos(TIMESTEP, camXY), int(obj.size))

def step():
    global TIMESTEP, camXY
    sim()
    if not (staticObj == None):
        camXY[0] = WIDTH//2 - staticObj.simSteps[TIMESTEP].pos.x
        camXY[1] = HEIGHT//2 - staticObj.simSteps[TIMESTEP].pos.y

    TIMESTEP += 1

def sim(steps=1, reset=False):
    if (not reset and len(objectList[0].simSteps) > TIMESTEP+1):
        return

    if (reset):
        for obj in objectList:
            obj.simSteps = [obj.simSteps[0]]
        
    for s in range(steps):
        for obj in objectList:
            nPos = PG.Vector2(obj.simSteps[-1].pos) + obj.simSteps[-1].vel

            nVel = PG.Vector2()
            nVel += obj.simSteps[-1].vel

            for other in objectList:
                if (obj != other):
                    m = obj.mass*other.mass
                    r = (obj.simSteps[-1].pos - other.simSteps[-1].pos).magnitude()
                    F = GRAV_CONS * (m)/(r**2)

                    _dir = (obj.simSteps[-1].pos - other.simSteps[-1].pos).normalize()

                    nVel -= (F/obj.mass)*_dir

            obj.simSteps.append(SO.simVars(nPos,nVel))


arrowKeysPressed = [False,False,False,False] # UP DOWN LEFT RIGHT
def arrowKeysHold(event):
    global arrowKeysPressed
    if not (POPUP):
        if (event.type == PG.KEYUP):
            if event.key == PG.K_UP:
                arrowKeysPressed[0] = False
            if event.key == PG.K_DOWN:
                arrowKeysPressed[1] = False
            if event.key == PG.K_LEFT:
                arrowKeysPressed[2] = False
            if event.key == PG.K_RIGHT:
                arrowKeysPressed[3] = False
            
        if (event.type == PG.KEYDOWN):
            if event.key == PG.K_UP:
                arrowKeysPressed[0] = True
            if event.key == PG.K_DOWN:
                arrowKeysPressed[1] = True
            if event.key == PG.K_LEFT:
                arrowKeysPressed[2] = True
            if event.key == PG.K_RIGHT:
                arrowKeysPressed[3] = True

def camMovement():
    if (arrowKeysPressed[0]): camXY[1] += camMoveSpeed
    if (arrowKeysPressed[1]): camXY[1] -= camMoveSpeed
    if (arrowKeysPressed[2]): camXY[0] += camMoveSpeed
    if (arrowKeysPressed[3]): camXY[0] -= camMoveSpeed

def mouseClick(event):
    global POPUP, POPUP_obj, PAUSED, TIMESTEP

    if (event.type == PG.MOUSEBUTTONDOWN):
        if (PG.mouse.get_pressed()[0]):
            pos = PG.mouse.get_pos() - camXY
                
            if not (POPUP): 
                TIMESTEP = 0
                PAUSED = True

                # Test for mouse over object hover
                for obj in objectList: 
                    if (obj.Contains(pos)):
                        POPUP = True
                        POPUP_obj = obj
                        popup.inputs = []
                        return
                        
                # Else add object to mouse pos
                objectList.append(SO.Object(pos, [0,0], 1000))

            else: 
                # Test for click outside of popup
                c = screen.get_at(PG.mouse.get_pos())
                if (c == BGCOLOR):
                    POPUP = False
                    sim(500, True)

        if (PG.mouse.get_pressed()[2] and not POPUP):
            pos = PG.mouse.get_pos() - camXY
            for obj in objectList: 
                if (obj.Contains(pos)):
                    objectList.remove(obj)
                    return
        

while True:
    # DRAW PHASE
    backgroundDrawing()
    spaceObjectDrawing()
    for obj in objectList:
        obj.DrawSimPath(screen, camXY, staticObj, WIDTH)
    if (POPUP and PAUSED): popup.Draw(screen, POPUP_obj, camXY)

    camMovement()

    # PYGAME INPUT EVENTS
    for event in PG.event.get():
        if (event.type == PG.QUIT): sys.exit()

        if event.type == PG.KEYUP: 
            if event.key == PG.K_p:
                PAUSED = not PAUSED
            if (POPUP):
                if event.key == PG.K_s:
                    POPUP = False
                    if (POPUP_obj.static):
                        POPUP_obj.static = False
                        staticObj = None
                    else:
                        for obj in objectList:
                            obj.static = False

                        POPUP_obj.static = True
                        staticObj = POPUP_obj

                        camXY[0] = WIDTH//2 - staticObj.startPosition[0]
                        camXY[1] = HEIGHT//2 - staticObj.startPosition[1]

        mouseClick(event)
        arrowKeysHold(event)

        if (POPUP and PAUSED):
            popup.Event_handler(event)

    # FRAMERATE, REDRAW, PHYSICS STEP
    if not (PAUSED):
        REALTIME += clock.get_time()/1000
        if (REALTIME > 1/PFPS):
            REALTIME = 0
            step()
            
    PG.display.flip()
    clock.tick(60)
