#!/usr/bin/env python3
import copy
import numpy as np
import pygame as PG
import random

MASS2SIZE = 1/3

class Object:
    def __init__(self, startPosition, startVelocity, mass, _list, zoom):
        self.sPos = PG.Vector2(startPosition)
        self.sVel = startVelocity

        self.mass = mass

        self.size = mass**(MASS2SIZE) + 20
        self.color = PG.Color(random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))

        self.simSteps = [simVars(self.sPos, self.sVel)]
        self.static = False

    def ResetSteps(self):    
        self.simSteps = [simVars(self.sPos, self.simSteps[0].vel)]

    def __ChangeCoordinates__(self, b1, b2): # LINGEBRA - Převod mezi souřadnicemi v různých bázích
        # from old to kanon base
        u = (self.sPos.x * b1[0] + 
             self.sPos.y * b1[1])

        a = np.array([[b2[0].x,b2[1].x], 
                      [b2[0].y,b2[1].y]])

        b = np.array(u)
        x = np.linalg.solve(a, b)

        self.sPos = PG.Vector2(x[0],x[1])
        self.ResetSteps()
        print(self.sPos)

    def ChangeCoordinates(self, b1, b2): # LINGEBRA - Převod mezi souřadnicemi v různých bázích
        # from old to kanon base
        u = (self.sPos.x * PG.Vector2(b1,0) + 
             self.sPos.y * PG.Vector2(0,b1))

        a = np.array([[b2,0],
                      [0,b2]])

        b = np.array(u)
        x = np.linalg.solve(a, b)

        self.sPos = PG.Vector2(x[0],x[1])
        self.ResetSteps()
        print(self.sPos)


    def SetMass(self, mass):
        oldmass = self.mass

        self.mass = mass
        self.size = mass**(MASS2SIZE) + 20

    def SetColor(self, color):
        self.color = PG.Color(color[0],color[1],color[2])

    def GetStepPos(self, idx, translate):
        pos = self.simSteps[idx].pos + translate 
        return (int(pos.x),int(pos.y))

    def DrawSimPath(self, screen, offset, static, w):
        if (len(self.simSteps) > 5000):
            s = len(self.simSteps) - 4999
        else:
            s = 1
            
        for step in range(s, len(self.simSteps)):
            # if not (static == None):
            #     p1 = (self.simSteps[step].pos+offset-static.simSteps[step].pos)+static.simSteps[0].pos
            #     p2 = (self.simSteps[step-1].pos+offset-static.simSteps[step-1].pos)+static.simSteps[0].pos
            # else:
            p1 = self.simSteps[step].pos+offset
            p2 = self.simSteps[step-1].pos+offset

            PG.draw.line(screen, self.color, p1, p2, 2)

    def Contains(self, pos, camZOOM):
        if ((self.sPos - pos).magnitude() <= self.size*camZOOM): return True

class simVars:
    def __init__(self, position=PG.Vector2(), velocity=PG.Vector2()):
        self.pos = PG.Vector2(position)
        self.vel = PG.Vector2(velocity)
        
