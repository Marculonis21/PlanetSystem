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

        self.size = mass**(MASS2SIZE) + 10
        self.color = PG.Color(random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))

        self.simSteps = [simVars(self.sPos, self.sVel)]

    def ResetSteps(self):    
        self.simSteps = [simVars(self.sPos, self.simSteps[0].vel)]

    def ChangeCoordinates(self, b1, b2): # LINGEBRA - Převod mezi souřadnicemi v různých bázích
        u = (self.sPos.x * PG.Vector2(b1,0) + 
             self.sPos.y * PG.Vector2(0,b1))

        a = np.array([[b2,0],
                      [0,b2]])

        b = np.array(u)
        x = np.linalg.solve(a, b)

        self.sPos = PG.Vector2(x[0],x[1])
        self.ResetSteps()

    def SetMass(self, mass):
        if (mass <= 0):
            mass = 1
            
        oldmass = self.mass

        self.mass = mass
        self.size = mass**(MASS2SIZE) + 10

    def SetColor(self, color):
        self.color = PG.Color(color[0],color[1],color[2])

    def GetStepPos(self, idx, translate):
        pos = self.simSteps[idx].pos + translate 
        return (int(pos.x),int(pos.y))

    def DrawSimPath(self, screen, offset, zoom, others):
        if (len(self.simSteps) > 10000):
            s = len(self.simSteps) - 9999
        else:
            s = 1
            
        # for step in range(s, len(self.simSteps)):
        for step in range(s, len(self.simSteps), len(self.simSteps)//100):
            p1 = self.simSteps[step].pos+offset
            # p2 = self.simSteps[step-1].pos+offset
            # PG.draw.line(screen, self.color, p1, p2, 2)

            PG.draw.circle(screen, self.color, p1, 2)

            colPos = self.Collides(step, others, zoom)
            if (colPos != None):
                PG.draw.circle(screen, PG.Color("red"), colPos+offset, self.size/zoom)
                break

    def Contains(self, pos, zoom):
        if ((self.sPos - pos).magnitude() <= self.size*zoom): return True

    def Collides(self, TIMESTEP, others, zoom):
        _pos = PG.Vector2(self.GetStepPos(TIMESTEP,PG.Vector2()))

        for obj in others:
            if (obj == self):
                continue
            
            _otherPos = PG.Vector2(obj.GetStepPos(TIMESTEP, PG.Vector2()))
            if ((_otherPos - _pos).magnitude() < (self.size/zoom) + (obj.size/zoom)):
                return _pos
                

class simVars:
    def __init__(self, position=PG.Vector2(), velocity=PG.Vector2()):
        self.pos = PG.Vector2(position)
        self.vel = PG.Vector2(velocity)
