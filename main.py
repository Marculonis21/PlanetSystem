#!/usr/bin/env python3

import pygame as PG
import sys

import SpaceObject as SO

WIDTH = HEIGHT = 800 

PG.init()
screen = PG.display.set_mode((WIDTH,HEIGHT))
PG.display.set_caption("SCREEN")
clock = PG.time.Clock()

#EVENTS
PAUSED = True

#VARIABLES
camXY = PG.Vector2(0,0)
gridSize = 0

TIMESTEP = 0
REALTIME = 0
FPS = 24
GRAV_CONS = 6.67430*10**(1)

objectList = []

def step():
    global TIMESTEP
    sim()
    TIMESTEP += 1

def backgroundDrawing():
    global gridSize
    screen.fill((30,30,30))

    gridSize = int(WIDTH//7)
    for i in range(WIDTH//gridSize + 1):
        posX = i*gridSize + camXY[0] - gridSize * (camXY[0]//gridSize)
        PG.draw.line(screen, PG.Color(50,50,50), (posX, 0), (posX, HEIGHT), 1)

    for i in range(HEIGHT//gridSize + 1):
        posY = i*gridSize + camXY[1] - gridSize * (camXY[1]//gridSize)
        PG.draw.line(screen, PG.Color(50,50,50), (0, posY), (WIDTH, posY), 1)

def spaceObjectDrawing():
    for obj in objectList:
        PG.draw.circle(screen, PG.Color("yellow"), obj.GetStepPos(TIMESTEP, camXY), int(obj.size))

def sim():
    for obj in objectList:
        nPos = PG.Vector2(obj.simSteps[TIMESTEP].pos)
        nVel = PG.Vector2()
        nVel += obj.simSteps[-1].vel

        for nObj in objectList:
            if (obj != nObj):
                m = obj.mass*nObj.mass
                r = (obj.simSteps[TIMESTEP].pos - nObj.simSteps[TIMESTEP].pos).magnitude()
                F = GRAV_CONS * (m)/(r**2)

                _dir = (obj.simSteps[TIMESTEP].pos - nObj.simSteps[TIMESTEP].pos).normalize()

                nVel -= (F/obj.mass)*_dir

        nPos += obj.simSteps[TIMESTEP].vel

        obj.simSteps.append(SO.simVars(nPos,nVel))
        

while True:
    backgroundDrawing()
    spaceObjectDrawing()

    for event in PG.event.get():
        if event.type == PG.QUIT: sys.exit()

        if event.type == PG.KEYUP:
            if event.key == PG.K_a:
                PAUSED = True
                TIMESTEP = 0

                objectList.append(SO.Object((camXY.x+WIDTH//2+200,camXY.y+HEIGHT//2+200), (0,-5), 800, TIMESTEP))
                objectList.append(SO.Object((camXY.x+WIDTH//4,camXY.y+HEIGHT//4), (0,5), 200, TIMESTEP))
            if event.key == PG.K_p:
                PAUSED = not PAUSED

            if event.key == PG.K_RIGHT:
                camXY[0] += 100
            if event.key == PG.K_LEFT:
                camXY[0] -= 100
            if event.key == PG.K_UP:
                camXY[1] -= 100
            if event.key == PG.K_DOWN:
                camXY[1] += 100

    if not (PAUSED):
        REALTIME += clock.get_time()/1000
        if (REALTIME > 1/FPS):
            REALTIME = 0
            step()
            
    # FRAMERATE 60 and REDRAW
    PG.display.flip()
    clock.tick(60)
