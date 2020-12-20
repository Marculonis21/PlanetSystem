#!/usr/bin/env python3

import copy
import numpy as np
import pygame as PG
import sys

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

#VARIABLES
REALTIME = 0
TIMESTEP = 0

PHSXTIME = 0.005
SIMSPEED = 1
step_size = int(SIMSPEED / PHSXTIME)

SELECTED = None
camXY = PG.Vector2(0,0)
camZOOM = 1

staticObj = None
objectList = []
popup = UI.ObjPopup()

#CONSTANTS
FPS = 30 
GRAV_CONS = 6.67430*10**(1)
camMoveSpeed = 15
gridSize = int(WIDTH//7)
BGCOLOR = (10,10,10)

def backgroundDrawing():
    global gridSize
    screen.fill(BGCOLOR)

def spaceObjectDrawing():
    for obj in objectList:
        pos = obj.GetStepPos(TIMESTEP, camXY)
        if (SELECTED == obj):
            PG.draw.circle(screen, PG.Color(100,100,100), pos, int(obj.size/camZOOM)+10, 1)
        PG.draw.circle(screen, obj.color, pos, int(obj.size/camZOOM))

def step():
    global TIMESTEP
    sim(step_size)

    TIMESTEP += step_size

def sim(steps=1, reset=False):
    if (reset or TIMESTEP == 0):
        for obj in objectList: obj.ResetSteps()
        
    for s in range(steps):
        for obj in objectList:
            nPos = PG.Vector2(obj.simSteps[-1].pos) + (obj.simSteps[-1].vel * PHSXTIME)/camZOOM

            nVel = PG.Vector2()
            nVel += obj.simSteps[-1].vel

            for other in objectList:
                if (obj != other):
                    m = obj.mass*other.mass
                    r = ((obj.simSteps[-1].pos - other.simSteps[-1].pos)*camZOOM).magnitude()
                    F = GRAV_CONS * (m)/(r**2)

                    _dir = (obj.simSteps[-1].pos - other.simSteps[-1].pos).normalize()

                    accel = _dir * (F/obj.mass)

                    nVel -= (accel * PHSXTIME)

            obj.simSteps.append(SO.simVars(nPos,nVel))


WSADKeysPressed = [False,False,False,False] 
def WSADmoveKeys(event):
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

def camMovement():
    if (WSADKeysPressed[0]): camXY[1] += camMoveSpeed
    if (WSADKeysPressed[1]): camXY[1] -= camMoveSpeed
    if (WSADKeysPressed[2]): camXY[0] += camMoveSpeed
    if (WSADKeysPressed[3]): camXY[0] -= camMoveSpeed

def mouseWheel(event):
    if (event.type == PG.MOUSEBUTTONDOWN):
        if (event.button == 5): # scrool down
            camZooming(0.1)
        if (event.button == 4): # scrool up
            camZooming(-0.1)

def camZooming(zoom):
    global camXY, camZOOM
    oldzoom = copy.copy(camZOOM)
    camZOOM += zoom

    # solve how to move well

    for obj in objectList:
        obj.ChangeCoordinates(oldzoom, camZOOM)

def mouseClick(event):
    global SELECTED, PAUSED, TIMESTEP

    if (event.type == PG.MOUSEBUTTONDOWN):
        if (PG.mouse.get_pressed()[0]):
            pos = PG.mouse.get_pos() - camXY
                
            # Test for mouse over object hover
            for obj in objectList: 
                if (obj.Contains(pos, camZOOM)):
                    SELECTED = obj
                    popup.inputs = []
                    return

            TIMESTEP = 0
            PAUSED = True
                        
            if not (SELECTED):
                # Else add object to mouse pos
                objectList.append(SO.Object(pos, [0,0], 1000, objectList, camZOOM))

            if (SELECTED):
                # Test for click outside of popup
                c = screen.get_at(PG.mouse.get_pos())
                if (c == BGCOLOR):
                    SELECTED = None

        if (PG.mouse.get_pressed()[2] and not SELECTED):
            pos = PG.mouse.get_pos() - camXY
            for obj in objectList: 
                if (obj.Contains(pos, camZOOM)):
                    objectList.remove(obj)
                    return

while True:
    # DRAW PHASE
    backgroundDrawing()

    # Problémy, simuluju a kreslím každé kolo, i když není potřeba = PAIN
    if (PAUSED and TIMESTEP == 0):
        sim(5000, True)
    if (PAUSED):
        for obj in objectList:
            obj.DrawSimPath(screen, camXY, camZOOM, objectList)

    spaceObjectDrawing()

    if (SELECTED and PAUSED): popup.Draw(screen, SELECTED)

    # PYGAME INPUT EVENTS
    camMovement()
    for event in PG.event.get():
        if (event.type == PG.QUIT): sys.exit()
        if (event.type == PG.KEYDOWN): 
            if (event.key == PG.K_SPACE):
                PAUSED = not PAUSED
                SELECTED = None

        mouseClick(event)
        WSADmoveKeys(event)
        mouseWheel(event)

        if (SELECTED and PAUSED):
            popup.Event_handler(event)

        
    # FRAMERATE, REDRAW, PHYSICS STEP
    if not (PAUSED):
        REALTIME += clock.get_time()/1000
        if (REALTIME > 1/FPS):
            REALTIME = 0
            step()
            
    PG.display.flip()
    clock.tick(60)
